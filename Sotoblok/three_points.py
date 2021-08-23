import cv2 as cv
import function as f

def three_points(img, A, B):

    k=0

    img1 = img.copy()

    a = B[0] -A[0]
    b = B[1] - A[1]


    x_center = (int(a / 2)) + A[0]
    y_center = (int(b / 2)) + A[1]

    x_st = (int(a / 6)) + A[0]
    y_st = (int(b / 6)) + A[1]

    x_end = (int( (5*a)/6) ) + A[0]
    y_end = (int( (5*b)/6) ) + A[1]

    mtx1 = f.chek_matrix(img, x_center, y_center)
    mtx2 = f.chek_matrix(img, x_st, y_st)
    mtx3 = f.chek_matrix(img, x_end, y_end)

    cv.circle(img1, (x_center, y_center), 1, (0, 255, 0), 1)
    cv.circle(img1, (x_st, y_st), 1, (255, 0, 0), 1)
    cv.circle(img1, (x_end, y_end), 1, (0, 0, 255), 1)


    if mtx1:
        k+=1
    if mtx2:
        k+=1
    if mtx3:
        k+=1

    if k>=2:
        return True
    else:
        return False