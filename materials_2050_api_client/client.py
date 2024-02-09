import requests
from .auth import Authenticator

from .auth import Authenticator

class API_Client:
    def __init__(self, base_api_url, developer_token):
        self.base_api_url = base_api_url
        self.authenticator = Authenticator(base_api_url, developer_token)
        self.api_token = self.authenticator.get_token()  # Obtain the API token upon instantiation

    def get_products(self, page=1):
        get_products_url = f'{self.base_api_url}developer/api/get_products?page={page}'
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.get(get_products_url, headers=headers)
            response.raise_for_status()
            products = response.json()
            return products
        except requests.RequestException as e:
            raise Exception(f"Failed call to get_products API: {e}")

    def get_products_open_api(self, page=1):
        get_products_open_api_url = f'{self.base_api_url}developer/api/get_products_open_api?page={page}'
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
            raise Exception(f"Failed call to get_products_open_api API: {e}")

    def get_filters(self):
        get_filters_url = f'{self.base_api_url}developer/api/get_product_filters'
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.get(get_filters_url, headers=headers)
            response.raise_for_status()
            filters = response.json()
            return filters
        except requests.RequestException as e:
            raise Exception(f"Failed call to get_filters API: {e}")

    def get_open_filters(self):
        filters = self.get_filters()  # Utilize the get_filters method to fetch all filters
        open_filters = {i: filters[i] for i in filters.keys() if
                        i in ['product_type', 'material_types', 'company', 'manufacturing_country', 'continent']}
        return open_filters

    def get_product_types(self):
        filters = self.get_filters()  # Assume this method already fetches the full filters dictionary
        product_types = {}
        if 'product_type' in filters:
            for item in filters['product_type']['filter_options']:
                product_types[item['name']] = item['id']
        else:
            raise Exception("Product type filters not found")
        return product_types

    def get_material_types(self):
        filters = self.get_filters()  # Assume this method already fetches the full filters dictionary
        material_types = {}
        if 'material_types' in filters:
            for item in filters['material_types']['filter_options']:
                material_types[item['name']] = item['id']
        else:
            raise Exception("Material type filters not found")
        return material_types

    def get_filtered_data_open_api(self, page=1, **filters):
        # Choose the correct base URL based on whether filters are provided or not
        base_url = f'{self.base_api_url}developer/api/get_products_open_api'  # Use 'get_products' endpoint if needed

        # Prepare query components based on filters
        query_components = []
        for key, value in filters.items():
            if key == 'product_url' and isinstance(value, list):  # Special handling for 'product_url' as a list
                query_components.extend([f'{key}={url}' for url in value])
            else:
                query_components.append(f'{key}={value}')

        # Construct the final URL with all filters applied
        filter_query = '&'.join(query_components)
        url = f"{base_url}?page={page}&{filter_query}" if filters else f"{base_url}?page={page}"

        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            products = response.json()
            return products
        except requests.RequestException as e:
            raise Exception(f"Failed call to get_filtered_data_open_api: {e}")





