from __future__ import division

import cv2
import numpy as np
import operator

from process_video import infinite_read_video_from


SCALE_FACTOR = 1 / 2
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 450


def angle_cos(p0, p1, p2):
    d1, d2 = (p0 - p1).astype('float'), (p2 - p1).astype('float')
    return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1) * np.dot(d2, d2)))


def find_squares_it(blured_img, min_area, max_area):
    for gray in cv2.split(blured_img):
        for thrs in xrange(2, 128, 2):
            if thrs == 0:
                bin_img = cv2.Canny(gray, 0, 50, apertureSize=5)
                bin_img = cv2.dilate(bin_img, None)
            else:
                retval, bin_img = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            bin_img, contours, hierarchy = cv2.findContours(bin_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.02 * cnt_len, True)
                if len(cnt) == 4:
                    area = cv2.contourArea(cnt)
                    if min_area < area < max_area:
                        if cv2.isContourConvex(cnt):
                            cnt = cnt.reshape(-1, 2)
                            max_cos = np.max([angle_cos(cnt[i], cnt[(i + 1) % 4], cnt[(i + 2) % 4]) for i in xrange(4)])
                            if max_cos < 0.05:
                                yield cnt, area


def normalize_color_image(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.blur(gray, ksize=(5, 5))
    # gray = cv2.equalizeHist(gray)
    return gray


def get_screen_transform(frame):
    resized = cv2.resize(frame, fx=SCALE_FACTOR, fy=SCALE_FACTOR, dsize=None, interpolation=cv2.INTER_AREA)
    resized_square = reduce(operator.mul, resized.shape[:2])
    processed = normalize_color_image(resized)

    squares = [r[0] for r in find_squares_it(processed,
                                             min_area=0.25 * resized_square,
                                             max_area=0.75 * resized_square)]
    if len(squares) == 0:
        cv2.imshow('No squares', processed)
        return
    avg_square = (sum(squares) / len(squares)).astype(np.float32)
    pol_sq = np.array([[d[0][0] for d in cv2.cartToPolar(float(x), float(y))] for x, y in avg_square])
    sorted_indices = np.lexsort((pol_sq[:, 1], pol_sq[:, 0]))
    pol_sq = pol_sq[sorted_indices]
    ordered_square = np.array([[d[0][0] for d in cv2.polarToCart(m, a)] for m, a in pol_sq], dtype=np.float32)

    cv2.drawContours(resized, [np.around(ordered_square).astype(int)], contourIdx=-1, color=(0, 255, 0), thickness=1)
    cv2.imshow('Squares', resized)

    base_screen = np.array([
        (0, 0),
        (0, SCREEN_HEIGHT),
        (SCREEN_WIDTH, 0),
        (SCREEN_WIDTH, SCREEN_HEIGHT),
    ], dtype=np.float32)

    return cv2.getPerspectiveTransform(ordered_square / SCALE_FACTOR, base_screen)


def get_lock_image_square(img, lock_found_threshold=0.96,
                          lock_image=cv2.imread("Lock.png")):
    found = cv2.matchTemplate(img, lock_image, method=cv2.TM_CCORR_NORMED)
    min_val, max_val, min_pos, max_pos = cv2.minMaxLoc(found)
    if max_val < lock_found_threshold:
        return None
    return max_pos, (max_pos[0] + lock_image.shape[1], max_pos[1]+lock_image.shape[0])


def process_image(frame):
    trans = get_screen_transform(frame)
    if trans is None:
        return
    transformed = cv2.warpPerspective(frame, trans, dsize=(SCREEN_WIDTH, SCREEN_HEIGHT))
    # transformed = frame
    lock_rect = get_lock_image_square(transformed)
    if lock_rect is not None:
        cv2.rectangle(transformed, *lock_rect, color=(0, 0, 255))
    cv2.imshow('Transformed', transformed)


def main(filename):
    infinite_read_video_from(filename, on_new_frame=process_image)


if __name__ == '__main__':
    # main(filename="captured_bright.mov")
    main(filename=0)