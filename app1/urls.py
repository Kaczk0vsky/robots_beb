from django.urls import path
from .views import return_all_robots, return_robot_data, add_new_robot, return_telemetry, return_location, return_latest_location, update_robot
from django.contrib import admin


urlpatterns = [
    path('return_all/', return_all_robots, name='ReturnAllRobots'),
    path('return_robot_data/', return_robot_data, name='ReturnRobotData'),
    path('add_new/', add_new_robot, name='AddNewRobot'),
    path('return_telemetry/', return_telemetry, name='ReturnTelemetry'),
    path('return_location/', return_location, name='ReturnLocation'),
    path('return_latest_location/', return_latest_location, name='ReturnLatestLocationOfAll'),
    path('modify_robot/', update_robot, name='UpdateRobotBrand'),
    path('admin/', admin.site.urls),
]
