from task1_beb.mqtt_communication import TimeMessure, mqtt_init, mqtt_loop_forever
from task1_beb.helpers import add_robot
import logging
import threading


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
