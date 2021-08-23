
def analysis_data(mas_data, min, max):
    '''данная функция анализирует данные которые пришли с сервера с датчиков емкости,
    высчитываем количество данных которые выпадают из диапазона'''
    defect = []
    number_defect_element = 0

    for ms_d in mas_data:
        df = []
        for md in ms_d:
            if md < min or md > max:
                df.append(md)
                number_defect_element += 1
        defect.append(df)

    return number_defect_element, defect

