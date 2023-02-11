from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from django.db import connection
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, authentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from app1.serializers import UserSerializer, GroupSerializer
from app1.models import Robot, SensorLog, Sensor, RobotModificationHistory


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(["GET"])
def return_all_robots(request):
    robot_data = Robot.objects.all().count()
    index = 1
    data = {}
    while index <= robot_data:
        data[index] = (
            Robot.objects.filter(pk=index)
            .values_list("serial_number", "type", "company")
            .get()
        )
        index += 1
    return Response(data)


@api_view(["GET"])
def return_robot_data(request):
    robot_data = Robot.objects.all().count()
    index = 1
    data = {}
    while index <= robot_data:
        data[index] = (
            f"{Robot.objects.filter(serial_number=index).values_list('production_date', 'type', 'company').get()}"
            + f"{SensorLog.objects.filter(sensor_id=Sensor.objects.get(type='telemetry')).last()}"
            + f"{SensorLog.objects.filter(sensor_id=Sensor.objects.get(type='location')).last()}"
        )
        index += 1
    return Response(data)


@api_view(["GET", "POST"])
def add_new_robot(request):
    template = loader.get_template("add_remove.html")

    # EP for adding new robot to database
    if request.method == "POST" and "add_new" in request.POST:
        serial_number = request.POST.get("serial_number")
        production_date = request.POST.get("production_date")
        type = request.POST.get("type")
        company = request.POST.get("company")
        Robot(
            serial_number=serial_number,
            production_date=production_date,
            type=type,
            company=company,
        ).save()
        return HttpResponseRedirect("/return_all/")

    # EP for removing robot from database with saved sensor log history
    elif request.method == "POST" and "remove" in request.POST:
        robot_to_remove = request.POST.get("serial_to_remove")
        Sensor.objects.filter(robot_id=robot_to_remove).update(robot_id=None)
        Robot.objects.get(pk=robot_to_remove).delete()
        return HttpResponseRedirect("/return_all/")

    # EP for modifying robot type
    elif request.method == "POST" and "modify" in request.POST:
        serial = request.POST.get("serial_modify")
        type = request.POST.get("type_modify")
        Robot.objects.filter(pk=serial).update(type=type)
        return HttpResponseRedirect("/return_all/")

    return HttpResponse(template.render({}, request))


@api_view(["GET", "POST"])
def return_telemetry(request):
    template = loader.get_template("return_telemetry.html")
    if request.method == "POST":
        fromdate = request.POST.get("fromdate")
        todate = request.POST.get("todate")
        serial = request.POST.get("serial_number")
        data = SensorLog.objects.filter(
            sensor_id=Sensor.objects.get(
                type="telemetry", robot_id=Robot.objects.get(pk=serial)
            ),
            timestamp__range=[fromdate, todate],
        ).values(
            "timestamp",
            "telemetry_humidity",
            "telemetry_temperature",
            "telemetry_pressure",
        )

        return Response(data)
    else:
        return HttpResponse(template.render({}, request))


@api_view(["GET", "POST"])
def return_location(request):
    template = loader.get_template("return_location.html")
    if request.method == "POST":
        fromdate = request.POST.get("fromdate")
        todate = request.POST.get("todate")
        serial = request.POST.get("serial_number")
        data = SensorLog.objects.filter(
            sensor_id=Sensor.objects.get(
                type="location", robot_id=Robot.objects.get(pk=serial)
            ),
            timestamp__range=[fromdate, todate],
        ).values(
            "timestamp",
            "location_latitude",
            "location_longitude",
        )
        return Response(data)
    else:
        return HttpResponse(template.render({}, request))


@api_view(["GET"])
def return_latest_location(request):
    number_of_robots = Robot.objects.count()
    index = 1
    data = {}
    while index <= number_of_robots:
        temp = {
            index: (
                SensorLog.objects.filter(
                    sensor_id=Sensor.objects.get(
                        type="location", robot_id=Robot.objects.get(pk=index)
                    ),
                )
                .values(
                    "timestamp",
                    "location_latitude",
                    "location_longitude",
                )
                .last()
            )
        }
        data.update(temp)
        index += 1
    return Response(data)


@api_view(["GET", "POST"])
def configure_communication(request):
    template = loader.get_template("communication.html")

    # detaching communication device from robot
    if request.method == "POST" and "detach" in request.POST:
        telemetry_state = request.POST.get("telemetry_1")
        location_state = request.POST.get("location_1")
        robot_serial = request.POST.get("serial_1")
        type = ""

        if telemetry_state == "True":
            type = "telemetry"
        elif location_state == "True":
            type = "location"

        if (
            type == ""
            or robot_serial == ""
            or telemetry_state == "True"
            and location_state == "True"
            or telemetry_state == "False"
            and location_state == "False"
        ):
            data = "Correct data input!"
            return Response(data)
        else:
            Sensor.objects.filter(
                robot_id=Robot.objects.get(serial_number=robot_serial),
                type=type,
            ).update(robot_id=None)
            data = Sensor.objects.all().values()
            return Response(data)

    # attaching communication device to a robot
    elif request.method == "POST" and "attach" in request.POST:
        telemetry_state = request.POST.get("telemetry_2")
        location_state = request.POST.get("location_2")
        robot_serial = request.POST.get("serial_2")
        type = ""

        if telemetry_state == "True":
            type = "telemetry"
        elif location_state == "True":
            type = "location"

        if (
            type == ""
            or robot_serial == ""
            or telemetry_state == "True"
            and location_state == "True"
            or telemetry_state == "False"
            and location_state == "False"
        ):
            data = "Correct data input!"
            return Response(data)
        else:
            Sensor(
                robot_id=Robot.objects.get(serial_number=robot_serial),
                type=type,
                fault_detected=False,
            ).save()
            data = Sensor.objects.all().values()
            return Response(data)

    # EP for removing communication device from one robot and adding it to another
    elif request.method == "POST" and "swap" in request.POST:
        telemetry_state = request.POST.get("telemetry_3")
        location_state = request.POST.get("location_3")
        detach = request.POST.get("serial_3")
        attach = request.POST.get("serial_4")
        type = ""

        if telemetry_state == "True":
            type = "telemetry"
        elif location_state == "True":
            type = "location"

        if (
            type == ""
            or detach == ""
            or attach == ""
            or telemetry_state == "True"
            and location_state == "True"
            or telemetry_state == "False"
            and location_state == "False"
        ):
            data = "Correct data input!"
            return Response(data)
        else:
            Sensor.objects.filter(
                robot_id=Robot.objects.get(serial_number=detach),
                type=type,
            ).update(robot_id=Robot.objects.get(serial_number=attach))
        data = Sensor.objects.all().values()
        return Response(data)

    # EP for creating communication device
    elif request.method == "POST" and "create_device" in request.POST:
        telemetry_state = request.POST.get("type_telemetry")
        location_state = request.POST.get("type_location")
        type = ""

        if telemetry_state == "True":
            type = "telemetry"
        elif location_state == "True":
            type = "location"

        if (
            type == ""
            or telemetry_state == "True"
            and location_state == "True"
            or telemetry_state == "False"
            and location_state == "False"
        ):
            data = "Correct data input!"
        else:
            Sensor(type=type).save()
            data = Sensor.objects.all().values()
        return Response(data)
    else:
        return HttpResponse(template.render({}, request))


def change_parameters(request):
    template = loader.get_template("change_parameters.html")
    serial = request.POST.get("serial")
    data = {}
    if request.method == "POST" and "get_robot" in request.POST:
        data = (
            Robot.objects.filter(serial_number=serial)
            .values(
                "serial_number",
                "production_date",
                "type",
                "company",
            )
            .get()
        )
        return HttpResponse(template.render(data, request))
    elif request.method == "POST" and "set_robot" in request.POST:
        new_date = request.POST.get("new_date")
        new_type = request.POST.get("new_type")
        new_company = request.POST.get("new_company")
        robot_msg = f"Changed parameters: \n"

        if new_date != "":
            robot_msg = (
                robot_msg
                + f"- production date - from {Robot.objects.values_list('production_date', flat=True).get(serial_number=serial)} to {new_date} \n"
            )
            Robot.objects.filter(serial_number=serial).update(production_date=new_date)

        if new_type != "":
            robot_msg = (
                robot_msg
                + f"- type - from {Robot.objects.values_list('type', flat=True).get(serial_number=serial)} to {new_type} \n"
            )
            Robot.objects.filter(serial_number=serial).update(type=new_type)

        if new_company != "":
            robot_msg = (
                robot_msg
                + f"- company - from {Robot.objects.values_list('company', flat=True).get(serial_number=serial)} to {new_company} \n"
            )
            Robot.objects.filter(serial_number=serial).update(company=new_company)

        RobotModificationHistory(
            robot_id=Robot.objects.get(serial_number=serial),
            text=robot_msg,
        ).save()

        data = RobotModificationHistory.objects.all().values()
        return HttpResponseRedirect("/return_all/")
    else:
        return HttpResponse(template.render(data, request))
