import os
from matplotlib import pyplot as plt


#строим график показания емкости по длинне шва
def create_grafica_C(X,C):

    fig = plt.figure()

    plt.title('Дефекты емкости')
    plt.xlabel('Длинна шва, мм')
    plt.ylabel('Погрешность,% ')
    plt.grid()

    plt.plot(X, C)

    #plt.show()
    fig.savefig('Def_C.png')


#строим график наличие клея по длинне шва
def create_grafica_G(X,G):
    fig = plt.figure()

    plt.title('Обнаружение клея')
    plt.xlabel('Длинна шва, мм')
    plt.ylabel('Погрешность,% ')
    plt.grid()

    plt.plot(X, G)
    fig.savefig('Find_glue.png')

#строим суммарный график диффектов на основе емкости и клея
def create_grafica_Sum(X,C,G):

    defect = []
    for i in range(len(G)):
        defect.append((C[i] + G[i])/2)

    fig = plt.figure()
    plt.title('Суммарная погрешность')
    plt.xlabel('Длинна шва, мм')
    plt.ylabel('Погрешность,% ')

    plt.bar(X, defect)

    fig.savefig('Sum_def.png')

#функция для отчистки файлов
def cleaner(file_name):

    file_list = os.listdir(file_name)

    file_name = file_name + '/'

    for i in file_list:
        if os.path.isdir(file_name + i):
            cleaner(file_name + i)
        else:
            os.remove(file_name + i)










