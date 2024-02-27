# pylint: skip-file

from django.shortcuts import render
from django.http import JsonResponse

from patient_requests.clients.medplum import MedplumClient
from collections import defaultdict

def home(request):
    return render(request, "pages/home.html", {})

def requests_for_practitioner(request, id):
    data = []
    location_hash = defaultdict(list)
    medplum = MedplumClient()
    res = medplum.get_practitioner_requests(id)
    raw_tasks = res.json()['entry']

    for task in raw_tasks:
        resource = task['resource']
        patient_reference = resource['requester']
        nurse_reference = resource['owner']

        location_obj = resource.get('location', None)
        location_reference = location_obj.get('reference', "") if location_obj else ""
        refs = location_reference.split('/')
        location_id = refs[-1]

        location_hash[location_id].append({
            "id": resource["id"],
            "patient_name": patient_reference.get('display', ""),
            "time_of_request": resource.get('authoredOn', ""),
            "completed": resource['status'] == 'completed',
            "category": resource["code"]["text"],
            "transcribed_text": resource.get('description', ""),
            "room_number": "Not Available",
            "bed_number": "Not Available"
        })

    requests = []
    for location_id, data in location_hash.items():
        if not location_id:
            for d in data:
                requests.append(d)
            continue

        location_res = medplum.get_location_by_id(location_id)
        location_name = location_res.get("name", "")
        room_number , bed_number = location_name.split(" - ")

        for d in data:
            d["room_number"] = room_number
            d["bed_number"] = bed_number
            requests.append(d)

    return JsonResponse({ "status": "Success", "data": requests })