from django.urls import path
from requests import views

urlpatterns = [
    path('', views.home, name='home'),
    path('practitioner/<int:id>/requests', views.requests_for_practitioner, name="requests_for_practitioner")
]