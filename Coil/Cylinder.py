
import numpy as np
import math

class Cylinder:


    def __init__(self, l1, l2, l3, R, thicnes, step):
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3
        self.R = R
        self.thicnes = thicnes
        self.step = step

    __t_in = 0
    __z_in = 0
    __passage = 0

    def straight_pass(self, l, zona_rev):

        koordinate_z = []
        koordinate_t = []

        if zona_rev:
            t_out = self.__t_in + (l/self.R + (self.thicnes * self.__passage)/self.R)
        else:
            t_out = self.__t_in + l/self.R

        end  = t_out - self.__t_in

        for t in np.arange(0, end, self.step):
            z = round(self.R * t + self.__z_in, 2)
            T = round(t + self.__t_in, 2)
            koordinate_z.append(z)
            koordinate_t.append(T)

        if zona_rev:
            z_out = self.__z_in + (self.l1 + self.thicnes * self.__passage)
        else:
            z_out = self.__z_in + l

        self.__t_in = t_out
        self.__z_in = z_out

        return koordinate_z, koordinate_t


    def reverse_pass(self, l, zona_rev):

        koordinate_z = []
        koordinate_t = []

        if zona_rev:
            t_out = self.__t_in + (l / self.R + (self.thicnes * self.__passage) / self.R)
        else:
            t_out = self.__t_in + l / self.R

        end = t_out - self.__t_in

        for t in np.arange(0, end, self.step):
            z = round(self.__z_in - self.R * t, 2)
            T = round(t + self.__t_in, 2)
            koordinate_z.append(z)
            koordinate_t.append(T)

        if zona_rev:
            z_out = self.__z_in - (self.l1 + self.thicnes * self.__passage)
        else:
            z_out = self.__z_in - l

        self.__t_in = t_out
        self.__z_in = z_out

        return koordinate_z, koordinate_t


    def winding(self):

        while(self.__passage<9):
            koordinate_z = []
            koordinate_t = []
            koordinate_t_grad = []

            self.__t_in = round(2 * math.pi + math.pi/2 + math.pi + self.__t_in, 2)
            koordinate_z.append(self.__z_in)
            koordinate_t.append(self.__t_in)

            zona_rev = True
            z, t = self.straight_pass(self.l1, zona_rev)
            koordinate_z.extend(z)
            koordinate_t.extend(t)

            zona_rev = False
            z, t = self.straight_pass(self.l2, zona_rev)
            koordinate_z.extend(z)
            koordinate_t.extend(t)

            zona_rev = True
            z, t = self.straight_pass(self.l3, zona_rev)
            koordinate_z.extend(z)
            koordinate_t.extend(t)

            self.__t_in = round(2 * math.pi + math.pi/2 + math.pi + self.__t_in, 2)
            koordinate_z.append(self.__z_in)
            koordinate_t.append(self.__t_in)

            # ОБРАТНАЯ НАМОТКА

            z, t = self.reverse_pass(self.l3, zona_rev)
            koordinate_z.extend(z)
            koordinate_t.extend(t)

            zona_rev = False
            z, t = self.reverse_pass(self.l2, zona_rev)
            koordinate_z.extend(z)
            koordinate_t.extend(t)

            zona_rev = True
            z, t = self.reverse_pass(self.l1, zona_rev)
            koordinate_z.extend(z)
            koordinate_t.extend(t)

            self.__passage += 1

        print(koordinate_z)
        print(koordinate_t)

        #Переводим радианы в градусы
        for t in koordinate_t:
            t_grad = round(math.degrees(t), 2)
            koordinate_t_grad.append(t_grad)

        file = open('cod_g.tap', 'w')
        file.write('G21 G49 G80 G90\nG0 X0 A0\n')
        for i in range(len(koordinate_z)):
            z = str(koordinate_z[i])
            t = str(koordinate_t_grad[i])
            if i == 0:
                string = 'G1 X' + z + ' A' + t + ' F10000\n'
            else:
                string = 'X' + z + ' A' + t + '\n'

            string = str(string)
            file.write(string)

        file.write('M30\n')

        file.close()











