from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.shortcuts import render
from django.db import connection

from app1.forms import NewRobot
from app1.models import Robot, RobotLog

def return_all_robots(request):
    robot_data = Robot.objects.all().count()
    index = 1
    data = {}
    while index <= robot_data:
        data[index] = Robot.objects.filter(pk=index).values_list('serial_number', 'type', 'company').get()
        index+=1
    return JsonResponse(data)
    
def return_robot_data(request):
    robot_data = Robot.objects.all().count()
    index = 1
    data = {}
    while index <= robot_data:
        data[index] = f"{Robot.objects.filter(pk=index).values_list('serial_number', 'production_date', 'type', 'company').get()}, {RobotLog.objects.filter(robot_id=index).values_list('robot_id', 'timestamp', 'telemetry_humidity', 'telemetry_temperature', 'telemetry_pressure', 'location_latitude', 'location_longitude').last()}"
        index+=1
    return JsonResponse(data)

def add_new_robot(request):
    if request.method == 'POST':
        form = NewRobot(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/app1/return_all/')
    else:
        form = NewRobot()
    return render(request, 'add_new.html')

def return_telemetry(request):
    template = loader.get_template('return_telemetry.html')
    if request.method == 'POST':
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        serial = request.POST.get('serial_number')
        with connection.cursor() as cursor:
            cursor.execute('SELECT robot_id, timestamp, telemetry_humidity, telemetry_temperature, telemetry_pressure FROM app1_robotlog WHERE (timestamp BETWEEN "'+fromdate+'" AND "'+todate+'") AND (robot_id = "'+str(serial)+'")')
            logs = cursor.fetchall()
        return JsonResponse(logs, safe=False)
    else:
        return HttpResponse(template.render({}, request))

def return_location(request):
    template = loader.get_template('return_location.html')
    if request.method == 'POST':
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        serial = request.POST.get('serial_number')
        with connection.cursor() as cursor:
            cursor.execute('SELECT robot_id, timestamp, location_latitude, location_longitude FROM app1_robotlog WHERE (timestamp BETWEEN "'+fromdate+'" AND "'+todate+'") AND (robot_id = "'+str(serial)+'")')
            logs = cursor.fetchall()
        return JsonResponse(logs, safe=False)
    else:
        return HttpResponse(template.render({}, request))

def return_latest_location(request):
    robot_data = Robot.objects.all().count()
    index = 1
    data = {}
    while index <= robot_data:
        data[index] = f"{RobotLog.objects.filter(robot_id=index).values_list('timestamp', 'location_latitude', 'location_longitude').last()}"
        index+=1
    return JsonResponse(data)

def update_robot(request):
    if request.method=='POST':
        serial = request.POST['serial_number']
        type = request.POST['type']
        Robot.objects.filter(pk=serial).update(type = type)
        return HttpResponseRedirect('/app1/return_all/')
    else:
        template = loader.get_template('modify_robot.html')
    
    return HttpResponse(template.render({}, request))
