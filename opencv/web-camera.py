from collections import namedtuple
import cv2
import numpy as np

KEYS_TO_QUIT = frozenset([ord('q'), 27, ord(' ')])

Point = namedtuple('Point', ('x', 'y'))

cap = cv2.VideoCapture(0)
cap_size = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

brightness = 0.5

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # norm = cv2.equalizeHist(gray)
    black = (gray - gray.min()).astype(np.uint8)
    white = (black * (255.0 / black.max())).astype(np.uint8)

    result = white
    # Display the resulting frame
    cv2.imshow('Result', result)
    pressed_key = cv2.waitKey(1) & 0xFF
    if pressed_key in KEYS_TO_QUIT:
        break
    if pressed_key == ord('+'):
        brightness = min(brightness + 0.02, 1.0)
        print "Brightness:", brightness
    if pressed_key == ord('-'):
        brightness = max(brightness - 0.02, 0.0)
        print "Brightness:", brightness

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
