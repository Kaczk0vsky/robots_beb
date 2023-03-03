import sys
import logging

sys.path.append("..")

from robot.mqtt_communication import MqttComunication, TimeMessure
from robot.helper import add_robot


def initialization():
    # Add new robot
    add_robot()

    # Initializing Logger console info
    logger = logging.getLogger(__name__)

    # Initializing sending messages every time interval passed
    mqtt_time = TimeMessure()
    mqtt_time.loop_forever()


if __name__ == "__main__":
    initialization()
