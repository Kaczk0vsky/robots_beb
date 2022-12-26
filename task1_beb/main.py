from task1_beb.mqtt_communication import on_connect, on_disconnect, TimeMessure, mqtt_init, mqtt_loop_forever
import logging
import django
import threading


def initialization():
    # Setting up Django
    django.setup()

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

# if __name__ == "__main__":
#     initialization()
