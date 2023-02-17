from django.contrib.auth.models import User, Group
from rest_framework import serializers

from .models import Robot


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class RobotSerializer(serializers.Serializer):
    class Meta:
        model = Robot
        fields = ["serial_number", "production_date", "type", "company"]
