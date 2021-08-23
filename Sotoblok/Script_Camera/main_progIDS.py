from pyueye import ueye
import numpy as np
import cv2

from pyueye.ueye import WB_MODE_DISABLE
from pyueye.ueye import double




def main():
    # init camera
    hcam = ueye.HIDS(0)
    ret = ueye.is_InitCamera(hcam, None)
    print(f"initCamera returns {ret}")

    #z = ueye.double

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

    # делаем автоматическую подстройку яркости для камеры
    x = ueye.c_double(1)
    y = ueye.c_double(0)
    ueye.is_SetAutoParameter(hcam, ueye.IS_SET_ENABLE_AUTO_GAIN, x, y)


    print('*******************************************')
    print('width = ',width)
    print('height = ', height)
    print('bitspixel = ', bitspixel)
    print('lineinc = ', lineinc)
    print('m_nColorMode = ', m_nColorMode)


    om =0
    points = []
    while True:
        img = ueye.get_data(mem_ptr, width, height, bitspixel, lineinc, copy=True)
        img = np.reshape(img, (height, width, 3))

        #img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)

        img_sniper = img.copy()

        h, w, _ = img.shape

        cv2.line(img_sniper, (0, int(h / 2)), (w, int(h / 2)), (0, 0, 255), 1)
        cv2.line(img_sniper, (int(w / 2), 0), (int(w / 2), h), (0, 0, 255), 1)


        cv2.imshow('uEye Python Example (q to exit)', img_sniper)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('f'):
            cv2.imwrite('foto.jpg', img)
    





    cv2.destroyAllWindows()

    # cleanup
    ret = ueye.is_StopLiveVideo(hcam, ueye.IS_FORCE_VIDEO_STOP)
    print(f"StopLiveVideo returns {ret}")
    ret = ueye.is_ExitCamera(hcam)
    print(f"ExitCamera returns {ret}")


if __name__ == '__main__':
    main()
