import cv2 as cv
import copy
import function as f
import three_points as tp

#points = [[219, 569], [452, 555], [182, 435], [492, 420], [40, 302], [340, 284], [72, 169], [330, 146], [597, 144],
#          [208, 69], [455, 54]]
#filename = './pictures/img.jpg'
#img2 = cv.imread(filename, cv.IMREAD_COLOR)


def number3(img, points):
    '''
    Функция принимает на вход изображение и массив точек узлов
    img - входное изображение
    points - массив узловых точек

    функция выполняет поиск граней на основе массива points, берется точка из массива высчитывается расстояния до
    остальных точек, если расстояние меньше порого Lenght_edge то предпологаем что есть грань между точками

    На выходе функция выдает массив граней ( грань это список с 4 параметрами которые описывают координаты 2-х точек)
    '''
    points1 = copy.deepcopy(points)
    Lenght_edge = 90#45  # 220

    img1 = img.copy()
    img2 = img1.copy()

    list_edge = []

    for i in points:
        node = 0
        for j in points1:

            a = i[0] - j[0]
            b = i[1] - j[1]

            l = (a ** 2 + b ** 2) ** 0.5

            if l > Lenght_edge or l == 0:
                continue
            else:
                matrix = tp.three_points(img2, i ,j)

                if matrix:
                    cv.line(img1, (i[0], i[1]), (j[0], j[1]), (0, 0, 255), 2)

                    node += 1

                    edge = [0, 0, 0, 0]
                    edge[0] = i[0]
                    edge[1] = i[1]
                    edge[2] = j[0]
                    edge[3] = j[1]
                    list_edge.append(edge)

                    

            if node >= 3:
                break

    cv.imwrite('./pictures/number3/line.jpg', img1)

    return list_edge, img1
