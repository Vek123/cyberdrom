import time
import threading
from piosdk.piosdk import Pioneer
from sklearn.cluster import KMeans  # pip install scikit-learn


def get_center_clusters(data, num_clasters):
    """ Поиск кластеров в наборе данных """
    kmeans = KMeans(n_clusters=num_clasters, max_iter=100)
    kmeans.fit(data)
    return kmeans.cluster_centers_


drones = []

drones.append(Pioneer(method=2, pioneer_ip="127.0.0.1", pioneer_mavlink_port=8000, logger=False))
drones.append(Pioneer(method=2, pioneer_ip="127.0.0.1", pioneer_mavlink_port=8001, logger=False))
drones.append(Pioneer(method=2, pioneer_ip="127.0.0.1", pioneer_mavlink_port=8002, logger=False))

points_interest = []  # массив хранит в себе все точки, где температура была 60
centre_fire = []  # массив куда запишутся центры кластеров
state_mission = [0, 0, 0]  # состояние каждой миссии. 0 - не выполняется, 1 - выполняется, 2 - выполнена


def search():
    state_mission[0] = 1
    # Полет по точкам для дрона 0
    mission_point = [
        [5, 1, 2.3],  # fire
        [5, 1.5, 2.3],
        [5, 2, 2.5],
        [5, 2.5, 3],
        [5, 3, 3],  # fire
        [5, 3.5, 3],
        [5, 4, 3],
        [5, 4.5, 3],
        [5, 5, 3],
        [5, 5.5, 3],
        [5, 6, 3],
        [5, 6.5, 3],
        [5, 7, 3],  # fire
        [2, 1, 3]
    ]
    current_mission_point = 0

    drones[0].arm()
    drones[0].takeoff()
    new_point = True
    while True:
        current_temp = drones[0].get_piro_sensor_data(blocking=True)
        if current_temp is not None and current_temp >= 100:
            curr_pos = drones[0].get_local_position_lps(blocking=True)
            if curr_pos is not None:
                print(curr_pos, current_temp)
                points_interest.append([curr_pos[0], curr_pos[1]])

        # print(drones[0].get_local_position_lps(blocking=True))
        if new_point:
            drones[0].go_to_local_point(x=mission_point[current_mission_point][0],
                                        y=mission_point[current_mission_point][1],
                                        z=mission_point[current_mission_point][2])

            new_point = False

        if drones[0].point_reached(True):
            new_point = True
            current_mission_point += 1

            if current_mission_point >= len(mission_point):
                break

        time.sleep(0.001)

    drones[0].land()
    state_mission[0] = 2


def action_drone1():
    state_mission[1] = 1
    mission_point = [
        centre_fire[1],
        [2, 4, 1.5]
    ]

    current_mission_point = 0

    drones[1].arm()
    drones[1].takeoff()
    new_point = True
    while True:
        if new_point:
            drones[1].go_to_local_point(x=mission_point[current_mission_point][0],
                                        y=mission_point[current_mission_point][1],
                                        z=mission_point[current_mission_point][2])

            new_point = False

        if drones[1].point_reached(True):
            new_point = True
            current_mission_point += 1

            if current_mission_point >= len(mission_point):
                break

        time.sleep(0.25)

    drones[1].land()
    state_mission[1] = 2


def action_drone2():
    state_mission[2] = 1
    mission_point = [
        centre_fire[0],
        [2, 6, 1.5]
    ]

    current_mission_point = 0

    drones[2].arm()
    drones[2].takeoff()
    new_point = True
    while True:
        if new_point:
            drones[2].go_to_local_point(x=mission_point[current_mission_point][0],
                                        y=mission_point[current_mission_point][1],
                                        z=mission_point[current_mission_point][2])

            new_point = False

        if drones[2].point_reached(True):
            if current_mission_point == 0:
                drones[2].led_custom(mode=2, color1=[255, 0, 0], color2=[200, 200, 200], timer=10)
                time.sleep(5)
            new_point = True
            current_mission_point += 1

            if current_mission_point >= len(mission_point):
                break

        time.sleep(0.25)

    drones[2].land()
    state_mission[2] = 2


is_start_thread = False
if __name__ == '__main__':
    # Создаем поток для поиска пожаров и запускаем
    search_thread = threading.Thread(target=search)
    search_thread.start()

    # Создаем поток для тушения пожаров
    action_drone1_thread = threading.Thread(target=action_drone1)
    action_drone2_thread = threading.Thread(target=action_drone2)

    # Основной цикл программы. Он работает вне зависимости от потоков.
    while True:
        # Если миссия 0 (поиск пожара) имеет статус 2(миссия закончена) и при этом центры пожаров еще не найдены
        if state_mission[0] == 2 and len(centre_fire) == 0:
            print(points_interest)

            # Вызываем функцию для поиска центров кластеров. Тк пожара 3, то кол-во кластеров равно двум
            centre = get_center_clusters(data=points_interest, num_clasters=3)
            print(centre)

            # Добавляем найденный центры в массив, так же приписываем им координату z
            for c in centre:
                centre_fire.append([c[0], c[1], 1])

        # Если миссия поиска завершена, и найдены центры, то запускаем потоки на тушение
        if state_mission[0] == 2 and len(centre_fire) != 0 and not is_start_thread:
            is_start_thread = True
            action_drone1_thread.start()
            action_drone2_thread.start()

        time.sleep(0.25)
