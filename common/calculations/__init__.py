"""
EIQ Calculations Package for the LORENZO POZZI Pesticide App.

This package provides a clean two-layer architecture for EIQ calculations:
- Layer 1: UOM standardization and validation
- Layer 2: Pure mathematical calculations

Usage:
    # Recommended: Use the unified calculator interface
    from common.calculations import eiq_calculator
    
    field_eiq = eiq_calculator.calculate_product_field_eiq(
        active_ingredients=ai_data,
        application_rate=32.0,
        application_rate_uom="fl oz/acre",
        applications=1,
        user_preferences=user_prefs
    )
    
    # Backward compatibility: Original function names still work
    from common.calculations import calculate_product_field_eiq
    
    field_eiq = calculate_product_field_eiq(
        active_ingredients, rate, unit, applications, user_preferences
    )
"""

from .layer_3_interface import (
    EIQCalculator,
    eiq_calculator
)

# Import Layer 1 components for advanced use
from .layer_1_uom_std import (
    EIQUOMStandardizer,
    StandardizedEIQInputs,
    ProductStandardizedInputs
)

# Import Layer 2 components for advanced use
from .layer_2_eiq_math import (
    calculate_field_eiq_single_ai,
    calculate_field_eiq_product,
    calculate_field_eiq_scenario,
    EIQResult
)

# Define what gets imported with "from common.calculations import *"
__all__ = [
    # Main calculator interface
    'eiq_calculator',
    'EIQCalculator',
    
    # Layer 1 - UOM Standardization
    'EIQUOMStandardizer',
    'StandardizedEIQInputs', 
    'ProductStandardizedInputs',
    
    # Layer 2 - Pure Calculations
    'calculate_field_eiq_single_ai',
    'calculate_field_eiq_product',
    'calculate_field_eiq_scenario',
    'EIQResult'
]