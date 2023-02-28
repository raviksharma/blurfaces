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


def get_video_properties(video_capture):
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    length = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    fourcc = video_capture.get(cv2.CAP_PROP_FOURCC)
    codec = decode_fourcc(fourcc)
    return width, height, length, fps, fourcc, codec


def get_face_encoding(in_face_file):
    try:
        face_to_blur = face_recognition.load_image_file(in_face_file)
        # expecting only 1 face in the image
        face_to_blur_enc = face_recognition.face_encodings(face_to_blur)[0]
        return face_to_blur_enc
    except FileNotFoundError:
        exit(f'file not found {in_face_file=}.')
    except IndexError:
        exit(f'no face found in the image file {in_face_file=}.')


def get_blurred_face(frame, censor_type, face_location):
    top, right, bottom, left = face_location
    if censor_type == 'facemasking':
        blurred_face = np.zeros((bottom-top, right-left, 3))
    elif censor_type == 'pixelation':
        face_image = frame[top:bottom, left:right]
        h, w = face_image.shape[:2]
        resized_image = cv2.resize(face_image, (8, 8), interpolation=cv2.INTER_AREA)
        blurred_face = cv2.resize(resized_image, (w, h), interpolation=cv2.INTER_AREA)
    else:
        face_image = frame[top:bottom, left:right]
        blurred_face = cv2.GaussianBlur(face_image, (0, 0), 30)
    frame[top:bottom, left:right] = blurred_face
    return frame


@click.command()
@click.option('--mode', default='all', type=click.Choice(['all', 'one', 'allexcept'], case_sensitive=False))
@click.option('--model', default='hog', type=click.Choice(['hog', 'cnn'], case_sensitive=False))
@click.option('--censor-type', default='gaussianblur', type=click.Choice(['gaussianblur', 'facemasking', 'pixelation'], case_sensitive=False))
@click.option('--count', default=1, help='How many times to upsample the image looking for faces. Higher numbers find smaller faces.')
@click.option('--in-face-file', type=str)
@click.argument('in-video-file', type=click.Path(exists=True))
def blurfaces(mode, model, censor_type, count, in_face_file, in_video_file):
    click.echo(click.format_filename(in_video_file))
    print(f'{mode=}, {model=}, {censor_type=}, {count=}, {in_face_file=}')

    _, file_extension = os.path.splitext(in_video_file)

    in_av_file = ffmpeg.input(in_video_file)
    a1 = in_av_file.audio if has_audio(in_video_file) else None

    video_capture = cv2.VideoCapture(in_video_file)
    width, height, length, fps, fourcc, codec = get_video_properties(video_capture)
    print(f'{width=}, {height=}, {length=}, {fps=}, {codec=}')

    with tempfile.NamedTemporaryFile(suffix=file_extension) as out_video_file:
        video_out = cv2.VideoWriter(
            out_video_file.name, int(fourcc), fps, (width, height))

        face_locations = []
        if mode == 'one':
            face_to_blur_enc = get_face_encoding(in_face_file)

            for i in trange(length+1):
                ret, frame = video_capture.read()
                if not ret:
                    video_out.release()
                    break

                face_locations = face_recognition.face_locations(frame, number_of_times_to_upsample=count, model=model)
                face_image_encodings = face_recognition.face_encodings(frame, face_locations)
                results = face_recognition.compare_faces(face_image_encodings, face_to_blur_enc)
                for found, face_location in zip(results, face_locations):
                    if found:
                        frame = get_blurred_face(frame, censor_type, face_location)
                video_out.write(frame)

        elif mode == 'allexcept':
            face_to_blur_enc = get_face_encoding(in_face_file)

            for i in trange(length+1):
                ret, frame = video_capture.read()
                if not ret:
                    video_out.release()
                    break

                face_locations = face_recognition.face_locations(frame, number_of_times_to_upsample=count, model=model)
                face_image_encodings = face_recognition.face_encodings(frame, face_locations)
                results = face_recognition.compare_faces(face_image_encodings, face_to_blur_enc)
                for found, face_location in zip(results, face_locations):
                    if not found:
                        frame = get_blurred_face(frame, censor_type, face_location)
                video_out.write(frame)
        else:  # mode = all
            for i in trange(length+1):
                ret, frame = video_capture.read()
                if not ret:
                    video_out.release()
                    break

                face_locations = face_recognition.face_locations(frame, number_of_times_to_upsample=count, model=model)
                for face_location in face_locations:
                    frame = get_blurred_face(frame, censor_type, face_location)
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
