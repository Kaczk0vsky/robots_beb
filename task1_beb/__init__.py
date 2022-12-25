from datetime import datetime
from dataclasses import dataclass
from task1_beb.main import initialization


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

if __name__ == "__main__":
    initialization()
    while True:
        print("1")
