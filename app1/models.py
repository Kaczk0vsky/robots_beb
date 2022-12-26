import datetime

from django.db import models
from django.utils import timezone


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
    serial_number = models.CharField(max_length = 50)
    production_date = models.DateField()
    type = models.CharField(
        max_length = 10,
        choices = ROBOT_TYPES_CHOICES,
        default = '4 wheeler'
    )
    company = models.CharField(max_length = 20)

    def __str__(self):
        return self.serial_number
