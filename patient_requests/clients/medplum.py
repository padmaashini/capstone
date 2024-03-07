# pylint: skip-file

from .client import Client 
import base64
import requests
from datetime import datetime
import os

class MedplumClient(Client):
    """
    Medplum API client.
    """
    BASE_URL = "https://api.medplum.com/fhir/R4"
    CLIENT_ID = os.getenv('MEDPLUM_CLIENT_ID')
    CLIENT_SECRET = os.getenv('MEDPLUM_CLIENT_SECRET')

    def headers(self):
        client_credentials = f"{self.CLIENT_ID}:{self.CLIENT_SECRET}"

        # Encode the credentials string to Base64
        client_credentials_base64 = base64.b64encode(client_credentials.encode()).decode()

        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {client_credentials_base64}"
        }

    def authorize(self):
        params = {
            "grant_type": "client_credentials",
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET
        }
   
        res = self._post("https://api.medplum.com/oauth2/token", data=params)
        return res.json() if res.status_code == 200 else None

    def get_access_token(self):
        authorized = self.authorize()

        return authorized["access_token"]
    
    def get_practitioner_requests(self, id):
        token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        res = requests.get(f"{self.BASE_URL}/Task?owner=Practitioner/{id}", headers=headers)
        return res
    
    def get_patient_by_id(self, patient_id):
        token = self.get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{self.BASE_URL}/Patient/{patient_id}", headers=headers)
        return response.json() if response.status_code == 200 else None

    def get_practitioner_by_id(self, practitioner_id):
        token = self.get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{self.BASE_URL}/Practitioner/{practitioner_id}", headers=headers)
        return response.json() if response.status_code == 200 else None

    def get_location_by_id(self, location_id):
        token = self.get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{self.BASE_URL}/Location/{location_id}", headers=headers)
        return response.json() if response.status_code == 200 else None

    def create_patient_request(self, mapping, transcribed_text, bucket):
        practitioner_id = mapping.practitioner_id
        patient_id = mapping.patient_id
        location_id = mapping.bed_id

        patient_res = self.get_patient_by_id(patient_id)
        location_res = self.get_location_by_id(location_id)

        patient_name = ""
        if patient_res.get('name'): 
            obj = patient_res.get('name', [])[0]
            given = obj.get('given', [])[0]
            family = obj.get('family', [])[0]

            patient_name = f"{given} {family}"
        practitioner_obj = patient_res.get("generalPractitioner", [])[0]
        practitioner_name = practitioner_obj['display'] if practitioner_obj else ""

        token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/fhir+json"
        }

        payload = {
            "resourceType": "Task",
            "status": "requested",
            "intent": "unknown",
            "description": transcribed_text,
            "authoredOn": datetime.now().isoformat(), 
            "owner": {
                "reference": f"Practitioner/{practitioner_id}",
                "display": practitioner_name
            },
            "requester": {
                "reference": f"Patient/{patient_id}",
                "display": patient_name
            },
            "location": {
                "reference": f"Location/{location_id}"
            },
            "code": {
                "text": bucket
            }   
        }

        response = requests.post(f"{self.BASE_URL}/Task", headers=headers, json=payload)
        return response.json() if response.status_code == 201 else None
