import threading
from jaw_creator import create_jaw
from piosdk.piosdk import Pioneer
from edusdk.edubot_sdk import EdubotGCS
from sklearn.cluster import KMeans
import dataclasses
import time


@dataclasses.dataclass
class RobotConfig:
    drone1_config = {
        "ip": "127.0.0.1",
        "port": 8000,
        "cords": (0, 0)
    }
    robot1_config = {
        "ip": "127.0.0.1",
        "port": 8001,
        "cords": (1, 0)
    }
    robot2_config = {
        "ip": "127.0.0.1",
        "port": 8002,
        "cords": (2, 0)
    }
    bucket_up = 150
    bucket_down = 0


drone1 = Pioneer(pioneer_ip=RobotConfig.drone1_config["ip"], pioneer_mavlink_port=RobotConfig.drone1_config["port"],
                 method=2)
robot1 = EdubotGCS(ip=RobotConfig.robot1_config["ip"], mavlink_port=RobotConfig.robot1_config["port"],
                   connection_method="udpout")
robot2 = EdubotGCS(ip=RobotConfig.robot2_config["ip"], mavlink_port=RobotConfig.robot2_config["port"],
                   connection_method="udpout")


def _get_fire_points(data, num_fire):
    kmeans = KMeans(n_clusters=num_fire, max_iter=100)
    kmeans.fit(data)
    return kmeans.cluster_centers_


fire_points = None
points = [
    [5, 0],
    [5, 0.5],
    [5, 1],  # FIRE
    [5, 1.5],
    [5, 2],
    [5, 2.5],  # FIRE
    [5, 3],
    [5, 3.5],
    [5, 4],  # FIRE
    [5, 4.5],
    [5, 5]
]
interest_points = []
drone1.arm()
drone1.takeoff()


def search():
    global fire_points
    for point in points:
        drone1.go_to_local_point(*point, z=1.5, yaw=create_jaw(drone1, *point))
        while not drone1.point_reached():
            time.sleep(0.5)
            pass
        curr_temp = drone1.get_piro_sensor_data()
        if curr_temp is not None and curr_temp >= 100:
            curr_position = drone1.get_local_position_lps()
            if curr_position is not None:
                print(f"Temperature: {curr_temp}, drone position: {curr_position}")
                interest_points.append([curr_position[0], curr_position[1]])
    fire_points = _get_fire_points(interest_points, 3)
    drone1.go_to_local_point(*RobotConfig.drone1_config["cords"], z=1.5,
                             yaw=create_jaw(drone1, *RobotConfig.drone1_config["cords"]))
    while not drone1.point_reached():
        time.sleep(0.5)
        pass
    drone1.land()
    drone1.disarm()
    if fire_points is not None:
        print("Drone found the cluster points successfully!\nCluster points: ", end='')
        for i in fire_points:
            print(i, end=' ')


def robot_script(model, bucket=False, script=None):
    for step in script:
        if step[0] == 'bucket' and bucket:
            print(f"Bucket status is {step[1]}")
        if step[0] == 'go':
            model.go_to_local_point(*step[1])
            while not model.point_reached():
                time.sleep(0.5)
                pass


t1 = threading.Thread(target=search, daemon=True)
t1.start()
t1.join()

robot1_script = [
    ['bucket', RobotConfig.bucket_up],
    ['go', [*fire_points[0]]],
    ['bucket', RobotConfig.bucket_down],
    ['go', [*RobotConfig.robot1_config["cords"]]],
    ['bucket', RobotConfig.bucket_up],
    ['go', [*fire_points[1]]],
    ['bucket', RobotConfig.bucket_down],
    ['go', [*RobotConfig.robot1_config["cords"]]]
]

robot2_script = [
    ['bucket', RobotConfig.bucket_up],
    ['go', [*fire_points[2]]],
    ['bucket', RobotConfig.bucket_down],
    ['go', [*RobotConfig.robot2_config["cords"]]]
]

t2 = threading.Thread(target=robot_script, args=[robot1, True, robot1_script])
t3 = threading.Thread(target=robot_script, args=[robot2, True, robot2_script])
t2.start()
t3.start()
t2.join()
t3.join()
