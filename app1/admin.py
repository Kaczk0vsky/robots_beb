from django.contrib import admin
from .models import Robot, Sensor, SensorLog, RobotModificationHistory, Company


class RobotsAdmin(admin.ModelAdmin):
    list_display = ("serial_number", "type", "company", "production_date")
    search_fields = ("serial_number", "type", "company")
    list_filter = (("production_date", admin.DateFieldListFilter),)


class SensorAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "robot_id")
    list_filter = (("robot_id", admin.RelatedOnlyFieldListFilter),)


class SensorLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sensor_id",
        "timestamp",
        "telemetry_humidity",
        "telemetry_temperature",
        "telemetry_pressure",
        "location_latitude",
        "location_longitude",
    )
    list_filter = (
        ("timestamp", admin.DateFieldListFilter),
        ("sensor_id", admin.RelatedOnlyFieldListFilter),
    )


class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "company_name", "nip")


class RobotModificationHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "robot_id", "timestamp")
    list_filter = (
        ("robot_id", admin.RelatedOnlyFieldListFilter),
        ("timestamp", admin.DateFieldListFilter),
    )


admin.site.register(Robot, RobotsAdmin)
admin.site.register(Sensor, SensorAdmin)
admin.site.register(SensorLog, SensorLogAdmin)
admin.site.register(RobotModificationHistory, RobotModificationHistoryAdmin)
admin.site.register(Company, CompanyAdmin)
