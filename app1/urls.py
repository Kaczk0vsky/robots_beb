from django.urls import path

from app1.views import (
    return_all_robots,
    return_robot_data,
    add_new_robot,
    return_telemetry,
    return_location,
    return_latest_location,
    update_robot,
    configure_communication,
    change_parameters,
    create_device,
)

urlpatterns = [
    path("return_all/", return_all_robots, name="Return_all_robots"),
    path("return_robot_data/", return_robot_data, name="Return_robot_data"),
    path("add_new/", add_new_robot, name="Add_new_robot"),
    path("return_telemetry/", return_telemetry, name="Return_telemetry"),
    path("return_location/", return_location, name="Return_location"),
    path(
        "return_latest_location/",
        return_latest_location,
        name="ReturnLatestLocationOfAll",
    ),
    path("modify_robot/", update_robot, name="Update_robot_brand"),
    path("communication/", configure_communication, name="Configure_communication"),
    path("update/", change_parameters, name="Change_robot_parameters"),
    path("communication/", create_device, name="Configure_communication"),
]
