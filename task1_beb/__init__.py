from datetime import datetime
from dataclasses import dataclass
from paho.mqtt import client as mqtt_client
import logging


logger = logging.getLogger(__name__)

@dataclass
class Robot_Telemetry:
    timestamp = datetime.now()
    humidity: int
    temperature: int
    pressure: int

@dataclass
class Robot_Location:
    timestamp = datetime.now()
    latitude: float
    longitude: float

#Initializing MQTT communication
