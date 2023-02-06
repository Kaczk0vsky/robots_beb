from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.shortcuts import render
from django.db import connection
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, authentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from app1.serializers import UserSerializer, GroupSerializer
from app1.models import Robot, SensorLog, Sensor


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
    if request.method == "POST":
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
        return HttpResponseRedirect("/app1/return_all/")
    else:
        form = Robot()
    return render(request, "add_new.html")


@api_view(["GET", "POST"])
def return_telemetry(request):
    template = loader.get_template("return_telemetry.html")
    if request.method == "POST":
        fromdate = request.POST.get("fromdate")
        todate = request.POST.get("todate")
        serial = request.POST.get("serial_number")
        data = RobotLog.objects.filter(robot_id=serial).values("log_id")

        dict = {}
        index = 0
        for x in data:
            log_ids = Log.objects.filter(
                timestamp__range=[fromdate, todate],
                id=x["log_id"],
            ).values(
                "timestamp",
                "telemetry_humidity",
                "telemetry_temperature",
                "telemetry_pressure",
            )
            dict[index + 1] = log_ids
            index += 1
        return Response(dict)
    else:
        return HttpResponse(template.render({}, request))


@api_view(["GET", "POST"])
def return_location(request):
    template = loader.get_template("return_location.html")
    if request.method == "POST":
        fromdate = request.POST.get("fromdate")
        todate = request.POST.get("todate")
        serial = request.POST.get("serial_number")
        data = RobotLog.objects.filter(robot_id=serial).values("log_id")

        dict = {}
        index = 0
        for x in data:
            log_ids = Log.objects.filter(
                timestamp__range=[fromdate, todate],
                id=x["log_id"],
            ).values(
                "timestamp",
                "location_latitude",
                "location_longitude",
            )
            dict[index + 1] = log_ids
            index += 1
        return Response(dict)
    else:
        return HttpResponse(template.render({}, request))


@api_view(["GET", "POST"])
def return_latest_location(request):
    robot_data = Robot.objects.all().count()
    index = 1
    data = {}
    while index <= robot_data:
        temp = RobotLog.objects.filter(robot_id=index).values("log_id").last()
        last_log_id = temp
        data[index] = Log.objects.filter(id=last_log_id["log_id"]).values(
            "timestamp",
            "location_latitude",
            "location_longitude",
        )
        print(data[index])
        index += 1
    return Response(data)


@api_view(["GET", "POST"])
def update_robot(request):
    if request.method == "POST":
        serial = request.POST["serial_number"]
        type = request.POST["type"]
        Robot.objects.filter(pk=serial).update(type=type)
        return HttpResponseRedirect("/app1/return_all/")
    else:
        template = loader.get_template("modify_robot.html")
    return HttpResponse(template.render({}, request))


@api_view(["GET"])
def detach_communication(request):
    if request.method == "POST":
        pass
        msg = f"Detached robot"
        return Response(msg)
