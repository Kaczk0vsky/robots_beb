from django.urls import path
from .views import ReturnAllRobots


urlpatterns = [
    path('return_all/', ReturnAllRobots, name='ReturnAllRobots'),
]
