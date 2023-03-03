from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group

# company class
class Company(models.Model):
    # unique id for each company
    id = models.IntegerField(primary_key=True, unique=True, editable=False)
    # company name
    company_name = models.CharField(max_length=256, unique=True)
    # NIP
    nip = models.IntegerField(blank=True, null=True, unique=True)
    # one to one relation from company to group model
    group = models.OneToOneField(
        Group, on_delete=models.CASCADE, blank=True, null=True, unique=True
    )

    def __str__(self):
        return self.company_name


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
    serial_number = models.CharField(
        max_length=256,
        unique=True,
        primary_key=True,
    )
    # production date of a robot
    production_date = models.DateField()
    # robot type created from ROBOT_TYPE_CHOICES
    type = models.CharField(
        max_length=10,
        choices=ROBOT_TYPES_CHOICES,
        default="4 wheeler",
    )
    # robot company which own it
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.serial_number


# sensor class
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
        editable=False,
    )
    # field for getting fault information
    fault_detected = models.BooleanField(editable=False, default=False)
    # robot to which sensor is attached, might be blank for creating an empty sensor device or detaching it from robot
    robot_id = models.ForeignKey(
        Robot,
        on_delete=models.CASCADE,
        editable=True,
        null=True,
        blank=True,
        db_column="robot_id",
    )

    def __str__(self):
        return str(self.id)


# logs from sensors
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
        return str(self.id)


# history of robot modifications
class RobotModificationHistory(models.Model):
    # unique id
    id = models.IntegerField(editable=False, primary_key=True, unique=True)
    # robot to which sensor is attached
    robot_id = models.ForeignKey(Robot, on_delete=models.CASCADE, editable=False)
    # field for storing modification message
    text = models.TextField()
    # timestamp for entering data
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
