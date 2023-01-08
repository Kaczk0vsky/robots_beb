from django.http import HttpResponse, HttpResponseRedirect
from django.db.models.functions import Extract
from app1.models import Robot
from django.template import loader
from django.shortcuts import render
from app1.forms import NewRobot


def ReturnAllRobots(request):
    robot_data = Robot.objects.all().values()
    template = loader.get_template('return_all.html')
    data = {
        'robots': robot_data,
    }
    
    return HttpResponse(template.render(data, request))
    
def ReturnRobotData(request):
    robot_data = Robot.objects.all().values()
    template = loader.get_template('return_robot_data.html')
    data = {
        'robots': robot_data,
    }

    return HttpResponse(template.render(data, request))

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
        searchresult = Robot.objects.raw('SELECT * FROM app1_robot WHERE (serial_number = "'+serial+'") AND (telemetry_timestamp BETWEEN "'+fromdate+'" AND "'+todate+'")')
        all_data = Robot.objects.raw('SELECT timestamp_all, humidity_all, temperature_all, pressure_all FROM app1_robot WHERE (serial_number = "'+serial+'") AND (telemetry_timestamp BETWEEN "'+fromdate+'" AND "'+todate+'")')
        data = {
            'robots': searchresult,
            'all_data': all_data,
        }

        return HttpResponse(template.render(data, request))
    else:
        robot_data = Robot.objects.all().values()
        data = {
            'robots': robot_data,
        }
        return HttpResponse(template.render(data, request))

def ReturnLocation(request):
    robot_data = Robot.objects.all().values()
    template = loader.get_template('return_location.html')
    data = {
        'robots': robot_data,
    }
    return HttpResponse(template.render(data, request))

def ReturnLatestLocationOfAll(request):
    robot_data = Robot.objects.all().values()
    template = loader.get_template('return_latest_location.html')
    data = {
        'robots': robot_data,
    }
    return HttpResponse(template.render(data, request))

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
    Robot.objects.filter(serial_number=serial).update(type = type)
    
    return HttpResponseRedirect('/app1/return_all/')
