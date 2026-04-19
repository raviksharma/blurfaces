"""blurfaces — Detect and censor faces in video."""

import json, os, subprocess, sys, tempfile
import click, cv2, numpy as np
from tqdm import tqdm

# -- Video I/O (ffmpeg) -----------------------------------------------------

def video_meta(path):
    """Probe *path* and return (w, h, nframes, fps, has_audio)."""
    info = json.loads(subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", "-show_streams", path],
        capture_output=True, text=True, check=True,
    ).stdout)
    streams = info.get("streams", [])
    has_audio = any(s["codec_type"] == "audio" for s in streams)
    vs = next((s for s in streams if s["codec_type"] == "video"), None)
    if vs is None:
        raise ValueError("no video stream found")
    num, den = (int(x) for x in vs["r_frame_rate"].split("/"))
    return int(vs["width"]), int(vs["height"]), int(vs.get("nb_frames", 0)), num / den, has_audio


def frame_reader(path, w, h):
    """Yield BGR numpy frames via ffmpeg pipe."""
    proc = subprocess.Popen(
        ["ffmpeg", "-i", path, "-f", "rawvideo", "-pix_fmt", "bgr24", "-v", "quiet", "pipe:1"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    nbytes = w * h * 3
    try:
        while (raw := proc.stdout.read(nbytes)) and len(raw) == nbytes:
            yield np.frombuffer(raw, np.uint8).reshape(h, w, 3).copy()
    finally:
        proc.stdout.close()
        proc.wait()


def frame_writer(path, w, h, fps):
    """Return a Popen whose stdin accepts raw BGR bytes."""
    return subprocess.Popen(
        ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
         "-s", f"{w}x{h}", "-r", str(fps), "-i", "pipe:0",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-v", "quiet", path],
        stdin=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )


def mux_audio(video_path, original_path, output_path):
    """Copy audio from *original_path* into the processed video."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-i", original_path,
         "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0",
         "-v", "quiet", output_path],
        check=True,
    )


# -- Face analysis (insightface) --------------------------------------------

_app = None

def get_app(model_pack, det_size):
    global _app
    if _app is None:
        import insightface
        _app = insightface.app.FaceAnalysis(name=model_pack)
        _app.prepare(ctx_id=0, det_size=(det_size, det_size))
    return _app


def load_reference(path, model_pack, det_size):
    """Return the normed embedding of the first face in *path*."""
    img = cv2.imread(path)
    if img is None:
        sys.exit(f"Error: cannot read image '{path}'")
    faces = get_app(model_pack, det_size).get(img)
    if not faces:
        sys.exit(f"Error: no face detected in '{path}'")
    return faces[0].normed_embedding


# -- Censoring ---------------------------------------------------------------

def apply_censor(frame, bbox, method):
    x1, y1, x2, y2 = (max(0, int(v)) for v in bbox)
    fh, fw = frame.shape[:2]
    x2, y2 = min(fw, x2), min(fh, y2)
    if x2 <= x1 or y2 <= y1:
        return
    roi = frame[y1:y2, x1:x2]
    if method == "blackout":
        frame[y1:y2, x1:x2] = 0
    elif method == "pixel":
        rh, rw = roi.shape[:2]
        small = cv2.resize(roi, (8, 8), interpolation=cv2.INTER_AREA)
        frame[y1:y2, x1:x2] = cv2.resize(small, (rw, rh), interpolation=cv2.INTER_AREA)
    elif method == "bar":
        rh = y2 - y1
        bar_top = y1 + int(rh * 0.3)
        bar_bot = y1 + int(rh * 0.55)
        frame[bar_top:bar_bot, x1:x2] = 0
    else:
        frame[y1:y2, x1:x2] = cv2.GaussianBlur(roi, (0, 0), 30)


# -- CLI ---------------------------------------------------------------------

@click.command("blurfaces")
@click.argument("video", type=click.Path(exists=True))
@click.option("--mode", default="all", type=click.Choice(["all", "target", "exclude"], case_sensitive=False),
              help="Who to censor: 'all' every face, 'target' only the --face person, 'exclude' everyone but --face.")
@click.option("--blur", "blur_method", default="blur", type=click.Choice(["blur", "blackout", "pixel", "bar"], case_sensitive=False),
              help="How to censor: 'blur' smooth blur, 'blackout' solid black, 'pixel' blocky mosaic, 'bar' black bar across the eyes.")
@click.option("--face", "face_file", type=click.Path(exists=True), default=None,
              help="Photo of the target face. Required when --mode is 'target' or 'exclude'.")
@click.option("--model", default="buffalo_l", type=click.Choice(["buffalo_l", "buffalo_s", "buffalo_sc"], case_sensitive=False),
              help="Accuracy vs speed: 'buffalo_l' most accurate, 'buffalo_s' balanced, 'buffalo_sc' fastest.")
@click.option("--det-size", default=640, type=int,
              help="Face detection resolution in px. Try 320 for speed, 960 for small/distant faces.")
@click.option("--threshold", default=0.45, type=float,
              help="How strict face matching is (0-1). Lower = stricter. Only used with --mode target/exclude.")
@click.option("-o", "--output", "output_path", default=None,
              help="Where to save the result. Defaults to 'out.<ext>' in the current directory.")
def cli(video, mode, blur_method, face_file, model, det_size, threshold, output_path):
    """Detect and censor faces in VIDEO.

    \b
    Quick start:
      blurfaces video.mp4                          Blur all faces
      blurfaces video.mp4 --face me.jpg --mode target  Blur only one person
      blurfaces video.mp4 --blur pixel              Use pixelation instead
    """
    if mode in ("target", "exclude") and not face_file:
        raise click.UsageError("--face is required for mode 'target' or 'exclude'")

    w, h, nframes, fps, has_aud = video_meta(video)
    click.echo(f"Video: {w}×{h}, {fps:.2f} fps, ~{nframes} frames, audio={'yes' if has_aud else 'no'}")

    ref = load_reference(face_file, model, det_size) if mode in ("target", "exclude") else None

    is_match = lambda f: float(np.dot(f.normed_embedding, ref)) >= threshold
    should_censor = {"all": lambda f: True, "target": is_match, "exclude": lambda f: not is_match(f)}[mode]

    out_file = output_path or "out" + os.path.splitext(video)[1]
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp4")
    os.close(tmp_fd)

    try:
        writer = frame_writer(tmp_path, w, h, fps)
        processed = 0
        for frame in tqdm(frame_reader(video, w, h), total=nframes or None, desc="Processing"):
            for f in get_app(model, det_size).get(frame):
                if should_censor(f):
                    apply_censor(frame, f.bbox, blur_method)
            writer.stdin.write(frame.tobytes())
            processed += 1
        writer.stdin.close()
        writer.wait()

        if has_aud:
            mux_audio(tmp_path, video, out_file)
        else:
            os.replace(tmp_path, out_file)
            tmp_path = None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    click.echo(f"Done — {processed} frames → {out_file}")


if __name__ == "__main__":
    cli()

