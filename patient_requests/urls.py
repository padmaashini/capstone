from django.urls import path
from patient_requests import views

urlpatterns = [
    path('', views.home, name='home'),
    path('practitioner/<uuid:id>/requests', views.requests_for_practitioner, name="requests_for_practitioner")
]