import math
import numpy as np

import cv2 as cv

def binarizacia():
    img = cv.imread('start.jpg', cv.IMREAD_GRAYSCALE)
    ret, th = cv.threshold(img, 170, 255, cv.THRESH_BINARY)

    cv.imshow('img', img)
    cv.imshow('th', th)
    cv.waitKey()
    cv.destroyAllWindows()
    cv.imwrite('img-bin.jpg', th)


#Построение скелета изображение
def skelet_img(img):
    # img = cv.imread(file_name, 0)
    size = np.size(img)
    skel = np.zeros(img.shape, np.uint8)

    ret, img = cv.threshold(img, 127, 255, 0)
    element = cv.getStructuringElement(cv.MORPH_CROSS, (3, 3))
    done = False

    while (not done):
        eroded = cv.erode(img, element)
        temp = cv.dilate(eroded, element)
        temp = cv.subtract(img, temp)
        skel = cv.bitwise_or(skel, temp)
        img = eroded.copy()

        zeros = size - cv.countNonZero(img)
        if zeros == size:
            done = True
    return skel

#Расширение с матрицей 5х5
def dilation(src):
    kernel = np.ones((5, 5), np.uint8)  # 5x5
    dilation = cv.dilate(src, kernel, iterations=1)
    return dilation

#Расширение с матрицей 3х3
def dilation_3(src):
    kernel = np.ones((3, 3), np.uint8)  # 3x3
    dilation = cv.dilate(src, kernel, iterations=1)
    return dilation

#Эрозия
def erosion(img):
    kernel = np.ones((3, 3), np.uint8)
    eros = cv.erode(img, kernel, iterations=1)
    return eros

#Комбинация морфологических операций
def morf(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    #gray = dilation(gray)
    #gray = erosion(gray)
    gray = skelet_img(gray)
    gray = dilation_3(gray)
    #gray = dilation(gray)



    img = cv.cvtColor(gray, cv.IMREAD_COLOR)

    return img

#Комбинация морфологических операций
def morf_sk(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    gray = skelet_img(gray)
    img = cv.cvtColor(gray, cv.IMREAD_COLOR)

    return img

#Алгоритм поиска узловых точек
def method_circl(img, x, y, R, l, j):
    # l - смещение пикселей по радиусу

    dlt_al = (l * 360) / (2 * math.pi * R)  # Шаг смещения по грани

    h, w, _ = img.shape

    i = 0 #Шаг радиуса
    k = 0 #Колличество пересечений радиуса с белым пикселем

    while (not (((dlt_al * i) >= 330) or (k >= 3))):  #Проверяем прошел радиут 330 градусов или были ли найдены 3 пересечения
        al = math.radians(dlt_al * i)

        #Находим координаты
        x1 = int(R * math.cos(al) + x)
        y1 = int(R * math.sin(al) + y)

        i += 1

        #Проверка на выход за границы снимка
        if (x1 >= w) or (y1 >= h) or (x1 <= 0) or (y1 <= 0):
            continue

        #Если радиус попал в белую точку
        if all(img[y1, x1] > [180, 180, 180]):

            i = i + j #добавляем к шагу радиуса прыжок
            k = k + 1 #Добавляем пересечение

            if k >= 3:
                return True
    return False

#Проверка значений пикселей на грани
def chek_matrix(img, x, y):
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    try:
        # ******************************************************
        l1 = [0, 0, 0]
        if img[y - 1, x - 1] >= 180:
            l1[0] = 1
        else:
            l1[0] = 0

        if img[y - 1, x] >= 180:
            l1[1] = 1
        else:
            l1[1] = 0

        if img[y - 1, x + 1] >= 180:
            l1[2] = 1
        else:
            l1[2] = 0
        # ******************************************************
        l2 = [0, 0, 0]
        if img[y, x - 1] >= 180:
            l2[0] = 1
        else:
            l2[0] = 0

        if img[y, x] >= 180:
            l2[1] = 1
        else:
            l2[1] = 0

        if img[y, x + 1] >= 180:
            l2[2] = 1
        else:
            l2[2] = 0
        # ******************************************************
        l3 = [0, 0, 0]
        if img[y + 1, x - 1] >= 180:
            l3[0] = 1
        else:
            l3[0] = 0

        if img[y + 1, x] >= 180:
            l3[1] = 1
        else:
            l3[1] = 0

        if img[y + 1, x + 1] >= 180:
            l3[2] = 1
        else:
            l3[2] = 0

        arr = np.array([l1, l2, l3])
        arr_one = np.zeros((3, 3), np.int)

        matrix = np.array_equal(arr, arr_one)

        if matrix:
            return False
        else:
            return True
    # ******************************************************
    except IndexError:
        return False


def anti_nois(img):

    hsv_min = np.array((0, 0, 49), np.uint8)
    hsv_max = np.array((255, 255, 255), np.uint8)

    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    thresh = cv.inRange(hsv, hsv_min, hsv_max)

    contours0, hierarchy = cv.findContours(thresh.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    img_black = img.copy()

    # Получаем черное изображение
    img_black1 = cv.bitwise_not(img_black)

    img_black = cv.bitwise_and(img, img_black1)

    #Создаем маску
    h, w = img.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)

    for cnt in contours0:
        point = [0, 0]
        if len(cnt) >5 and len(cnt) <50:  # 10
            ellipse = cv.fitEllipse(cnt)

            x = int(ellipse[0][0])
            y = int(ellipse[0][1])

            if (0 < x < w) and (0 < y  < h):


                if len(cnt) >8:
                    cv.ellipse(img_black, ellipse, (255, 255, 255), 1)
                    cv.floodFill(img_black, mask, (x, y), (255, 255, 255))
                else:
                    cv.ellipse(img_black, ellipse, (255, 255, 255), 2)

    img_black_inv = cv.bitwise_not(img_black)

    res = cv.bitwise_and(img,img_black_inv)

    return res


def translation_koordinate(img, one_mm, points):

    h,w,_ = img.shape

    x_cent = int(w/2)
    y_cent = int(h/2)


    koordinates = []
    for p in points:
        k = []
        x = p[0] - x_cent
        y = y_cent - p[1]

        x_m = round(x/one_mm,2)
        y_m = round(y/one_mm,2)

        k.append(x_m)
        k.append(y_m)

        koordinates.append(k)

    return koordinates




