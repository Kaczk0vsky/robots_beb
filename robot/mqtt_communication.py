import logging
import json
import os
from paho.mqtt import client as mqtt
from datetime import datetime

from robot.settings_reader import mqtt_settings, robot_info
from robot.helper import (
    time_in_seconds,
    update_data,
    make_robot_info,
    mqtt_topics,
    sensors_data,
)

logger = logging.getLogger(__name__)
mqqt_config = mqtt_settings()
robot_data = robot_info()
client = mqtt.Client()
name = make_robot_info()


class TimeMessure:
    def __init__(self):
        self.start_time = datetime.now()
        self.interval_time = int(mqqt_config["interval_time"])

    def loop_forever(self):
        while True:
            if self.interval_time <= time_in_seconds(datetime.now() - self.start_time):
                update_data()
                send_data()
                self.start_time = datetime.now()


def mqtt_init():
    mqtt_username = os.getenv("MQTT_CLIENT_USERNAME")
    if not mqtt_username:
        pass
    else:
        client.username_pw_set(
            username=str(os.getenv("MQTT_CLIENT_USERNAME")),
            password=str(os.getenv("MQTT_CLIENT_PASSWORD")),
        )
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(os.getenv("MQTT_CLIENT_HOST"), int(os.getenv("MQTT_CLIENT_PORT")))
    client.subscribe(mqqt_config["topic"], 1)


def on_connect(client, userdata, flags, rc):
    error_count = 0
    while error_count <= 5:
        if rc == 0:
            logger.info(name + "Connected to MQTT Server.")
            break
        else:
            logger.error(name + "Cannot connect to MQTT Server - return code %d\n", rc)
            error_count = error_count + 1
        if error_count == 5:
            return logger.info(
                name + "Couldn`t connect to MQTT Server after several tries"
            )

    client.on_connect = on_connect
    return client


def on_disconnect(client, userdata, flags, rc):
    logger.info(name + "Disconnected from MQTT Server. Trying to reconnect...")
    while rc != 0:
        client.connect(mqqt_config["host"], int(mqqt_config["port"]))


def send_data():
    logger.info(name + f'Sent robot parameters on topic {mqqt_config["topic"]}.')
    for x in mqtt_topics:
        if "telemetry" in mqtt_topics[x]:
            temp = {
                "timestamp": sensors_data["timestamp"],
                "humidity": sensors_data["humidity"],
                "temperature": sensors_data["temperature"],
                "pressure": sensors_data["pressure"],
            }
            client.publish(
                f'Robot serial: {robot_data["serial_number"]}/{mqtt_topics[x]}',
                json.dumps(temp),
            )
        elif "location" in mqtt_topics[x]:
            temp = {
                "timestamp": sensors_data["timestamp"],
                "latitude": sensors_data["latitude"],
                "longitude": sensors_data["longitude"],
            }
            client.publish(
                f'Robot serial: {robot_data["serial_number"]}/{mqtt_topics[x]}',
                json.dumps(temp),
            )
        else:
            client.publish(
                f'Robot serial: {robot_data["serial_number"]}/{mqtt_topics[x]}',
                json.dumps(sensors_data["fault_log"]),
            )


def mqtt_loop_forever():
    client.loop_forever()
