import os
import django
from celery import Celery, shared_task
from paho.mqtt import client as mqtt

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task1_beb.settings")
django.setup()

from app1.models import SensorLog

app = Celery("task1_beb")
client = mqtt.Client()

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# @shared_task
# def mqtt_send(robot_serial, robot_topic, robot_data):
#     client.publish(
#         f"robot serial-{robot_serial}/{robot_topic}",
#         robot_data,
#     )


@shared_task
def save_robot_data(timestamp, data1, data2, data3, type, sensor_id):
    if type == "telemetry":
        SensorLog(
            sensor_id=sensor_id,
            timestamp=timestamp,
            telemetry_humidity=data1,
            telemetry_temperature=data2,
            telemetry_pressure=data3,
        ).save()
    elif type == "location":
        SensorLog(
            sensor_id=sensor_id,
            timestamp=timestamp,
            location_latitude=data1,
            locatioon_longitude=data2,
        ).save()
