from piosdk.piosdk import Pioneer
import threading
from edusdk.edubot_sdk import EdubotGCS
from jaw_creator import create_jaw

### QR-Code: x=5, y=8; Fire: x=8, y=2
### Drone1: x=0, y=0; Drone2: x=0, y=10; Drone3: x=10, y=10; Car1: x=2, y=0

drones = {"drone1": [1, 1],
          "drone2": [5, 0],
          "drone3": [0, 0]}
robots = {"car1": [10, 0],
          "car2": [0, 10]}
fires = {"fire1": [2, 2]}
qr_codes = {"qr1": [7, 0]}

drone1 = Pioneer(method=2, pioneer_ip="127.0.0.1", pioneer_mavlink_port=30000)
drone2 = Pioneer(method=2, pioneer_ip="127.0.0.1", pioneer_mavlink_port=30001)
drone3 = Pioneer(method=2, pioneer_ip="127.0.0.1", pioneer_mavlink_port=30002)

car1 = EdubotGCS(ip="127.0.0.1", mavlink_port=40000, connection_method="udpout")
car2 = EdubotGCS(ip="127.0.0.1", mavlink_port=40001, connection_method="udpout")


def task_drone1():
    drone1.arm()
    drone1.takeoff()
    drone1.go_to_local_point(fires["fire1"][0], fires["fire1"][1], 1.5,
                             yaw=create_jaw(drone1, fires["fire1"][0], fires["fire1"][1]))
    while not drone1.point_reached():
        pass
    fire_info = drone1.get_piro_sensor_data()
    if fire_info is not None:
        print("Информация о пожаре получена успешно!")
    drone1.go_to_local_point(drones["drone1"][0], drones["drone1"][1], 1.5,
                             yaw=create_jaw(drone1, drones["drone1"][0], drones["drone1"][1]))
    while not drone1.point_reached():
        pass
    drone1.land()
    drone1.disarm()
    print(fire_info)

def task_drone2():
    drone2.arm()
    drone2.takeoff()
    drone2.go_to_local_point(qr_codes["qr1"][0], qr_codes["qr1"][1], 1.5,
                             yaw=create_jaw(drone2, qr_codes["qr1"][0], qr_codes["qr1"][1]))
    while not drone2.point_reached():
        pass
    qr_info = drone2.get_qr_reader_data()
    if qr_info is not None:
        print("Информация с QR-кода получена успешно!")
    drone2.go_to_local_point(drones["drone2"][0], drones["drone2"][1], 1.5,
                             yaw=create_jaw(drone2, drones["drone2"][0], drones["drone2"][1]))
    while not drone2.point_reached():
        pass
    drone2.land()
    drone2.disarm()
    print(qr_info)


def task_drone3():
    drone3.arm()
    drone3.takeoff()
    drone3.go_to_local_point(3, 3, 1.5,
                             yaw=create_jaw(drone3, 3, 3))
    while not drone3.point_reached():
        pass
    drone3.land()
    drone3.disarm()


def task_car1():
    car1.go_to_local_point(5, 0)


def task_car2():
    car2.go_to_local_point(0, 5)


thread1 = threading.Thread(target=task_drone1)
thread2 = threading.Thread(target=task_drone2)
thread3 = threading.Thread(target=task_drone3)
thread4 = threading.Thread(target=task_car1)
thread5 = threading.Thread(target=task_car2)
thread2.start()
thread1.start()
thread1.join()
thread2.join()
thread3.start()
thread4.start()
thread5.start()
thread3.join()
thread4.join()
thread5.join()


