import cv2 as cv
import numpy as np


def binariz(file_name):
    '''Функция принимает путь до изображения, которое необходимо биноризовать
    функция проводит бинаризацию по пороговому значению и возврвщает путь к полученному изображению'''
    img = cv.imread(file_name, cv.IMREAD_GRAYSCALE)
    ret, th = cv.threshold(img, 128, 255, cv.THRESH_BINARY)  # 170

    h, w = img.shape

    mas_brigh = []
    for i in range(h):
        for j in range(w):
            brightness = img[i, j]
            mas_brigh.append(brightness)

    arr_mas = np.asarray(mas_brigh)
    arr_sum = np.sum(arr_mas, axis=0)
    threshold = arr_sum / (h * w)
    
    cv.waitKey()
    cv.destroyAllWindows()
    s = './foto_cam/start-bin.bmp'

    if arr_sum > 300000000:
        return -1

    cv.imwrite(s, th)
    return s



