import pandas as pd
import numpy as np
import json
import warnings
from .utils import *

# Ensure all instances of this specific warning are always shown
warnings.simplefilter('always', UserWarning)
class ProductData:

    def __init__(self, data):
        """
        Initializes the ProductData with the data to be processed. Depending on the type of data provided,
        populates both a dictionary and a DataFrame representation of the data.

        :param data: A pandas DataFrame or a dictionary representing the product data.
        """
        if isinstance(data, list):
            self.data = data
            self.dataframe = self.to_dataframe().replace({np.nan: None})
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
            self.dataframe = df
            self.data = self.df_to_list(df)
        else:
            raise ValueError("Unsupported data type. Please provide a list of products or a pandas DataFrame.")

    def df_to_list(self, df):

        df.replace({np.nan: None}, inplace=True)

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

    def to_dataframe(self):
        """
        Converts the data into a pandas DataFrame, ensuring that columns
        starting with 'material_facts' are placed at the end and sorted.

        :return: pandas DataFrame containing the data with ordered columns.
        """
        # Normalize the data to create an initial dataframe
        df = pd.json_normalize(self.data)

        # Separate columns starting with 'material_facts'
        material_facts_cols = [col for col in df.columns if col.startswith('material_facts')]
        other_cols = [col for col in df.columns if not col.startswith('material_facts')]

        # Sort the 'material_facts' columns
        sorted_material_facts_cols = sorted(material_facts_cols)

        # Combine the columns back together, with 'material_facts' columns at the end
        ordered_columns = other_cols + sorted_material_facts_cols

        # Re-index the dataframe with the ordered columns
        return df[ordered_columns]

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

    def convert_df_to_unit(self, unit='declared_unit'):
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
        columns_to_scale = [col for col in scalable_columns if col in self.dataframe.columns]

        # Create new df that we will adjust
        scaled_df = self.dataframe.copy()

        if unit != 'declared_unit':
            # Column to use for scaling
            scaling_column = f'material_facts.scaling_factors.{unit}.value'

            # Ensure the scaling column exists
            if scaling_column in self.dataframe.columns:
                scaled_df.loc[:, columns_to_scale] = scaled_df.loc[:, columns_to_scale].div(self.dataframe.loc[:, scaling_column], axis=0)
                return scaled_df
            else:
                print(f'Unit scaling column "{scaling_column}" not found in DataFrame. No scaling applied.')
                return None
        else:
            return scaled_df


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
                "the same unit, which may affect the validity of applying statistical methods to these fields.",
                UserWarning  # This is the default, but specifying it makes the intention clear
            )

        # Extract available units
        available_units = self.get_available_units()

        # Check if the specified unit is available
        if unit != 'declared_unit' and unit not in available_units:
            raise ValueError(f'Unit "{unit}" not available. Available units: {available_units}')

        # Since the unit is valid, proceed to convert the DataFrame to the specified unit
        self.dataframe = self.convert_df_to_unit(unit)

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



