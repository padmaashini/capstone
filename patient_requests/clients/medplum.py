# pylint: skip-file

from .client import Client 
import base64

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
        print('p', params)
        res = self._post("https://api.medplum.com/oauth2/token", data=params)
        return res.json() if res.status_code == 200 else None
        # from requests.clients.medplum import MedplumClient

    def get_practitioner_requests(self, id):
        pass