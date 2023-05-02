import threading
from piosdk.piosdk import Pioneer
from edusdk.edubot_sdk import EdubotGCS
import dataclasses
import time
import numpy as np
from fire_search_module import Searcher


@dataclasses.dataclass
class RobotConfig:
    drone1_config = {
        "ip": "127.0.0.1",
        "port": 8000,
        "cords": (0, 0),
        "echelon": 1
    }
    drone2_config = {
        "ip": "127.0.0.1",
        "port": 8001,
        "cords": (1, 0),
        "echelon": 1.5
    }
    robot1_config = {
        "ip": "127.0.0.1",
        "port": 8002,
        "cords": (8, 0)
    }
    robot2_config = {
        "ip": "127.0.0.1",
        "port": 8003,
        "cords": (5, 0)
    }
    fires = [
        [1, 5],
        [3, 8],
        [5, 5],
        [8, 2],
        [8.2, 5.6]
    ]
    drone1_field = [
        [1, 1],
        [5, 8]
    ]
    drone2_field = [
        [5, 2],
        [9, 8]
    ]


def get_snake_trajectory(start_point, end_point, step_x, step_y):
    cord_step_x = (end_point[0] - start_point[0]) / step_x
    cord_step_y = (end_point[1] - start_point[1]) / step_y
    curr_x = start_point[0]
    curr_y = start_point[1]
    trajectory = []
    while not [curr_x, curr_y] == end_point:
        trajectory.append([curr_x, curr_y])
        if curr_x % 2 == start_point[0] % 2:
            curr_y += cord_step_y
        else:
            curr_y -= cord_step_y
        if curr_y - 1 == end_point[1]:
            curr_x += cord_step_x
            curr_y -= cord_step_y
        elif curr_y + 1 == start_point[1]:
            curr_x += cord_step_x
            curr_y += cord_step_y
    trajectory.append(end_point)
    return trajectory


# for i in range(RobotConfig.field_work[0][0], RobotConfig.field_work[1][0]+1):
#     for j in range(RobotConfig.field_work[0][1], RobotConfig.field_work[1][1]+1):


drone1 = Searcher(pioneer_ip=RobotConfig.drone1_config["ip"], pioneer_mavlink_port=RobotConfig.drone1_config["port"],
                  method=2)
drone2 = Searcher(pioneer_ip=RobotConfig.drone2_config["ip"], pioneer_mavlink_port=RobotConfig.drone2_config["port"],
                  method=2)
robot1 = EdubotGCS(ip=RobotConfig.robot2_config["ip"], mavlink_port=RobotConfig.robot2_config["port"],
                   connection_method="udpout")
robot2 = EdubotGCS(ip=RobotConfig.robot2_config["ip"], mavlink_port=RobotConfig.robot2_config["port"],
                   connection_method="udpout")
points1 = get_snake_trajectory([1, 1], [5, 8], 4, 7)
points2 = get_snake_trajectory([5, 1], [9, 8], 4, 7)

fire_points1 = None
fire_points2 = None


def tr1():
    global fire_points1
    fire_points1 = drone1.search(points1, 2, RobotConfig.drone1_config["cords"], stop_cord=[4, 1]) #fire_search_module.search(drone1, RobotConfig.drone1_config["cords"], points1, 3)


def tr2():
    global fire_points2
    fire_points2 = drone2.search(points2, 3, RobotConfig.drone2_config["cords"])


thread1 = threading.Thread(target=tr1, daemon=True)
thread2 = threading.Thread(target=tr2, daemon=True)
thread1.start()
thread2.start()
thread1.join()
thread2.join()
