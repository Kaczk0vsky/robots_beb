from django.urls import path

from app1.views import AdminView, UserView

urlpatterns = [
    path("user_view/", UserView.as_view()),
    path("admin_view/", AdminView.as_view()),
]
