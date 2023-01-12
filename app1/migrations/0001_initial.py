# Generated by Django 3.2.16 on 2023-01-12 17:17

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RobotLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('robot_id', models.CharField(editable=False, max_length=256)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('telemetry_humidity', models.IntegerField(default=0, editable=False)),
                ('telemetry_temperature', models.IntegerField(default=0, editable=False)),
                ('telemetry_pressure', models.IntegerField(default=0, editable=False)),
                ('location_latitude', models.IntegerField(default=0, editable=False)),
                ('location_longitude', models.IntegerField(default=0, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Robot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(max_length=256, unique=True)),
                ('production_date', models.DateField()),
                ('type', models.CharField(choices=[('4 wheeler', '4 wheeler'), ('amphibian', 'amphibian'), ('tracked', 'tracked'), ('flying', 'flying')], default='4 wheeler', max_length=10)),
                ('company', models.CharField(max_length=256)),
                ('robot_logs', models.ForeignKey(blank=True, db_column='robot_logs', editable=False, on_delete=django.db.models.deletion.CASCADE, to='app1.robotlog')),
            ],
        ),
    ]
