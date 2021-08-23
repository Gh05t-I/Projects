import cv2 as cv
import function as f


def number2(img2, white_point):
    points = []

    img3 = f.dilation(img2)
    img3 = f.erosion(img3)

    h, w, _ = img2.shape

    img_show = img3.copy()  # 3

    for p in white_point:
        j = p[1]
        i = p[0]
        proverka = f.method_circl(img3, j, i, 6, 2, 4)  # 3
        if proverka:
            point = [i, j]
            img_show[i, j] = [0, 0, 255]
            cv.circle(img_show, (j, i), 2, (0, 0, 255), 2)  # radius =2

            points.append(point)

    cv.imwrite('./pictures/number2/img3.jpg', img_show)

    return img_show
