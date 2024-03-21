import requests
from .auth import Authenticator

from .auth import Authenticator
from .utils import *

class API_Client:
    def __init__(self, developer_token, base_api_url = "https://app.2050-materials.com/"):
        self.base_api_url = base_api_url
        self.authenticator = Authenticator(developer_token, base_api_url)
        self.api_token, self.refresh_token = self.authenticator.get_api_and_refresh_token()

    def refresh_api_token(self):
        """
        Refreshes the API token using the Authenticator's refresh_api_token method.
        Also updates the API_Client's api_token with the new token.
        """
        try:
            self.authenticator.refresh_api_token()  # This updates the authenticator's api_token
            self.api_token = self.authenticator.api_token  # Update the API_Client's api_token
            print("API Token refreshed successfully.")
        except Exception as e:
            print(f"Error refreshing API token: {e}")

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

    def get_filters_mapping(self):
        filters = self.get_filters()  # Retrieve the filters
        filter_mappings = {}  # Initialize the dictionary to hold all mappings

        # Iterate over each filter category in the filters
        for filter_key, filter_value in filters.items():
            if 'filter_options' in filter_value:
                # If filter_options is present, create a mapping for this category
                category_mapping = {}
                for item in filter_value['filter_options']:
                    if 'name' in item:
                        category_mapping[item['name']] = item['id']
                    elif 'performance' in item:
                        category_mapping[item['performance']] = item['id']
                    elif 'key' in item:
                        category_mapping[item['option']] = item['key']
                # Assign the category mapping to the corresponding filter key
                filter_mappings[filter_key] = category_mapping
            else:
                # Optionally, handle the absence of filter_options in any category if needed
                pass  # For now, we simply pass, but you could raise an error or log a warning

        return filter_mappings

    def get_filters_template(self):
        return parameters_description

    def get_filtered_data_page(self, page=1, **filters):

        base_url = f'{self.base_api_url}developer/api/get_products'  # Use 'get_products' endpoint if needed

        # Prepare query components based on filters
        query_components = []
        for key, value in filters.items():
            if isinstance(value, list) or isinstance(value, set):
                for subvalue in value:
                    query_components.append(f'{key}={subvalue}')
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
            raise Exception(f"Failed call to get_filtered_data: {e}")

    def get_filtered_data(self, **filters):
        items_per_page = 200
        all_products = []  # This will store all products across pages
        page = 1  # Start from the first page

        response = self.get_filtered_data_page(page, **filters)

        total_products = response['TotalProducts']
        # integer division trick to get one more page if there is a remainder
        total_pages = (total_products + items_per_page - 1) // items_per_page

        while page <= total_pages:

            all_products.extend(response['results'])  # Append the current page's products

            if total_pages>1:
                print(f'Total products {total_products}. Finished fetching page {page} out of {total_pages}')

            page += 1  # Go to the next page

            if not response['next']:
                break  # If no response, exit the loop
            else:
                response = self.get_filtered_data_page(page, **filters)

        return all_products

    def get_filtered_data_open_api(self, page=1, **filters):

        base_url = f'{self.base_api_url}developer/api/get_products_open_api'

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







