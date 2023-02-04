from django.db import models
from django.utils import timezone


# class for robot instance
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


# class for robot instance
class Log(models.Model):
    # robot id
    id = models.IntegerField(editable=False, primary_key=True, unique=True)
    # robot telemetry timestamp param
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    # robot humidity param
    telemetry_humidity = models.IntegerField(default=0, editable=False)
    # robot temperature param
    telemetry_temperature = models.IntegerField(default=0, editable=False)
    # robot pressure param
    telemetry_pressure = models.IntegerField(default=0, editable=False)
    # robot location latitude param
    location_latitude = models.IntegerField(default=0, editable=False)
    # robot location logitude param
    location_longitude = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return f"Log [{self.id}] on {self.timestamp}"


# relation one to many between robot class and log class
class RobotLog(models.Model):
    # unique id for each log
    id = models.IntegerField(primary_key=True, unique=True, editable=False)
    # getting robot class
    robot_id = models.ForeignKey(Robot, on_delete=models.CASCADE, editable=False)
    # getting log class
    log_id = models.ForeignKey(Log, on_delete=models.CASCADE, editable=False)

    def __str__(self):
        return f"Robot [{self.robot_id}] : [{self.log_id}]"
