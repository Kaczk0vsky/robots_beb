from datetime import datetime
from dataclasses import dataclass
from paho.mqtt import client as mqtt
from task1_beb.settings_reader import mqtt_settings
from task1_beb.mqtt_communication import on_connect, on_disconnect, on_message
import logging


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


# Initializing Logger console info
logger = logging.getLogger(__name__)

# Initializing MQTT communication
client = mqtt.Client()
mqqt_config = mqtt_settings()

if "username" in mqqt_config:
    client.username_pw_set(mqqt_config["username"], password = mqqt_config["password"])
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.connect(mqqt_config["host"], int(mqqt_config["port"]))

# TODO: Add threading
# client.loop_forever()