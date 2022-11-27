# blurfaces

## Tool Description

Blurs faces in video.


## Installation
1. Make sure you have Python version 3.10.6 or greater installed

2. Download the tool's repository using the command:

        git clone git@github.com:raviksharma/blurfaces.git

3. Move to the tool's directory and install the tool

        cd blurfaces
        pip install -r requirements.txt

## Usage

`python3 blur_faces.py <file_name>`

(expects file in the same location as script)

## Additional Information

- uses https://github.com/ageitgey/face_recognition for face detection
- uses https://ffmpeg.org/ for audio and video processing
- tool is not perfect; should be used with other manual editing before final publish
- next steps
   - fix the command line user interface
   - add a web user interface
   - add more video formats
   - smooth face_locations (fixes failure in detecting in odd frames)
   - detect scene change and use it to reset face_locations[]
