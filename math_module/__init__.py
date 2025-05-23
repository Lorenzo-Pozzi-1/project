"""
Math module for the LORENZO POZZI Pesticide App.

This module provides mathematical functions for calculations such as EIQ values
and unit conversions used throughout the application.
"""

# EIQ calculation functions
from math_module.eiq_calculations import (
    calculate_field_eiq, calculate_product_field_eiq,
    format_eiq_result, get_impact_category
)

# UOM system components
from data.repository_UOM import (
    UOMRepository, CompositeUOM
)

__all__ = [
    # EIQ calculations
    'calculate_field_eiq',
    'calculate_product_field_eiq',
    'format_eiq_result',
    'get_impact_category',
    
    # UOM system
    'UOMRepository',
    'CompositeUOM'
]