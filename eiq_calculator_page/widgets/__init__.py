"""
Widget exports for the EIQ Calculator page.

This module exposes all the widget classes from the widgets subfolder.
"""

from common.widgets.product_selection import (
    ProductSearchField, ProductTypeSelector, ProductSelectionWidget
)

from common.widgets.application_params import (
    ApplicationRateWidget, ApplicationParamsWidget
)

from eiq_calculator_page.widgets.result_display import (
    ColorCodedEiqItem, EiqResultDisplay, EiqComparisonTable
)

from common.styles import (
    get_eiq_color, get_eiq_rating,
    EIQ_LOW_THRESHOLD as LOW_THRESHOLD, 
    EIQ_MEDIUM_THRESHOLD as MEDIUM_THRESHOLD, 
    EIQ_HIGH_THRESHOLD as HIGH_THRESHOLD,
    EIQ_LOW_COLOR, EIQ_MEDIUM_COLOR, EIQ_HIGH_COLOR, EIQ_EXTREME_COLOR
)

__all__ = [
    'ProductSearchField',
    'ProductTypeSelector',
    'ProductSelectionWidget',
    'ApplicationRateWidget',
    'ApplicationParamsWidget',
    'ColorCodedEiqItem',
    'EiqResultDisplay',
    'EiqComparisonTable',
    'get_eiq_color',
    'get_eiq_rating',
    'LOW_THRESHOLD',
    'MEDIUM_THRESHOLD',
    'HIGH_THRESHOLD',
    'EIQ_LOW_COLOR',
    'EIQ_MEDIUM_COLOR',
    'EIQ_HIGH_COLOR',
    'EIQ_EXTREME_COLOR'
]