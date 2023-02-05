from django.db import models
from django.utils import timezone

# robot class
class Robot(models.Model):
    # creating choices for field
    FOUR_WHEELER = "4 wheeler"
    AMPHIBIAN = "amphibian"
    TRACKED = "tracked"
    FLYING = "flying"
    ROBOT_TYPES_CHOICES = [
        (FOUR_WHEELER, ("4 wheeler")),
        (AMPHIBIAN, ("amphibian")),
        (TRACKED, ("tracked")),
        (FLYING, ("flying")),
    ]
    # unique robot serial number
    serial_number = models.CharField(max_length=256, unique=True, primary_key=True)
    # production date of a robot
    production_date = models.DateField()
    # robot type created from ROBOT_TYPE_CHOICES
    type = models.CharField(
        max_length=10,
        choices=ROBOT_TYPES_CHOICES,
        default="4 wheeler",
    )
    # robot company which own it
    company = models.CharField(max_length=256)

    def __str__(self):
        return self.serial_number


# sensor class - one robot can have many sensors
class Sensor(models.Model):
    # unique id for each sensor
    id = models.IntegerField(primary_key=True, unique=True, editable=False)
    # creating choices for field
    TELEMETRY = "telemetry"
    LOCATION = "location"
    SENSOR_TYPES_CHOICES = [
        (TELEMETRY, ("telemetry")),
        (LOCATION, ("location")),
    ]
    # sensor types created from SENSOR_TYPE_CHOICES
    type = models.CharField(
        max_length=10,
        choices=SENSOR_TYPES_CHOICES,
        default="telemetry",
    )
    # robot to which sensor is attached
    robot_id = models.ForeignKey(Robot, on_delete=models.CASCADE, editable=False)

    def __str__(self):
        return f"Sensor - [{self.type}] in robot {self.robot_id}"


# log from sensors - one sensor can hava many logs
class SensorLog(models.Model):
    # unique id
    id = models.IntegerField(editable=False, primary_key=True, unique=True)
    # sensor id
    sensor_id = models.ForeignKey(Sensor, on_delete=models.CASCADE, editable=False)
    # robot telemetry timestamp param
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    # robot humidity param
    telemetry_humidity = models.IntegerField(default=0, editable=False, blank=True)
    # robot temperature param
    telemetry_temperature = models.IntegerField(default=0, editable=False, blank=True)
    # robot pressure param
    telemetry_pressure = models.IntegerField(default=0, editable=False, blank=True)
    # robot location latitude param
    location_latitude = models.IntegerField(default=0, editable=False, blank=True)
    # robot location logitude param
    location_longitude = models.IntegerField(default=0, editable=False, blank=True)

    def __str__(self):
        return f"Log [{self.id}] on {self.timestamp}"
