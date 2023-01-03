import json

from django.core import serializers
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from app1.models import Robot
from django.forms.models import model_to_dict


def ReturnAllRobots(request):
    data = {
        'type': Robot.type,
        'company': Robot.company,
    }

    data['type'] = model_to_dict(data['type'])
    data['company'] = model_to_dict(data['company'])
    return HttpResponse(json.simplejson.dumps(data), mimetype="application/json")
    