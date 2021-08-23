#!/usr/bin/env python

import sys
import numpy as np
import cv2 as cv

def elipse(img):

    hsv_min = np.array((0, 135, 123), np.uint8)
    hsv_max = np.array((255, 255, 255), np.uint8)

    cv.imwrite('./pictures/hvost.jpg', img)

    points = []

    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    thresh = cv.inRange(hsv, hsv_min, hsv_max)
    contours0, hierarchy = cv.findContours(thresh.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours0:
        point = [0,0]
        if len(cnt) > 5: #10
            ellipse = cv.fitEllipse(cnt)

            x = int(ellipse[0][0])
            y = int(ellipse[0][1])

            point[0] = x
            point[1] = y
            points.append(point)

            cv.circle(img, (x, y), 2, (255, 0, 0), 2)

            cv.ellipse(img, ellipse, (0, 255, 0), 2)

    cv.imwrite('./pictures/number3/img_with_point.jpg', img)
    return points




