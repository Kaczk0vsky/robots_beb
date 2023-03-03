from celery import Celery, shared_task
from paho.mqtt import client as mqtt
import os
import django

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task1_beb.settings")
django.setup()

from app1.models import SensorLog, Sensor

app = Celery("task1_beb")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@shared_task
def mqtt_send(robot_serial, robot_topic, robot_data):
    client = mqtt.Client(transport="websockets")
    mqtt_username = os.getenv("MQTT_CLIENT_USERNAME")
    if not mqtt_username:
        pass
    else:
        client.username_pw_set(
            username=str(os.getenv("MQTT_CLIENT_USERNAME")),
            password=str(os.getenv("MQTT_CLIENT_PASSWORD")),
        )
    client.connect(os.getenv("MQTT_CLIENT_HOST"), int(os.getenv("MQTT_CLIENT_PORT")))
    client.publish(
        f"Robot serial: {robot_serial}/{robot_topic}",
        robot_data,
    )
    client.loop_stop()


@shared_task
def save_robot_data(timestamp, data1, data2, data3, type, sensor_id):
    if type == "telemetry":
        SensorLog(
            sensor_id=Sensor.objects.get(id=sensor_id),
            timestamp=timestamp,
            telemetry_humidity=data1,
            telemetry_temperature=data2,
            telemetry_pressure=data3,
        ).save()
    elif type == "location":
        SensorLog(
            sensor_id=Sensor.objects.get(id=sensor_id),
            timestamp=timestamp,
            location_latitude=data1,
            location_longitude=data2,
        ).save()
