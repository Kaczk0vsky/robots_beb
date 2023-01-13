import os
import django
import datetime
import random
from django.conf import settings
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task1_beb.settings")
django.setup()

from robot.settings_reader import robot_info
from app1.models import Robot, RobotLog

#dicts containing robot data
robot_telemetry = {
    'humidity': 0,
    'temperature': 0,
    'pressure': 0,
}

robot_location = {
    'latitude': 0.0,
    'longitude': 0.0,
}

robot_timestamp = {
    'timestamp': timezone.now(),
}

def time_in_seconds(time_messured):
    return datetime.timedelta.total_seconds(time_messured)

def update_data():
    #getting info from settings.toml as a dict
    robot = robot_info()

    #randomizing data send:
    robot_timestamp["timestamp"] = timezone.now()
    robot_telemetry["humidity"] = random.randint(0, 100)
    robot_telemetry["temperature"] = random.randint(-10, 40)
    robot_telemetry["pressure"] = random.randint(970, 1030)
    robot_location["latitude"] = random.randint(0, 90)
    robot_location["longitude"] = random.randint(0, 90)

    #saving latest robot data
    RobotLog.objects.filter(robot_id = robot["serial_number"]).update_or_create(
                                                                    robot_id = robot["serial_number"],
                                                                    timestamp = robot_timestamp["timestamp"], 
                                                                    telemetry_humidity = robot_telemetry["humidity"],
                                                                    telemetry_temperature = robot_telemetry["temperature"],
                                                                    telemetry_pressure = robot_telemetry["pressure"],
                                                                    location_latitude = robot_location["latitude"],
                                                                    location_longitude = robot_location["longitude"],)

def make_robot_info():
    robot = robot_info()
    return f'Robot {robot["serial_number"]} - {robot["production_date"]}. Type: {robot["type"]} - '

def add_robot():
    robot = robot_info()
    if Robot.objects.filter(pk=robot["serial_number"]).exists():
        pass
    else:
        Robot(
            serial_number = robot["serial_number"],
            production_date = robot["production_date"],
            type = robot["type"], 
            company = robot["company"], 
            ).save()
    