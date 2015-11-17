from __future__ import division
from collections import namedtuple
import os
import operator

import cv2
import numpy as np

from record_video import infinite_read_video_from

Point = namedtuple('Point', 'x, y')
LOCK_IMAGE = cv2.imread("Lock.png")


def angle_cos(p0, p1, p2):
    d1, d2 = (p0 - p1).astype('float'), (p2 - p1).astype('float')
    result = abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1) * np.dot(d2, d2)))
    return result


def find_screen_square(frame):
    img_square = reduce(operator.mul, frame.shape[:2])
    img = cv2.GaussianBlur(frame, (5, 5), 0)
    squares = []
    # for gray in cv2.split(img):
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = frame
    gray = cv2.blur(gray, (15, 15))
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # gray = clahe.apply(gray)
    cv2.imshow('gray', gray)
    for thrs in xrange(32, 48):
        if thrs == 0:
            bin_img = cv2.Canny(gray, 0, 50, apertureSize=5)
            bin_img = cv2.dilate(bin_img, None)
        else:
            retval, bin_img = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
        cv2.imshow('bin %d' % thrs, bin_img)
        bin_img, contours, hierarchy = cv2.findContours(bin_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            cnt_len = cv2.arcLength(cnt, closed=True)
            cnt = cv2.approxPolyDP(cnt, epsilon=0.2 * cnt_len, closed=True)
            if len(cnt) == 4 and cv2.isContourConvex(cnt):
                area = cv2.contourArea(cnt)
                if img_square * 0.1 < area < img_square * 0.9:
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos(cnt[i], cnt[(i + 1) % 4], cnt[(i + 2) % 4]) for i in range(4)])
                    if max_cos < 0.1:
                        squares.append(np.sort(cnt, axis=0))
    return squares


def image_processor(frame):
    frame = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    squares = find_screen_square(frame)
    img_with_squares = frame.copy()
    cv2.drawContours(img_with_squares, squares, contourIdx=-1, color=(0, 255, 0), thickness=1)
    cv2.imshow('Squares', img_with_squares)
    if not squares:
        return
    if len(squares) > 1:
        strange_squares = [s for s in squares[1:] if (np.abs(squares[0] - s).max() > 12)]
        squares = strange_squares + squares[0:1]
    assert len(squares) == 1
    screen = np.array(squares[0], dtype=np.float32)
    screen_width = 720
    screen_height = 450
    base_screen = np.array([(screen_width, 0), (0, 0), (0, screen_height), (screen_width, screen_height)],
                           dtype=np.float32)
    trans = cv2.getPerspectiveTransform(screen, base_screen)
    transformed = cv2.warpPerspective(frame, trans, dsize=(screen_width, screen_height))

    found = cv2.matchTemplate(transformed, LOCK_IMAGE, method=cv2.TM_CCOEFF_NORMED)
    cv2.normalize(src=found, dst=found, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=-1)
    min_val_, max_val, min_loc, max_loc = cv2.minMaxLoc(found)
    cv2.rectangle(transformed,
                  pt1=max_loc,
                  pt2=(max_loc[0] + LOCK_IMAGE.shape[1], max_loc[1]+LOCK_IMAGE.shape[0]),
                  color=(0, 255, 0), thickness=1)

    cv2.imshow("result", transformed)


def main(filename):
    infinite_read_video_from(filename, on_new_frame=image_processor, sleep=1)


if __name__ == '__main__':
    file_name = 0
    # file_name = os.path.expanduser("~/tmp/captured_bright.mov")
    main(file_name)
    cv2.destroyAllWindows()
