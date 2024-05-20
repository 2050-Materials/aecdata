import pandas as pd
import numpy as np
import json
import warnings
from itertools import product
from datetime import datetime
from .utils import *

# Ensure all instances of this specific warning are always shown
warnings.simplefilter('always', UserWarning)

class ProductData:
    def __init__(self, data):
        self._data = None
        self._dataframe = None

        if isinstance(data, list):
            self.data = data  # This will trigger the setter to update both _data and _dataframe
        elif isinstance(data, pd.DataFrame):
            self.dataframe = data  # This will trigger the setter to update both _data and _dataframe
        else:
            raise ValueError("Unsupported data type. Please provide a list of products or a pandas DataFrame.")

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        def add_scaling_factor(product):
            # Ensure 'material_facts' exists and proceed if it does
            if 'material_facts' in product:
                # Initialize 'material_facts' if not already present
                if 'scaling_factors' not in product['material_facts']:
                    declared_unit = product['material_facts'].get('declared_unit', None)
                    if declared_unit:
                        product['material_facts']['scaling_factors'] = {
                            declared_unit: {'value': 1, 'estimated': False}
                        }
            return product

        # Process each product to potentially add missing scaling factors
        products = [add_scaling_factor(product) for product in value]

        self._data = products
        self._dataframe = self.to_dataframe(products).replace({np.nan: None})

    @property
    def dataframe(self):
        return self._dataframe

    @dataframe.setter
    def dataframe(self, value):
        self._dataframe = value.replace({np.nan: None})
        self._data = self.df_to_list(value)

    def df_to_list(self, df):

        df = df.replace({np.nan: None})

        def remove_nulls(d):
            """Recursively remove dictionary keys with None values and empty dictionaries."""
            if not isinstance(d, dict):
                return d
            cleaned = {k: remove_nulls(v) for k, v in d.items() if v is not None}
            # Now, also check and remove any keys that map to empty dictionaries after cleaning
            return {k: v for k, v in cleaned.items() if v != {}}

        def remove_estimated_false_when_field_null(d):
            estimated_fields = [key for key in d if '_estimated' in key]
            for field in estimated_fields:
                if not d.get(field.split('_estimated')[0]) and field in d:
                    del d[field]
        def row_to_nested_dict(row, ignore_null=True):
            result = {}
            for col_name, value in row.items():
                parts = col_name.split('.')
                current_level = result
                for part in parts[:-1]:
                    if part not in current_level:
                        current_level[part] = {}
                    current_level = current_level[part]
                current_level[parts[-1]] = value

            if ignore_null:
                result = remove_nulls(result)
                remove_estimated_false_when_field_null(result)
            return result

        nested_data = [row_to_nested_dict(row) for index, row in df.iterrows()]
        return nested_data

    def to_dataframe(self, data):
        """
        Converts the data into a pandas DataFrame, ensuring that columns
        starting with 'material_facts' are placed at the end and sorted.

        :return: pandas DataFrame containing the data with ordered columns.
        """
        # Normalize the data to create an initial dataframe
        df = pd.json_normalize(data)

        # Separate columns starting with 'material_facts'
        material_facts_cols = [col for col in df.columns if col.startswith('material_facts')]
        other_cols = [col for col in df.columns if not col.startswith('material_facts')]

        # Sort the 'material_facts' columns
        sorted_material_facts_cols = sorted(material_facts_cols)

        # Combine the columns back together, with 'material_facts' columns at the end
        if 'unique_product_uuid_v2' in df.columns:
            ordered_columns = ['unique_product_uuid_v2'] + [col for col in other_cols if col!='unique_product_uuid_v2'] + sorted_material_facts_cols
            # Re-index the dataframe with the ordered columns
            return df[ordered_columns]
        else:
            return df

    def to_csv(self, file_path):
        """
        Converts the data into a CSV file.

        :param file_path: The path (including filename) where the CSV will be saved.
        """

        df = self.dataframe.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")

    def to_json(self, file_path):
        """
        Converts the data into a JSON file.

        :param file_path: The path (including filename) where the JSON file will be saved.
        """
        with open(file_path, 'w') as f:
            json.dump(self.data, f)
        print(f"Data saved to {file_path}")

    def to_json_string(self):
        """
        Converts the data into a JSON string.

        :return: String containing the JSON representation of the data.
        """
        return json.dumps(self.data)

    def get_available_units(self):
        """
        Extracts and returns a set of available units from the DataFrame based on the
        'material_facts.scaling_factors' columns.

        :return: A set of available units.
        """
        scaling_factor_columns = {col for col in self.dataframe.columns if 'material_facts.scaling_factors.' in col}
        # Extract available units by splitting the column names and getting the penultimate part of the name
        available_units = {col.split('.')[-2] for col in scaling_factor_columns if '.value' in col}
        return available_units

    def convert_df_to_unit(self, df, unit='declared_unit', amount=1):
        # Extract available units
        available_units = self.get_available_units()

        # Check if the specified unit is available
        if unit != 'declared_unit' and unit not in available_units:
            print(f'Unit not available. Available units {available_units}')
            return None

        scalable_columns = []
        # Add lca fields
        for field in lca_fields:
            for module in lca_modules:
                scalable_columns.append(f'material_facts.{field}.{module}')

        # Add lca num fields
        for field in mf_num_fields:
            scalable_columns.append(f'material_facts.{field}')

        # Filter the list of all breakdown fields to those that exist in the dataframe
        columns_to_scale = [col for col in scalable_columns if col in df.columns]

        # Create new df that we will adjust
        scaled_df = df.copy()

        if unit != 'declared_unit':
            scaling_column = f'material_facts.scaling_factors.{unit}.value'

            # Ensure the scaling column exists
            if scaling_column in df.columns:
                scaled_df.loc[:, columns_to_scale] = amount*scaled_df.loc[:, columns_to_scale].div(df.loc[:, scaling_column], axis=0)
                return scaled_df
            else:
                print(f'Unit scaling column "{scaling_column}" not found in DataFrame. No scaling applied.')
                return None
        else:
            scaled_df.loc[:, columns_to_scale] = amount * scaled_df.loc[:, columns_to_scale]
            return scaled_df

    def scale_products_by_unit_and_amount(self, products_info):
        # Create an empty DataFrame to hold the results
        scaled_products_df = pd.DataFrame()

        # Iterate over the items in the products_info dictionary
        for uuid, info in products_info.items():
            # Extract the unit and amount for the product
            unit = info.get('unit', 'declared_unit')
            amount = info.get('amount', 1)

            # Find the row in the DataFrame for the current product UUID
            product_row = self.dataframe[self.dataframe['unique_product_uuid_v2'] == uuid]

            # If the product is found in the DataFrame
            if not product_row.empty:
                # Scale the DataFrame to the specified unit
                scaled_row = self.convert_df_to_unit(product_row, unit, amount)

                # scaled_row_squeezed = scaled_row.squeeze()
                # scaling_factor_name = f'material_facts.scaling_factors.{unit}.value'
                #
                # # Now scaled_row_squeezed is a Series, and you can check and access values directly
                # if scaling_factor_name not in scaled_row_squeezed or not scaled_row_squeezed[scaling_factor_name]:
                #     print(f"Unit {unit} for product {scaled_row_squeezed['unique_product_uuid_v2']} not available")

                # If the DataFrame was successfully scaled
                if scaled_row is not None:
                    # # Scale the row by the specified amount
                    # scaled_row = scaled_row.multiply(amount, axis=0)

                    # Append the scaled row to the results DataFrame
                    scaled_products_df = pd.concat([scaled_products_df, scaled_row], ignore_index=True)
                else:
                    print(f"Scaling to unit '{unit}' failed for product {uuid}.")
            else:
                print(f"Product UUID '{uuid}' not found in DataFrame.")

        return scaled_products_df.reset_index(drop=True)


    def get_product_contributions(self, products_info, field_name):
        # Use the existing method to scale the DataFrame
        scaled_df = self.scale_products_by_unit_and_amount(products_info)

        # Ensure the DataFrame is ready for operations
        scaled_df = scaled_df.infer_objects()

        # Check if the specified field and required columns are available
        required_columns = ['name', 'unique_product_uuid_v2', field_name]
        missing_columns = [col for col in required_columns if col not in scaled_df.columns]
        if missing_columns:
            print(f"Missing required fields: {', '.join(missing_columns)} in scaled DataFrame.")
            return None

        scaled_df = scaled_df.copy()
        # Create a new column combining 'name' and 'unique_product_uuid_v2' with a newline character
        scaled_df['label'] = scaled_df['name'] + '\n(' + scaled_df['unique_product_uuid_v2'] + ')'

        scaled_df.replace([np.inf, -np.inf], np.nan, inplace=True)

        # Aggregate the data by summing the specified field, grouped by the new 'label' attribute
        contributions = scaled_df.groupby('label')[field_name].sum()

        return contributions


    def to_epdx(self):
        def create_epdx_dict_from_row(row, modules_to_epdx, lca_field_to_epdx):
            # Initialize the dictionary to hold the EPDx structured data
            epdx_dict = {}

            # Iterate through the LCA fields to EPDx abbreviations mapping
            for lca_field, epdx_abbr in lca_field_to_epdx.items():
                # Skip the mapping if the EPDx abbreviation is None
                if epdx_abbr is None:
                    continue

                # Initialize the sub-dictionary for this LCA field
                epdx_dict[epdx_abbr] = {}

                # Iterate through the modules to EPDx abbreviations mapping
                for module, epdx_module_abbr in modules_to_epdx.items():
                    # Construct the column name based on the LCA field and module
                    column_name = f"material_facts.{lca_field}.{module}"

                    # Retrieve the value from the row using the column name
                    # If the column doesn't exist in the row, default to None
                    value = row.get(column_name, None)

                    # Map the value to the correct module abbreviation in the sub-dictionary
                    epdx_dict[epdx_abbr][epdx_module_abbr] = value

            return epdx_dict

        def convert_date_to_timestamp(date_str, date_format="%Y-%m-%d"):
            """
            Converts a date string to a Unix timestamp.

            Parameters:
            - date_str (str): The date string to convert.
            - date_format (str): The format of the date string.

            Returns:
            - float: Unix timestamp, or None if the input is invalid.
            """
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, date_format)
                    return int(date_obj.timestamp())
                except ValueError:
                    # Handle the case where date_str does not match date_format
                    return None
            return None

        def determine_standard(compliances):
            """
            Determines the 'standard' based on the presence of specific keywords
            in the 'compliances' list.

            Parameters:
            - compliances (list): A list of compliance strings.

            Returns:
            - str: 'EN15804A1', 'EN15804A2', or 'UNKNOWN' based on the contents of the list.
            """
            if compliances is None:
                return 'UNKNOWN'

            # Flatten the list to a string to make searching easier
            compliances_str = ' '.join(compliances)

            # Check for '15804' first
            if '15804' in compliances_str:
                # Next, check for 'A2' and 'A1'
                if 'A2' in compliances_str:
                    return 'EN15804A2'
                elif 'A1' in compliances_str:
                    return 'EN15804A1'

            # Default return if conditions are not met
            return 'UNKNOWN'

        def map_subtype_to_epdx(certificate_subtype):
            """
            Maps 'certificate_subtype' to the EPDx 'subtype' based on predefined mappings.

            Parameters:
            - certificate_subtype (str): The subtype from 'material_facts.certificate_subtype'.

            Returns:
            - str: The corresponding EPDx subtype or 'UNKNOWN' if no direct mapping exists.
            """
            return subtype_to_epdx.get(certificate_subtype, 'UNKNOWN')

        def generate_conversions(row):
            conversions = []

            for unit in unit_mapping_to_epdx.keys():
                estimated_key = f'material_facts.scaling_factors.{unit}.estimated'
                value_key = f'material_facts.scaling_factors.{unit}.value'

                # Check if the current row has the necessary keys for this unit
                if estimated_key in row and value_key in row and pd.notna(row[value_key]):
                    conversion_dict = {
                        'value': row[value_key],
                        'to': unit_mapping_to_epdx[unit],
                        'meta_data': {'estimated': row[estimated_key]}
                    }
                    conversions.append(conversion_dict)

            return conversions

        epdx_products_list = []

        # Get the current datetime as a Unix timestamp
        published_date_timestamp = int(datetime.now().timestamp())

        # Iterate through each row of the dataframe
        for index, row in self.dataframe.iterrows():
            epdx_product = initial_epdx.copy()

            # 2050 materials uuid
            epdx_product['id'] = row['unique_product_uuid_v2']

            # Product name
            epdx_product['name'] = row['name']

            # Map the unit using unit_mapping_to_epdx
            declared_unit = row.get('material_facts.declared_unit', None)  # Default to None if not found
            epdx_unit = unit_mapping_to_epdx.get(declared_unit, 'UNKNOWN')  # Default to 'UNKNOWN' if no mapping exists
            epdx_product['declared_unit'] = epdx_unit

            # Version of ilcd
            epdx_product['version'] = 'UNKNOWN'

            # Add the published_date
            epdx_product['published_date'] = published_date_timestamp

            # Convert valid_until date to Unix timestamp using the helper function
            valid_until_str = row.get('material_facts.data_source_link__certificate_expiry', '')
            epdx_product['valid_until'] = convert_date_to_timestamp(valid_until_str)

            # EPDx version
            epdx_product['format_version'] = '1.2.0'

            # Data source
            epdx_product['source'] = '2050 Materials Product Database'

            # life expectancy
            epdx_product['reference_service_life'] = row.get('life_expectancy', None)

            # Certificate Subtype
            certificate_subtype = row.get('material_facts.certificate_subtype', '')
            epdx_product['subtype'] = map_subtype_to_epdx(certificate_subtype)

            # Determine the 'standard' field based on 'material_facts.compliances'
            compliances = row.get('material_facts.compliances', None)
            epdx_product['standard'] = determine_standard(compliances)

            # location assign country
            epdx_product['location'] = row.get('country', None)

            # Generate conversions list
            conversions = generate_conversions(row.to_dict())
            epdx_product['conversions'] = conversions

            # Generate LCA results from the current row and merge them directly into epdx_product
            lca_results = create_epdx_dict_from_row(row.to_dict(), modules_to_epdx, lca_field_to_epdx)
            epdx_product.update(lca_results)

            # Append the fully constructed EPDx product dict to the list
            epdx_products_list.append(epdx_product)

        return epdx_products_list

    def filter_df_by_dict(self, df, filter_dict):
        # Start with the full DataFrame
        filtered_df = df
        # Apply each filter
        for key, value in filter_dict.items():
            if isinstance(value, list):
                # If value is a list, filter using 'isin' for direct matches
                # or check list columns for any item in the list values
                if df[key].apply(lambda x: isinstance(x, list)).any():
                    # Check if any item from the list in 'value' is in any list in the DataFrame
                    filtered_df = filtered_df[
                        filtered_df[key].apply(lambda x: any(item in x for item in value) if x is not None else False)]
                else:
                    # For normal columns, filter where the column's value is in 'value' list
                    filtered_df = filtered_df[filtered_df[key].isin(value)]
            else:
                # Check if the column contains lists
                if df[key].apply(lambda x: isinstance(x, list)).any():
                    # Use apply() to filter rows where the list contains the value
                    filtered_df = filtered_df[filtered_df[key].apply(lambda x: value in x if x is not None else False)]
                else:
                    # If the column does not contain lists, filter normally
                    filtered_df = filtered_df[filtered_df[key] == value]
        return filtered_df


class ProductStatistics(ProductData):
    def __init__(self, data, unit='declared_unit'):
        # Check if the input is a ProductData instance
        if isinstance(data, ProductData):
            # Directly use the DataFrame from the ProductData instance
            self.dataframe = data.dataframe.copy()  # Make a copy to ensure independence
            self.data = data.data  # Assuming you want to also copy the original data structure
        else:
            # Initialize the ProductData part of this instance
            super().__init__(data)

        # Check if the 'declared_unit' is being used
        if unit == 'declared_unit':
            warnings.warn(
                "Unit is set to 'declared_unit'. Be advised that LCA fields are not expressed in "
                "the same unit, which may affect the validity of applying statistical methods to these fields. "
                "We recommend you set a unit using the 'unit' parameter e.g. unit='kg'.",
                UserWarning  # This is the default, but specifying it makes the intention clear
            )

        # Extract available units
        available_units = self.get_available_units()

        # Check if the specified unit is available
        if unit != 'declared_unit' and unit not in available_units:
            raise ValueError(f'Unit "{unit}" not available. Available units: {available_units}')

        # Since the unit is valid, proceed to convert the DataFrame to the specified unit
        df = self.convert_df_to_unit(self.dataframe, unit)
        if unit in available_units:
            df['estimated'] = df[f'material_facts.scaling_factors.{unit}.estimated']
        elif unit == 'declared_unit':
            df['estimated'] = False

        # Drop rows where the 'estimated' column has None values
        df.dropna(subset=['estimated'], inplace=True)

        self.dataframe = df
        self.data = self.df_to_list(df)

        # Store the unit for potential future reference
        self.unit = unit

    def get_lca_fields(self, fields='all', modules='all'):
        """
        Returns LCA fields data based on the specified unit of measurement.

        :param unit: The unit of measurement to apply. If it's not 'declared_unit',
                     scale the values accordingly.
        :param fields: The list of fields to include. If 'all', use all LCA fields.
        :param modules: The list of modules to include. If 'all', use all modules.
        :return: a DataFrame with the LCA fields columns scaled by the unit if available.
        """
        if fields == 'all':
            fields = lca_fields  # lca_fields should be defined in your utils.py or within this class

        if modules == 'all':
            modules = lca_modules  # lca_modules should be defined in your utils.py or within this class

        all_lca_fields = []
        for field in fields:
            for module in modules:
                all_lca_fields.append(f'material_facts.{field}.{module}')

        scaled_df = self.dataframe

        # Filter the list of all breakdown fields to those that exist in the dataframe
        available_columns = [col for col in all_lca_fields if col in self.dataframe.columns]
        if scaled_df is not None:
            return scaled_df[available_columns]
        else:
            return scaled_df

    def get_available_groupings(self):
        df = self.dataframe
        group_by_dict = {
            'material_type': set(df['material_type']),
            'material_type_family': set(df['material_type_family']),
            'product_type': set(df['product_type']),
            'product_type_family': set(df['product_type_family']),
            'manufacturing_continent': set(df['manufacturing_continent']),
            'material_facts.data_source': set(df['material_facts.data_source']),
            'company': set(df['company']),
        }
        return group_by_dict

    def get_available_fields_dict(self):
        df = self.dataframe
        fields = {}
        all_lca_fields = []
        for field in lca_fields:
            for module in lca_modules:
                all_lca_fields.append(f'material_facts.{field}.{module}')

        all_mf_num_fields = [f'material_facts.{field}' for field in mf_num_fields]
        all_mf_perc_fields = [f'material_facts.{field}' for field in mf_perc_fields]
        all_physical_properties_fields = physical_properties_fields

        fields['material_fact_numerical_fields'] = [field for field in all_mf_num_fields if field in df.columns]
        fields['material_fact_percentage_fields'] = [field for field in all_mf_perc_fields if field in df.columns]
        fields['physical_properties_fields'] = [field for field in all_physical_properties_fields if field in df.columns]
        fields['lca_field_modules'] = [field for field in all_lca_fields if field in df.columns]
        return fields

    def get_available_fields(self):
        fields_dict = self.get_available_fields_dict()
        available_fields = []
        for category, field_list in fields_dict.items():
            available_fields += field_list
        return available_fields


    def get_group_by_combinations(self, df, group_by, min_count):
        # Filter out any None values upfront
        filtered_group_by = {k: v for k, v in group_by.items() if v is not None}

        # Convert sets to lists for itertools.product
        values_product = product(*[list(v) for v in filtered_group_by.values()])

        # Create a list of dictionaries for each combination
        combinations = [
            dict(zip(filtered_group_by.keys(), combination))
            for combination in values_product
        ]

        # Create a new list to hold dictionaries that meet the min_count condition
        valid_combinations = []

        for combination in combinations:
            # Filter the DataFrame based on the current combination
            filtered_df = self.filter_df_by_dict(df, combination)
            # Get the count of remaining products
            count = len(filtered_df)

            # Only add to the list if count >= min_count
            if count >= min_count:
                # Add the count to the dictionary
                combination['count'] = count
                valid_combinations.append(combination)

        return valid_combinations

    def get_group_by_dict(self, df, group_by):
        if group_by is None:
            # Create a set from all unique strings in lists for 'product_type'
            group_by_dict = {
                'product_type': set(df['product_type'])}
        else:
            group_by_dict = {}
            for group in group_by:
                # Use set.union to combine all unique elements if the column contains lists
                if df[group].apply(lambda x: isinstance(x, list)).any():
                    group_by_dict[group] = set().union(*df[group].apply(lambda x: x if isinstance(x, list) else [x]))
                else:
                    group_by_dict[group] = set(df[group])
        return group_by_dict

    def get_statistics(self, group_by=None, fields=None, statistical_metrics=None, include_estimated_values=False, remove_outliers=True, method='IQR', sqrt_tranf=True, min_count=4):
        def get_field_statistics(statistical_metrics, field, filtered_df, remove_outliers, method, sqrt_tranf, min_count):
            outlier_ids = []
            statistical_metrics = [f'{field}.{s}' for s in statistical_metrics]
            empty_field_statistics = {
                f'{field}.count': None,
                f'{field}.mean': None,
                f'{field}.median': None,
                f'{field}.standard_deviation': None,
                f'{field}.minimum': None,
                f'{field}.maximum': None,
                f'{field}.quartiles': None,
                f'{field}.coefficient_of_variation': None,
                f'{field}.range': None,
                f'{field}.outlier_ids': outlier_ids
            }
            empty_filtered_dict = {k: empty_field_statistics[k] for k in statistical_metrics}
            if len(filtered_df) < min_count:
                return empty_filtered_dict

            if remove_outliers:
                '''Sqrt transformation'''
                if sqrt_tranf:
                    # Check whether the majority is negative and flip the sign so we can apply sqrt transf
                    is_majority_negative = (filtered_df[field] < 0).sum() > (len(filtered_df) / 2)
                    if is_majority_negative:
                        filtered_df.loc[:, field] = -filtered_df[field]

                    filtered_df = filtered_df[filtered_df[field] >= 0]
                    try:
                        filtered_df[field] = np.sqrt(filtered_df[field])
                    except:
                        sqrt_tranf = False

                '''Drop products with z-scores greater than 1.96, which corresponds to 95% confidence'''
                if method == 'zscore':
                    # Calculate z-scores of the values in the filtered_df[field]
                    mean = filtered_df[field].mean()
                    std_dev = filtered_df[field].std()
                    z_scores = np.abs((filtered_df[field] - mean) / std_dev)
                    # Filter out outliers
                    outlier_mask = z_scores > 1.96
                    outlier_ids = filtered_df.index[outlier_mask].tolist()
                    filtered_df = filtered_df[~outlier_mask]

                '''Repeat zscore method until the max outlier has z_value less than 5'''
                if method == 'repeated_zscore':
                    z_max = 20
                    while z_max > 6:
                        # Calculate z-scores of the values in the filtered_df[field]
                        mean = filtered_df[field].mean()
                        std_dev = filtered_df[field].std()
                        z_scores = np.abs((filtered_df[field] - mean) / std_dev)
                        # Filter out outliers (values with z-scores greater than 1.96, which corresponds to 95% confidence)
                        outlier_mask = z_scores > 1.96
                        outlier_ids.extend(filtered_df.index[outlier_mask].tolist())
                        filtered_df = filtered_df[~outlier_mask]
                        z_max = z_scores.max()

                if method == 'IQR':
                    # Calculate the first quartile (Q1), the third quartile (Q3), and the interquartile range (IQR)
                    Q1 = filtered_df[field].quantile(0.25)
                    Q3 = filtered_df[field].quantile(0.75)
                    IQR = Q3 - Q1

                    # Filter out outliers (values below Q1 - 1.5 * IQR or above Q3 + 1.5 * IQR)
                    outlier_mask = ~filtered_df[field].between(Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)
                    outlier_ids = filtered_df.index[outlier_mask].tolist()
                    filtered_df.index[outlier_mask].tolist()
                    filtered_df = filtered_df[~outlier_mask]

                if sqrt_tranf:
                    filtered_df[field] = filtered_df[field] ** 2
                    # Fix the sign
                    if is_majority_negative:
                        filtered_df[field] = - filtered_df[field]

            if len(filtered_df) < min_count:
                return empty_filtered_dict

            # Calculate statistics
            count = len(filtered_df[field])
            mean = filtered_df[field].mean()
            median = filtered_df[field].median()
            std = filtered_df[field].std()
            minimum = filtered_df[field].min()
            maximum = filtered_df[field].max()
            Q1_val = filtered_df[field].quantile(0.25)
            Q2 = median
            Q3_val = filtered_df[field].quantile(0.75)
            Q4 = maximum
            # Check if Q1 is NaN
            if pd.isna(Q1_val):
                quartiles = None
            else:
                quartiles = np.array([float(Q1_val), float(Q2), float(Q3_val), float(Q4)])
            coefficient_of_variation = float(std / mean) if mean else None
            field_statistics = {
                f'{field}.count': int(count),
                f'{field}.mean': float(mean),
                f'{field}.median': float(median),
                f'{field}.standard_deviation': float(std),
                f'{field}.minimum': float(minimum),
                f'{field}.maximum': float(maximum),
                f'{field}.quartiles': quartiles,
                f'{field}.coefficient_of_variation': coefficient_of_variation,
                f'{field}.range': float(maximum - minimum),
                f'{field}.outlier_ids': outlier_ids
            }
            filtered_dict = {k: field_statistics[k] for k in statistical_metrics}
            return filtered_dict

        df = self.dataframe

        statistics_df = pd.DataFrame()

        if not include_estimated_values:
            df = df[df['estimated']==False]

        if fields is None or fields == 'all':
            fields = self.get_available_fields()

        if statistical_metrics is None:
            statistical_metrics = ['count', 'mean', 'median']

        group_by_dict = self.get_group_by_dict(df, group_by)

        filter_conditions = self.get_group_by_combinations(df, group_by_dict, min_count)

        for filter_condition in filter_conditions:

            count = filter_condition.pop('count', None)
            filtered_materialfacts = self.filter_df_by_dict(df, filter_condition)
            stats_dict = {}
            name_dict = filter_condition.copy()
            name_dict['total_count'] = count
            for field_name in fields:
                filtered_df = filtered_materialfacts[[field_name]].dropna()
                if len(filtered_df) >= min_count:
                    field_dict = get_field_statistics(statistical_metrics, field_name, filtered_df, remove_outliers, method, sqrt_tranf, min_count)
                    stats_dict.update(field_dict)

            if stats_dict:
                full_dict = {**name_dict, **stats_dict}
                new_row = pd.DataFrame([full_dict])
                new_row = new_row.dropna(axis=1, how='all')  # Drop columns where all values are NA
                statistics_df = pd.concat([statistics_df, new_row], ignore_index=True)

        calculated_fields =  [f"{field}.{metric}" for field in fields for metric in statistical_metrics]
        name_fields = [field for field in statistics_df.columns if field not in calculated_fields]
        statistics_df = statistics_df.sort_values(name_fields)
        desired_column_order = list(name_fields) + calculated_fields
        statistics_df = statistics_df.reindex(columns=desired_column_order)
        statistics_df.columns = [col.replace('breakdown__', '') for col in statistics_df.columns]
        statistics_df.dropna(axis=1, how='all', inplace=True)
        count_keys = ['total_count'] + [i for i in statistics_df.keys() if ('.count' in i)]
        for key in count_keys:
            if key in statistics_df.keys():
                statistics_df[key] = statistics_df[key].fillna(0).astype('int64')


        return statistics_df.reset_index(drop=True)

    def remove_outliers_from_df(self, filtered_df, field, method, sqrt_tranf):

        '''Sqrt transformation'''
        if sqrt_tranf:
            # Check whether the majority is negative and flip the sign so we can apply sqrt transf
            is_majority_negative = (filtered_df[field] < 0).sum() > (len(filtered_df) / 2)
            if is_majority_negative:
                filtered_df.loc[:, field] = -filtered_df[field]

            filtered_df = filtered_df[filtered_df[field] >= 0]
            try:
                filtered_df[field] = np.sqrt(filtered_df[field])
            except:
                sqrt_tranf = False

        '''Drop products with z-scores greater than 1.96, which corresponds to 95% confidence'''
        if method == 'zscore':
            # Calculate z-scores of the values in the filtered_df[field]
            mean = filtered_df[field].mean()
            std_dev = filtered_df[field].std()
            z_scores = np.abs((filtered_df[field] - mean) / std_dev)
            # Filter out outliers
            outlier_mask = z_scores > 1.96
            filtered_df = filtered_df[~outlier_mask]

        '''Repeat zscore method until the max outlier has z_value less than 5'''
        if method == 'repeated_zscore':
            z_max = 20
            while z_max > 6:
                # Calculate z-scores of the values in the filtered_df[field]
                mean = filtered_df[field].mean()
                std_dev = filtered_df[field].std()
                z_scores = np.abs((filtered_df[field] - mean) / std_dev)
                # Filter out outliers (values with z-scores greater than 1.96, which corresponds to 95% confidence)
                outlier_mask = z_scores > 1.96
                filtered_df = filtered_df[~outlier_mask]
                z_max = z_scores.max()

        if method == 'IQR':
            # Calculate the first quartile (Q1), the third quartile (Q3), and the interquartile range (IQR)
            Q1 = filtered_df[field].quantile(0.25)
            Q3 = filtered_df[field].quantile(0.75)
            IQR = Q3 - Q1

            # Filter out outliers (values below Q1 - 1.5 * IQR or above Q3 + 1.5 * IQR)
            outlier_mask = ~filtered_df[field].between(Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)
            filtered_df.index[outlier_mask].tolist()
            filtered_df = filtered_df[~outlier_mask]

        if sqrt_tranf:
            filtered_df[field] = filtered_df[field] ** 2
            # Fix the sign
            if is_majority_negative:
                filtered_df[field] = - filtered_df[field]

        return filtered_df

    def filter_dataframe_based_on_field(self, field, filters=None, include_estimated_values=False, remove_outliers=True, method='IQR', sqrt_tranf=True):

        if filters:
            df = self.filter_df_by_dict(self.dataframe, filters)
        else:
            df = self.dataframe

        if not include_estimated_values:
            df = df[df['estimated'] == False]

        if field not in self.get_available_fields():
            return pd.DataFrame()

        df = df.dropna(subset=[field])

        if remove_outliers:
            df = self.remove_outliers_from_df(df, field, method, sqrt_tranf)

        return df.reset_index(drop=True)

    def get_field_distribution(self, field, filters=None, include_estimated_values=False, remove_outliers=True, method='IQR', sqrt_tranf=True):
        df = self.filter_dataframe_based_on_field(field, filters, include_estimated_values, remove_outliers, method, sqrt_tranf)
        return df
        # self.plot_histogram(df, field)

    def get_grouped_data(self, df, field, group_by_field):
        # Ensure the group_by_field is in the DataFrame
        if group_by_field not in df.columns:
            raise ValueError(f"{group_by_field} column is not available in the DataFrame.")

        # Get unique values for the group_by_field column
        group_by_dict = self.get_group_by_dict(df, [group_by_field])

        # Create a boxplot for each unique value in the group_by_field column
        # grouped_data = [df[df[group_by_field] == value][field] for value in group_by_dict[group_by_field]]
        grouped_data_dict = {value: df[df[group_by_field] == value][field] for value in group_by_dict[group_by_field]}

        return grouped_data_dict


    def get_field_distribution_boxplot(self, field, group_by_field, filters=None, include_estimated_values=False, remove_outliers=True, method='IQR', sqrt_tranf=True):
        df = self.filter_dataframe_based_on_field(field, filters, include_estimated_values, remove_outliers, method, sqrt_tranf)
        # After preparing and filtering the DataFrame, plot it
        grouped_data_dict = self.get_grouped_data(df, field, group_by_field)
        return grouped_data_dict

