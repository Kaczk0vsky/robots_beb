from django.db import models
from django.utils import timezone


class RobotData(models.Model):
    robot_data = models.CharField(max_length=10)

class RobotHumidity(models.Model):
    robot_data = models.CharField(max_length=10)

class RobotTemperature(models.Model):
    robot_data = models.CharField(max_length=10)

class RobotPressure(models.Model):
    robot_data = models.CharField(max_length=10)

class Robot(models.Model):
    FOUR_WHEELER = '4 wheeler'
    AMPHIBIAN = 'amphibian'
    TRACKED = 'tracked'
    FLYING = 'flying'
    ROBOT_TYPES_CHOICES = [
        (FOUR_WHEELER, ('4 wheeler')),
        (AMPHIBIAN, ('amphibian')),
        (TRACKED, ('tracked')),
        (FLYING, ('flying')),
    ]
    serial_number = models.CharField(max_length = 50, unique=True)
    production_date = models.DateField()
    type = models.CharField(
        max_length = 10,
        choices = ROBOT_TYPES_CHOICES,
        default = '4 wheeler'
    )
    company = models.CharField(max_length = 20)

    #Hidden params
    telemetry_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    telemetry_humidity = models.CharField(max_length=5, default=0, editable=False)
    telemetry_temperature = models.CharField(max_length=5, default=0, editable=False)
    telemetry_pressure = models.CharField(max_length=5, default=0, editable=False)
    location_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    location_latitude = models.CharField(max_length=5, default=0, editable=False)
    location_longitude = models.CharField(max_length=5, default=0, editable=False)

    #Many to many fields for saving multiple records
    timestamp_all = models.ManyToManyField(RobotData)
    humidity_all = models.ManyToManyField(RobotHumidity)
    temperature_all = models.ManyToManyField(RobotTemperature)
    pressure_all = models.ManyToManyField(RobotPressure)

    def __str__(self):
        return self.serial_number

