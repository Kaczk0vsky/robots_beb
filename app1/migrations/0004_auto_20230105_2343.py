# Generated by Django 3.2.16 on 2023-01-05 22:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0003_auto_20230105_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='robot',
            name='location_timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='robot',
            name='telemetry_timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]