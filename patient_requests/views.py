# pylint: skip-file

from django.shortcuts import render
from django.http import JsonResponse

from patient_requests.clients.medplum import MedplumClient
from collections import defaultdict
import concurrent.futures
from patient_requests.prioritizer import RequestPrioritizer
import datetime

def home(request):
    return render(request, "pages/home.html", {})

def parse_authored_time(authored_on):
    time_format = '%Y-%m-%dT%H:%M:%S.%f'
    try:
        return datetime.datetime.strptime(authored_on, time_format)
    except ValueError:
        # Handle cases where authored_on might not have fractional seconds
        return datetime.datetime.strptime(authored_on.split('.')[0], '%Y-%m-%dT%H:%M:%S')


def requests_for_practitioner(request, id):
    data = []
    location_hash = defaultdict(dict)
    patient_hash = defaultdict(dict)
    medplum = MedplumClient()
    res = medplum.get_practitioner_requests(id)
    raw_tasks = res.json()['entry']

    # Collect unique patient and location IDs
    patient_ids = set()
    location_ids = set()

    raw_tasks.sort(key=lambda task: parse_authored_time(task['resource'].get("authoredOn", "")))

    for task in raw_tasks:
        resource = task['resource']
        patient_reference = resource['requester']['reference']
        patient_ids.add(patient_reference.split('/')[-1])

        location_reference = resource.get('location', {}).get('reference', '')
        if location_reference:
            location_ids.add(location_reference.split('/')[-1])

    # Fetch patient and location details in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        patient_futures = {executor.submit(medplum.get_patient_by_id, pid): pid for pid in patient_ids}
        location_futures = {executor.submit(medplum.get_location_by_id, lid): lid for lid in location_ids}

        for future in concurrent.futures.as_completed(patient_futures):
            patient_id = patient_futures[future]
            patient_hash[patient_id] = future.result()

        for future in concurrent.futures.as_completed(location_futures):
            location_id = location_futures[future]
            location_hash[location_id] = future.result()

    # Process tasks
    requests = []
    for task in raw_tasks:
        resource = task['resource']
        patient_id = resource['requester']['reference'].split('/')[-1]
        location_id = resource.get('location', {}).get('reference', '').split('/')[-1] if resource.get('location', {}).get('reference', '') else ""

        patient_info = patient_hash.get(patient_id, {})
        location_info = location_hash.get(location_id, {})

        patient_name = ""
        if patient_info and patient_info.get('name'):
            name_obj = patient_info.get('name', [])[0]
            given = name_obj.get('given', [])[0]
            family = name_obj.get('family', "")
            patient_name = f"{given} {family}"

        location_name = location_info.get("name", "") if location_info else ""
        room_number, bed_number = location_name.split(" - ") if location_name else ("Not Available", "Not Available")

        category = resource["code"]["text"]
        condition_obj = patient_info.get("extension", [])
        condition = {}
        if condition_obj:
            condition = condition_obj[0]

        authored_on = resource.get('authoredOn', "")
        priority = RequestPrioritizer.calculate_priority(condition.get("valueString", None), category, authored_on)

        requests.append({
            "id": resource["id"],
            "patient_name": patient_name,
            "time_of_request": authored_on,
            "completed": resource['status'] == 'completed',
            "category": category,
            "transcribed_text": resource.get('description', ""),
            "room_number": room_number,
            "bed_number": bed_number,
            "priority": priority
        })
    
    
    sorted_requests = sorted(requests, key=lambda x: x['priority'])
    return JsonResponse({"status": "Success", "data": sorted_requests})
