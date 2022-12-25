from paho.mqtt import client as mqtt
from task1_beb.settings_reader import mqtt_settings
from task1_beb.mqtt_communication import on_connect, on_disconnect, on_message, on_publish, on_subscribe
import logging

def initialization():
    # Initializing MQTT communication
    client = mqtt.Client()
    mqqt_config = mqtt_settings()

    if "username" in mqqt_config:
        client.username_pw_set(mqqt_config["username"], password = mqqt_config["password"])
    client.connect(mqqt_config["host"], int(mqqt_config["port"]))

    # Initializing Logger console info
    logger = logging.getLogger(__name__)

    # client.on_connect = on_connect
    # client.on_disconnect = on_disconnect
    # client.on_message = on_message
    # client.on_publish = on_publish
    # client.on_subscribe = on_subscribe

if __name__ == "__main__":
    initialization()