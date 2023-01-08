import os
import django
#Crimes against humanity
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task1_beb.settings")
django.setup()

from task1_beb.settings_reader import robot_info
from django.conf import settings
from app1.models import Robot, RobotData
import datetime
import random

robot_telemetry = {
    'timestamp': datetime.datetime.now(),
    'humidity': 0,
    'temperature': 0,
    'pressure': 0,
}

robot_location = {
    'timestamp': datetime.datetime.now(),
    'latitude': 0.0,
    'longitude': 0.0,
}


def time_in_seconds(time_messured):
    return datetime.timedelta.total_seconds(time_messured)

def update_data():
    robot = robot_info()

    #Randomizing data send:
    robot_telemetry["timestamp"] = datetime.datetime.now()
    robot_telemetry["humidity"] = random.randint(0, 100)
    robot_telemetry["temperature"] = random.randint(-10, 40)
    robot_telemetry["pressure"] = random.randint(970, 1030)
    robot_location["timestamp"] = datetime.datetime.now()
    robot_location["latitude"] = random.randint(0, 90)
    robot_location["longitude"] = random.randint(0, 90)

    Robot.objects.filter(serial_number=robot["serial_number"]).update(telemetry_timestamp = robot_telemetry["timestamp"], 
                                                                      telemetry_humidity=robot_telemetry["humidity"],
                                                                      telemetry_temperature = robot_telemetry["temperature"],
                                                                      telemetry_pressure = robot_telemetry["pressure"],
                                                                      location_timestamp = robot_location["timestamp"],
                                                                      location_latitude = robot_location["latitude"],
                                                                      location_longitude = robot_location["longitude"],)
        
def make_robot_info():
    robot = robot_info()
    return f'Robot {robot["serial_number"]} - {robot["production_date"]}. Type: {robot["type"]} - '

def add_robot():
    robot = robot_info()
    if Robot.objects.filter(serial_number = robot["serial_number"]).exists():
        pass
    else:
        new_robot = Robot(serial_number = robot["serial_number"], production_date = robot["production_date"], type = robot["type"], company = robot["company"])
        new_robot.save()
