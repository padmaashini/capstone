# pylint: skip-file

from requests.clients.client import Client 

class MedplumClient(Client):
    """
    Medplum API client.
    """
    BASE_URL = "https://api.medplum.com/fhir/R4"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_practitioner_requests(self):
        pass