import wake2
from threading import Thread, Event
from pyueye import ueye
import numpy as np
import cv2
import struct
import shutil
from time import sleep
import os
import sys
from PIL import Image


import dielectric_defect as dd
import vision
import another_function as af

addr = 0x20

# для команды 0x21
num_measurement = 0  # Количество принятых измерений(пакетов)
mas_data = []
package = 10  # Сколько замеров будет в массиве данных для анализа
stem = 12  # Количество стержней
min = 0
max = 0
C = []  # Емкосные дефекты


# для команды 0x22
parameters = False  # Проверка на передачу границ min and max

# Для команды 0x23
counter_foto = 0
X = []  # используется для 21
G = []  # Клеевой дефект


# Для команды 0x24
one_mm = 0  # Содержит колличество пикселей в одном милиметре

# Для команды 0x26
Center = 0
Number_seam = 0
y = 0
file_for_clean = ['./calibration', './seam','./defect_glue'] # список файлов которые отчищаются

event = Event()     # получение информации с камеры
event_cam = Event() #отвечает за завершения программы


def rx(frm, to, cmd, data):
    '''данная функция вызывается модулем wake2 который отвечает за взаимодействие
     клиентской и серверной части программы, функция принимает:
    frm - адрес от кого пришла команда
    to - кому пришел пакет
    cmd - номер команды которую требуется выполнить
    data - данные котрые приходят с сервера'''

    if to == 0 or to == addr:

        global parameters
        global min
        global max
        global num_measurement
        global mas_data
        global C

        global one_mm

        global counter_foto
        global X
        global G

        global Center
        global Number_seam
        global y
        global file_for_clean

        print('comand in function')

        # Команда анализа полученных данных
        if cmd == 0x21:

            if len(data) == stem * 2:
                measurement = struct.unpack('<12H', data)
                ls_mes = list(measurement)
                mas_data.append(ls_mes)
                num_measurement += 1

                data = bytearray()
            else:
                data = 120  # Присваиваем номер ошибки
                data = struct.pack('<H', data)

            if num_measurement == package and parameters:
                num_def_el, defective = dd.analysis_data(mas_data, min, max)

                num_el = package * stem
                percent_deffect = (num_def_el * 100) / num_el
                C.append(percent_deffect)

                # Обнуление переменных
                num_measurement = 0
                mas_data = []
                # parameters = False

                data = int(percent_deffect * 100 + 0.5)
                data = struct.pack('<H', data)

            w.tx(addr, frm, cmd, data)

        # Команда передачи гнаниц нормального диапазона
        if cmd == 0x22:

            if len(data) == 4:
                borde = struct.unpack('<HH', data)

                min = borde[0]
                max = borde[1]
                parameters = True

                data = bytearray()
            else:
                data = struct.pack('<H', 120)

            w.tx(addr, frm, cmd, data)


        # Команда захвата изображения и обработка, поиск клея.
        if cmd == 0x23:

            if len(data) == 8:
                koor = struct.unpack('<ff', data)

                print(koor)
                x = koor[0]
                y = koor[1]

                print('x= ',x)
                print('y = ',y)

                print('Number seam = ', Number_seam)
                print('center = ', Center)

                X.append(x)
                event.set() #Сохраняем файл с камеры
                sleep(0.5)

                # Копирование файла для скрипта
                file_name = './seam/' + str(counter_foto) + '.png'
                shutil.copy('./image.png', file_name)

                #Пересохраняем изображение в jpg для сервера
                img_save = Image.open('./image.png')
                img_save.save('./image.jpg')

                # Копирование файла для сервера
                shutil.copy('./image.jpg', './For_serv/' + str(Number_seam) + '_x' + "{:09.3F}".format(round(x, 3)) + '_y' + "{:09.3F}".format(round(y, 3)) + '.jpg')
                file_name = './For_serv/' + str(Number_seam) + '_x' + "{:09.3F}".format(round(x, 3)) + '_y'+ "{:09.3F}".format(round(y, 3)) +  '.jpg'
                file_name = os.path.abspath(file_name)

                cent,img = vision.find_roi(Center) #получаем область интереса

                cv2.imwrite('./ROI/roi.png', img)

                file_name1 = './For_serv/D' + str(Number_seam) + '_x' + "{:09.3F}".format(round(x, 3)) + '_y'+ "{:09.3F}".format(round(y, 3)) +  '.jpg'
                gl = vision.find_glue(img, one_mm, counter_foto,cent,file_name1) #поиск клея на изображении

                data1 = bytes(file_name, 'cp1251')

                if gl != 0:
                    G.append(gl)
                    # передаем ошибку, процент клея
                    data = int(gl + 0.5)
                    data = struct.pack('<H{}s'.format(len(file_name)), data, data1)
                else:
                    G.append(0)
                    data = 0    #bytearray()
                    data = struct.pack('<H{}s'.format(len(file_name)), data, data1)

            else:
                data = 120
                data = struct.pack('<H', data)

            counter_foto += 1
            w.tx(addr, frm, cmd, data)


        # Калибровка камеры, определяем сколько пикселей в одном милиметре
        if cmd == 0x24:

            event.set()
            sleep(0.5)

            shutil.copy('./image.png', './calibration/calib.png')

            one_mm = vision.calibration(counter_foto)
            print('one_mm = ', one_mm)

            if one_mm != -1:
                data = bytearray()
            else:
                data = 124
                data = struct.pack('<H', data)

            w.tx(addr, frm, cmd, data)


        # Старт программы, передается положение шва
        if cmd == 0x26:

            if len(data) == 4:
                Center_data = struct.unpack('<HH', data)

                Center = Center_data[0]
                Number_seam = Center_data[1]


                print('Center = ',Center)
                print('Number_seam = ',Number_seam)


                for i in file_for_clean:
                    af.cleaner(i)

                data = bytearray()

            else:
                data = 120
                data = struct.pack('<H', data)

            w.tx(addr, frm, cmd, data)


        # Завершение скрипта
        if cmd == 0x25:
            print('Exit')
            print('x =', X)
            print('c =', C)
            print('g =', G)

            #af.create_grafica_G(X, G)
            #af.create_grafica_C(X, C)
            #af.create_grafica_Sum(X, C, G)

            event_cam.set()
            sleep(1)
            w.stop()
            quit()

def cam():
    '''данная функция осоществляет инициализацию камеры и ее запуск'''
    # init camera
    hcam = ueye.HIDS(0)
    ret = ueye.is_InitCamera(hcam, None)
    print(f"initCamera returns {ret}")

    # set color mode
    m_nColorMode = ueye.IS_CM_BGR8_PACKED
    ret = ueye.is_SetColorMode(hcam, ueye.IS_CM_BGR8_PACKED)
    print(f"SetColorMode IS_CM_BGR8_PACKED returns {ret}")

    # set region of interest
    width = 1280
    height = 1080
    rect_aoi = ueye.IS_RECT()
    rect_aoi.s32X = ueye.int(0)
    rect_aoi.s32Y = ueye.int(0)
    rect_aoi.s32Width = ueye.int(width)
    rect_aoi.s32Height = ueye.int(height)
    ueye.is_AOI(hcam, ueye.IS_AOI_IMAGE_SET_AOI, rect_aoi, ueye.sizeof(rect_aoi))
    print(f"AOI IS_AOI_IMAGE_SET_AOI returns {ret}")

    # allocate memory
    mem_ptr = ueye.c_mem_p()
    mem_id = ueye.int()
    bitspixel = 24  # for colormode = IS_CM_BGR8_PACKED
    ret = ueye.is_AllocImageMem(hcam, width, height, bitspixel,
                                mem_ptr, mem_id)
    print(f"AllocImageMem returns {ret}")

    # set active memory region
    ret = ueye.is_SetImageMem(hcam, mem_ptr, mem_id)
    print(f"SetImageMem returns {ret}")

    # continuous capture to memory
    ret = ueye.is_CaptureVideo(hcam, ueye.IS_DONT_WAIT)
    print(f"CaptureVideo returns {ret}")

    # get data from camera and display
    lineinc = width * int((bitspixel + 7) / 8)

    # setting fps ( для замедления камеры )
    fps = ueye.c_double()
    ueye.is_SetFrameRate(hcam, 3, fps)
    print('fps = ', fps)

    print('*******************************************')
    print('width = ', width)
    print('height = ', height)
    print('bitspixel = ', bitspixel)
    print('lineinc = ', lineinc)
    print('m_nColorMode = ', m_nColorMode)
    count = 0

    addr = 0x20
    frm = 0x01
    cmd =0x20
    data = bytearray()
    sleep(0.5)
    w.tx(addr, frm, cmd, data)

    while True:
        img = ueye.get_data(mem_ptr, width, height, bitspixel, lineinc, copy=True)
        img = np.reshape(img, (height, width, 3))

        if event.wait(timeout=0.1):
            count += 1
            cv2.imwrite('./image.png', img)
        else:
            pass

        event.clear()

        if event_cam.wait(timeout=0.1):
            break
        else:
            pass

    # cleanup
    event_cam.clear()
    ret = ueye.is_StopLiveVideo(hcam, ueye.IS_FORCE_VIDEO_STOP)
    print(f"StopLiveVideo returns {ret}")
    ret = ueye.is_ExitCamera(hcam)
    print(f"ExitCamera returns {ret}")

l = len(sys.argv)
if l <= 1:
    w = wake2.wake2(('localhost', 20000), rx)
else:
    w = wake2.wake2((sys.argv[1], 20000), rx)

th = Thread(target=cam, args=(), daemon=True)
th.start()
event.clear()



