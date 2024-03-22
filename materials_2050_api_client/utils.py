filters_template = {
    'sort_by': "Sort By (Available options are - carbon_sorting, latest, recycled_content, recyclable_content)",
    'group_by': "Products are grouped by (Available options are - company_name, product_type, material, manufacturing_location, continent, price_range, building_applications, building_types, certification_types)",
    'mf_unit': "Include dictionary with material facts in specified units. Accepts a single value or multiple values. Use 'all' to include all units. For example, to express material facts in square meters and square feet, use mf_unit='m2'&mf_unit='ft2'.",
    'name': "Search with the name of the product",
    'product_type': "Product Type Ids (e.g. product_type=2 or [2,3])",
    'product_type_family': "Product Type Family Ids (e.g. product_type_family=3 or [2,3])",
    'material_types': "Material Types Ids (e.g. material_types=4 or [2,3])",
    'material_types_family': "Material Types Family Ids (e.g. material_types_family=3 or [2,3])",
    'building_applications': "Building Applications Ids (e.g. building_applications=4 or [2,3])",
    'company': "Company Ids (e.g. company=4 or [22,23])",
    'building_types': "Building Types Ids (e.g. building_types=4 or [1,2,3,4])",
    'fire_performance': "Fire Performance Name (e.g. fire_performance= A1 or ['  B-s1,d0','M3 (NF P92-501 : 1995)'])",
    'manufacturing_country': "Manufacturing Country Ids (e.g. manufacturing_country=4 or manufacturing_country=United State)",
    'continent': "Continent Ids (e.g. continent=5 or [2,3])",
    'certificate_type': "Certificate Type Ids (e.g. certificate_type=2or [2,3])",
    'certificate_type_family': "Certificate Type Family Ids (e.g. certificate_type_family=1or [2,3])",
    'norm_price': "Norm Price Ids (e.g. norm_price=4 or [2,3])",
}

lca_fields_input = ['net_fresh_water_use', 'non_renewable_primary_energy',
              'non_renewable_primary_energy_raw_materials', 'non_renewable_secondary_fuels',
              'renewable_primary_energy', 'renewable_primary_energy_raw_materials',
              'renewable_secondary_fuels', 'secondary_material_use',
              'total_non_renewable_primary_energy', 'total_renewable_primary_energy']
lca_fields_output = ['components_for_reuse', 'exported_electrical_energy',
              'exported_thermal_energy', 'hazardous_waste_disposed', 'materials_for_energy_recovery',
              'materials_for_recycling', 'non_hazardous_waste_disposed',
              'radioactive_waste_disposed']

lca_fields_impact = ['abiotic_depletion_potential_non_fossil', 'acidification_potential',
              'ozone_depletion_potential', 'eutrophication_potential',
              'formation_potential_of_tropospheric_ozone', 'global_warming_potential_fossil',
              'global_warming_potential_biogenic', 'global_warming_potential_luluc', 'water_deprivation_potential']

lca_fields = lca_fields_input + lca_fields_output + lca_fields_impact

lca_modules = [
    'A1', 'A2', 'A3', 'A1A2A3', 'A4', 'A5', 'B1', 'B2', 'B3',
    'B4', 'B5', 'B6', 'B7', 'C1', 'C2', 'C3', 'C4', 'D'
]


unit_to_field_mapping = {
    ('kg', 'm3'): 'density',
    ('kg', 'm2'): 'grammage',
    ('kg', 'm'): 'linear_density',
    ('kg', 'piece'): 'mass_per_piece',
    ('m3', 'm2'): 'thickness',
    ('m3', 'm'): 'cross_sectional_area',
}

primary_units = ['kg', 'm', 'm2', 'm3', 'piece']

mf_num_fields = [
    'carbon_sorting', 'on_site_installation', 'use_and_maintenance', 'water_use_kg', 'odp',
    'total_co2e_kg_mf', 'total_co2e_kg_mf_corrected',
    'total_biogenic_co2e', 'total_biogenic_co2e_corrected',
    'manufacturing', 'manufacturing_corrected',
    'end_of_life', 'end_of_life_corrected',
]

# lca fields that are related to the mf_num_fields fields
related_lca_fields = [
    'global_warming_potential_fossil', 'ozone_depletion_potential', 'net_fresh_water_use',
    'global_warming_potential_biogenic',
    'secondary_material_use', 'materials_for_energy_recovery', 'materials_for_recycling', 'components_for_reuse'
]

mf_perc_fields = ["recycled_content", "recyclable_content", "reuse_potential", "energy_recovery_possibility"]

physical_properties_fields = ['density', 'grammage', 'linear_density', 'mass_per_piece', 'thickness', 'cross_sectional_area']


