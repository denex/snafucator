from __future__ import division, print_function
import os
from contextlib import contextmanager

import cv2


def is_user_wants_to_quit(key):
    return key > 0 and key == 27 or key == ord('q')


@contextmanager
def video_writer(filename, width, height, fps=10.0):
    writer = cv2.VideoWriter(filename=filename,
                             fourcc=cv2.VideoWriter_fourcc(*[c for c in 'avc1']),
                             fps=fps,
                             frameSize=(width, height))
    assert writer.isOpened()
    yield writer
    writer.release()
    print("Video %dx%d in '%s'" % (width, height, filename))


@contextmanager
def video_capture(filename=0):
    capture = cv2.VideoCapture(filename)
    assert capture.isOpened(), "Cannot open %s" % str(filename)
    yield capture
    capture.release()


def write_camera_to(out_filename):
    fps = 10.0
    sleep_time = int(round(1000 / fps))
    with video_capture() as camera:
        width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        with video_writer(out_filename, width, height, fps) as video:
            while True:
                ret, frame = camera.read()
                cv2.imshow('Camera', frame)
                video.write(frame)

                if is_user_wants_to_quit(cv2.waitKey(sleep_time)):
                    break


def read_video_generator(filename):
    key = 0
    while not is_user_wants_to_quit(key):
        with video_capture(filename) as video:
            while video.isOpened():
                ret, frame = video.read()
                if not ret:
                    break
                yield frame


def infinite_read_video_from(filename, on_new_frame=None):
    for frame in read_video_generator(filename=filename):
        cv2.waitKey(100)
        if on_new_frame is not None:
            on_new_frame(frame)
        else:
            cv2.imshow('Camera', frame)


if __name__ == '__main__':
    # write_camera_to(os.path.expanduser("~/tmp/capture.mov"))
    # infinite_read_video_from(os.path.expanduser("~/tmp/captured_bright.mov"))
    infinite_read_video_from(0)
