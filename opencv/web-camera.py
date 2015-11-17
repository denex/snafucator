from collections import namedtuple
import cv2

Point = namedtuple('Point', ('x', 'y'))

cap = cv2.VideoCapture(0)
cap_size = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    norm = cv2.equalizeHist(gray)
    result = norm.copy()

    gray_blured_image = cv2.blur(norm, (5, 5))
    sobeled = cv2.Sobel(gray_blured_image, ddepth=cv2.CV_8U,
                        dx=1, dy=1)

    thresh, bw_image = cv2.threshold(sobeled, thresh=0, maxval=255,
                                     type=cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    cv2.imshow('Monochrome dx=%d, dy=%d' % (1, 1), bw_image)

    element = cv2.getStructuringElement(shape=cv2.MORPH_RECT,
                                        ksize=(10, 10))
    morphed = cv2.morphologyEx(bw_image, op=cv2.MORPH_CLOSE, kernel=element)
    cv2.imshow('Morphed dx=%d, dy=%d' % (1, 1), morphed)
    _, contours, heirs = cv2.findContours(morphed.copy(), mode=cv2.RETR_EXTERNAL,
                                          method=cv2.CHAIN_APPROX_NONE)
    try:
        heirs = heirs[0]
    except:
        heirs = []

    rects = []
    for cnt, heir in zip(contours, heirs):
        _, _, _, outer_i = heir
        if outer_i >= 0:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        rect = (Point(x, y), Point(x + w, y + h))
        rects.append(rect)
        cv2.rectangle(result, rect[0], rect[1], (0, 255, 0))

    # Display the resulting frame
    cv2.imshow('Result', result)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
