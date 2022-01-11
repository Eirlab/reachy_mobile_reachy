import matplotlib.pyplot as plt
import numpy as np
from cv2 import cv2


def isolate_grid(img_path, img_name, debug=False):
    # Load image and convert to grayscale
    image = cv2.imread(img_path + img_name)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)

    # filter out noise, then threshold
    sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpen = cv2.filter2D(blur, -1, sharpen_kernel)
    thresh = cv2.threshold(sharpen, 150, 255, cv2.THRESH_BINARY_INV)[1]

    # morphology treatment then find contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    # find the largest contour
    max_cnt = None
    max_area = 0
    maximum = 100000
    for c in cnts:
        area = cv2.contourArea(c)
        if max_area < area < maximum:
            max_area = area
            max_cnt = c

    # crop the largest contour
    x, y, w, h = cv2.boundingRect(max_cnt)
    x = x - 10 if x - 10 > 0 else x
    y = y - 10 if y - 10 > 0 else y
    h = h + 10 if h + 10 < image.shape[0] else h
    w = w + 10 if w + 10 < image.shape[1] else w
    ROI = image[y:y + h, x:x + w]
    cv2.imwrite('process/' + img_name, ROI)
    if debug:
        plt.imshow(ROI)
        plt.show()


if __name__ == '__main__':
    isolate_grid('data/', '001.jpg', debug=True)
