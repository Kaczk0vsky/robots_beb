# Generated by Django 3.2.16 on 2023-01-05 22:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0004_auto_20230105_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='robot',
            name='location_latitude',
            field=models.CharField(default=0, editable=False, max_length=5),
        ),
        migrations.AlterField(
            model_name='robot',
            name='location_longitude',
            field=models.CharField(default=0, editable=False, max_length=5),
        ),
        migrations.AlterField(
            model_name='robot',
            name='location_timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.AlterField(
            model_name='robot',
            name='telemetry_humidity',
            field=models.CharField(default=0, editable=False, max_length=5),
        ),
        migrations.AlterField(
            model_name='robot',
            name='telemetry_pressure',
            field=models.CharField(default=0, editable=False, max_length=5),
        ),
        migrations.AlterField(
            model_name='robot',
            name='telemetry_temperature',
            field=models.CharField(default=0, editable=False, max_length=5),
        ),
        migrations.AlterField(
            model_name='robot',
            name='telemetry_timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
    ]