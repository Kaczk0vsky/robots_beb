import os
import django
from celery import Celery, shared_task
from paho.mqtt import client as mqtt

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task1_beb.settings")
django.setup()

from app1.models import RobotLog
from robot.settings_reader import robot_info

app = Celery("task1_beb")
client = mqtt.Client()

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@shared_task
def mqtt_send(robot_serial, robot_topic, robot_data):
    client.publish(
        f"Robot serial: {robot_serial}/{robot_topic}",
        robot_data,
    )


@shared_task
def save_robot_data(timestamp, humidity, temperature, pressure, latitude, longitude):
    robot = robot_info()

    RobotLog.objects.filter(robot_id=robot["serial_number"]).update_or_create(
        robot_id=robot["serial_number"],
        timestamp=timestamp,
        telemetry_humidity=humidity,
        telemetry_temperature=temperature,
        telemetry_pressure=pressure,
        location_latitude=latitude,
        location_longitude=longitude,
    )
