# blurfaces

## Tool Description

Blurs faces in video.

input | mode=all, censor-type=gaussianblur
:-: | :-:
<video src='https://user-images.githubusercontent.com/600723/212699288-73a89730-a92b-4136-a340-0e8739fc832d.mp4'/>|<video src='https://user-images.githubusercontent.com/600723/212761619-ddd63219-f4b1-4b7d-b890-1d66ae190fb0.mp4'/>
mode=one, censor-type=pixelation | mode=allexcept, censor-type=facemasking
<video src='https://user-images.githubusercontent.com/600723/221906178-4ba56e9e-b143-4f10-9da1-0e9aada87abe.mp4'/>|<video src='https://user-images.githubusercontent.com/600723/221908350-1d4a7f09-765d-45b0-8293-b1ed3be2a209.mp4'/>


## Installation
1. Make sure you have Python version 3.10.6 or greater installed

2. Download the tool's repository using the command:

        git clone git@github.com:raviksharma/blurfaces.git

3. Move to the tool's directory and install the tool

        cd blurfaces
        pip install -r requirements.txt

## Usage

`python3 blur_faces.py <input_file>`

## Additional Information

- uses https://github.com/ageitgey/face_recognition for face detection
- uses https://ffmpeg.org/ for audio and video processing
- tool is not perfect; should be used with other manual editing before final publish
- next steps
   - smooth face_locations (fixes failure in detecting odd frames)
   - detect scene change and use it to reset face_locations[]
   - choose num_jitters
   - blur only one face
   - blur all but one face
