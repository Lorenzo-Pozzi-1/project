"""
EIQ Calculator package for the LORENZO POZZI Pesticide App.

This package provides the components for Environmental Impact Quotient (EIQ) 
calculations of pesticide applications.
"""

# Import the common styles and thresholds first
from common.styles import (
    get_eiq_color, get_eiq_rating,
    EIQ_LOW_THRESHOLD as LOW_THRESHOLD,
    EIQ_MEDIUM_THRESHOLD as MEDIUM_THRESHOLD, 
    EIQ_HIGH_THRESHOLD as HIGH_THRESHOLD
)

# Import calculation functions
from common.calculations import (
    calculate_field_eiq,
    calculate_product_field_eiq,
    format_eiq_result,
    get_impact_category
)

# Import UOM
from data.repository_UOM import UOMRepository, CompositeUOM

# Now import the UI components
from eiq_calculator_page.eiq_calculator_page import EiqCalculatorPage
from eiq_calculator_page.single_calculator_tab import SingleProductCalculatorTab
from eiq_calculator_page.multi_calculator_tab import ProductComparisonCalculatorTab

# Import widgets for direct access - these are exposed for convenience
from common.widgets.product_selection import ProductSelectionWidget, ProductSearchField
from common.widgets.application_params import ApplicationParamsWidget
from eiq_calculator_page.widgets_results_display import EiqResultDisplay, ColorCodedEiqItem

__all__ = [
    # Main page and tabs
    'EiqCalculatorPage',
    'SingleProductCalculatorTab',
    'ProductComparisonCalculatorTab',
    
    # Widget components
    'ProductSelectionWidget',
    'ProductSearchField',
    'ApplicationParamsWidget',
    'EiqResultDisplay',
    'ColorCodedEiqItem',
    
    # Utilities and constants
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