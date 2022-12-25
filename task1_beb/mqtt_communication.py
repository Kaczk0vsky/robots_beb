from paho.mqtt import client as mqtt
from task1_beb.settings_reader import mqtt_settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
mqqt_config = mqtt_settings()


class MQTTTimeMessure:
    def __init__(self):
        self.start_time = datetime.now()
        self.interval_time = int(mqqt_config["interval_time"])

    def loop_forever(self):
        while True:
            time_delta = datetime.now() - self.start_time
            hours = time_delta.seconds // 3600
            minutes = time_delta.seconds // 60 - hours * 60
            seconds = time_delta.seconds - minutes * 60 - hours * 3600
            time_delta = f"{hours}:{minutes}:{seconds}"
            if self.interval_time <= time_delta:
                logger.info("5")
                self.start_time = datetime.now()


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
    logger.info("now")