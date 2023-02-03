import os
import django
import datetime
import random
import logging
import json
from django.conf import settings
from django.utils import timezone
from paho.mqtt import client as mqtt

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task1_beb.settings")
django.setup()

from robot.settings_reader import robot_info, robot_sensors, mqtt_settings
from app1.models import Robot, RobotLog


logger = logging.getLogger(__name__)
mqqt_config = mqtt_settings()
robot_data = robot_info()
client = mqtt.Client()


# dicts containing robot data
robot_telemetry = {
    "humidity": 0,
    "temperature": 0,
    "pressure": 0,
}

robot_location = {
    "latitude": 0.0,
    "longitude": 0.0,
}

robot_timestamp = {
    "timestamp": timezone.now(),
}

sensors_data = {}
mqtt_topics = {}


def time_in_seconds(time_messured):
    return datetime.timedelta.total_seconds(time_messured)


def update_data():
    # getting info from settings.toml as a dict
    robot = robot_info()

    # randomizing data send:
    robot_timestamp["timestamp"] = str(timezone.now())
    timestamp = robot_timestamp["timestamp"].encode(encoding="UTF-8").hex()
    robot_telemetry["humidity"] = str(random.randint(0, 100))
    humidity = robot_telemetry["humidity"].encode(encoding="UTF-8").hex()
    robot_telemetry["temperature"] = str(random.randint(-10, 40))
    temperature = robot_telemetry["temperature"].encode(encoding="UTF-8").hex()
    robot_telemetry["pressure"] = str(random.randint(970, 1030))
    pressure = robot_telemetry["pressure"].encode(encoding="UTF-8").hex()
    robot_location["latitude"] = str(random.randint(0, 90))
    latitude = robot_location["latitude"].encode(encoding="UTF-8").hex()
    robot_location["longitude"] = str(random.randint(0, 90))
    longitude = robot_location["longitude"].encode(encoding="UTF-8").hex()

    # saving latest robot data
    RobotLog.objects.filter(robot_id=robot["serial_number"]).update_or_create(
        robot_id=robot["serial_number"],
        timestamp=robot_timestamp["timestamp"],
        telemetry_humidity=robot_telemetry["humidity"],
        telemetry_temperature=robot_telemetry["temperature"],
        telemetry_pressure=robot_telemetry["pressure"],
        location_latitude=robot_location["latitude"],
        location_longitude=robot_location["longitude"],
    )

    # update sensor data dict
    robot = robot_sensors()

    random_fault = random.randint(0, 100)
    if random_fault >= 40 and random_fault <= 60:
        fault_log = "fault detected"
    else:
        fault_log = ""

    data_dict = {
        "timestamp": timestamp,
        "humidity": humidity,
        "temperature": temperature,
        "pressure": pressure,
        "latitude": latitude,
        "longitude": longitude,
        "fault_log": fault_log,
    }

    robot["telemetry"] = int(robot["telemetry"])
    robot["location"] = int(robot["location"])
    number_of_sensors = robot["telemetry"] + robot["location"]
    index = 1
    while index <= number_of_sensors:
        x = index + number_of_sensors
        if index < 10:
            sensors_data[f"SNR0{index}"] = data_dict
        else:
            sensors_data[f"SNR{index}"] = data_dict
        index += 1
        sensors_data.update(data_dict)


def make_robot_info():
    robot = robot_info()
    return f'Robot {robot["serial_number"]} - {robot["production_date"]}. Type: {robot["type"]} - '


def add_robot():
    robot = robot_info()
    if Robot.objects.filter(pk=robot["serial_number"]).exists():
        pass
    else:
        Robot(
            serial_number=robot["serial_number"],
            production_date=robot["production_date"],
            type=robot["type"],
            company=robot["company"],
        ).save()


def create_sensors():
    robot = robot_sensors()
    robot["telemetry"] = int(robot["telemetry"])
    robot["location"] = int(robot["location"])
    number_of_sensors = robot["telemetry"] + robot["location"]
    index = 1
    while index <= number_of_sensors:
        x = index + number_of_sensors
        if index < 10:
            if robot["telemetry"] >= 1:
                temp_topic = {f"SNR0{index}": f"sensors/SNR0{index}/telemetry"}
                fault_log = {f"SNR{x}": f"sensors/SNR0{index}/fault_log"}
                robot["telemetry"] -= 1
            elif robot["location"] >= 1:
                temp_topic = {f"SNR0{index}": f"sensors/SNR0{index}/location"}
                fault_log = {f"SNR{x}": f"sensors/SNR0{index}/fault_log"}
                robot["location"] -= 1
        else:
            if robot["telemetry"] >= 1:
                temp_topic = {f"SNR{index}": f"sensors/SNR{index}/telemetry"}
                fault_log = {f"SNR{x}": f"sensors/SNR{index}/fault_log"}
                robot["telemetry"] -= 1
            elif robot["location"] >= 1:
                temp_topic = {f"SNR{index}": f"sensors/SNR{index}/location"}
                fault_log = {f"SNR{x}": f"sensors/SNR{index}/fault_log"}
                robot["location"] -= 1
        mqtt_topics.update(temp_topic)
        mqtt_topics.update(fault_log)
        index += 1
