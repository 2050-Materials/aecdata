import requests
from .utils import *

class Authenticator:
    def __init__(self, developer_token, base_api_url = production_base_url):
        self.base_api_url = base_api_url
        self.developer_token = developer_token
        self.api_token = None
        self.refresh_token = None

    def get_token(self):
        base_token_url = f'{self.base_api_url}developer/api/token/getapitoken/'
        get_token_headers = {'Authorization': f'Bearer {self.developer_token}'}

        try:
            response = requests.get(base_token_url, headers=get_token_headers)
            response.raise_for_status()
            token_data = response.json()
            self.api_token = token_data['api_token']
            return self.api_token
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch API token: {e}")

    def get_api_and_refresh_token(self):
        base_token_url = f'{self.base_api_url}developer/api/token/getapitoken/'
        get_token_headers = {'Authorization': f'Bearer {self.developer_token}'}

        try:
            response = requests.get(base_token_url, headers=get_token_headers)
            response.raise_for_status()
            token_data = response.json()
            self.api_token = token_data['api_token']
            self.refresh_token = token_data['refresh_token']
            return self.api_token, self.refresh_token
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch API token: {e}")

    def refresh_api_token(self):
        # Ensure there's a refresh token available
        if not self.refresh_token:
            raise Exception("No refresh token available. Please use get_api_and_refresh_token() first.")

        refresh_url = f'{self.base_api_url}developer/api/token/refresh/'
        refresh_headers = {
            'Authorization': f'Bearer {self.refresh_token}'
        }
        refresh_data = {
            'refresh': self.refresh_token
        }

        try:
            refresh_response = requests.post(refresh_url, headers=refresh_headers, data=refresh_data)
            refresh_response.raise_for_status()  # This will raise an exception for HTTP errors
            refresh_data = refresh_response.json()
            self.api_token = refresh_data['api_token']  # Update the api_token with the new one
        except requests.RequestException as e:
            raise Exception(f"Failed to refresh API token: {e}")

