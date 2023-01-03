from django.contrib import admin
from .models import Robot


class RobotsAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'type', 'company', 'production_date')
    search_fields = ('serial_number', 'type', 'company')
    list_filter = (
        ('production_date', admin.DateFieldListFilter),
    )


admin.site.register(Robot, RobotsAdmin)
