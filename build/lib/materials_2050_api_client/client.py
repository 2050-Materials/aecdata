import requests
from .auth import Authenticator

class API_Client:
    def __init__(self, base_url):
        self.base_url = base_url
        self.auth = Authenticator()

    def get_products(self):
        # New method specifically for getting products
        get_products_open_api_url = f'{self.base_api_url}developer/api/get_products_open_api'
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.get(get_products_open_api_url, headers=headers)
            response.raise_for_status()
            products = response.json()
            return products
        except requests.RequestException as e:
            raise Exception(f"Failed call to get_products API: {e}")

