# pylint: skip-file

from django.shortcuts import render
from django.http import JsonResponse

from patient_requests.clients.medplum import MedplumClient

def home(request):
    return render(request, "pages/home.html", {})

def requests_for_practitioner(request, id):
    data = []
    medplum = MedplumClient()
    res = medplum.get_practitioner_requests(id)
    raw_tasks = res.json()['entry']

    for task in raw_tasks:
        resource = task['resource']
        patient_reference = resource['requester']
        nurse_reference = resource['owner']
        data.append({
            "id": resource["id"],
            "patient_name": patient_reference['display'],
            "room_number": "TO_FILL_IN",
            "bed_number": "TO_FILL_IN",
            "time_of_request": resource['authoredOn'],
            "completed": resource['status'] == 'completed',
            "category": resource["code"]["text"],
            "transcribed_test": "TO_FILL_IN"
        })
    
    return JsonResponse({ "status": "Success", "data": data })