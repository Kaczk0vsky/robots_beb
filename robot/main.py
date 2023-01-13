import sys
import logging
import threading
sys.path.append("..")

from robot.mqtt_communication import TimeMessure, mqtt_init, mqtt_loop_forever
from robot.helper import add_robot


def initialization():
    #Add new robot
    add_robot()

    # Initializing Logger console info
    logger = logging.getLogger(__name__)
    
    # Initializing MQTT communication
    mqtt_init()
    
    # Starting threading
    threads = []
    threads.append(threading.Thread(target=mqtt_loop_forever, daemon=True))
    mqtt_time = TimeMessure()
    threads.append(threading.Thread(target=mqtt_time.loop_forever))

    for thread in threads:
        thread.start()

if __name__ == '__main__':
    initialization()
    