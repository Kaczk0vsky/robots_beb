from django.urls import path
from .views import ReturnAllRobots, ReturnRobotData, AddNewRobot


urlpatterns = [
    path('return_all/', ReturnAllRobots, name='ReturnAllRobots'),
    path('return_robot_data/', ReturnRobotData, name='ReturnRobotData'),
    path('add_new/', AddNewRobot, name='AddNewRobot'),
]
