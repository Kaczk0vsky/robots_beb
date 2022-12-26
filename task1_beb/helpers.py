import datetime
import random

robot_telemetry = {
    'timestamp': datetime.datetime.now(),
    'humidity': 0,
    'temperature': 0,
    'pressure': 0,
}

robot_location = {
    'timestamp': datetime.datetime.now(),
    'latitude': 0.0,
    'longitude': 0.0,
}


def time_in_seconds(time_messured):
    return datetime.timedelta.total_seconds(time_messured)

def update_data():
    #Randomizing data send:
    robot_telemetry["timestamp"] = datetime.datetime.now()
    robot_telemetry["humidity"] = random.randint(0, 100)
    robot_telemetry["temperature"] = random.randint(-10, 40)
    robot_telemetry["pressure"] = random.randint(970, 1030)
    robot_location["timestamp"] = datetime.datetime.now()
    robot_location["latitude"] = random.randint(0, 90)
    robot_location["longitude"] = random.randint(0, 90)
