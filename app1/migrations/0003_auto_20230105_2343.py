# Generated by Django 3.2.16 on 2023-01-05 22:43

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0002_auto_20221226_2115'),
    ]

    operations = [
        migrations.AddField(
            model_name='robot',
            name='location_latitude',
            field=models.CharField(default=0, max_length=5),
        ),
        migrations.AddField(
            model_name='robot',
            name='location_longitude',
            field=models.CharField(default=0, max_length=5),
        ),
        migrations.AddField(
            model_name='robot',
            name='location_timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 5, 22, 43, 1, 509676, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='robot',
            name='telemetry_humidity',
            field=models.CharField(default=0, max_length=5),
        ),
        migrations.AddField(
            model_name='robot',
            name='telemetry_pressure',
            field=models.CharField(default=0, max_length=5),
        ),
        migrations.AddField(
            model_name='robot',
            name='telemetry_temperature',
            field=models.CharField(default=0, max_length=5),
        ),
        migrations.AddField(
            model_name='robot',
            name='telemetry_timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 5, 22, 43, 1, 509676, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='robot',
            name='serial_number',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]