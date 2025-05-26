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
    eiq_calculator
)

# Import UOM
from data.repository_UOM import UOMRepository, CompositeUOM

# Now import the UI components
from eiq_calculator_page.page_eiq_calculator import EiqCalculatorPage
from eiq_calculator_page.tab_single_calculator import SingleProductCalculatorTab
from eiq_calculator_page.tab_multi_calculator import ProductComparisonCalculatorTab

# Import widgets for direct access - these are exposed for convenience
from common.widgets.product_selection import ProductSelectionWidget, ProductSearchField
from common.widgets.application_params import ApplicationParamsWidget
from eiq_calculator_page.widget_product_card import ProductCard
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
    'ProductCard',
    
    # Utilities and constants
    'get_eiq_color',
    'LOW_THRESHOLD',
    'MEDIUM_THRESHOLD',
    'HIGH_THRESHOLD',
    'eiq_calculator',
    'UOMRepository',
    'CompositeUOM'
]