"""
EIQ calculator package for the LORENZO POZZI Pesticide App.

This package provides the components for Environmental Impact Quotient (EIQ) 
calculations of pesticide applications.
"""

from ui.eiq.eiq_calculator_page import EiqCalculatorPage
from ui.eiq.single_product_calculator import SingleProductCalculator
from ui.eiq.product_comparison import ProductComparisonCalculator

# Import from the new modules
from ui.eiq.eiq_calculations import (
    calculate_field_eiq, calculate_product_field_eiq, 
    format_eiq_result, get_impact_category
)

from ui.eiq.eiq_conversions import (
    convert_concentration_to_percent, convert_application_rate,
    convert_concentration_to_decimal, convert_eiq_units,
    APPLICATION_RATE_CONVERSION, CONCENTRATION_CONVERSION
)

from ui.eiq.eiq_ui_components import (
    ProductSearchField, EiqResultDisplay, ColorCodedEiqItem,
    get_products_from_csv, get_product_info, get_eiq_color
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
    'APPLICATION_RATE_CONVERSION',
    'CONCENTRATION_CONVERSION',
    'ProductSearchField',
    'EiqResultDisplay',
    'ColorCodedEiqItem',
    'get_products_from_csv',
    'get_product_info',
    'get_eiq_color'
]