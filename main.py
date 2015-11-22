from __future__ import division, print_function, unicode_literals
import sys
import time
import logging
from datetime import datetime

import cv2
import numpy as np

from keyboard import Keyboard
from pin import pin_generator, get_pin_index
from opencv import record_video as Camera
from opencv import cv_image as Image


def cv_sleep(seconds):
    start_time = time.time()
    while time.time() - start_time < seconds:
        cv2.waitKey(int(1000 * seconds))


def transform_rect(points, trans_matrix):
    np_lock = np.array(points, dtype=np.float32).reshape(1, -1, 2)
    transformed = (cv2.perspectiveTransform(np_lock, trans_matrix).reshape(-1, 2) / 2).astype(int)
    return transformed


def try_pin(pin, keyboard, camera):
    while True:
        cv_sleep(0.1)
        ret, frame = camera.read()
        if not ret:
            raise Exception("Camera closed")
        trans_matrix, img_w_square = Image.get_screen_transform(frame)
        if trans_matrix is None:
            cv2.imshow('No Trans', img_w_square)
            continue

        scrn = cv2.warpPerspective(frame, trans_matrix,
                                   dsize=(Image.SCREEN_WIDTH, Image.SCREEN_HEIGHT),
                                   flags=cv2.WARP_INVERSE_MAP)
        screen_norm = Image.normalize_color_image(scrn)
        lock_rect = Image.find_image_on_screen(screen_norm, Image.LOCK_IMAGE, 0.95)
        if lock_rect is None:
            cv2.imshow('No Lock', screen_norm)
            return True
        lock_rect_on_frame = transform_rect(lock_rect, trans_matrix)
        cv2.rectangle(img_w_square,
                      pt1=tuple(lock_rect_on_frame[0]),
                      pt2=tuple(lock_rect_on_frame[1]),
                      color=(0, 0, 255))
        cv2.imshow('Square', img_w_square)
        pin_already_entered_rect = Image.find_image_on_screen(screen_norm, Image.PIN_ENTERED_IMAGE, 0.9955)
        if pin_already_entered_rect is not None:
            pin_already_entered_rect_on_frame = transform_rect(pin_already_entered_rect, trans_matrix)
            cv2.rectangle(img_w_square,
                          pt1=tuple(pin_already_entered_rect_on_frame[0]),
                          pt2=tuple(pin_already_entered_rect_on_frame[1]),
                          color=(0, 0, 255))
            cv2.imshow('Already entered', img_w_square)
            continue
        empty_pin_rect = Image.find_image_on_screen(screen_norm, Image.EMPTY_IMAGE, found_threshold=0.9935)
        if empty_pin_rect is None:
            cv2.imshow('Not empty', screen_norm)
            continue
        empty_on_frame = transform_rect(empty_pin_rect, trans_matrix)
        cv2.rectangle(img_w_square,
                      pt1=tuple(empty_on_frame[0]),
                      pt2=tuple(empty_on_frame[1]),
                      color=(255, 255, 0))
        cv2.imshow('Square', img_w_square)
        break

    message = "Trying PIN: %d" % pin
    logging.warning(message)
    print(message, file=sys.stderr)

    str_pin = str(pin)
    for ch in str_pin:
        keyboard.send_key(ch)
        cv_sleep(0.05)
    cv_sleep(0.3)
    while True:
        cv_sleep(0.1)
        ret, frame = camera.read()
        if not ret:
            raise Exception("Camera closed")
        trans_matrix2, img_w_square = Image.get_screen_transform(frame)
        if trans_matrix2 is None:
            cv2.imshow('No Trans2', img_w_square)
            continue
        scrn = cv2.warpPerspective(frame, trans_matrix2,
                                   dsize=(Image.SCREEN_WIDTH, Image.SCREEN_HEIGHT),
                                   flags=cv2.WARP_INVERSE_MAP)
        screen_norm = Image.normalize_color_image(scrn)
        pin_entered = Image.find_image_on_screen(screen_norm, Image.PIN_ENTERED_IMAGE, found_threshold=0.994)
        if pin_entered is None:
            cv2.imshow('No entered yet', screen_norm)
            continue
        keyboard.send_key('\n')
        message = "entered"
        logging.warning(message)
        print(message, file=sys.stderr)
        cv_sleep(0.3)
        entered_rect = transform_rect(pin_entered, trans_matrix2)
        cv2.rectangle(img_w_square,
                      pt1=tuple(entered_rect[0]),
                      pt2=tuple(entered_rect[1]),
                      color=(0, 255, 0))
        cv2.imshow("entered", img_w_square)
        break
    return False


LAST_PIN = 2719


def main():
    pin_index = get_pin_index(LAST_PIN)
    print("%.1f%%" % (100 * pin_index / 10000))
    with Keyboard() as keyboard:
        with Camera.video_capture(filename=0) as camera:
            for pin in pin_generator(last_pin=LAST_PIN):
                start_time = time.time()
                if try_pin(pin, keyboard, camera):
                    print("Got pin:", pin)
                    break
                message = "Pin: %d time: %.1fs" % (pin, time.time() - start_time)
                logging.warning(message)
                print(message, file=sys.stderr)
            else:
                raise Exception("No PIN accepted")


if __name__ == '__main__':
    logging.basicConfig(filename=datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M-%S.log'),
                        format='%(asctime)s: %(message)s')
    main()
