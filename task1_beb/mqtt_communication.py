from paho.mqtt import client as mqtt
from task1_beb.settings_reader import mqtt_settings
import logging

logger = logging.getLogger(__name__)
mqqt_config = mqtt_settings()

def on_connect(client, userdata, flags, rc):
    error_count = 0
    while error_count <= 5:
        if rc == 0:
            logger.info("Connected to MQTT Server.")
            break
        else:
            logger.error("Failed to connect, return code %d\n", rc)
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
    logger.info(" Received message " + str(message.payload)
                + " on topic '" + message.topic
                + "' with QoS " + str(message.qos))

def send_data():
    pass