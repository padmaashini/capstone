from django.urls import path
from requests import views

urlpatterns = [
    path("", views.home, name='home'),
]