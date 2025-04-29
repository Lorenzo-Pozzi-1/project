"""
EIQ calculator package for the LORENZO POZZI Pesticide App.

This package provides the components for Environmental Impact Quotient (EIQ) 
calculations of pesticide applications.
"""

from ui.eiq.eiq_calculator_page import EiqCalculatorPage
from ui.eiq.single_product_calculator import SingleProductCalculator
from ui.eiq.product_comparison import ProductComparisonCalculator
from ui.eiq.eiq_utils_and_components import (
    calculate_field_eiq, calculate_product_field_eiq, 
    format_eiq_result, get_impact_category, convert_concentration_to_percent
)

__all__ = [
    'EiqCalculatorPage',
    'SingleProductCalculator', 
    'ProductComparisonCalculator',
    'calculate_field_eiq',
    'calculate_product_field_eiq',
    'format_eiq_result',
    'get_impact_category',
    'convert_concentration_to_percent'
]