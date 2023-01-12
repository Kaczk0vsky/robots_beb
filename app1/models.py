from django.db import models
from django.utils import timezone


class RobotLog(models.Model):
    #robot id
    robot_id = models.CharField(max_length=256 ,editable=False)
    #robot telemetry timestamp param
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    #robot humidity param
    telemetry_humidity = models.IntegerField(default=0, editable=False)
    #robot temperature param
    telemetry_temperature = models.IntegerField(default=0, editable=False)
    #robot pressure param
    telemetry_pressure = models.IntegerField(default=0, editable=False)
    #robot location latitude param
    location_latitude = models.IntegerField(default=0, editable=False)
    #robot location logitude param
    location_longitude = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return f"Robot: {self.robot_id} - {self.timestamp}"


class Robot(models.Model):
    #creating choices for field 
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
    #unique robot serial number
    serial_number = models.CharField(max_length=256, unique=True)
    #production date of a robot
    production_date = models.DateField()
    #robot type created from ROBOT_TYPE_CHOICES
    type = models.CharField(
        max_length = 10,
        choices = ROBOT_TYPES_CHOICES,
        default = '4 wheeler'
    )
    #robot company which own it
    company = models.CharField(max_length=256)

    def __str__(self):
        return self.serial_number
        