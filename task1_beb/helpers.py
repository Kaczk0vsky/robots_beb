import datetime


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
