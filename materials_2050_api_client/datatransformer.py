import pandas as pd
from datetime import datetime
from .utils import *

unit_mapping_to_epdx = {
    'm': 'M',
    'm2': 'M2',
    'm3': 'M3',
    'kg': 'KG',
    'piece': 'PCS',
}
subtype_to_epdx ={
    'Specific Dataset': 'Specific',
    'Average Dataset': 'Generic',
    'Representative Dataset': 'Representative',
    'Generic Dataset': 'Generic',
    'Template Dataset': 'UNKNOWN',
}
initial_epdx = {
    'id': None,
    'name': None,
    'declared_unit': None,
    'version': None,
    'published_date': None,
    'valid_until': None,
    'format_version': None,
    'source': None,
    'reference_service_life': None,
    'standard': None,
    'comment': None,
    'location': None,
    'subtype': None,
    'conversions': None,
    'gwp': None,
    'odp': None,
    'ap': None,
    'ep': None,
    'pocp': None,
    'adpe': None,
    'adpf': None,
    'penre': None,
    'pere': None,
    'perm': None,
    'pert': None,
    'penrt': None,
    'penrm': None,
    'sm': None,
    'rsf': None,
    'nrsf': None,
    'fw': None,
    'hwd': None,
    'nhwd': None,
    'rwd': None,
    'cru': None,
    'mfr': None,
    'mer': None,
    'eee': None,
    'eet': None,
    'meta_data': None
}
modules_to_epdx = {
    'A1A2A3':'a1a3',
    'Α4':'a4',
    'Α5':'a4',
    'B1': 'b1',
    'B2': 'b2',
    'B3': 'b3',
    'B4': 'b4',
    'B5': 'b5',
    'B6': 'b6',
    'B7': 'b7',
    'C1': 'c1',
    'C2': 'c2',
    'C3': 'c3',
    'C4': 'c4',
    'D': 'd',
}
lca_field_to_epdx = {
    'net_fresh_water_use': 'fw',
    'non_renewable_primary_energy': 'penre',
    'non_renewable_primary_energy_raw_materials': 'penrm',
    'non_renewable_secondary_fuels': 'nrsf',
    'renewable_primary_energy': 'pere',
    'renewable_primary_energy_raw_materials': 'perm',
    'renewable_secondary_fuels': 'rsf',
    'secondary_material_use': 'sm',
    'total_non_renewable_primary_energy': 'penrt',
    'total_renewable_primary_energy': 'pert',
    'components_for_reuse': 'cru',
    'exported_electrical_energy': 'eee',
    'exported_thermal_energy': 'eet',
    'hazardous_waste_disposed': 'hwd',
    'materials_for_energy_recovery': 'mer',
    'materials_for_recycling': 'mfr',
    'non_hazardous_waste_disposed': 'nhwd',
    'radioactive_waste_disposed': 'rwd',
    'abiotic_depletion_potential_fossil': 'adpf',
    'abiotic_depletion_potential_non_fossil': 'adpe',
    'acidification_potential': 'ap',
    'ozone_depletion_potential': 'odp',
    'eutrophication_potential': 'ep',
    'formation_potential_of_tropospheric_ozone': 'pocp',
    'global_warming_potential_fossil': 'gwp',
    'global_warming_potential_biogenic': None,  # Not directly mapped, may consider 'gwp' if appropriate
    'global_warming_potential_luluc': None,  # Not directly mapped, may need a custom field or consider 'gwp'
    'water_deprivation_potential': None,  # Not directly mapped, may need a custom field or consider 'fw'
}

class DataTransformer:
    def __init__(self, product_data):
        self.product_data = product_data

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
        for index, row in self.product_data.dataframe.iterrows():
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
            epdx_product['reference_service_life'] = row['life_expectancy']

            # Certificate Subtype
            certificate_subtype = row.get('material_facts.certificate_subtype', '')
            epdx_product['subtype'] = map_subtype_to_epdx(certificate_subtype)

            # Determine the 'standard' field based on 'material_facts.compliances'
            compliances = row.get('material_facts.compliances', None)
            epdx_product['standard'] = determine_standard(compliances)

            # location assign country
            epdx_product['location'] = row['country']

            # Generate conversions list
            conversions = generate_conversions(row.to_dict())
            epdx_product['conversions'] = conversions

            # Generate LCA results from the current row and merge them directly into epdx_product
            lca_results = create_epdx_dict_from_row(row.to_dict(), modules_to_epdx, lca_field_to_epdx)
            epdx_product.update(lca_results)

            # Append the fully constructed EPDx product dict to the list
            epdx_products_list.append(epdx_product)

        return epdx_products_list

    def from_epdx(self, epdx_data):
        """
        Transforms data from EPDx format back to the internal format, updating self.product_data.
        """
        # Convert EPDx data (assumed to be a dictionary) to the format suitable for ProductData
        # This is a placeholder implementation
        # Your conversion logic goes here
        # Update self.product_data accordingly
        self.product_data.data = []  # Replace [] with the converted list of products from epdx_data

