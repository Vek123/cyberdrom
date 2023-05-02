import math


def create_jaw(drone=None, x=0, y=0):
    try:
        start_cords = drone.get_local_position_lps()  # запрашиваем координаты дрона (Работает криво из-за проблем piosdk)
        if start_cords is None:
            start_cords = [0, 0, 0]
        # print(f"Начальные координаты отсчёта: {start_cords[0]}, {start_cords[1]}") # Выводим начальные координаты дрона (для отладки)

        ### ВЫЧИСЛЯЕМ СТОРОНЫ ВИРТУАЛЬНОГО ТРЕУГОЛЬНИКА

        a = abs(x - start_cords[0])
        b = abs(y - start_cords[1])
        c = round(math.sqrt(a ** 2 + b ** 2), 2)

        ### ВЫЧИСЛЯЕМ УГОЛ ОТНОСИТЕЛЬНО НАПРАВЛЕНИЯ ПОЛЁТА ДРОНА
        # Угол вычисляется с помощью теоремы косинусов

        # Если дрон двигается в положительном направлении по оси X и по оси Y
        if x - start_cords[0] > 0 and y - start_cords[1] > 0:
            angle = round(math.degrees(math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))), 0)
        # Если дрон двигается в положительном направлении по оси X, а по оси Y в отрицательном направлении
        elif x - start_cords[0] > 0 and y - start_cords[1] < 0:
            angle = 180 - round(math.degrees(math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))), 0)
        # Если дрон двигается в отрицательном направлении по оси X и по оси Y
        elif x - start_cords[0] < 0 and y - start_cords[1] < 0:
            angle = -180 + round(math.degrees(math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))), 0)
        # Если дрон двигается в отрицательном направлении по оси X, а по оси Y в положительном направлении
        elif x - start_cords[0] < 0 and y - start_cords[1] > 0:
            angle = -round(math.degrees(math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))), 0)
        # Если дрон двигается только по оси Y в положительном направлении
        elif x - start_cords[0] == 0 and y - start_cords[1] > 0:
            angle = 0
        # Если дрон двигается только по оси Y в отрицательном направлении
        elif x - start_cords[0] == 0 and y - start_cords[1] < 0:
            angle = 180
        # Если дрон двигается только по оси X в положительном направлении
        elif x - start_cords[0] > 0 and y - start_cords[1] == 0:
            angle = 90
        # Если дрон двигается только по оси Y в отрицательном направлении
        elif x - start_cords[0] < 0 and y - start_cords[1] == 0:
            angle = 270
        else:
            angle = 0
        return angle  # Возвращаем необходимый угол поворота дрона относительно оси Y
    except AttributeError:
        return None
