from paho.mqtt import client as mqtt
from task1_beb.settings_reader import mqtt_settings
from task1_beb.mqtt_communication import on_connect, on_disconnect, on_message
from datetime import datetime
from dataclasses import dataclass
from task1_beb.mqtt_communication import MQTTTimeMessure
import logging
import django
import threading


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
    

def initialization():
    # Setting up Django
    django.setup()

    # Initializing Logger console info
    logger = logging.getLogger(__name__)

    # Initializing MQTT communication
    client = mqtt.Client()
    mqqt_config = mqtt_settings()

    if "username" in mqqt_config:
        client.username_pw_set(mqqt_config["username"], password = mqqt_config["password"])
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(mqqt_config["host"], int(mqqt_config["port"]))

    # Starting threading
    threads = []
    threads.append(threading.Thread(target=client.loop_forever, daemon=True))
    mqtt_time = MQTTTimeMessure()
    threads.append(threading.Thread(target=mqtt_time.loop_forever))

    for thread in threads:
        thread.start()


# if __name__ == "__main__":
#     initialization()