import requests
import warnings
from .auth import Authenticator
from .utils import *

# Ensure all instances of this specific warning are always shown
warnings.simplefilter('always', UserWarning)

class User:
    def __init__(self, developer_token, base_api_url = production_base_url):
        self.base_api_url = base_api_url
        self.authenticator = Authenticator(developer_token, base_api_url)
        self.api_token, self.refresh_token = self.authenticator.get_api_and_refresh_token()
        self._filters = None
        self._field_description = None

    @property
    def filters(self):
        if self._filters is None:
            self._filters = self.get_filters()
        return self._filters

    @property
    def field_description(self):
        if self._field_description is None:
            self._field_description = self.get_field_description()
        return self._field_description

    def refresh_api_token(self):
        """
        Refreshes the API token using the Authenticator's refresh_api_token method.
        Also updates the User's api_token with the new token.
        """
        try:
            self.authenticator.refresh_api_token()  # This updates the authenticator's api_token
            self.api_token = self.authenticator.api_token  # Update the User's api_token
            print("API Token refreshed successfully.")
        except Exception as e:
            print(f"Error refreshing API token: {e}")

    def get_filters_template(self):
        field_description = self.field_description
        return field_description.get('filters_template', None)

    def get_input_lca_fields_description(self):
        field_description = self.field_description
        return field_description.get('lca_fields', {}).get('input_fields', None)

    def get_output_lca_fields_description(self):
        field_description = self.field_description
        return field_description.get('lca_fields', {}).get('output_fields', None)

    def get_impact_lca_fields_description(self):
        field_description = self.field_description
        return field_description.get('lca_fields', {}).get('impact_fields', None)

    def get_material_facts_fields_description(self):
        field_description = self.field_description
        return field_description.get('material_facts', None)

    def get_physical_properties_fields_description(self):
        field_description = self.field_description
        return field_description['physical_properties']

    def get_technical_parameters_fields_description(self):
        field_description = self.field_description
        return field_description['technical_parameters']

    def get_product_fields_description(self):
        field_description = self.field_description
        return field_description['product_fields']

    def get_unit_categories(self):
        return unit_categories

    def get_primary_units(self):
        return primary_units

    def get_mf_num_fields(self):
        return mf_num_fields

    def get_mf_perc_fields(self):
        return mf_perc_fields

    def get_physical_properties_fields(self):
        return physical_properties_fields

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

    def get_field_description(self):
        return field_description

    def get_open_filters(self):
        filters = self.filters
        open_filters = {i: filters[i] for i in filters.keys() if
                        i in ['product_type', 'material_types', 'company', 'manufacturing_country', 'continent']}
        return open_filters

    def get_filters_mapping(self):
        filters = self.filters  # Retrieve the filters
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

        return filter_mappings

    def get_products_page(self, page=1, openapi=False, **filters):

        base_url = f'{self.base_api_url}developer/api/get_products'  # Use 'get_products' endpoint if needed
        if openapi:
            base_url = f'{self.base_api_url}developer/api/get_products_open_api'

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
            if e.response.status_code == 401:  # Unauthorized
                raise Exception(
                    "Unauthorized access. Consider using the free but limited version by including the parameter openapi=True in your request.")
            else:
                raise Exception(f"Failed call to get_products: {e}")

    def get_products(self, openapi=False, **filters):
        items_per_page = 200
        all_products = []  # This will store all products across pages
        page = 1  # Start from the first page

        if not filters:
            warnings.warn(
                "You are retrieving all products. No filters were applied. This will take a while..",
                UserWarning  # This is the default, but specifying it makes the intention clear
            )

        response = self.get_products_page(page, openapi=openapi, **filters)

        total_products = response['TotalProducts']
        # integer division trick to get one more page if there is a remainder
        total_pages = (total_products + items_per_page - 1) // items_per_page
        if total_pages > 1:
            print(f'Total products {total_products}.')

        while page <= total_pages:

            all_products.extend(response['results'])  # Append the current page's products

            if total_pages>1:
                print(f'Finished fetching page {page} out of {total_pages}')

            page += 1  # Go to the next page

            if not response['next']:
                break  # If no response, exit the loop
            else:
                response = self.get_products_page(page, openapi=openapi, **filters)

        return all_products

    # def get_products_open_api(self, page=1, **filters):
    #
    #     base_url = f'{self.base_api_url}developer/api/get_products_open_api'
    #
    #     # Prepare query components based on filters
    #     query_components = []
    #     for key, value in filters.items():
    #         if key == 'product_url' and isinstance(value, list):  # Special handling for 'product_url' as a list
    #             query_components.extend([f'{key}={url}' for url in value])
    #         else:
    #             query_components.append(f'{key}={value}')
    #
    #     # Construct the final URL with all filters applied
    #     filter_query = '&'.join(query_components)
    #     url = f"{base_url}?page={page}&{filter_query}" if filters else f"{base_url}?page={page}"
    #
    #     headers = {
    #         'Authorization': f'Bearer {self.api_token}',
    #         'Content-Type': 'application/json',
    #     }
    #
    #     try:
    #         response = requests.get(url, headers=headers)
    #         response.raise_for_status()
    #         products = response.json()
    #         return products
    #     except requests.RequestException as e:
    #         raise Exception(f"Failed call to get_products_open_api: {e}")







