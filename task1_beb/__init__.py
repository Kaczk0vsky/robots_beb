from datetime import datetime
from dataclasses import dataclass
from paho.mqtt import client as mqtt
import logging

# Initializing Logger console info
logger = logging.getLogger(__name__)


@dataclass
class RobotTelemetry:
    timestamp = datetime.now()
    humidity: int
    temperature: int
    pressure: int


@dataclass
class RobotLocation:
    timestamp = datetime.now()
    latitude: float
    longitude: float


def mqtt_startup():
    # Initializing MQTT communication
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe


def on_connect():
    pass


def on_disconnect():
    pass


def on_message(client, userdata, message, tmp=None):
    logger.info(" Received message " + str(message.payload)
                + " on topic '" + message.topic
                + "' with QoS " + str(message.qos))


def on_publish():
    pass


def on_subscribe():
    pass
