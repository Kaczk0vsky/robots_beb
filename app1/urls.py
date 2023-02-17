from django.urls import path

from app1.views import (
    return_all_robots,
    return_robot_data,
    add_new_robot,
    return_logs,
    return_latest_location,
    configure_communication,
    change_parameters,
)

urlpatterns = [
    path("robots/", return_all_robots, name="Return_all_robots"),
    path("return_robot_data/", return_robot_data, name="Return_robot_data"),
    path("add_remove/", add_new_robot, name="Add_new_robot"),
    path("return_logs/", return_logs, name="Return_location"),
    path(
        "return_latest_location/",
        return_latest_location,
        name="ReturnLatestLocationOfAll",
    ),
    path("communication/", configure_communication, name="Configure_communication"),
    path("update/", change_parameters, name="Change_robot_parameters"),
]
