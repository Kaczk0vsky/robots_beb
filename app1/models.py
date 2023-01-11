from django.db import models
from django.utils import timezone


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

    #hidden params - non-visible and non-editable
    #robot telemetry timestamp param
    timestamp = models.DateTimeField(default=timezone.now)
    #robot humidity param
    telemetry_humidity = models.CharField(max_length=256)
    #robot temperature param
    telemetry_temperature = models.CharField(max_length=256)
    #robot pressure param
    telemetry_pressure = models.CharField(max_length=256)
    #robot location latitude param
    location_latitude = models.CharField(max_length=256)
    #robot location logitude param
    location_longitude = models.CharField(max_length=256)

    def __str__(self):
        return self.serial_number
