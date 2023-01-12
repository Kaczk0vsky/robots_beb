from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from app1.models import Robot, RobotLog
from django.template import loader
from django.shortcuts import render
from app1.forms import NewRobot
from django.db import connection


def ReturnAllRobots(request):
    robot_data = Robot.objects.all().count()
    index = 1
    data = {}
    while index <= robot_data:
        data[index] = Robot.objects.filter(pk=index).values_list('serial_number', 'type', 'company').get()
        index+=1
    print(data)
    return JsonResponse({'robot_data': data})
    
def ReturnRobotData(request):
    robot_data = Robot.objects.all().count()
    index = 1
    data = {}
    while index <= robot_data:
        data[index] = f"{Robot.objects.filter(pk=index).values().get()}, {RobotLog.objects.filter(robot_id=index).values().last()}"
        index+=1
    print(data)
    return JsonResponse({'robot_data': data})

def AddNewRobot(request):
    if request.method == 'POST':
        form = NewRobot(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/app1/return_all/')
    else:
        form = NewRobot()
    return render(request, 'add_new.html')

def ReturnTelemetry(request):
    template = loader.get_template('return_telemetry.html')
    if request.method == 'POST':
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        serial = request.POST.get('serial_number')
        logs = RobotLog.objects.raw('SELECT * FROM app1_robotlog WHERE (timestamp BETWEEN "'+fromdate+'" AND "'+todate+'") AND (robot_id = "'+str(serial)+'")')
        data = {
            'robots': logs,
        }
        return HttpResponse(template.render(data, request))
    else:
        robot_data = Robot.objects.all().values()
        data = {
            'robots': robot_data,
        }
        return HttpResponse(template.render(data, request))

def ReturnLocation(request):
    template = loader.get_template('return_location.html')
    if request.method == 'POST':
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        serial = request.POST.get('serial_number')
        logs = RobotLog.objects.raw('SELECT * FROM app1_robotlog WHERE (timestamp BETWEEN "'+fromdate+'" AND "'+todate+'") AND (robot_id = "'+str(serial)+'")')
        data = {
            'robots': logs,
        }
        return HttpResponse(template.render(data, request))
    else:
        robot_data = Robot.objects.all().values()
        data = {
            'robots': robot_data,
        }
        return HttpResponse(template.render(data, request))

def ReturnLatestLocationOfAll(request):
    robot_data = Robot.objects.all().count()
    index = 1
    data = {}
    while index <= robot_data:
        data[index] = f"{RobotLog.objects.filter(robot_id=index).values_list('timestamp', 'location_latitude', 'location_longitude').last()}"
        index+=1
    print(data)
    return JsonResponse({'robot_data': data})

def GetRobotBrand(request):
    robot_data = Robot.objects.all().values()
    template = loader.get_template('modify_robot.html')
    data = {
        'robots': robot_data,
    }
    
    return HttpResponse(template.render(data, request))

def ModifyRobotBrand(request):
    serial = request.POST['serial_number']
    type = request.POST['type']
    Robot.objects.filter(pk=serial).update(type = type)
    
    return HttpResponseRedirect('/app1/return_all/')
