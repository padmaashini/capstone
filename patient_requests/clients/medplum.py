# pylint: skip-file

from .client import Client 
import base64
import requests
class MedplumClient(Client):
    """
    Medplum API client.
    """
    BASE_URL = "https://api.medplum.com/fhir/R4"
    CLIENT_ID = "26783641-2608-46d7-9875-1a57658e978f"
    CLIENT_SECRET = "8869347129b106856c90d73d9242a1a0e267c212fdb8359ccbbe8eb438ef9af2"

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
        # id example for testing: b292f7a7-0adc-40db-bb76-6245b8411fda
        # id = { 'reference': f"Practitioner/{id}" }
        # practitioner_id = "b292f7a7-0adc-40db-bb76-6245b8411fda"
        res = requests.get(f"{self.BASE_URL}/Task?owner=Practitioner/{id}", headers=headers)
        return res
    
    def create_patient_request(self, mapping, transcribed_text):
        # TO-DO; fix id of patient, and figure out the location stuff
        # 
        practitioner_id = mapping.practitioner_id
        patient_id = mapping.patient_id
        bed_num = mapping.bed_id
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
            "owner": {
                "reference": f"Practitioner/{practitioner_id}"
            },
            "requester": {
                "reference": f"Patient/{patient_id}",
            },
            "location": bed_num,
            "code": {
                "text": "Food"
            }   
        }

        response = requests.post(f"{self.BASE_URL}/Task", headers=headers, json=payload)
        print('response', response.json())
        return response.json() if response.status_code == 201 else None

    # resourceType: 'Task',
    #   status: 'requested',
    #   intent: 'unknown',
    #   owner: {
    #     reference: "Practitioner/b292f7a7-0adc-40db-bb76-6245b8411fda",
    #     id: "b292f7a7-0adc-40db-bb76-6245b8411fda",
    #     display: "Padmaashini Sukumaran"
    #   },
    #   requester: {
    #     reference: "Patient/841396bb-4ef1-4ef7-abf1-418cae990bac",
    #     id: "841396bb-4ef1-4ef7-abf1-418cae990bac",
    #     display: "John Smith"
    #   },
    #   code: {
    #     text: requestType
    #   },
    #   authoredOn: getCurrentDateTimeInEST()