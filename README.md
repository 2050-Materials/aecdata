# 2050 Materials API Client

The 2050 Materials API Client is a Python library designed to simplify access to the 2050-materials API, providing an easy-to-use interface for fetching environmental data about construction materials. This library handles authentication, token management, and API requests, offering a straightforward way to integrate 2050-materials data into your Python applications.

## Installation

Since this repository is private, you'll need to install the library locally. To do this, follow these steps:

### Clone the Repository

First, clone the repository to your local machine. You'll need access to the repository to do this. If you haven't configured SSH keys for GitHub, you might be prompted to enter your username and password.

```
git clone https://github.com/2050-Materials/aecdata.git
cd aecdata
```

### Install library
Navigate to the root directory of the cloned repository where the setup.py file is located, then run:
```
pip install .
```
## API Authentication and Client Usage Documentation

## `Authenticator` Class (`auth.py`)

The `Authenticator` class is designed to handle the authentication process for accessing the API. It manages both API tokens and refresh tokens to ensure continued access.

### Initialization

-   `__init__(self, developer_token, base_api_url)`: Initializes the `Authenticator` instance.
    -   `developer_token`: The developer token provided for API access.
    -   `base_api_url`: The base URL for the API endpoints.

### Methods

-   `get_token(self)`: Retrieves the API token using the developer token. This method is ideal for operations that only require a single API token without the need for a refresh token.
-   `get_api_and_refresh_token(self)`: Retrieves both the API token and a refresh token. This is useful for long-running applications that may need to refresh the API token.
-   `refresh_api_token(self)`: Refreshes the API token using the refresh token. This method should be used when the API token has expired and a new one is needed without re-authenticating using the developer token.

## `User` Class (`client.py`)

The `User` class provides methods to interact with the API, utilizing the `Authenticator` for handling authentication.

### Initialization

-   `__init__(self, developer_token, base_api_url = "https://app.2050-materials.com/")`: Creates an `User` instance.
    -   `developer_token`: The developer token provided for API access.
    -   `base_api_url`: The base URL for the API endpoints. Defaults to the 2050-materials API.

### Methods

-   `refresh_api_token(self)`: Refreshes the API token. Utilizes the `Authenticator`'s `refresh_api_token` method and updates the client's API token.
-   `get_products(self, page=1)`: Fetches products from the API. Supports pagination.
-   `get_products_open_api(self, page=1)`: Fetches products from an open API endpoint, if available. Supports pagination.
-   `get_filters(self)`: Retrieves filter options for querying products.
-   `get_open_filters(self)`: Filters and returns a subset of the available filters based on predefined criteria.
-   `get_filters_mapping(self)`: Creates and returns a mapping of filter options for easier use in queries.
-   `get_filtered_data_page(self, page=1, **filters)`: Fetches a specific page of filtered product data.
-   `get_filtered_data(self, **filters)`: Fetches all pages of filtered product data based on the provided filters.
-   `get_filtered_data_open_api(self, page=1, **filters)`: Fetches a specific page of filtered product data from an open API endpoint, supporting custom filters.

## Usage Example

```
# Initialize the API client with your developer token
client = User(developer_token="your_developer_token_here")

# Refresh the API token
client.refresh_api_token()

# Fetch and print the first page of products
products = client.get_products(page=1)
print(products)

# Get and apply filters for product queries
filters = client.get_filters_mapping()
filtered_data = client.get_filtered_data(product_type=filters['product_type']['Concrete'])
print(filtered_data)
```

This documentation provides a comprehensive overview of the classes and methods for authenticating and interacting with the API. Developers can use this guide to understand how to implement these classes in their own applications for efficient API usage.
