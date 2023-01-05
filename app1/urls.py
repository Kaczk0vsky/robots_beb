from django.urls import path
from .views import ReturnAllRobots, ReturnRobotData


urlpatterns = [
    path('return_all/', ReturnAllRobots, name='ReturnAllRobots'),
    path('return_robot_data/', ReturnRobotData, name='ReturnRobotData'),
]
