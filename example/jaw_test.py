from piosdk.piosdk import Pioneer
from jaw_creator import create_jaw
from dataclasses import dataclass


@dataclass
class RobotConfig:
    drone1 = {
        "ip": "127.0.0.1",
        "port": 8000,
        "cords": (0, 0)
    }
    points = [
        [4, 5],
        [2, 1],
        [-3, -1]
    ]


drone1 = Pioneer(pioneer_ip=RobotConfig.drone1["ip"], pioneer_mavlink_port=RobotConfig.drone1["port"],
                 method=2)
drone1.arm()
drone1.takeoff()
for point in RobotConfig.points:
    drone1.go_to_local_point(*point, yaw=create_jaw(drone1, *point))
    while not drone1.point_reached():
        continue
drone1.go_to_local_point(0, 0, yaw=create_jaw(drone1, 0, 0))
while not drone1.point_reached():
    continue
drone1.land()
drone1.disarm()
