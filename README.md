# 2050 Materials API Client

The 2050 Materials API Client is a Python library designed to simplify access to the 2050-materials API, providing an easy-to-use interface for fetching environmental data about construction materials. This library handles authentication, token management, and API requests, offering a straightforward way to integrate 2050-materials data into your Python applications.

## Installation

Since this repository is private, you'll need to install the library locally. To do this, follow these steps:

### Clone the Repository

First, clone the repository to your local machine. You'll need access to the repository to do this. If you haven't configured SSH keys for GitHub, you might be prompted to enter your username and password.

```
git clone https://github.com/2050-Materials/materials_2050_api_client.git
cd materials_2050_api_client
```

### Install library
Navigate to the root directory of the cloned repository where the setup.py file is located, then run:
```
pip install .
```

## Class: API_Client

The `API_Client` class serves as the main interface to the 2050-materials API.

### Initialization

To use the `API_Client`, initialize it with the base API URL and your developer token:

```
from materials_2050_api_client import API_Client

client = API_Client(base_api_url="https://app.2050-materials.com/", developer_token="your_developer_token_here")
```


### Methods

#### `get_products`

Fetches a list of products from the API. Accepts a page parameter for pagination.

```
products = client.get_products(page=1)
```

#### `get_products_open_api`
Fetches a list of products using the open API endpoint. Accepts a page parameter for pagination.

```
products_open_api = client.get_products_open_api(page=1)
```

#### `get_filters`
Retrieves all available filters from the API.

```
filters = client.get_filters()
```

#### `get_open_filters`
Fetches a subset of filters, specifically for 'product_type', 'material_types', 'company', 'manufacturing_country', and 'continent'.

```
open_filters = client.get_open_filters()
```

#### `get_product_types`
Extracts and returns a dictionary of product types from the filters.

```
product_types = client.get_product_types()

```

#### `get_material_types`
Extracts and returns a dictionary of product types from the filters.

```
material_types = client.get_product_types()

```

#### `get_filtered_data_open_api`
Filters the get_products_open_api data based on provided filters. This method accepts a page parameter for pagination and arbitrary keyword arguments `(**filters)` for filtering.
```
filtered_products = client.get_filtered_data_open_api(page=1, name="Product Name", product_type=71)
```