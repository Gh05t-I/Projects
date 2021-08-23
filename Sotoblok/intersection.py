import math
import cv2 as cv


def intersection(img,lineA, lineB):

    root = True

    img_c = img.copy()

    x1 = lineA[0]
    x2 = lineA[2]
    y1 = lineA[1]
    y2 = lineA[3]

    x3 = lineB[0]
    x4 = lineB[2]
    y3 = lineB[1]
    y4 = lineB[3]

    a = x2 - x1
    b = y2 - y1
    c = y4 - y3
    d = x4 - x3

    AandB = a * d + b * c  # Скалярное произведение
    modAB = (a ** 2 + b ** 2) ** 0.5 * (d ** 2 + c ** 2) ** 0.5  # Произведение длин векторов

    cos = AandB / modAB 

    # Значение могут получаться больше 1 и -1
    if (cos > 1) or (cos < -1):
        cos = int(cos)
        print('cos int = ', cos)

    rad = math.acos(cos)

    degree = int(math.degrees(rad))

    point = []

    if degree == 0 or degree == 180:
        return None
    elif degree == 90:
        if lineA[0] == lineA[2]:
            x = lineA[0]
            y = lineB[1]
        else:
            x = lineB[0]
            y = lineA[1]

        # проверка на совпадение линии реза и грани с осями.
        if (x2 == x1) or (y3 == y4):
            if x == x2 and y == y3:
                pass
            else:
                root = False
        elif (y2 == y1) or (x3 == x4):
            if x == x3 and y == y2:
                pass
            else:
                root = False
        else:
            # по каноническому уравнению прямой расчитываем значение правой и левой части
            lx_1 = (x - x1) / (x2 - x1)
            ry_1 = (y - y1) / (y2 - y1)

            lx_2 = (x - x3) / (x4 - x3)
            ry_2 = (y - y3) / (y4 - y3)

            if lx_1 == ry_1 and lx_2 == ry_2:
                pass
            else:
                root = False
    else:
        try:
            y = (x1 * b * c - y1 * c * a + y3 * d * b - x3 * b * c) / ((b * d) - (c * a))

            if b == 0:
                x = ((y - y3) * d + x3 * c) / c
            else:
                x = ((y - y1) * a + x1 * b) / b
        except ZeroDivisionError:
            root = False
            print('корней нет')
    if root:
        point.append(x)
        point.append(y)
    return point




def two_del_five(edge):
    a = edge[2] - edge[0]
    b = edge[3] - edge[1]

    x = int((2 * a) / 5) + edge[0]
    y = int((2 * b) / 5) + edge[1]

    point = []
    point.append(x)
    point.append(y)

    return point
    

def knife(img, edge, x_cut, y_cut, R=20):

    img_c = img.copy()

    if edge[1] > edge[3]:
        y = edge[1]
        x = edge[0]
    else:
        y = edge[3]
        x = edge[2]

    horizont = [0, y, x, y]

    a = edge[2] - edge[0]
    b = edge[3] - edge[1]
    c = horizont[3] - horizont[1]
    d = horizont[2] - horizont[0]

    AandB = a * d + b * c  # Скалярное произведение
    modAB = (a ** 2 + b ** 2) ** 0.5 * (d ** 2 + c ** 2) ** 0.5  # Произведение длин векторов

    cos = AandB / modAB

    rad = math.acos(cos)
    degree = (math.degrees(rad)) * (1)

    if degree > 90:
        degree = 180 - degree
    
    alfa = 90 - degree  # строим перпендикуляр

    #требуется для построения перпендикуляра, особенность векторного произ. и зеркальной системы координат.
    if ((a > 0) and (b > 0)) or ((a < 0) and (b < 0)):
        alfa = alfa * (-1)
        print('new alfa = ', alfa)

    rad = math.radians(alfa)
    x1 = R * math.cos(rad) + x_cut
    y1 = R * math.sin(rad) + y_cut

    if alfa >= 0:
        alfa = alfa - 180
    else:
        alfa = alfa + 180

    rad = math.radians(alfa)
    x2 = R * math.cos(rad) + x_cut
    y2 = R * math.sin(rad) + y_cut

    knife = []
    knife.append(x1)
    knife.append(y1)
    knife.append(x2)
    knife.append(y2)
    knife.append(alfa)

    return knife
