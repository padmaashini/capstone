from django.shortcuts import render
from django.http import JsonResponse

from patient_requests.clients.medplum import MedplumClient

def home(request):
    return render(request, "pages/home.html", {})

def requests_for_practitioner(request, id):
    print('id', id)
    data = []

    m = MedplumClient()
    print('headers', m.headers())
    res = m.authorize()
    print('r', res)
    return JsonResponse({ "status": "Success", "data": data })