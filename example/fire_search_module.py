from jaw_creator import create_jaw
from sklearn.cluster import KMeans
import time


def _get_fire_points(data, num_fire):   # Функция поиска центров пожаров среди точек интереса
    kmeans = KMeans(n_clusters=num_fire, max_iter=100)
    kmeans.fit(data)
    return kmeans.cluster_centers_


_interest_points = []  # Точки интереса для KMeans


def search(drone, home_position, points, num_clusters):
    """Возвращает координаты пожаров : list[]"""
    # drone - Объект Pioneer
    # home_position - Изначальная позиция дрона
    # points - Координаты точек, по которым должен пролететь дрон, для определения пожаров
    # num_clusters - Количество пожаров
    drone.arm()
    drone.takeoff()

    ### ПРОЛЁТ ДРОНА ПО ЗАДАННЫМ ТОЧКАМ ###

    for point in points:
        drone.go_to_local_point(*point, z=1.5, yaw=create_jaw(drone, *point))
        while not drone.point_reached():
            time.sleep(0.5)
            pass
        curr_temp = drone.get_piro_sensor_data()
        if curr_temp is not None and curr_temp >= 100:  # Отбор точек с высокой температурой
            curr_position = drone.get_local_position_lps()
            if curr_position is not None:
                print(f"Temperature: {curr_temp}, drone position: {curr_position}")
                _interest_points.append([curr_position[0], curr_position[1]])  # Добавление точки интереса
                                                                               # с текущей позицией дрона [x, y]
    fire_points = _get_fire_points(_interest_points, num_clusters)  # Нахождение пожаров среди точек интереса
    drone.go_to_local_point(*home_position, z=1.5,
                            yaw=create_jaw(drone, *home_position))  # Возвращение дрона на изначальные координаты
    while not drone.point_reached():
        time.sleep(0.5)
        pass
    drone.land()
    drone.disarm()
    if fire_points is not None:     # Обозначение о выполнении миссии
        print("Drone found the cluster points successfully!\nCluster points: ", end='')
        # for i in fire_points:
        #     print(i, end=' ')
    return fire_points  # Возвращение точек пожара в формате: [[x1, y1], [x2, y2]]
