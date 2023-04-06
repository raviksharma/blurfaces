# blurfaces

## Tool Description

Blurs faces in video.

<table>
<tbody>
<tr>
<td>sample</td>
<td>mode=<b>all</b>, censor-type=<b>gaussianblur</b></td>
</tr>
<tr>
<td><video src='https://user-images.githubusercontent.com/600723/212699288-73a89730-a92b-4136-a340-0e8739fc832d.mp4'/></td>
<td><video src='https://user-images.githubusercontent.com/600723/212761619-ddd63219-f4b1-4b7d-b890-1d66ae190fb0.mp4'/></td>
</tr>
<tr>
<td>mode=<b>one</b>, censor-type=<b>pixelation</b></td>
<td>mode=<b>allexcept</b>, censor-type=<b>facemasking</b></td>
</tr>
<tr>
<td><video src='https://user-images.githubusercontent.com/600723/221906178-4ba56e9e-b143-4f10-9da1-0e9aada87abe.mp4'/></td>
<td><video src='https://user-images.githubusercontent.com/600723/221908350-1d4a7f09-765d-45b0-8293-b1ed3be2a209.mp4'/></td>
</tr>
</tbody>
</table>

## Installation
1. Make sure you have Python version 3.10.6 or greater installed

2. Download the tool's repository using the command:

        git clone git@github.com:raviksharma/blurfaces.git

3. Move to the tool's directory and install the tool

        cd blurfaces
        pip install -r requirements.txt

## Usage

```
$ python3 blur_faces.py --help
Usage: blur_faces.py [OPTIONS] IN_VIDEO_FILE

Options:
  --mode [all|one|allexcept]
  --model [hog|cnn]
  --censor-type [gaussianblur|facemasking|pixelation]
  --count INTEGER                 How many times to upsample the image looking
                                  for faces. Higher numbers find smaller
                                  faces.

  --in-face-file TEXT
  --help                          Show this message and exit.
```

Example
```
python3 blur_faces.py media/friends.mp4 --mode allexcept --model cnn --censor-type facemasking --in-face-file media/Ross_Geller.jpg
```

## Additional Information

- originally developed for [Bellingcat Oct 2022 Hackathon](https://www.bellingcat.com/resources/2022/10/06/automated-map-searches-scam-busting-tools-and-twitter-search-translations-here-are-the-results-of-bellingcats-second-hackathon/)
- uses [face_recognition](https://github.com/ageitgey/face_recognition) for face detection
- uses [ffmpeg](https://ffmpeg.org/) for audio and video processing
- tool is not perfect; should be used with other manual editing before final publish
- next steps
   - smooth face_locations (fixes failure in detecting odd frames)
   - detect scene change and use it to reset face_locations[]
   - choose num_jitters
