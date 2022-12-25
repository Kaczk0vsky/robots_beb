from paho.mqtt import client as mqtt
from task1_beb.settings_reader import mqtt_settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT Server.")
    else:
        logger.error("Failed to connect, return code %d\n", rc)

    client.on_connect = on_connect
    
    return client

def on_disconnect():
    logger.info("Disconnected from MQTT Server.")


def on_message(client, userdata, message, tmp=None):
    logger.info(" Received message " + str(message.payload)
                + " on topic '" + message.topic
                + "' with QoS " + str(message.qos))


def on_publish():
    pass


def on_subscribe():
    pass

def send_data():
    pass