from django import forms
from .models import Robot


class NewRobot(forms.ModelForm):
    class Meta:
        model = Robot
        fields = [
            "serial_number",
            "production_date",
            "type",
            "company",
        ]
        labels = {
            "serial_number": "Serial number",
            "production_date": "Production date",
            "type": "Type",
            "company": "Company",
        }
