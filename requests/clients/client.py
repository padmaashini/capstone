# pylint: skip-file
import os
import requests
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

class Client(ABC):
    """
    Base client class for common functionalities among all child clients. 
    """
    @abstractmethod
    def headers(self) -> Dict[str, str]:
        pass

    def _get(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Internal method to perform a GET request.
        """
        response = requests.get(url, headers=self.headers(), params=params)

        if response.status_code != 200:
            logging.error(f"Request failed with status code {response.status_code}")
        return response
    
    def _post(self, url, data):
        response = requests.post(url, headers=self.headers(), json=data)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
        return response