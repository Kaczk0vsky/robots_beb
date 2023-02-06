import os
import django
import datetime
import random
from django.conf import settings
from django.utils import timezone
from paho.mqtt import client as mqtt

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task1_beb.settings")
django.setup()

from robot.settings_reader import robot_info
from app1.models import Robot, Sensor, SensorLog
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

sensors_data = {}
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
        if random_fault >= 40 and random_fault <= 60:
            fault_log = True
        else:
            fault_log = False
        Sensor.objects.filter(robot_id=temp["id"]).update(fault_detected=fault_log)
        # getting data read from sensors
        robot_timestamp["timestamp"] = str(timezone.now())
        if Sensor.objects.filter(id=temp["id"], type="telemetry"):
            robot_telemetry["humidity"] = str(random.randint(0, 100))
            robot_telemetry["temperature"] = str(random.randint(-10, 40))
            robot_telemetry["pressure"] = str(random.randint(970, 1030))
            SensorLog(
                sensor_id=Sensor.objects.get(id=temp["id"]),
                timestamp=robot_timestamp["timestamp"],
                telemetry_humidity=robot_telemetry["humidity"],
                telemetry_temperature=robot_telemetry["temperature"],
                telemetry_pressure=robot_telemetry["pressure"],
            ).save()
        elif Sensor.objects.filter(id=temp["id"], type="location"):
            robot_location["latitude"] = str(random.randint(0, 90))
            robot_location["longitude"] = str(random.randint(0, 90))
            SensorLog(
                sensor_id=Sensor.objects.get(id=temp["id"]),
                timestamp=robot_timestamp["timestamp"],
                location_longitude=robot_location["longitude"],
                location_latitude=robot_location["latitude"],
            ).save()

    # creating mqtt topics
    create_mqtt_topics()

    # creating mqtt data
    sensors_data = create_mqtt_data()

    # # update sensor data dict
    # save_robot_data.delay(
    #     robot_timestamp["timestamp"],
    #     robot_telemetry["humidity"],
    #     robot_telemetry["temperature"],
    #     robot_telemetry["pressure"],
    #     robot_location["latitude"],
    #     robot_location["longitude"],
    # )

    # robot["telemetry"] = int(robot["telemetry"])
    # robot["location"] = int(robot["location"])
    # number_of_sensors = robot["telemetry"] + robot["location"]
    # index = 1
    # while index <= number_of_sensors:
    #     x = index + number_of_sensors
    #     if index < 10:
    #         sensors_data[f"SNR0{index}"] = data_dict
    #     else:
    #         sensors_data[f"SNR{index}"] = data_dict
    #     index += 1
    #     sensors_data.update(data_dict)


def make_robot_info():
    robot = robot_info()
    return f'Robot {robot["serial_number"]} - {robot["production_date"]}. Type: {robot["type"]} - '


def add_robot():
    # creating robot class
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

    # adding one telemetry sensor and one location sensor
    if Sensor.objects.filter(type="telemetry").exists():
        pass
    else:
        Sensor(
            type="telemetry",
            robot_id=Robot.objects.get(pk=robot["serial_number"]),
            fault_detected=False,
        ).save()
    if Sensor.objects.filter(type="location").exists():
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


# TODO: Hexadecimal format
#
# timestamp = robot_timestamp["timestamp"].encode(encoding="UTF-8").hex()
# humidity = robot_telemetry["humidity"].encode(encoding="UTF-8").hex()
# temperature = robot_telemetry["temperature"].encode(encoding="UTF-8").hex()
# pressure = robot_telemetry["pressure"].encode(encoding="UTF-8").hex()
# latitude = robot_location["latitude"].encode(encoding="UTF-8").hex()
# longitude = robot_location["longitude"].encode(encoding="UTF-8").hex()
#
def create_mqtt_data():
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
