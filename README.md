# AECData

AECData is a Python library designed to facilitate seamless interaction with the 2050-materials platform API (see documentation [here](https://docs.2050-materials.com/getting-started-with-2050-materials/using-the-api)). By abstracting the complexities of authentication and data retrieval, this library empowers developers to focus on analyzing and utilizing environmental data about construction materials effectively.

## Key Features

- **Simplified Authentication**: Manages API tokens automatically, streamlining the authentication process.
- **Flexible Data Retrieval**: Supports fetching data using customizable filters to meet diverse analysis needs.
- **Data Manipulation and Analysis**: Offers tools for transforming, scaling, and statistically analyzing the data.
- **Visualization Support**: Provides functionalities for visualizing data distributions and product contributions.

## Introduction and Outline

The library is structured to guide the user through a seamless process from authentication to data analysis:

1. **Initialization**: Start by creating a `User` instance with your developer token ([see how to get a token here](https://docs.2050-materials.com/getting-started-with-2050-materials/using-the-api#get-a-developer-token)). This instance will manage your authentication and serve as your gateway to fetching data.
   
2. **Fetching Data**: Utilize the `User` class to retrieve data from the API. You can apply various filters to narrow down the data according to your needs.
   
3. **Data Manipulation**: Once you have fetched the data, you can construct a `ProductData` object. This object allows for extensive manipulation and transformation of the data, enabling you to prepare it for analysis or visualization in a format that suits your requirements.
   
4. **Statistical Analysis and Visualization**: For advanced data analysis, the `ProductStatistics` class extends `ProductData` to provide statistical insights. It enables outlier removal, distribution analysis, and more, coupled with visualization capabilities to help interpret the data effectively.


## Installation

The AECData library can be installed directly from PyPI to ensure you have the latest version. Use the following pip command:

```
pip install aecdata
```

For source code, issues, and contributions, the project is hosted on GitHub at: 

```
git clone https://github.com/2050-Materials/aecdata.git
```

## Usage Documentation

## `Authenticator` Class

The `Authenticator` class is designed to handle the authentication process for accessing the API. It is used internally to manage both API tokens and to ensure continued access.

### Initialization

-   `__init__(self, developer_token, base_api_url)`: Initializes the `Authenticator` instance.
    -   `developer_token`: The developer token provided for API access.
    -   `base_api_url`: The base URL for the API endpoints.

### Methods

-   `get_token(self)`: Retrieves the API token using the developer token. This method is ideal for operations that only require a single API token without the need for a refresh token.
-   `get_api_and_refresh_token(self)`: Retrieves both the API token and a refresh token. This is useful for long-running applications that may need to refresh the API token.
-   `refresh_api_token(self)`: Refreshes the API token using the refresh token. This method should be used when the API token has expired and a new one is needed without re-authenticating using the developer token.

## `User` Class

The `User` class provides a high-level interface for interacting with the 2050-materials API, handling authentication, and performing API requests to fetch and manage data related to construction materials.

### Attributes

- `base_api_url`: The base URL for the API endpoints. It defaults to the 2050-materials API but can be customized if necessary.
- `authenticator`: An instance of the `Authenticator` class responsible for managing authentication tokens.
- `api_token`: The current API token obtained through the `Authenticator`. It's used for authenticating API requests.
- `refresh_token`: A token that can be used to refresh the `api_token` when it expires, ensuring continuous access without re-authentication.
- `_filters`: A private attribute that caches filters available for querying the API.
- `_field_description`: A private attribute that stores detailed descriptions of available fields for products, used for filtering and data retrieval.

### Properties

- `filters`: A property that lazily fetches and returns available filters for querying the API, caching the result.
- `field_description`: A property that lazily fetches and returns detailed descriptions of available product fields, caching the result.

### Methods

#### Initialization

- `__init__(self, developer_token, base_api_url="https://app.2050-materials.com/")`: Initializes a new `User` instance with a given developer token and optionally a custom API base URL.

#### Public Methods

- `refresh_api_token(self)`: Utilizes the `Authenticator` to refresh the API token. Updates the `User` instance's `api_token` with the new value.
- `get_filters(self)`: Fetches and caches filter options available for querying products from the API.
- `get_field_description(self)`: Fetches and caches the descriptions of available fields for products, aiding in data manipulation and query customization.
- `get_filters_template(self)`: Retrieves a template of filters available for product queries.
- `get_input_lca_fields_description(self)`: Gets descriptions for input fields related to Life Cycle Assessment (LCA) data.
- `get_output_lca_fields_description(self)`: Retrieves descriptions for output fields of LCA data.
- `get_impact_lca_fields_description(self)`: Fetches descriptions of impact fields within LCA data.
- `get_material_facts_fields_description(self)`: Provides descriptions of material facts fields, aiding in understanding data structure.
- `get_physical_properties_fields_description(self)`: Details descriptions of fields related to the physical properties of materials.
- `get_technical_parameters_fields_description(self)`: Retrieves descriptions of technical parameters fields.
- `get_product_fields_description(self)`: Gets descriptions of product-related fields.
- `get_unit_categories(self)`: Returns the categories of units used within the data.
- `get_primary_units(self)`: Provides a list of primary units for data measurement.
- `get_mf_num_fields(self)`: Lists numerical fields related to material facts.
- `get_mf_perc_fields(self)`: Lists percentage fields within material facts data.
- `get_physical_properties_fields(self)`: Returns a list of fields detailing the physical properties of materials.
- `get_filters_mapping(self)`: Creates and returns a mapping of filter options to simplify query construction.
- `get_products_page(self, page=1, openapi=False, **filters)`: Fetches a specific page of product data, optionally applying filters.
- `get_products(self, openapi=False, **filters)`: Fetches all products, optionally applying filters, and handles pagination automatically. Use `openapi=False` to use the free Open API.

## Usage Example

```
# Initialize the API user with your developer token
user = User(developer_token = developer_token)

# Lazy calculation of filters
user.filters 

# Refresh the API token
user.refresh_api_token()

# Fetch all filter mappings
all_mappings = user.get_filters_mapping()

# Fetch products whose material type family is Ceramic
filters = {
    'material_type_family': all_mappings['material_types_family']['Ceramic'],
}
filtered_products = user.get_products(openapi=False, **filters) # Set openapi=True for the free version
```

## `ProductData` Class

The `ProductData` class is designed to manage and manipulate the data fetched from the 2050-materials API. It offers functionalities for converting data between different formats, scaling product data based on units and amounts, and generating plots for product contributions.

### Attributes

- `_data`: A private attribute that holds the original data passed to the instance, either as a list of dictionaries or a pandas DataFrame.
- `_dataframe`: A private attribute that stores the data in a pandas DataFrame format, allowing for easy manipulation and analysis.

### Initialization

- `__init__(self, data)`: Accepts data either as a list of product dictionaries or a pandas DataFrame and initializes the `ProductData` instance. The constructor ensures that `_data` and `_dataframe` are synchronized.

### Properties

- `data`: Provides access to the raw data. Setting this property updates both the `_data` attribute and the corresponding DataFrame in `_dataframe`.
- `dataframe`: Allows access to the data in a pandas DataFrame format. Setting this property updates `_dataframe` and the raw data in `_data`.

### Methods

#### Data Conversion

- `to_dataframe(self, data)`: Converts the list of dictionaries (or the raw data) into a pandas DataFrame with ordered columns, facilitating data analysis.
- `to_csv(self, file_path)`: Exports the data to a CSV file, saving it to the specified path.
- `to_json(self, file_path)`: Exports the data to a JSON file at the given path.
- `to_json_string(self)`: Converts the data into a JSON-formatted string, useful for serialization or sending data over a network.

#### Unit Conversion and Scaling

- `get_available_units(self)`: Extracts and returns a set of available units for scaling based on the data's 'material_facts.scaling_factors' entries.
- `convert_df_to_unit(self, df, unit='declared_unit', amount=1)`: Scales the DataFrame's numerical fields to the specified unit and amount.
- `scale_products_by_unit_and_amount(self, products_info)`: Scales product data based on a dictionary mapping product UUIDs to units and amounts, facilitating comparisons and aggregations.

#### Plotting and Visualization

- `plot_product_contributions(self, products_info, field_name)`: Generates a pie chart illustrating the contributions of each product to the specified field (e.g., CO2 emissions).

#### Data Transformation for EPDx Format

- `to_epdx(self)`: Converts the data into the EPDx format, suitable for environmental product declarations.


## Usage Example

```
# Create ProductData object from API data
product_data = ProductData(filtered_products)

# Access the dataframe
df = product_data.dataframe

# Create a custom project with specified products, units and amounts
products_info = {
    '6aa6d32c-f8cf-11ed-9c01-0242ac120004' : {'amount': 0.2}, 
    'c0800dc0-f8cc-11ed-9c01-0242ac120004' : {'amount': 0.30}, 
    '6ab16fb2-f8cf-11ed-9c01-0242ac120004' : {'unit':'m2'},
    '6aab7152-f8cf-11ed-9c01-0242ac120004' : {'unit':'m2', 'amount': 1},
}
scale_df = product_data.scale_products_by_unit_and_amount(products_info)

# Vizualise the contributions from each product for a specific LCA field
product_data.plot_product_contributions(products_info, 'material_facts.manufacturing')

# Convert to EPDx format
epdx_products = product_data.to_epdx()
```

## `ProductStatistics` Class

The `ProductStatistics` class extends the `ProductData` class, offering advanced statistical analysis capabilities for the product data obtained from the 2050-materials API. It enables users to perform detailed statistical analyses, including filtering based on various criteria, removing outliers, and plotting distributions.

### Attributes

Inherits all attributes from the `ProductData` class.

### Initialization

- `__init__(self, data, unit='declared_unit')`: Initializes a new instance of the `ProductStatistics` class. It accepts either a list of products, a pandas DataFrame, or an instance of `ProductData`. The `unit` parameter specifies the measurement unit for statistical analysis.

### Methods

#### Statistical Analysis

- `get_lca_fields(self, fields='all', modules='all')`: Returns a DataFrame filtered to include only the specified LCA fields and modules, allowing for targeted analysis.
- `get_available_groupings(self)`: Identifies possible groupings for the data based on its characteristics, aiding in segmented analysis.
- `get_available_fields_dict(self)`: Lists all available fields within the data that can be used for statistical analysis.
- `get_available_fields(self)`: Returns a list of all fields available for analysis, consolidating the information from `get_available_fields_dict`.
- `filter_df_by_dict(self, df, filter_dict)`: Applies a dictionary of filters to the DataFrame, allowing for refined data selection.
- `get_group_by_combinations(self, df, group_by, min_count)`: Determines valid combinations for grouping the data, based on specified criteria and a minimum count threshold for inclusion.
- `get_group_by_dict(self, df, group_by)`: Generates a dictionary representing potential groupings for the data, based on the specified group_by criteria.
- `get_statistics(self, group_by=None, fields=None, statistical_metrics=None, include_estimated_values=False, remove_outliers=True, method='IQR', sqrt_tranf=True, min_count=4)`: Computes statistical metrics for the specified fields and groupings, offering options to include estimated values, remove outliers, and adjust for small sample sizes.

#### Data Filtering and Transformation

- `remove_outliers_from_df(self, filtered_df, field, method, sqrt_tranf)`: Removes outliers from the DataFrame based on the specified field and method, optionally applying a square root transformation for variance stabilization.
- `filter_dataframe_based_on_field(self, field, filters=None, include_estimated_values=False, remove_outliers=True, method='IQR', sqrt_tranf=True)`: Filters the DataFrame based on specified criteria, including the treatment of estimated values and outliers.

#### Plotting and Visualization

- `plot_histogram(self, df, field)`: Generates a histogram for the specified field, visualizing the distribution of values.
- `get_field_distribution(self, field, filters=None, include_estimated_values=False, remove_outliers=True, method='IQR', sqrt_tranf=True)`: Filters the DataFrame and plots the distribution of the specified field, offering insights into the data's structure.
- `plot_distribution_boxplot(self, df, field, group_by_field)`: Creates a boxplot for the specified field, grouped by another field, highlighting the variance and distribution within the data.
- `get_field_distribution_boxplot(self, field, group_by_field, filters=None, include_estimated_values=False, remove_outliers=True, method='IQR', sqrt_tranf=True)`: Filters the DataFrame and generates a boxplot for the specified field, providing a visual representation of statistical distributions.

## Usage Example

```
# Create ProductStatistics (extension of ProductData)
stats_obj = ProductStatistics(product_data.dataframe, unit='m2')

# Choose fields to group by
group_by = [
    'country',
    'manufacturing_continent',
]

# Get all available fields
all_available_fields  = stats_obj.get_available_fields()

# Calculate statistics dataframe
stat_df = stats_obj.get_statistics(group_by=group_by, fields=all_available_fields, statistical_metrics=['count', 'mean', 'median'], include_estimated_values=False, remove_outliers=True, method='IQR', sqrt_tranf=True, min_count=3)

# Apply further filters and get field distribution
filters = {
    'material_type':'Ceramic',
}
stats_obj.get_field_distribution(field='material_facts.manufacturing', filters=filters, include_estimated_values=True, remove_outliers=False, method='IQR', sqrt_tranf=True)

# Get field distribution boxplot for all product types
stats_obj.get_field_distribution_boxplot(field='material_facts.manufacturing', group_by_field='product_type', filters=None, include_estimated_values=True, remove_outliers=True, method='IQR', sqrt_tranf=True)
```

