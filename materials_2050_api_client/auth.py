import requests

class Authenticator:
    def __init__(self, base_api_url, developer_token):
        self.base_api_url = base_api_url
        self.developer_token = developer_token

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


    def refresh_token(self):
        # Implement token refresh
        pass
