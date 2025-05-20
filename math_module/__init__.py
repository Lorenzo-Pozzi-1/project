"""
Math module for the LORENZO POZZI Pesticide App.

This module provides mathematical functions for calculations such as EIQ values
and unit conversions used throughout the application.
"""

from math_module.eiq_calculations import (
    calculate_field_eiq, calculate_product_field_eiq,
    format_eiq_result, get_impact_category
)
from math_module.eiq_conversions import (
    convert_concentration_to_percent, convert_application_rate,
    convert_concentration_to_decimal, convert_eiq_units,
    standardize_eiq_calculation, convert_eiq_to_metric,
    APPLICATION_RATE_CONVERSION, CONCENTRATION_CONVERSION,
    get_uom_category, is_weight_uom, is_volume_uom
)

__all__ = [
    'calculate_field_eiq',
    'calculate_product_field_eiq',
    'format_eiq_result',
    'get_impact_category',
    'convert_concentration_to_percent',
    'convert_application_rate',
    'convert_concentration_to_decimal',
    'convert_eiq_units',
    'standardize_eiq_calculation',
    'convert_eiq_to_metric',
    'APPLICATION_RATE_CONVERSION',
    'CONCENTRATION_CONVERSION',
    'get_uom_category',
    'is_weight_uom', 
    'is_volume_uom'
]