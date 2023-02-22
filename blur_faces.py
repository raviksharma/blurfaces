import os
import click
import numpy as np
import tempfile
import ffmpeg
import face_recognition
import cv2
from tqdm import trange


def decode_fourcc(cc):
    return ''.join([chr((int(cc) >> 8 * i) & 0xFF) for i in range(4)])


def has_audio(file_path):
    streams = ffmpeg.probe(file_path)['streams']
    for stream in streams:
        if stream['codec_type'] == 'audio':
            return True
    return False


@click.command()
@click.option('--model', default='hog', type=click.Choice(['hog', 'cnn'], case_sensitive=False))
@click.option('--censor_type', default='gaussianblur', type=click.Choice(['gaussianblur', 'facemasking'], case_sensitive=False))
@click.option('--count', default=1, help='How many times to upsample the image looking for faces. Higher numbers find smaller faces.')
@click.argument('in_video_file', type=click.Path(exists=True))
def blurfaces(model, censor_type, count, in_video_file):
    click.echo(click.format_filename(in_video_file))
    print(f'{model=}')
    print(f'{censor_type=}')
    print(f'{count=}')

    _, file_extension = os.path.splitext(in_video_file)

    in_av_file = ffmpeg.input(in_video_file)
    a1 = in_av_file.audio if has_audio(in_video_file) else None

    video_capture = cv2.VideoCapture(in_video_file)
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    length = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    fourcc = video_capture.get(cv2.CAP_PROP_FOURCC)
    codec = decode_fourcc(fourcc)
    print(f'{width=} {height=} {length=} {fps=} {codec=}')

    with tempfile.NamedTemporaryFile(suffix=file_extension) as out_video_file:
        video_out = cv2.VideoWriter(
            out_video_file.name, int(fourcc), fps, (width, height))

        face_locations = []
        for i in trange(length+1):
            ret, frame = video_capture.read()
            if not ret:
                video_out.release()
                break

            face_locations = face_recognition.face_locations(frame, number_of_times_to_upsample=count, model=model)
            for (top, right, bottom, left) in face_locations:
                face_image = frame[top:bottom, left:right]
                if censor_type == 'gaussianblur':
                    blurred_face = cv2.GaussianBlur(face_image, (0, 0), 30)
                else:
                    blurred_face = np.zeros((bottom-top, right-left, 3))
                frame[top:bottom, left:right] = blurred_face
            video_out.write(frame)

        video_capture.release()
        cv2.destroyAllWindows()

        blurred_video_input = ffmpeg.input(out_video_file.name)
        streams = [blurred_video_input, a1] if a1 else [blurred_video_input]
        stream = ffmpeg.output(*streams, 'out' + file_extension).overwrite_output()
        ffmpeg.run(stream)

    return 0


if __name__ == '__main__':
    blurfaces()
