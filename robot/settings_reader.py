import os
import toml


def robot_info():
    return toml.load(os.path.dirname(os.path.abspath(__file__)) + "/settings.toml")[
        "robot_info"
    ]


def mqtt_settings():
    return toml.load(os.path.dirname(os.path.abspath(__file__)) + "/settings.toml")[
        "mqtt"
    ]
