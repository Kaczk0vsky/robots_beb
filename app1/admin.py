from django.contrib import admin
from .models import Robot, Sensor, SensorLog


class RobotsAdmin(admin.ModelAdmin):
    list_display = ("serial_number", "type", "company", "production_date")
    search_fields = ("serial_number", "type", "company")
    list_filter = (("production_date", admin.DateFieldListFilter),)


admin.site.register(Robot, RobotsAdmin)
admin.site.register(Sensor)
admin.site.register(SensorLog)
