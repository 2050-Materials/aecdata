import pandas as pd
import numpy as np
import json
import warnings
from itertools import product
import matplotlib.pyplot as plt
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
        self._data = value
        self._dataframe = self.to_dataframe(value).replace({np.nan: None})

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
        df = self.convert_df_to_unit(unit)
        if unit in available_units:
            df['estimated'] = df[f'material_facts.scaling_factors.{unit}.estimated']
        elif unit == 'declared_unit':
            df['estimated'] = False

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

    def filter_df_by_dict(self, df, filter_dict):
        # Start with the full DataFrame
        filtered_df = df
        # Apply each filter
        for key, value in filter_dict.items():
            # Adjust the filtering logic as needed, assuming equality here
            # You might need to handle nested keys or other special cases
            filtered_df = filtered_df[filtered_df[key] == value]
        return filtered_df

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

        # Initialize DataFrame
        statistics_df = pd.DataFrame()

        if not include_estimated_values:
            df = df[df['estimated']==False]

        if fields is None or fields == 'all':
            fields = self.get_available_fields()

        if statistical_metrics is None:
            statistical_metrics = ['count', 'mean', 'median']

        # Set default group_by if not provided
        if group_by is None:
            group_by_dict = {'product_type': set(df['product_type'])}
        else:
            group_by_dict = {}
            for group in group_by:
                df.loc[:,group] = df[group].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
                group_by_dict[group] = set(df[group])

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

    def get_field_distribution(self, field, filters=None, return_df=False, include_estimated_values=False, remove_outliers=True, method='IQR', sqrt_tranf=True):
        def remove_outliers_from_df(filtered_df, field, method, sqrt_tranf):

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

        if filters:
            df = self.filter_df_by_dict(self.dataframe, filters)
        else:
            df = self.dataframe

        if not include_estimated_values:
            df = df[df['estimated']==False]

        if field not in self.get_available_fields():
            raise ValueError(f"{field} is not available.")
        else:
            df = df.dropna(subset=[field])

        if remove_outliers:
            df = remove_outliers_from_df(df, field, method, sqrt_tranf)

        # Plotting
        bin_count = min(len(df[field].unique()), 50)  # Limit the number of bins to a maximum of 50
        plt.figure(figsize=(10, 6))
        n, bins, patches = plt.hist(df[field], bins=bin_count, color='#2ab0ff', alpha=0.7, rwidth=0.85)
        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Value', fontsize=15)
        plt.ylabel('Frequency', fontsize=15)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.title(f'Distribution of {field}', fontsize=15)
        plt.axvline(x=df[field].mean(), color='r', linestyle='-', label=f'Mean: {df[field].mean():.3f}')
        plt.axvline(x=df[field].median(), color='m', linestyle='-', label=f'Median: {df[field].median():.3f}')
        plt.legend(loc='upper right')
        plt.show()

        if return_df:
            return df.reset_index(drop=True)
