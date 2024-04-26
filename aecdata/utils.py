production_base_url = "https://app.2050-materials.com/"

unit_to_field_mapping = {
    ('kg', 'm3'): 'density',
    ('kg', 'm2'): 'grammage',
    ('kg', 'm'): 'linear_density',
    ('kg', 'piece'): 'mass_per_piece',
    ('m3', 'm2'): 'thickness',
    ('m3', 'm'): 'cross_sectional_area',
}

unit_categories = {
    'm': ['m', 'ft', 'in'],
    'm2': ['m2', 'ft2', 'in2'],
    'm3': ['m3', 'ft3', 'in3'],
    'kg': ['kg', 'lb', 'mt', 'ust'],
    'piece': ['piece']
}

primary_units = list(unit_categories.keys())

mf_num_fields = [
    'on_site_installation', 'use_and_maintenance', 'water_use_kg', 'odp',
    'total_co2e_kg_mf', 'total_co2e_kg_mf_corrected',
    'total_biogenic_co2e', 'total_biogenic_co2e_corrected',
    'manufacturing', 'manufacturing_corrected',
    'end_of_life', 'end_of_life_corrected',
    # 'carbon_sorting',
]

mf_perc_fields = ["recycled_content", "recyclable_content", "reuse_potential", "energy_recovery_possibility"]

physical_properties_fields = list(unit_to_field_mapping.values())

'''Following dict are for tranforming to epdx'''
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

field_description = {}

field_description['filters_template']  = {
    'sort_by': "Sort By (Available options are - carbon_sorting, latest, recycled_content, recyclable_content, update & created)",
    'group_by': "Products are grouped by (Available options are - company_name, product_type, material, manufacturing_location, continent, price_range, building_applications, building_types, certification_types)",
    'unique_product_uuid_v2': "Search a specific product with UUID (2050 Materials unique id) (e.g. unique_product_uuid_v2=ac22f2a4-f960-11ed-92ea-0242ac120004)",
    'product_url': "Search a specific product with product url (e.g. product_url='https://app.2050-materials.com/product/details_designer/isolconfort-srl-eps-eco-espanso-k120/')",
    "compliances": "compliances (e.g. compliances=EN 15804)",
    "updated_after": "Products updated after a date (e.g. updated_after=2022-12-31)",
    "updated_before": "Products updated before a date (e.g. updated_before=2022-12-31)",
    "created_after": "Products created after a date (e.g. created_after=2022-12-31)",
    "created_before": "Products created before a date (e.g. created_before=2022-12-31)",
    "created_between": "Products created during date range (e.g. created_between=2022-12-31,2023-12-31)",
    "updated_between": "Products updated during date range (e.g. updated_between=2022-12-31,2023-12-31)",
    'mf_unit': "Include dictionary with material facts in specified units. Accepts a single value or multiple values. Use 'all' to include all units. For example, to express material facts in square meters and square feet, use mf_unit='m2'&mf_unit='ft2'.",
    'name': "Search with the name of the product (e.g. name='Mycelium Insulation Panel')",
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

field_description['lca_fields'] = {}

field_description['lca_fields']['input_fields'] = {'net_fresh_water_use': {'description': 'Use of net fresh water',
  'short_name': 'FW',
  'unit': 'kg'},
 'non_renewable_primary_energy': {'description': 'Use of non-renewable primary energy',
  'short_name': 'PENRE',
  'unit': 'MJ'},
 'non_renewable_primary_energy_raw_materials': {'description': 'Use of non-renewable primary energy resources used as raw materials',
  'short_name': 'PENRM',
  'unit': 'MJ'},
 'non_renewable_secondary_fuels': {'description': 'Use of non-renewable secondary fuels',
  'short_name': 'NRSF',
  'unit': 'MJ'},
 'renewable_primary_energy': {'description': 'Use of renewable primary energy',
  'short_name': 'PERE',
  'unit': 'MJ'},
 'renewable_primary_energy_raw_materials': {'description': 'Use of renewable primary energy resources used as raw materials',
  'short_name': 'PERM',
  'unit': 'MJ'},
 'renewable_secondary_fuels': {'description': 'Use of renewable secondary fuels',
  'short_name': 'RSF',
  'unit': 'MJ'},
 'secondary_material_use': {'description': 'Use of secondary material',
  'short_name': 'SM',
  'unit': 'kg'},
 'total_non_renewable_primary_energy': {'description': 'Total use of non-renewable primary energy resource',
  'short_name': 'PENRT',
  'unit': 'MJ'},
 'total_renewable_primary_energy': {'description': 'Total use of renewable primary energy resources',
  'short_name': 'PERT',
  'unit': 'MJ'}}

field_description['lca_fields']['output_fields'] = {'components_for_reuse': {'description': 'Components for re-use',
  'short_name': 'CRU',
  'unit': 'kg'},
 'exported_electrical_energy': {'description': 'Exported electrical energy',
  'short_name': 'EEE',
  'unit': 'MJ'},
 'exported_thermal_energy': {'description': 'Exported thermal energy',
  'short_name': 'EET',
  'unit': 'MJ'},
 'hazardous_waste_disposed': {'description': 'Hazardous waste disposed',
  'short_name': 'HWD',
  'unit': 'kg'},
 'materials_for_energy_recovery': {'description': 'Materials for energy recovery',
  'short_name': 'MER',
  'unit': 'kg'},
 'materials_for_recycling': {'description': 'Materials for recycling',
  'short_name': 'MFR',
  'unit': 'kg'},
 'non_hazardous_waste_disposed': {'description': 'Non-hazardous waste dispose',
  'short_name': 'NHWD',
  'unit': 'kg'},
 'radioactive_waste_disposed': {'description': 'Radioactive waste disposed',
  'short_name': 'RWD',
  'unit': 'kg'}}

field_description['lca_fields']['impact_fields'] = {'abiotic_depletion_potential_fossil': {'description': 'Abiotic depletion potential for fossil resources',
  'short_name': 'ADPF',
  'unit': 'MJ'},
 'abiotic_depletion_potential_non_fossil': {'description': 'Abiotic depletion potential for non-fossil resources',
  'short_name': 'ADPE',
  'unit': 'kg Sb-equivalent'},
 'acidification_potential': {'description': 'Acidification potential of soil and water',
  'short_name': 'AP',
  'unit': 'kg SO2-equivalent'},
 'ozone_depletion_potential': {'description': 'Depletion potential of the stratospheric ozone layer',
  'short_name': 'ODP',
  'unit': 'mg CFC 11-equivalent'},
 'eutrophication_potential': {'description': 'Eutrophication potential',
  'short_name': 'EP',
  'unit': 'kg Phosphate-equivalent'},
 'formation_potential_of_tropospheric_ozone': {'description': 'Formation potential of tropospheric ozone',
  'short_name': 'POCP',
  'unit': 'kg NMVOC-equivalent'},
 'global_warming_potential_fossil': {'description': 'Global warming potential, Fossil',
  'short_name': 'GWP-f',
  'unit': 'kg CO2-equivalent'},
 'global_warming_potential_biogenic': {'description': 'Global warming potential, Biogenic',
  'short_name': 'GWP-b',
  'unit': 'kg CO2-equivalent'},
 'global_warming_potential_luluc': {'description': 'Global warming potential, LULUC (Land Use, Land-Use Change, and Forestry)',
  'short_name': 'GWP-luluc',
  'unit': 'kg CO2-equivalent'},
 'water_deprivation_potential': {'description': 'Water (user) deprivation potential',
  'short_name': 'WDP',
  'unit': 'm3 world-equivalent'}}


field_description['material_facts'] = {
    'total_co2e_kg_mf': {
        'description': 'Total Fossil Carbon (stages reported)',
        'unit': 'kg CO2-equivalent'
    },
    'total_co2e_kg_mf_corrected': {
        'description': 'Corrected Total Fossil Carbon (stages reported)',
        'unit': 'kg CO2-equivalent'
    },
    'total_biogenic_co2e': {
        'description': 'Total Biogenic Carbon',
        'unit': 'kg CO2-equivalent'
    },
    'total_biogenic_co2e_corrected': {
        'description': 'Corrected Total Biogenic Carbon',
        'unit': 'kg CO2-equivalent'
    },
    'manufacturing': {
        'description': 'Fossil Carbon (A1-A3)',
        'unit': 'kg CO2-equivalent'
    },
    'manufacturing_corrected': {
        'description': 'Corrected Fossil Carbon (A1-A3)',
        'unit': 'kg CO2-equivalent'
    },
    'on_site_installation': {
        'description': 'Fossil Carbon (A5)',
        'unit': 'kg CO2-equivalent'
    },
    'use_and_maintenance': {
        'description': 'Fossil Carbon (B1-B5)',
        'unit': 'kg CO2-equivalent'
    },
    'end_of_life': {
        'description': 'Fossil Carbon (C1, C3, C4)',
        'unit': 'kg CO2-equivalent'
    },
    'end_of_life_corrected': {
        'description': 'Corrected Fossil Carbon (C1, C3, C4)',
        'unit': 'kg CO2-equivalent'
    },
    'water_use_kg': {
        'description': 'Freshwater use (A1-A3)',
        'unit': 'kg'
    },
    'recycled_content': {
        'description': 'Recycled Content',
        'unit': '%'
    },
    'recyclable_content': {
        'description': 'Recyclable Content',
        'unit': '%'
    },
    'reuse_potential': {
        'description': 'Re-use Potential',
        'unit': '%'
    },
    'energy_recovery_possibility': {
        'description': 'Energy Recovery Possibility',
        'unit': '%'
    },
    'odp': {
        'description': 'Ozone Depletion Potential (A1-A3)',
        'unit': 'mg CFC 11-equivalent'
    },
    "data_source": {"description": "Data Source"},
    "compliances": {"description": "Compliances"},
    "declared_unit": {"description": "Declared Unit"},
    "language": {"description": "Language"},
    "data_source_link__date_of_issue": {"description": "Date of Issue"},
    "data_source_link__certificate_expiry": {"description": "Certificate Expiry Date"},
    "data_source_link__certificate_type__family__name": {"description": "Certificate Type"},
    "mass_per_declared_unit": {"description": "Mass per Declared Unit"},
    "mass_per_declared_unit_estimated": {"description": "Mass per Declared Unit (Estimated)"},
    "plant_or_group": {"description": "Plant or Group"},
    "certificate_subtype": {"description": "Certificate Subtype"},
}

field_description['physical_properties'] = {
    'density': {
        'description': 'Density',
        'unit': 'kg/m3'
    },
    'density_estimated': {
        'description': 'Density Estimated?',
    },
    'grammage': {
        'description': 'Specific Density',
        'unit': 'kg/m2'
    },
    'grammage_estimated': {
        'description': 'Specific Density Estimated?',
    },
    'linear_density': {
        'description': 'Linear Density',
        'unit': 'kg/m'
    },
    'linear_density_estimated': {
        'description': 'Linear Density Estimated?',
    },
    'mass_per_piece': {
        'description': 'Mass per piece',
        'unit': 'kg'
    },
    'mass_per_piece_estimated': {
        'description': 'Mass per piece Estimated?',
    },
    'thickness': {
        'description': 'Thickness',
        'unit': 'm'
    },
    'thickness_estimated': {
        'description': 'Thickness Estimated?',
    },
    'cross_sectional_area': {
        'description': 'Cross sectional area',
        'unit': 'm2'
    },
    'cross_sectional_area_estimated': {
        'description': 'Cross sectional area Estimated?',
    },
    'mass_per_declared_unit': {
        'description': 'Mass per declared unit',
        'unit': 'kg/DU'
    },
    'mass_per_declared_unit_estimated': {
        'description': 'Mass per declared unit Estimated?',
    },
    'scaling_factors': {
        'description': 'Scaling Factors for Unit Conversion. '
                       'This dictionary maps target units (keys) to their corresponding scaling factors (values). '
                       'To convert a value from a declared unit to one of these target units, divide the value by the scaling factor associated with the target unit. '
                       'Each scaling factor specifies how much one unit of the declared unit is equivalent to in the target unit, facilitating accurate and consistent unit conversions.',
    }

}

field_description['technical_parameters'] = {
    "retail_price": {"description": "Price Range"},
    "fire_performance": {"description": "Fire Performance"},
    "color": {"description": "Colour"},
    "steel_grade": {"description": "Steel grade"},
    "u_value": {
        "description": "U-Value",
        "unit": "w/m2k"
    },
    "acoustic_performance": {
        "description": "Acoustic Performance",
        "unit": "dB"
    },
    "maintenance": {
        "description": "Maintenance",
        "unit": "Frequency"
    },
    "porosity": {
        "description": "Porosity",
        "unit": "%"
    },
    "life_expectancy": {
        "description": "Life expectancy",
        "unit": "years"
    },
    "warranty": {
        "description": "Warranty",
        "unit": "years"
    },
    "compression_strength": {"description": "Compression Strength"},
    "impact_strength": {"description": "Impact Strength"},
    "thermal_conductivity": {
        "description": "Thermal Conductivity",
        "unit": "W/mK"
    },
    "thermal_conductivity_estimated": {
        "description": "Thermal conductivity estimated?",
    },
    "texture": {"description": "Texture"},
    "elasticity_plasticity": {"description": "Elasticity Plasticity"},
    "abrasion_resistance": {"description": "Abrasion Resistance"},
    "corrosion_resistance": {"description": "Corrosion Resistance"},
    "weathering_resistance": {"description": "Weathering Resistance"},
    "typical_lead_time": {"description": "Typical Lead Time"},
    "slip_resistance": {"description": "Slip Resistance"},
    "solar_heat_gain_coefficient": {"description": "Solar Heat Gain Coefficient"},
    "concrete_mix": {"description": "Concrete Mix"},
    "consistence_class": {"description": "Consistence Class"},
}

field_description['product_fields'] = {
    "unique_product_uuid_v2": {"description": "Unique Product UUID"},
    "name": {"description": "Product name"},
    "description": {"description": "Product description"},
    "company": {"description": "Company name"},
    "group_elements_nrm_1": {"description": "Group Elements NRM 1"},
    "elements_nrm_1": {"description": "Elements NRM 1"},
    "product_type": {"description": "Product Type"},
    "product_type_family": {"description": "Product Type Family"},
    "material_type": {"description": "Material Type"},
    "building_applications": {"description": "Building Applications"},
    "building_types": {"description": "Building Types"},
    "material_type_family": {"description": "Material Type Family"},
    "manufacturing_location": {"description": "Manufacturing Location"},
    "country": {"description": "Country"},
    "city": {"description": "City"},
    "manufacturing_continent": {"description": "Manufacturing Continent"},
    "product_url": {"description": "Product URL"},
    "product_slug": {"description": "Product Slug"},
    "updated": {"description": "Product Updated"},
    "certificate_url": {"description": "Certificate URL"},
    "work_section_caws": {"description": "Common Arrangement of Work Sections (CAWS)"},
    "csi_masterformat": {"description": "Construction Specifications Institute (CSI) MasterFormat"},
    "uniclass_systems": {"description": "Uniclass Systems"},
    "uniclass_products": {"description": "Uniclass Products"},
}

field_description['lca_modules'] = {
    'A1': {'description': 'Raw material supply: Extraction and processing of raw materials.'},
    'A2': {'description': 'Transport to the manufacturer: Transportation of raw materials to the factory.'},
    'A3': {'description': 'Manufacturing: The manufacturing process of the product.'},
    'A1A2A3': {'description': 'Product stage combined: Covers raw material extraction, transport to the manufacturer, and manufacturing combined.'},
    'A4': {'description': 'Transport to the construction site: Transportation of the construction product to the building site.'},
    'A5': {'description': 'Installation in the building: The process of installing the product into the building during construction.'},
    'B1': {'description': 'Use: The use of the product during the building’s life, including maintenance and energy use.'},
    'B2': {'description': 'Maintenance: Activities involved in maintaining the product during its life cycle.'},
    'B3': {'description': 'Repair: The repair of the product, if necessary, during its life cycle.'},
    'B4': {'description': 'Replacement: The replacement of the product during the building’s life cycle.'},
    'B5': {'description': 'Refurbishment: Refurbishment or renovation of the building/product.'},
    'B6': {'description': 'Operational energy use: The energy used by the product during its operational life.'},
    'B7': {'description': 'Operational water use: The water used by the product during its operational life.'},
    'C1': {'description': 'Deconstruction: The process of deconstructing the building at the end of its life.'},
    'C2': {'description': 'Transportation of waste: Transport of demolished materials and products.'},
    'C3': {'description': 'Waste processing: Processing of waste materials for disposal or recycling.'},
    'C4': {'description': 'Disposal: Final disposal of waste materials.'},
    'D': {'description': 'Benefits and loads beyond the system boundary: Credits for recycling, energy recovery, etc.'}
}

lca_fields = []
for category,fields in field_description['lca_fields'].items():
    lca_fields += list(fields.keys())

lca_modules = list(field_description['lca_modules'].keys())