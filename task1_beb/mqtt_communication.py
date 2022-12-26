from paho.mqtt import client as mqtt
from task1_beb.settings_reader import mqtt_settings
from datetime import datetime
from task1_beb.helpers import time_in_seconds, robot_location, robot_telemetry
import logging

logger = logging.getLogger(__name__)
mqqt_config = mqtt_settings()
client = mqtt.Client()


class TimeMessure:
    def __init__(self):
        self.start_time = datetime.now()
        self.interval_time = int(mqqt_config["interval_time"])

    def loop_forever(self):
        while True:
            if self.interval_time <= time_in_seconds(datetime.now() - self.start_time):
                send_data()
                self.start_time = datetime.now()


def mqtt_init():
    if "username" in mqqt_config:
        client.username_pw_set(mqqt_config["username"], password = mqqt_config["password"])
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(mqqt_config["host"], int(mqqt_config["port"]))
    client.subscribe(mqqt_config["topic"], 1)

def on_connect(client, userdata, flags, rc):
    error_count = 0
    while error_count <= 5:
        if rc == 0:
            logger.info("Connected to MQTT Server.")
            break
        else:
            logger.error("Cannot connect to MQTT Server - return code %d\n", rc)
            error_count = error_count + 1
        if error_count == 5:
            return logger.info("Couldn`t connect to MQTT Server after several tries")

    client.on_connect = on_connect
    return client

def on_disconnect(client, userdata, flags, rc):
    logger.info("Disconnected from MQTT Server. Trying to reconnect...")
    while rc != 0:
        client.connect(mqqt_config["host"], int(mqqt_config["port"]))


def on_message(client, userdata, message, tmp=None):
    logger.info("Received message " + str(message.payload)
                + " on topic '" + message.topic
                + "' with QoS " + str(message.qos))

def send_data():
    client.publish(mqqt_config["topic"], robot_telemetry["humidity"])

def mqtt_loop_forever():
    client.loop_forever()
