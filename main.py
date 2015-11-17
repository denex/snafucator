from __future__ import division, print_function, unicode_literals
import time
import logging

from keyboard import Keyboard
from pin import pin_generator


def try_pin(pin, keyboard):
    """
    :type pin: int
    """
    # assert screen ready
    # for c in pin:
    #     while not
    logging.warning("Trying PIN:" + str(pin))
    str_pin = str(pin) + '\n'
    for ch in str_pin:
        keyboard.send_key(ch)
        time.sleep(0.03)
    return False


def main():

    # opencv = OpenCV()

    with Keyboard() as keyboard:
        for pin in pin_generator(last_pin=4983):
            if try_pin(pin, keyboard):
                break
        else:
            raise Exception("No PIN accepted")


if __name__ == '__main__':
    main()
