import os
import click
import random
import ffmpeg
import face_recognition
import cv2
from tqdm import trange


def get_out_file(file_extension):
    return ''.join(random.choice('0123456789ABCDEF') for i in range(6)) + '_video_only' + file_extension


def decode_fourcc(cc):
    return ''.join([chr((int(cc) >> 8 * i) & 0xFF) for i in range(4)])


@click.command()
@click.argument('in_video_file', type=click.Path(exists=True))
def blurfaces(in_video_file):
    click.echo(click.format_filename(in_video_file))

    filename, file_extension = os.path.splitext(in_video_file)
    in_av_file = ffmpeg.input(in_video_file)
    a1 = in_av_file.audio

    video_capture = cv2.VideoCapture(in_video_file)
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    length = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    fourcc = video_capture.get(cv2.CAP_PROP_FOURCC)
    codec = decode_fourcc(fourcc)
    print(f'{width=} {height=} {length=} {fps=} {codec=}')

    out_video_file = get_out_file(file_extension)
    video_out = cv2.VideoWriter(
        out_video_file, int(fourcc), fps, (width, height))

    face_locations = []
    for i in trange(length+1):
        ret, frame = video_capture.read()
        if not ret:
            video_out.release()
            break

        face_locations = face_recognition.face_locations(frame)
        for (top, right, bottom, left) in face_locations:
            face_image = frame[top:bottom, left:right]
            blurred_face = cv2.GaussianBlur(face_image, (0, 0), 30)
            frame[top:bottom, left:right] = blurred_face
        video_out.write(frame)

    video_capture.release()
    cv2.destroyAllWindows()

    stream = ffmpeg.input(out_video_file)
    stream = ffmpeg.output(stream, a1, 'out' + file_extension)
    ffmpeg.run(stream)
    os.remove(out_video_file)

    return 0


if __name__ == '__main__':
    blurfaces()
