"""
EIQ calculator package for the LORENZO POZZI Pesticide App.

This package provides the components for Environmental Impact Quotient (EIQ) 
calculations of pesticide applications.
"""

from eiq_calculator_page.eiq_calculator_page import EiqCalculatorPage
from eiq_calculator_page.single_product_calculator import SingleProductCalculator
from eiq_calculator_page.product_comparison import ProductComparisonCalculator
from eiq_calculator_page.eiq_ui_components import (
    ProductSearchField, EiqResultDisplay, ColorCodedEiqItem,
    get_products_from_repo, get_product_info, get_eiq_color
)
from math_module.eiq_calculations import (
    calculate_field_eiq, calculate_product_field_eiq, 
    format_eiq_result, get_impact_category
)
from math_module.eiq_conversions import (
    convert_concentration_to_percent, convert_application_rate,
    convert_concentration_to_decimal, convert_eiq_units,
    standardize_eiq_calculation, convert_eiq_to_metric,
    APPLICATION_RATE_CONVERSION, CONCENTRATION_CONVERSION
)

__all__ = [
    'EiqCalculatorPage',
    'SingleProductCalculator', 
    'ProductComparisonCalculator',
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
    'ProductSearchField',
    'EiqResultDisplay',
    'ColorCodedEiqItem',
    'get_products_from_repo',
    'get_product_info',
    'get_eiq_color'
]