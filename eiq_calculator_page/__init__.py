"""
EIQ Calculator package for the LORENZO POZZI Pesticide App.

This package provides the components for Environmental Impact Quotient (EIQ) 
calculations of pesticide applications.
"""

from eiq_calculator_page.eiq_calculator_page import EiqCalculatorPage
from eiq_calculator_page.single_calculator_tab import SingleProductCalculatorTab
from eiq_calculator_page.multi_calculator_tab import ProductComparisonCalculatorTab

# Import widgets for direct access
from common.widgets.product_selection import ProductSelectionWidget, ProductSearchField
from common.widgets.application_params import ApplicationParamsWidget
from eiq_calculator_page.widgets.result_display import EiqResultDisplay, ColorCodedEiqItem
from common.styles import get_eiq_color, EIQ_LOW_THRESHOLD as LOW_THRESHOLD, EIQ_MEDIUM_THRESHOLD as MEDIUM_THRESHOLD, EIQ_HIGH_THRESHOLD as HIGH_THRESHOLD

# Re-export EIQ calculation functions
from math_module.eiq_calculations import (
    calculate_field_eiq, calculate_product_field_eiq, 
    format_eiq_result, get_impact_category
)

# Re-export UOM system components
from data.UOM_repository import UOMRepository, CompositeUOM

__all__ = [
    'EiqCalculatorPage',
    'SingleProductCalculatorTab',
    'ProductComparisonCalculatorTab',
    'ProductSelectionWidget',
    'ProductSearchField',
    'ApplicationParamsWidget',
    'EiqResultDisplay',
    'ColorCodedEiqItem',
    'get_eiq_color',
    'LOW_THRESHOLD',
    'MEDIUM_THRESHOLD',
    'HIGH_THRESHOLD',
    'calculate_field_eiq',
    'calculate_product_field_eiq',
    'format_eiq_result',
    'get_impact_category',
    'UOMRepository',
    'CompositeUOM'
]