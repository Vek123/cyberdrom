from jaw_creator import create_jaw
from sklearn.cluster import KMeans
import time
from piosdk.piosdk import Pioneer


class Searcher(Pioneer):
    # def __init__(self, points=None, num_clusters=0, home_position=None):
    #     self.points = points
    #     self.num_clusters = num_clusters
    #     self.interest_points = []  # Точки интереса для KMeans
    #     self.home_position = home_position

    @staticmethod
    def get_fire_points(data, num_fire):  # Функция поиска центров пожаров среди точек интереса
        kmeans = KMeans(n_clusters=num_fire, max_iter=100, n_init='auto')
        kmeans.fit(data)
        return kmeans.cluster_centers_

    def search(self, points, num_clusters, home_position, stop_cord=None):
        """Возвращает координаты пожаров : np.array[]"""
        # drone - Объект Pioneer
        # home_position - Изначальная позиция дрона
        # points - Координаты точек, по которым должен пролететь дрон, для определения пожаров
        # num_clusters - Количество пожаров
        self.arm()
        self.takeoff()
        interest_points = []
        ### ПРОЛЁТ ДРОНА ПО ЗАДАННЫМ ТОЧКАМ ###

        for point in points:  # Проходим по точкам по порядку
            if point == stop_cord:  # Проверка на стопающую точку
                break
            # print(f"Interest_points for {str(self)}: {interest_points}") # Вывод массива точек интереса для объекта
            # класса
            self.go_to_local_point(*point, z=1.5, yaw=create_jaw(self, *point))  # отправляем дрона на следующую точку
            while not self.point_reached():  # проверка на достижение точки
                time.sleep(0.5)
                pass
            curr_temp = self.get_piro_sensor_data()  # измеряем температуру
            if curr_temp is not None and curr_temp >= 30:  # Отбор точек с высокой температурой
                curr_position = self.get_local_position_lps()
                while curr_position is None:  # проверка на получение координат дрона
                    curr_position = self.get_local_position_lps()
                self.fire_detection()  # мигание светодиодом
                time.sleep(5)  # пауза 5 сек
                # print(f"Temperature: {curr_temp}, drone position: {curr_position}") # вывод позиции дрона и
                # измеренной температуры
                interest_points.append([curr_position[0], curr_position[1]])  # Добавление точки интереса
                # с текущей позицией дрона [x, y]
        fire_points = self.get_fire_points(interest_points,
                                           num_clusters)  # Нахождение пожаров среди точек интереса
        self.go_to_local_point(*home_position, z=1.5,
                               yaw=create_jaw(self, *home_position))  # Возвращение дрона на изначальные координаты
        while not self.point_reached():
            time.sleep(0.5)
            pass
        self.land()
        self.disarm()
        if fire_points is not None:  # Обозначение о выполнении миссии
            print("Drone found the cluster points successfully!\nCluster points: ", end='')
            for i in fire_points:
                print(i, end=' ')
        return fire_points  # Возвращение точек пожара в формате: [[x1, y1], [x2, y2]]
