from django.http import HttpResponse, JsonResponse
from app1.models import Robot
from django.template import loader


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
