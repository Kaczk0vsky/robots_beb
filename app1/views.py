from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.mixins import PermissionRequiredMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from xhtml2pdf import pisa

import requests
import datetime

from app1.serializers import UserSerializer, GroupSerializer, RobotSerializer
from app1.models import Robot, SensorLog, Sensor, RobotModificationHistory, Company
from task1_beb.celery import mqtt_send


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


class UserView(APIView):
    """
    Class that that collects all function together.
    Allows a company user to use some EP. If user with admin privileges is logged in you get access to all elements in database.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    serializer_class = RobotSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["__all__"]
    ordering_fields = ["__all__"]
    ordering = ["serial_number"]
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
            # Admin is logged in
            if current_user["groups"] == None:
                sensor_id = (
                    Sensor.objects.filter(
                        type="location",
                        robot_id=Robot.objects.get(
                            pk=serial,
                        ),
                    )
                    .values_list("id", flat=True)
                    .all()
                )

                data = {}
                for element in sensor_id:
                    temp_data = {
                        element: SensorLog.objects.filter(
                            sensor_id=Sensor.objects.get(id=element),
                            timestamp__range=[fromdate, todate],
                        ).values(
                            "timestamp",
                            "location_latitude",
                            "location_longitude",
                        )
                    }
                    data.update(temp_data)
            # User is logged in
            else:
                try:
                    sensor_id = (
                        Sensor.objects.filter(
                            type="location",
                            robot_id=Robot.objects.get(
                                pk=serial,
                                company=Company.objects.get(id=current_user["groups"]),
                            ),
                        )
                        .values_list("id", flat=True)
                        .all()
                    )
                except:
                    data = "This robot doesnt`t belong to your company!"
                    return Response(data)

                data = {}
                for element in sensor_id:
                    temp_data = {
                        element: SensorLog.objects.filter(
                            sensor_id=Sensor.objects.get(id=element),
                            timestamp__range=[fromdate, todate],
                        ).values(
                            "timestamp",
                            "location_latitude",
                            "location_longitude",
                        )
                    }
                    data.update(temp_data)

            return Response(data)

        # EP returning telemetry logs for specified robot in specified timestamp
        elif "search_telemetry" in request.POST:
            fromdate = request.POST.get("fromdate_telemetry")
            todate = request.POST.get("todate_telemetry")
            serial = request.POST.get("serial_number_telemetry")
            # Admin is logged in
            if current_user["groups"] == None:
                sensor_id = (
                    Sensor.objects.filter(
                        type="telemetry",
                        robot_id=Robot.objects.get(
                            pk=serial,
                        ),
                    )
                    .values_list("id", flat=True)
                    .all()
                )

                data = {}
                for element in sensor_id:
                    temp_data = {
                        element: SensorLog.objects.filter(
                            sensor_id=Sensor.objects.get(id=element),
                            timestamp__range=[fromdate, todate],
                        ).values(
                            "timestamp",
                            "telemetry_humidity",
                            "telemetry_temperature",
                            "telemetry_pressure",
                        )
                    }
                    data.update(temp_data)
            # User is logged in
            else:
                try:
                    sensor_id = (
                        Sensor.objects.filter(
                            type="telemetry",
                            robot_id=Robot.objects.get(
                                pk=serial,
                                company=Company.objects.get(id=current_user["groups"]),
                            ),
                        )
                        .values_list("id", flat=True)
                        .all()
                    )
                except:
                    data = "This robot doesnt`t belong to your company!"
                    return Response(data)

                data = {}
                for element in sensor_id:
                    temp_data = {
                        element: SensorLog.objects.filter(
                            sensor_id=Sensor.objects.get(id=element),
                            timestamp__range=[fromdate, todate],
                        ).values(
                            "timestamp",
                            "telemetry_humidity",
                            "telemetry_temperature",
                            "telemetry_pressure",
                        )
                    }
                    data.update(temp_data)
            return Response(data)

        # EP returning all robots
        elif "return_all" in request.POST:
            logged = request.user
            current_user = (
                User.objects.filter(username=logged.username).values("groups").get()
            )
            if current_user["groups"] == None:
                data = Robot.objects.all().values("serial_number", "type", "company")
            else:
                data = Robot.objects.filter(company=current_user["groups"]).values(
                    "serial_number", "type", "company"
                )
            paginator = PageNumberPagination()
            result_page = paginator.paginate_queryset(data, request)

            return Response(result_page)

        # EP returning all robots latest data
        elif "return_latest" in request.POST:
            logged = request.user
            current_user = (
                User.objects.filter(username=logged.username).values("groups").get()
            )

            if current_user["groups"] == None:
                robot_params = Robot.objects.all().values(
                    "serial_number", "production_date", "type", "company"
                )
                robots_serials = Robot.objects.all().values_list(
                    "serial_number", flat=True
                )
            else:
                robot_params = (
                    Robot.objects.filter(company=current_user["groups"])
                    .all()
                    .values("serial_number", "production_date", "type", "company")
                )
                robots_serials = (
                    Robot.objects.filter(company=current_user["groups"])
                    .all()
                    .values_list("serial_number", flat=True)
                )

            telemetry_logs = {}
            location_logs = {}
            for element in robots_serials:
                sensor_id_telemetry = (
                    Sensor.objects.filter(
                        type="telemetry",
                        robot_id=Robot.objects.get(
                            pk=element,
                        ),
                    )
                    .values_list("id", flat=True)
                    .all()
                )
                sensor_id_location = (
                    Sensor.objects.filter(
                        type="location",
                        robot_id=Robot.objects.get(
                            pk=element,
                        ),
                    )
                    .values_list("id", flat=True)
                    .all()
                )

                for index in sensor_id_telemetry:
                    temp_telemetry = {
                        f"Robot serial - {element} - sensor id: {index}": SensorLog.objects.filter(
                            sensor_id=Sensor.objects.get(id=index),
                        )
                        .values(
                            "timestamp",
                            "telemetry_humidity",
                            "telemetry_temperature",
                            "telemetry_pressure",
                        )
                        .last()
                    }
                    telemetry_logs.update(temp_telemetry)

                for index in sensor_id_location:
                    temp_location = {
                        f"Robot serial - {element} - sensor id: {index}": SensorLog.objects.filter(
                            sensor_id=Sensor.objects.get(id=index),
                        )
                        .values(
                            "timestamp",
                            "location_latitude",
                            "location_longitude",
                        )
                        .last()
                    }
                    location_logs.update(temp_location)

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

            if current_user["groups"] == None:
                robots_serials = Robot.objects.all().values_list(
                    "serial_number", flat=True
                )
            else:
                robots_serials = (
                    Robot.objects.filter(company=current_user["groups"])
                    .all()
                    .values_list("serial_number", flat=True)
                )
            data = {}
            location_logs = {}
            for element in robots_serials:
                sensor_id_location = (
                    Sensor.objects.filter(
                        type="location",
                        robot_id=Robot.objects.get(
                            pk=element,
                        ),
                    )
                    .values_list("id", flat=True)
                    .all()
                )
                for index in sensor_id_location:
                    temp_location = {
                        f"Robot serial - {element} - sensor id: {index}": SensorLog.objects.filter(
                            sensor_id=Sensor.objects.get(id=index),
                        )
                        .values(
                            "timestamp",
                            "location_latitude",
                            "location_longitude",
                        )
                        .last()
                    }
                    location_logs.update(temp_location)
                data = {
                    "location_logs": location_logs,
                }

            return Response(data)

        elif "create_report" in request.POST:
            serial = request.POST.get("serial_number_export")

            data = ""
            sensor_id_telemetry = (
                Sensor.objects.filter(
                    type="telemetry",
                    robot_id=Robot.objects.get(
                        pk=serial,
                    ),
                )
                .values_list("id", flat=True)
                .all()
            )
            sensor_id_location = (
                Sensor.objects.filter(
                    type="location",
                    robot_id=Robot.objects.get(
                        pk=serial,
                    ),
                )
                .values_list("id", flat=True)
                .all()
            )

            for index in sensor_id_telemetry:
                temp_data = f'Robot serial: {serial}, sensor id: {index}, sensor type: telemetry - {SensorLog.objects.filter(sensor_id=Sensor.objects.get(id=index)).values("timestamp","telemetry_humidity","telemetry_temperature", "telemetry_pressure").last()}'
                data += temp_data

            for index in sensor_id_location:
                temp_data = f'Robot serial: {serial}, sensor id: {index}, sensor type: location - {SensorLog.objects.filter(sensor_id=Sensor.objects.get(id=index)).values("timestamp","location_latitude","location_longitude").last()}'
                data += temp_data

            result_file = open("robot_logs.pdf", "w+b")
            pisa_status = pisa.CreatePDF(data, dest=result_file)
            result_file.close()

            if pisa_status.err:
                data = "An error occuered during exporting .pdf file..."
            else:
                data = "Exported to .pdf"
            return Response(data)


class AdminView(APIView, PermissionRequiredMixin):
    """
    Class that that collects all function together.
    Allows an database admin to do evertyhing.
    """

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminUser]
    template = loader.get_template("admin.html")

    def get(self, request, format=None):
        return HttpResponse(self.template.render({}, request))

    def post(self, request, format=None):
        # EP for changing robot parameters
        if "get_robot" in request.POST:
            serial = request.POST.get("serial_get_robot")
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
            serial = request.POST.get("serial_get_robot")
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
                if Company.objects.filter(id=new_company).exists():
                    Robot.objects.filter(serial_number=serial).update(
                        company=Company.objects.get(id=new_company)
                    )
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
            sensor_id_location = (
                Sensor.objects.filter(
                    type="location", robot_id=Robot.objects.get(pk=serial)
                )
                .values_list("id", flat=True)
                .all()
            )

            for element in sensor_id_location:
                SensorLog.objects.filter(
                    sensor_id=Sensor.objects.get(pk=element),
                    timestamp__year=date_list[0],
                    timestamp__month=date_list[1],
                    timestamp__day=date_list[2],
                ).delete()

            data = "Deleted logs from specified day!"
            return Response(data)

        # EP for setting temperature for specified robot for the whole day
        elif "change" in request.POST:
            serial = str(request.POST.get("serial_temp"))
            day = str(request.POST.get("temp_day"))
            date_list = day.split("-")
            temperature = request.POST.get("temperature")
            sensor_id_telemetry = (
                Sensor.objects.filter(
                    type="telemetry", robot_id=Robot.objects.get(pk=serial)
                )
                .values_list("id", flat=True)
                .all()
            )

            for element in sensor_id_telemetry:
                SensorLog.objects.filter(
                    sensor_id=Sensor.objects.get(pk=element),
                    timestamp__year=date_list[0],
                    timestamp__month=date_list[1],
                    timestamp__day=date_list[2],
                ).update(telemetry_temperature=temperature)

            data = "Changed temperature logs!"
            return Response(data)

        return HttpResponse(self.template.render({}, request))


# Function that generates auth token automaticlly after creating user
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# Function performing sending mqqt message after saving telemetry sensor log object into database
@receiver(post_save, sender=SensorLog)
def save_telemetry_log(sender, instance, **kwargs):
    sensor_id = instance.sensor_id
    id = (
        SensorLog.objects.filter(sensor_id=sensor_id)
        .values_list("sensor_id", flat=True)
        .last()
    )
    type = Sensor.objects.filter(id=id).values_list("type", flat=True).get()

    if type == "telemetry":
        serial = Sensor.objects.filter(id=id).values_list("robot_id", flat=True).get()
        robot_data = "Telemetry succesfully saved"
        robot_topic = "debug/msg"
        mqtt_send.delay(serial, robot_topic, robot_data)
