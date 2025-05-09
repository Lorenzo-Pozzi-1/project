"""
EIQ calculator package for the LORENZO POZZI Pesticide App.

This package provides the components for Environmental Impact Quotient (EIQ) 
calculations of pesticide applications.
"""

from eiq_calculator.eiq_calculator_page import EiqCalculatorPage
from eiq_calculator.single_product_calculator import SingleProductCalculator
from eiq_calculator.product_comparison import ProductComparisonCalculator
from eiq_calculator.eiq_calculations import (
    calculate_field_eiq, calculate_product_field_eiq, 
    format_eiq_result, get_impact_category
)
from eiq_calculator.eiq_conversions import (
    convert_concentration_to_percent, convert_application_rate,
    convert_concentration_to_decimal, convert_eiq_units,
    standardize_eiq_calculation, convert_eiq_to_metric,
    APPLICATION_RATE_CONVERSION, CONCENTRATION_CONVERSION
)
from eiq_calculator.eiq_ui_components import (
    ProductSearchField, EiqResultDisplay,
    get_eiq_color
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
    'get_eiq_color'
]