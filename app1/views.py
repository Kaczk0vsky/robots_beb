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
    robot_data = Robot.objects.all().values()
    template = loader.get_template('return_telemetry.html')
    data = {
        'robots': robot_data,
    }
    return HttpResponse(template.render(data, request))

def ReturnedTelemetry(request):
    serial = request.POST['serial_number']
    start_time = request.POST['start_time']
    end_time = request.POST['end_time']

    table_size = Robot.objects.filter(serial_number=serial).count()
    robot_data = Robot.objects.filter(serial_number=serial, start_time=start_time).values()     # =Extract('start_time', 'end_time')

    template = loader.get_template('returned_telemetry.html')
    data = {
        'robots': robot_data,
        'table_size': table_size,
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
