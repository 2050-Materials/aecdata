

lca_fields = ['net_fresh_water_use', 'non_renewable_primary_energy','non_renewable_primary_energy_raw_materials','non_renewable_secondary_fuels','renewable_primary_energy',
    'renewable_primary_energy_raw_materials','renewable_secondary_fuels','secondary_material_use','total_non_renewable_primary_energy','total_renewable_primary_energy','components_for_reuse',
    'exported_electrical_energy','exported_thermal_energy','hazardous_waste_disposed','materials_for_energy_recovery','materials_for_recycling','non_hazardous_waste_disposed',
    'radioactive_waste_disposed','abiotic_depletion_potential_fossil','abiotic_depletion_potential_non_fossil','acidification_potential','ozone_depletion_potential','eutrophication_potential',
    'formation_potential_of_tropospheric_ozone','global_warming_potential_fossil','global_warming_potential_biogenic','global_warming_potential_luluc','water_deprivation_potential'
              ]

lca_modules = ['A1', 'A2', 'A3', 'A1A2A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'C1', 'C2', 'C3', 'C4', 'D']

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