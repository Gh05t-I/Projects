import numpy as np
import cv2 as cv
import os
from time import sleep
from pyueye import ueye as ui
from datetime import datetime


# Функция для работы с камерой, подключение, съемка кадра.
def get_image():
    # print(datetime.utcnow().strftime('%H:%M:%S.%f'))

    hCam = ui.HIDS(0)  # Создаем объект камеры(нет точного описания)

    # Производим взаимодействия драйверов и камеры,
    # устанавливаем соединение с камерой, без данной функции взаимодействие с камерой не возможно
    res = ui.is_InitCamera(hCam, None)

    si = ui.SENSORINFO()  # Структура содержит информацию о типе сенсора
    res = ui.is_GetSensorInfo(hCam, si)  # Получение информации которая содержится в SENSORINFO

    bpp = 8 if si.nColorMode == ui.IS_COLORMODE_MONOCHROME else 24  # Проверка, какого вида камера (проверка на монохром)

    # Определяем размер и позицию интересуемой области
    rAOI = ui.IS_RECT()
    res = ui.is_AOI(hCam, ui.IS_AOI_IMAGE_GET_AOI, rAOI, ui.sizeof(rAOI))

    pBuf = ui.c_mem_p();
    nBuf = ui.c_int();
    # Выделяет память под изображения исходя из высоты, ширины и глубины цвета
    res = ui.is_AllocImageMem(hCam, rAOI.s32Width, rAOI.s32Height, bpp, pBuf, nBuf)

    # Делает выделенную память активной, только в активную память можно сохранить изображение
    res = ui.is_SetImageMem(hCam, pBuf, nBuf)

    # Захват изображения

    res = ui.is_FreezeVideo(hCam, ui.IS_WAIT)

    ifp = ui.IMAGE_FILE_PARAMS(pBuf, nBuf)  # Структура с параметрами изображение
    ifp.pwchFileName = "image.bmp"  # Имя файла
    ifp.nFileType = ui.IS_IMG_BMP  # Тип файла ( можно выбрать jpg, bmp,png)
    ifp.nQuality = 100  # Качество изображения

    # Сохраняет захваченное изображение
    res = ui.is_ImageFile(hCam, ui.IS_IMAGE_FILE_CMD_SAVE, ifp, ui.sizeof(ifp))

    # print(datetime.utcnow().strftime('%H:%M:%S.%f'))

    # Завершаем работу с камерой
    res = ui.is_ExitCamera(hCam)

def find_roi(x):

    '''функция вычисляет область интереса, на вход приходит
    процент от ширины - х'''

    if x >= 100 or x<= 0:
        return

    f = os.path.abspath('./image.png')
    # fn = './image.bmp'
    print(f)
    img = cv.imread(f, cv.IMREAD_COLOR)

    h, w, _ = img.shape
    print('Ширина  ', h, w)

    x = int(w * x / 100 + 0.5) #вычисляем координату x

    # граница левого края
    y1 = 0
    x1 = 1 #x - 125
    if x1 < 0:
        x1 = 0

    # граница правого края
    y2 = h
    x2 = w - 1 #x + 125
    if x2 > w:
        x2 = w

    print('ROI = ', y1, y2, x1, x2)
    ROI = img[y1:y2, x1:x2]


    print( 'x = ', x)
    print('x1 = ', x1)
    print('x2 = ', x2)
    print('y1 = ', y1)
    print('y2 = ', y2)

    #cv.imread('./ROI/roi.png', ROI)

    return x,ROI #возвращаем полученную координату и само изображение


# Поиск клея на снимке
def find_glue(img, one_mm, count,center,fale_name1):
    '''данная функция ищит на изображении дефекты
    img - изображение которое анализируем
    one_mm - количество пикселей в милиметре полученное при калибровке
    count - номер изображения
    center - координата полученная при выделении области интереса
    file_name1 - имя файла куда сохраняются файлы'''

    f = os.path.abspath('./image.png')
    img_drow = cv.imread(f, cv.IMREAD_COLOR)

    glue = False

    #Цветовая комбинация для щелочи
    hsv_min = np.array((0, 122, 0), np.uint8)
    hsv_max = np.array((69, 255, 255), np.uint8)    
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)  # меняем цветовую модель с BGR на HSV
    thresh = cv.inRange(hsv, hsv_min, hsv_max)  # применяем цветовой фильтр

    #Цветовая комбинация для клея, вариант 1
    hsv_min = np.array((29, 52, 122), np.uint8)
    hsv_max = np.array((32, 92, 200), np.uint8)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)  # меняем цветовую модель с BGR на HSV
    thresh1 = cv.inRange(hsv, hsv_min, hsv_max)  # применяем цветовой фильтр
    
    thresh = cv.bitwise_or(thresh, thresh1)
    
    #Цветовая комбинация для клея, вариант 2
    hsv_min = np.array((24, 95, 0), np.uint8)
    hsv_max = np.array((31, 255, 255), np.uint8)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)  # меняем цветовую модель с BGR на HSV
    thresh2 = cv.inRange(hsv, hsv_min, hsv_max)  # применяем цветовой фильтр
        
    thresh = cv.bitwise_or(thresh, thresh2)

    cv.imwrite('./ROI/tht'+ str(count) +'.png', thresh)
    
    contours0, hierarchy = cv.findContours(thresh.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    sum_area = 0

    if not contours0:
        print('not glue')
        return 0
    else:
        # перебираем все найденные контуры в цикле
        for cnt in contours0:
            rect = cv.minAreaRect(cnt)  # пытаемся вписать прямоугольник
            box = cv.boxPoints(rect)    # поиск четырех вершин прямоугольника
            box = np.int0(box)          # округление координат
            area = int(rect[1][0] * rect[1][1])

            print(box)
            print('************************************')

            if area > 15:
                print('find contur more 15')
                a = rect[1][0]

                box[0][0] = box[0][0] + center - 125
                box[1][0] = box[1][0] + center - 125
                box[2][0] = box[2][0] + center - 125
                box[3][0] = box[3][0] + center - 125

                cv.drawContours(img_drow, [box], 0, (0, 0, 255), 2)  # рисуем прямоугольник

                # Получаем время в данный момент времени
                t = str(datetime.now())
                ls = t.split(' ')
                t = ls[1]

                if a > int(one_mm / 10 + 0.5):
                    glue = True
        glue_pix = 0
        if glue:
            print('write img')

            cv.imwrite('./defect_glue/defect-glue' + str(count) +'.png', img_drow)
            cv.imwrite(fale_name1, img_drow)

            h, w, _ = thresh.shape
            area = h * w

            percent = (100 * glue_pix) / area
            print('persent = ', percent)
            return percent

        return 0


# Вычисляем отношение 1мм == Х pixcel
def calibration(count):
    '''данная функция проводит калибровку по стандартному объекту,
    получаем количество пикселей в милиметре'''

    w_mm = 20 #длинна калибровочного объекта

    f = os.path.abspath('./image.png')
    print(f)

    img = cv.imread(f)

    hsv_min = np.array((120, 0, 0), np.uint8)
    hsv_max = np.array((255, 255, 255), np.uint8)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)  # меняем цветовую модель с BGR на HSV
    thresh = cv.inRange(hsv, hsv_min, hsv_max)  # применяем цветовой фильтр

    hsv_min = np.array((0, 130, 0), np.uint8)
    hsv_max = np.array((255, 255, 255), np.uint8)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)  # меняем цветовую модель с BGR на HSV
    thresh2 = cv.inRange(hsv, hsv_min, hsv_max)  # применяем цветовой фильтр

    thresh = cv.bitwise_or(thresh, thresh2)

    contours0, hierarchy = cv.findContours(thresh.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    square = []

    for cnt in contours0:
        rect = cv.minAreaRect(cnt)  # пытаемся вписать прямоугольник
        box = cv.boxPoints(rect)    # поиск четырех вершин прямоугольника
        box = np.int0(box)          # округление координат
        area = int(rect[1][0] * rect[1][1])

        ls = []

        if area > 10000:

            cv.drawContours(img, [box], 0, (0, 0, 255), 2)  # рисуем прямоугольник

            a = rect[1]
            b = rect[2]

            ls.append(a)
            ls.append(b)

        if ls:
            square.append(ls)

    print("Calib = ", square)

    if square:
        angle = square[0][1]
        if -1 <= angle <= 1 or -91 <= angle <= -89 or 89 <= angle <= 91:
            cv.imwrite('./calibration/calib_' + str(count) + '.png', img)
        else:
            print('Calibration: angle = ', angle)
            cv.imwrite('./calibration/defect/defect-calib_' + str(count) + '.png', img)
            return -1
    else:
        cv.imwrite('./calibration/calib_notFound_' + str(count) + '.png', img)
        return -2


    w_pix = round(square[0][0][0], 2)

    one_mm = int(w_pix / w_mm + 0.5)

    return one_mm

