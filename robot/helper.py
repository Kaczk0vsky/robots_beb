import os
import django
import datetime
import random
from django.conf import settings
from django.utils import timezone
from django.contrib.staticfiles import finders
from paho.mqtt import client as mqtt

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task1_beb.settings")
django.setup()

from robot.settings_reader import robot_info
from app1.models import Robot, Sensor, SensorLog, Company
from task1_beb.celery import save_robot_data


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

mqtt_topics = {}


def time_in_seconds(time_messured):
    return datetime.timedelta.total_seconds(time_messured)


def update_data():
    # getting info from settings.toml as a dict
    robot = robot_info()

    sensors_id = Sensor.objects.filter(robot_id=robot["serial_number"]).values("id")

    # creating logs depending on what sensors have each robot
    for x in sensors_id:
        # checking for fault of sensors in robot
        temp = x
        random_fault = random.randint(0, 100)
        if random_fault >= 20 and random_fault <= 70:
            fault_log = True
        else:
            fault_log = False
        Sensor.objects.filter(id=temp["id"]).update(fault_detected=fault_log)

        # getting data read from sensors
        robot_timestamp["timestamp"] = str(timezone.now())
        if Sensor.objects.filter(id=temp["id"], type="telemetry"):
            robot_telemetry["humidity"] = str(random.randint(0, 100))
            robot_telemetry["temperature"] = str(random.randint(-10, 40))
            robot_telemetry["pressure"] = str(random.randint(970, 1030))
            save_robot_data.delay(
                robot_timestamp["timestamp"],
                robot_telemetry["humidity"],
                robot_telemetry["temperature"],
                robot_telemetry["pressure"],
                "telemetry",
                temp["id"],
            )
        elif Sensor.objects.filter(id=temp["id"], type="location"):
            robot_location["latitude"] = str(random.randint(0, 90))
            robot_location["longitude"] = str(random.randint(0, 90))
            save_robot_data.delay(
                robot_timestamp["timestamp"],
                robot_location["latitude"],
                robot_location["longitude"],
                0,
                "location",
                temp["id"],
            )

    # creating mqtt topics
    create_mqtt_topics()

    # creating mqtt data
    sensors_data = create_mqtt_data()

    # returning data dict for mqtt
    return sensors_data


def make_robot_info():
    robot = robot_info()
    return f'Robot {robot["serial_number"]} - {robot["production_date"]}. Type: {robot["type"]} - '


def add_robot():
    # creating robot class
    robot = robot_info()
    if robot["company"] != "":
        if Company.objects.filter(id=robot["company"]).exists():
            pass
        else:
            Company(company_name=robot["company"]).save()
    if Robot.objects.filter(pk=robot["serial_number"]).exists():
        pass
    else:
        if robot["company"] != "":
            Robot(
                serial_number=robot["serial_number"],
                production_date=robot["production_date"],
                type=robot["type"],
                company=Company.objects.get(id=robot["company"]),
            ).save()
        else:
            Robot(
                serial_number=robot["serial_number"],
                production_date=robot["production_date"],
                type=robot["type"],
            ).save()

    # adding one telemetry sensor and one location sensor
    if Sensor.objects.filter(
        type="telemetry", robot_id=Robot.objects.get(pk=robot["serial_number"])
    ).exists():
        pass
    else:
        Sensor(
            type="telemetry",
            robot_id=Robot.objects.get(pk=robot["serial_number"]),
            fault_detected=False,
        ).save()
    if Sensor.objects.filter(
        type="location", robot_id=Robot.objects.get(pk=robot["serial_number"])
    ).exists():
        pass
    else:
        Sensor(
            type="location",
            robot_id=Robot.objects.get(pk=robot["serial_number"]),
            fault_detected=False,
        ).save()


def create_mqtt_topics():
    # creating mqtt topics
    robot = robot_info()

    sensors_id = Sensor.objects.filter(robot_id=robot["serial_number"]).values("id")
    sensors_amount = Sensor.objects.filter(robot_id=robot["serial_number"]).count()
    index = 1
    for x in sensors_id:
        temp = x
        if Sensor.objects.filter(id=temp["id"], type="telemetry"):
            number = index + sensors_amount
            temp_topic = {index: f"sensors/SNR0{index}/telemetry"}
            fault_log = {number: f"sensors/SNR0{index}/fault_log"}
        elif Sensor.objects.filter(id=temp["id"], type="location"):
            number = index + sensors_amount
            temp_topic = {index: f"sensors/SNR0{index}/location"}
            fault_log = {number: f"sensors/SNR0{index}/fault_log"}
        mqtt_topics.update(temp_topic)
        mqtt_topics.update(fault_log)
        index += 1


def create_mqtt_data():
    # getting mqtt data to be send to topics
    robot = robot_info()
    sensors_data = {}
    sensors_id = Sensor.objects.filter(robot_id=robot["serial_number"]).values("id")
    index = 1

    for x in sensors_id:
        temp = x
        if Sensor.objects.filter(id=temp["id"], type="telemetry"):
            temp_dict = {
                f"SNR{index}": SensorLog.objects.filter(
                    sensor_id=Sensor.objects.get(id=temp["id"], type="telemetry")
                )
                .values(
                    "timestamp",
                    "telemetry_humidity",
                    "telemetry_temperature",
                    "telemetry_pressure",
                )
                .last()
            }
        elif Sensor.objects.filter(id=temp["id"], type="location"):
            temp_dict = {
                f"SNR{index}": SensorLog.objects.filter(
                    sensor_id=Sensor.objects.get(id=temp["id"], type="location")
                )
                .values(
                    "timestamp",
                    "location_latitude",
                    "location_longitude",
                )
                .last()
            }
        sensors_data.update(temp_dict)
        index += 1

    return sensors_data


def get_fault_log():
    # getting fault log status of each sensor for robot specified in settings.toml
    robot = robot_info()

    fault_log = Sensor.objects.filter(
        robot_id=Robot.objects.get(pk=robot["serial_number"]),
    ).values("fault_detected")
    fault_list = list()

    for x in fault_log:
        if x["fault_detected"] == False:
            fault_list.append("fault_recovered")
        elif x["fault_detected"] == True:
            fault_list.append("fault_detected")

    return fault_list
