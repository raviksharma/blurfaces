# blurfaces

Detect and censor faces in video using [insightface](https://github.com/deepinsight/insightface) and ffmpeg.

## Samples

| Input | Blur (default) |
|-------|----------------|
| <video src="media/TODO_input.mp4" /> | <video src="media/TODO_blur.mp4" /> |

| Blackout | Pixel |
|----------|-------|
| <video src="media/TODO_blackout.mp4" /> | <video src="media/TODO_pixel.mp4" /> |

| Bar | Target (one face) |
|-----|-------------------|
| <video src="media/TODO_bar.mp4" /> | <video src="media/TODO_target.mp4" /> |

<!-- Replace the TODO filenames above with actual sample videos -->

## Features

- **Three modes** — blur all faces, just one specific face, or everyone *except* one face
- **Four blur styles** — blur, blackout, pixelation, or eye bar
- **Speed / accuracy tradeoff** — choose model pack (`buffalo_l` → `buffalo_sc`) and detection resolution
- **GPU support** — uses ONNX Runtime; swap in `onnxruntime-gpu` for CUDA acceleration
- **Audio preserved** — audio is muxed back into the output automatically

## Installation

Requires Python 3.12+, [uv](https://docs.astral.sh/uv/), and ffmpeg.

```bash
git clone git@github.com:raviksharma/blurfaces.git
cd blurfaces
uv sync
```

For GPU support:

```bash
uv sync --extra gpu
```

## Usage

```bash
# Blur all faces
uv run blurfaces video.mp4

# Blur one specific person with pixelation
uv run blurfaces video.mp4 --mode target --face person.jpg --blur pixel

# Blur everyone except one person
uv run blurfaces video.mp4 --mode exclude --face person.jpg --blur blackout

# Faster processing (smaller model + lower detection resolution)
uv run blurfaces video.mp4 --model buffalo_sc --det-size 320

# Custom output path
uv run blurfaces video.mp4 -o censored.mp4
```

## Docker

```bash
docker build -t blurfaces .
docker run --rm -v $(pwd)/media:/data blurfaces /data/video.mp4 -o /data/out.mp4
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--mode` | `all` | `all`, `target`, or `exclude` |
| `--blur` | `blur` | `blur`, `blackout`, `pixel`, or `bar` |
| `--face` | — | Reference face image (required for `target`/`exclude`) |
| `--model` | `buffalo_l` | `buffalo_l` (accurate), `buffalo_s` (balanced), `buffalo_sc` (fast) |
| `--det-size` | `640` | Detection resolution in pixels |
| `--threshold` | `0.45` | Cosine similarity threshold for face matching |
| `-o` | `out.<ext>` | Output file path |

## Additional Information

- originally developed for [Bellingcat Oct 2022 Hackathon](https://www.bellingcat.com/resources/2022/10/06/automated-map-searches-scam-busting-tools-and-twitter-search-translations-here-are-the-results-of-bellingcats-second-hackathon/)
- tool is not perfect; should be used with other manual editing before final publish
- next steps
   - smooth face locations (fixes failure in detecting odd frames)
   - detect scene change and use it to reset face locations
