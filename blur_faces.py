import os
import sys
import random
import ffmpeg
import face_recognition
import cv2
from tqdm import trange

in_video_file = sys.argv[1]
out_video_file = ''.join(random.choice('0123456789ABCDEF') for i in range(6)) + '_blurred_faces_' + in_video_file

video_capture = cv2.VideoCapture(in_video_file)
in_av_file = ffmpeg.input(in_video_file)
a1 = in_av_file.audio

width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
length = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

fps = video_capture.get(cv2.CAP_PROP_FPS)

print(width, height, length, fps)

video_out = cv2.VideoWriter(
            out_video_file, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

face_locations = []

for i in trange(length+1):
    # Grab a single frame of video
    ret, frame = video_capture.read()
    if not ret:
        video_out.release()
        break

    face_locations = face_recognition.face_locations(frame)
    for (top, right, bottom, left) in face_locations:

        # Extract the region of the image that contains the face
        face_image = frame[top:bottom, left:right]

        # Blur the face
        blurred_face = cv2.GaussianBlur(face_image, (0, 0), 30)

        # Put the blurred face region back into the frame image
        frame[top:bottom, left:right] = blurred_face

    video_out.write(frame)

video_capture.release()
cv2.destroyAllWindows()

stream = ffmpeg.input(out_video_file)
stream = ffmpeg.output(stream, a1, 'audio_' + out_video_file)
ffmpeg.run(stream)
os.remove(out_video_file)
