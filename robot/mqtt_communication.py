import logging
import json
import os
from paho.mqtt import client as mqtt
from datetime import datetime

from robot.settings_reader import mqtt_settings, robot_info

# from task1_beb.celery import mqtt_send
from robot.helper import (
    time_in_seconds,
    update_data,
    make_robot_info,
    get_fault_log,
    mqtt_topics,
)

logger = logging.getLogger(__name__)
mqqt_config = mqtt_settings()
robot_data = robot_info()
client = mqtt.Client(transport="websockets")
name = make_robot_info()


class MqttComunication:
    def __init__(self):
        mqtt_username = os.getenv("MQTT_CLIENT_USERNAME")
        if not mqtt_username:
            pass
        else:
            client.username_pw_set(
                username=str(os.getenv("MQTT_CLIENT_USERNAME")),
                password=str(os.getenv("MQTT_CLIENT_PASSWORD")),
            )
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.connect(
            os.getenv("MQTT_CLIENT_HOST"), int(os.getenv("MQTT_CLIENT_PORT"))
        )
        client.subscribe(f"robot serial-{robot_data['serial_number']}", 1)

    def on_connect(self, client, userdata, flags, rc):
        error_count = 0

        while error_count <= 5:
            if rc == 0:
                logger.info(make_robot_info() + "Connected to MQTT Server.")
                break
            else:
                logger.error(
                    make_robot_info()
                    + "Cannot connect to MQTT Server - return code %d\n",
                    rc,
                )
                error_count = error_count + 1
            if error_count == 5:
                return logger.info(
                    make_robot_info()
                    + "Couldn`t connect to MQTT Server after several tries"
                )

            client.on_connect = self.on_connect
            return client

    def on_disconnect(self, client, userdata, flags, rc):
        logger.info(
            make_robot_info() + "Disconnected from MQTT Server. Trying to reconnect..."
        )
        while rc != 0:
            client.connect(mqqt_config["host"], int(mqqt_config["port"]))

    def send_data(self, sensors_data):
        logger.info(
            make_robot_info()
            + f"Sent robot parameters on topic - robot serial-{robot_data['serial_number']}."
        )
        index = 1
        i = 1
        while i <= len(mqtt_topics):
            if "telemetry" in mqtt_topics[i] and i <= (len(mqtt_topics) / 2):
                temp_dict = sensors_data[f"SNR{i}"]
                timestamp = str(temp_dict["timestamp"]).encode(encoding="UTF-8").hex()
                humidity = (
                    str(temp_dict["telemetry_humidity"]).encode(encoding="UTF-8").hex()
                )
                temperature = (
                    str(temp_dict["telemetry_temperature"])
                    .encode(encoding="UTF-8")
                    .hex()
                )
                pressure = (
                    str(temp_dict["telemetry_pressure"]).encode(encoding="UTF-8").hex()
                )
                temp = {
                    "timestamp": timestamp,
                    "humidity": humidity,
                    "temperature": temperature,
                    "pressure": pressure,
                }
                # mqtt_send.delay(
                #     robot_data["serial_number"], mqtt_topics[x], json.dumps(temp)
                # )
                client.publish(
                    f'Robot serial: {robot_data["serial_number"]}/{mqtt_topics[i]}',
                    json.dumps(temp),
                )
            elif "location" in mqtt_topics[i] and i <= (len(mqtt_topics) / 2):
                temp_dict = sensors_data[f"SNR{i}"]
                timestamp = str(temp_dict["timestamp"]).encode(encoding="UTF-8").hex()
                latitude = (
                    str(temp_dict["location_latitude"]).encode(encoding="UTF-8").hex()
                )
                longitude = (
                    str(temp_dict["location_longitude"]).encode(encoding="UTF-8").hex()
                )
                temp = {
                    "timestamp": timestamp,
                    "latitude": latitude,
                    "longitude": longitude,
                }
                # mqtt_send.delay(
                #     robot_data["serial_number"], mqtt_topics[x], json.dumps(temp)
                # )
                client.publish(
                    f'Robot serial: {robot_data["serial_number"]}/{mqtt_topics[i]}',
                    json.dumps(temp),
                )
            else:
                # getting fault info
                fault_log = get_fault_log(index)
                # mqtt_send.delay(
                #     robot_data["serial_number"], mqtt_topics[x], json.dumps(temp)
                # )
                client.publish(
                    f'Robot serial: {robot_data["serial_number"]}/{mqtt_topics[i]}',
                    json.dumps(fault_log),
                )
                index += 1
            i += 1

    def mqtt_loop_forever(self):
        client.loop_forever()


# class for time messuring
class TimeMessure:
    def __init__(self):
        self.start_time = datetime.now()
        self.interval_time = int(mqqt_config["interval_time"])
        self.mqtt = MqttComunication()

    def loop_forever(self):
        while True:
            if self.interval_time <= time_in_seconds(datetime.now() - self.start_time):
                sensors_data = update_data()
                self.mqtt.send_data(sensors_data)
                self.start_time = datetime.now()
