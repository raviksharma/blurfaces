# blurfaces

Detect and censor faces in video using insightface and ffmpeg.

## Samples

| Input | Blackout (default) |
|-------|----------------|
| <video src="https://user-images.githubusercontent.com/600723/212699288-73a89730-a92b-4136-a340-0e8739fc832d.mp4" /> | <video src="https://github.com/user-attachments/assets/4b08deff-0247-4904-b273-f5b98b2d53a7" /> |

| Blur | Pixel |
|----------|-------|
| <video src="https://github.com/user-attachments/assets/35f03c27-d9cc-45cc-a19a-45cc31d78809" /> | <video src="https://github.com/user-attachments/assets/77640f04-f4f0-48c4-836b-c39de4bf28b2" /> |

## Features

- **Three modes** — blur all faces, just one specific face, or everyone *except* one face
- **Four blur styles** — blur, blackout, pixelation, or eye bar
- **Speed / accuracy tradeoff** — choose model pack (`buffalo_l` → `buffalo_sc`) and detection resolution
- **GPU support** — uses ONNX Runtime; swap in `onnxruntime-gpu` for CUDA acceleration
- **Audio preserved** — audio is muxed back into the output automatically

## Installation

Requires Python 3.12+, uv, and ffmpeg.

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
| `--blur` | `blackout` | `blur`, `blackout`, `pixel`, or `bar` |
| `--face` | NA | Reference face image (required for `target`/`exclude`) |
| `--model` | `buffalo_sc` | `buffalo_l` (accurate), `buffalo_s` (balanced), `buffalo_sc` (fast) |
| `--det-size` | `640` | Detection resolution in pixels |
| `--threshold` | `0.45` | Cosine similarity threshold for face matching |
| `-o` | `out.<ext>` | Output file path |

## Additional Information

- originally developed for [Bellingcat Oct 2022 Hackathon](https://www.bellingcat.com/resources/2022/10/06/automated-map-searches-scam-busting-tools-and-twitter-search-translations-here-are-the-results-of-bellingcats-second-hackathon/)
- tool is not perfect; should be used with other manual editing before final publish
- next steps
   - smooth face locations (fixes failure in detecting odd frames)
   - detect scene change and use it to reset face locations
