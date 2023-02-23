from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from django.db import connection
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, authentication, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

import requests
import datetime

from app1.serializers import UserSerializer, GroupSerializer, RobotSerializer
from app1.models import Robot, SensorLog, Sensor, RobotModificationHistory, Company


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


class RobotViewSet(APIView):
    """
    List all robots in database.
    """

    queryset = Robot.objects.all()
    serializer_class = RobotSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["serial_number", "production_date", "type", "company"]

    def get(self, request, format=None):
        robots = Robot.objects.all().values()
        return Response(robots)


class UserView(APIView):
    """
    Class that that collects all function together.
    Allows a company user to use some EP. If user with admin privileges is logged in you get access to all elements in database.
    """

    template = loader.get_template("user.html")

    def get(self, request, format=None):
        return HttpResponse(self.template.render({}, request))

    def post(self, request, format=None):
        logged = request.user
        current_user = (
            User.objects.filter(username=logged.username).values("groups").get()
        )

        # EP returning location logs for specified robot in specified timestamp
        if "search_location" in request.POST:
            fromdate = request.POST.get("fromdate")
            todate = request.POST.get("todate")
            serial = request.POST.get("serial_number")
            if current_user["groups"] == None:
                data = SensorLog.objects.filter(
                    sensor_id=Sensor.objects.get(
                        type="location",
                        robot_id=Robot.objects.filter(
                            pk=serial,
                        ).get(),
                    ),
                    timestamp__range=[fromdate, todate],
                ).values(
                    "timestamp",
                    "location_latitude",
                    "location_longitude",
                )
            else:
                data = SensorLog.objects.filter(
                    sensor_id=Sensor.objects.get(
                        type="location",
                        robot_id=Robot.objects.filter(
                            pk=serial,
                            company=Company.objects.get(id=current_user["groups"]),
                        ).get(),
                    ),
                    timestamp__range=[fromdate, todate],
                ).values(
                    "timestamp",
                    "location_latitude",
                    "location_longitude",
                )
            return Response(data)

        # EP returning telemetry logs for specified robot in specified timestamp
        elif "search_telemetry" in request.POST:
            fromdate = request.POST.get("fromdate_telemetry")
            todate = request.POST.get("todate_telemetry")
            serial = request.POST.get("serial_number_telemetry")
            if current_user["groups"] == None:
                data = SensorLog.objects.filter(
                    sensor_id=Sensor.objects.get(
                        type="telemetry",
                        robot_id=Robot.objects.filter(
                            pk=serial,
                        ).get(),
                    ),
                    timestamp__range=[fromdate, todate],
                ).values(
                    "timestamp",
                    "telemetry_humidity",
                    "telemetry_temperature",
                    "telemetry_pressure",
                )
            else:
                data = SensorLog.objects.filter(
                    sensor_id=Sensor.objects.get(
                        type="telemetry",
                        robot_id=Robot.objects.filter(
                            pk=serial,
                            company=Company.objects.get(id=current_user["groups"]),
                        ).get(),
                    ),
                    timestamp__range=[fromdate, todate],
                ).values(
                    "timestamp",
                    "telemetry_humidity",
                    "telemetry_temperature",
                    "telemetry_pressure",
                )
            return Response(data)

        # EP returning all robots
        elif "return_all" in request.POST:
            content = {
                "user": str(request.user),  # `django.contrib.auth.User` instance.
                "auth": str(request.auth),  # None
            }
            print(content)

            logged = request.user
            current_user = (
                User.objects.filter(username=logged.username).values("groups").get()
            )
            if current_user["groups"] == None:
                robots = Robot.objects.all().values("serial_number", "type", "company")
            else:
                robots = (
                    Robot.objects.filter(company=current_user["groups"])
                    .all()
                    .values("serial_number", "type", "company")
                )

            paginator = PageNumberPagination()
            result_data = paginator.paginate_queryset(robots, request)
            return Response(result_data)

        # EP returning all robots latest data
        elif "return_latest" in request.POST:
            logged = request.user
            current_user = (
                User.objects.filter(username=logged.username).values("groups").get()
            )
            group_name = (
                Group.objects.filter(pk=current_user["groups"]).values("name").get()
            )
            robot_data = Robot.objects.all().count()

            if current_user["groups"] == None:
                index = 1
                data = {}
                while index <= robot_data:
                    data[index] = (
                        f"{Robot.objects.filter(serial_number=index).values_list('production_date', 'type', 'company').get()}"
                        + f"{SensorLog.objects.filter(sensor_id=Sensor.objects.get(type='telemetry')).last()}"
                        + f"{SensorLog.objects.filter(sensor_id=Sensor.objects.get(type='location')).last()}"
                    )
                    index += 1
            else:
                robot_params = (
                    Robot.objects.filter(company=current_user["groups"])
                    .all()
                    .values("serial_number", "production_date", "type", "company")
                )

                index = 1
                telemetry_logs = {}
                location_logs = {}

                while index <= robot_data:
                    temp_company = (
                        Robot.objects.filter(serial_number=index)
                        .values("company")
                        .get()
                    )
                    if current_user["groups"] == temp_company["company"]:
                        temp_telemetry_logs = {
                            index: (
                                SensorLog.objects.filter(
                                    sensor_id=Sensor.objects.get(
                                        robot_id=Robot.objects.get(
                                            company=Company.objects.get(
                                                company_name=group_name["name"]
                                            ),
                                            serial_number=index,
                                        ),
                                        type="telemetry",
                                    )
                                )
                                .values(
                                    "timestamp",
                                    "telemetry_humidity",
                                    "telemetry_temperature",
                                    "telemetry_pressure",
                                )
                                .last()
                            )
                        }
                        temp_location_logs = {
                            index: (
                                SensorLog.objects.filter(
                                    sensor_id=Sensor.objects.get(
                                        robot_id=Robot.objects.get(
                                            company=Company.objects.get(
                                                company_name=group_name["name"]
                                            ),
                                            serial_number=index,
                                        ),
                                        type="location",
                                    )
                                )
                                .values(
                                    "timestamp",
                                    "location_latitude",
                                    "location_longitude",
                                )
                                .last()
                            )
                        }
                        telemetry_logs.update(temp_telemetry_logs)
                        location_logs.update(temp_location_logs)
                    index += 1

                data = {
                    "robot_data": robot_params,
                    "telemetry_logs": telemetry_logs,
                    "location_logs": location_logs,
                }
            return Response(data)

        # EP returning latest robot location logs for all robots
        elif "return_latest_location" in request.POST:
            logged = request.user
            current_user = (
                User.objects.filter(username=logged.username).values("groups").get()
            )

            number_of_robots = Robot.objects.count()
            index = 1
            data = {}
            if current_user["groups"] == None:
                while index <= number_of_robots:
                    temp = {
                        index: (
                            SensorLog.objects.filter(
                                sensor_id=Sensor.objects.get(
                                    type="location",
                                    robot_id=Robot.objects.get(
                                        pk=index,
                                    ),
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
            else:
                while index <= number_of_robots:
                    temp_company = (
                        Robot.objects.filter(serial_number=index)
                        .values("company")
                        .get()
                    )
                    if current_user["groups"] == temp_company["company"]:
                        print(index)
                        temp = {
                            index: (
                                SensorLog.objects.filter(
                                    sensor_id=Sensor.objects.get(
                                        type="location",
                                        robot_id=Robot.objects.filter(
                                            pk=index,
                                            company=Company.objects.get(
                                                id=current_user["groups"]
                                            ),
                                        ).get(),
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


class AdminView(APIView):
    """
    Class that that collects all function together.
    Allows an database admin to do evertyhing.
    """

    template = loader.get_template("admin.html")

    def get(self, request, format=None):
        return HttpResponse(self.template.render({}, request))

    def post(self, request, format=None):
        # EP for changing robot parameters
        if "get_robot" in request.POST:
            serial = request.POST.get("serial")
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
            return HttpResponse(self.template.render(data, request))
        elif "set_robot" in request.POST:
            serial = request.POST.get("serial")
            new_date = request.POST.get("new_date")
            new_type = request.POST.get("new_type")
            new_company = request.POST.get("new_company")
            robot_msg = f"Changed parameters: \n"

            if new_date != "":
                robot_msg = (
                    robot_msg
                    + f"- production date - from {Robot.objects.values_list('production_date', flat=True).get(serial_number=serial)} to {new_date} \n"
                )
                Robot.objects.filter(serial_number=serial).update(
                    production_date=new_date
                )

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
                if Company.objects.filter(company_name=new_company).exists():
                    pass
                else:
                    Company(company_name=new_company).save()
                Robot.objects.filter(serial_number=serial).update(
                    company=Company.objects.get(company_name=new_company)
                )

            RobotModificationHistory(
                robot_id=Robot.objects.get(serial_number=serial),
                text=robot_msg,
            ).save()

            data = RobotModificationHistory.objects.all().values()
            return Response(data)

        # detaching communication device from robot
        elif "detach" in request.POST:
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
        elif "attach" in request.POST:
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
        elif "swap" in request.POST:
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
        elif "create_device" in request.POST:
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

        # EP for adding new robot to database
        elif "add_new" in request.POST:
            serial_number = request.POST.get("serial_number")
            production_date = request.POST.get("production_date")
            type = request.POST.get("type")
            company = request.POST.get("company")
            if Company.objects.filter(company_name=company).exists():
                pass
            else:
                Company(company_name=company).save()
            Robot(
                serial_number=serial_number,
                production_date=production_date,
                type=type,
                company=Company.objects.get(company_name=company),
            ).save()
            data = Robot.objects.all().values()
            return Response(data)

        # EP for removing robot from database with saved sensor log history
        elif "remove" in request.POST:
            robot_to_remove = request.POST.get("serial_to_remove")
            Sensor.objects.filter(robot_id=robot_to_remove).update(robot_id=None)
            Robot.objects.get(pk=robot_to_remove).delete()
            data = Robot.objects.all().values()
            return Response(data)

        # EP for modifying robot type
        elif "modify" in request.POST:
            serial = request.POST.get("serial_modify")
            type = request.POST.get("type_modify")
            Robot.objects.filter(pk=serial).update(type=type)
            data = Robot.objects.all().values()
            return Response(data)

        # EP for adding company based on given NIP
        elif "add_company" in request.POST:
            nip = request.POST.get("nip")
            today_date = datetime.date.today()
            data = requests.get(
                f"https://wl-api.mf.gov.pl/api/search/nip/{nip}?date={today_date}"
            )
            result = data.json()

            get_result = result["result"]
            get_subject = get_result["subject"]
            company_name = get_subject["name"]

            Group(name=company_name).save()
            Company(
                company_name=company_name,
                nip=nip,
                group=Group.objects.get(name=company_name),
            ).save()

            return Response(result)

        # EP for deleting location of specified robot in selected day
        elif "delete" in request.POST:
            day = str(request.POST.get("day"))
            serial = request.POST.get("serial")
            date_list = day.split("-")

            SensorLog.objects.filter(
                sensor_id=Sensor.objects.get(
                    type="location", robot_id=Robot.objects.get(pk=serial)
                ),
                timestamp__year=date_list[0],
                timestamp__month=date_list[1],
                timestamp__day=date_list[2],
            ).delete()
            data = "Deleted logs from specified day!"
            return Response(data)

        # EP for setting temperature for specified robot/robots for the whole day
        elif "change" in request.POST:
            serial = str(request.POST.get("serial_temp"))
            serial_list = serial.split("-")
            day = str(request.POST.get("temp_day"))
            date_list = day.split("-")
            temperature = request.POST.get("temperature")
            index = 0
            while index <= len(serial_list) - 1:
                SensorLog.objects.filter(
                    sensor_id=Sensor.objects.get(
                        type="telemetry",
                        robot_id=Robot.objects.get(pk=serial_list[index]),
                    ),
                    timestamp__year=date_list[0],
                    timestamp__month=date_list[1],
                    timestamp__day=date_list[2],
                ).update(telemetry_temperature=temperature)
                index += 1
            data = "Changed temperature logs!"
            return Response(data)

        return HttpResponse(self.template.render({}, request))


# Function that generates auth token automaticlly after creating user
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
