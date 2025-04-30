"""
EIQ Unit Conversion Utilities for the LORENZO POZZI Pesticide App.

This module provides conversion functions for application rates, 
active ingredient concentrations, and other units used in EIQ calculations.
"""

# Application rate conversion factors to lb/acre (standard for EIQ calculation)
APPLICATION_RATE_CONVERSION = {                 # CHECK WITH PAPER NOTES AND UPDATE, MANAGE SEEDS AND AMMONT/LENGTH 
    # Imperial units to lb/acre
    "lbs/acre": 1.0,      # Base unit
    "oz/acre": 1/16.0,    # 16 oz = 1 pound
    "fl oz/acre": 1/16.0, # Assuming density of 1.0 for liquids
    "pints/acre": 1.0,    # Assumption: 1 pint = 1 pound
    "quarts/acre": 2.0,   # Assumption: 1 quart = 2 pounds
    "gal/acre": 8.0,      # Assumption: 1 gallon = 8 pounds
    
    # Metric units to lb/acre
    "kg/ha": 0.892,       # 1 kg/ha = 0.892 lbs/acre
    "g/ha": 0.000892,     # 1 g/ha = 0.000892 lbs/acre
    "l/ha": 0.892,        # Assumption: 1 L/ha = 0.892 lbs/acre (density of 1.0)
    "ml/ha": 0.000892,    # 1 ml/ha = 0.000892 lbs/acre (density of 1.0)
}

# AI concentration conversion factors to decimal (for percentage calculations)
CONCENTRATION_CONVERSION = {
    "%": 0.01,            # Direct percentage (e.g., 50% = 0.5)
    "g/l": 0.001,         # Approximate conversion (e.g., 500 g/L ≈ 0.5 or 50%)
    "lb/gal": 0.00834      # Approximate conversion (e.g., 8.34 lb/gal ≈ 0.5 or 50%)     CHECK THIS
    # CFU / ML ??????????
}

def convert_application_rate(rate, from_unit, to_unit="lbs/acre"):
    """
    Convert application rate from one unit to another.
    
    Args:
        rate (float): Application rate value
        from_unit (str): Source unit of measure
        to_unit (str): Target unit of measure (default: lbs/acre for EIQ calculation)
    
    Returns:
        float: Converted application rate
    """
    if rate is None:
        return None
        
    if from_unit == to_unit:
        return rate
        
    try:
        # Convert to standard unit (lbs/acre)
        if from_unit in APPLICATION_RATE_CONVERSION:
            standard_rate = rate * APPLICATION_RATE_CONVERSION[from_unit]
            
            # If target is not the standard unit, convert to target
            if to_unit != "lbs/acre" and to_unit in APPLICATION_RATE_CONVERSION:
                return standard_rate / APPLICATION_RATE_CONVERSION[to_unit]
            
            return standard_rate
    except (ValueError, TypeError, ZeroDivisionError) as e:
        print(f"Error converting application rate: {e}")
        
    # Default return if conversion fails
    return rate

def convert_concentration_to_decimal(concentration, uom):
    """
    Convert concentration to decimal value (0-1) based on unit of measure.
    
    Args:
        concentration (float): Concentration value
        uom (str): Unit of measure for concentration
        
    Returns:
        float or None: Concentration as decimal (0-1)
    """
    if concentration is None:
        return None
        
    try:
        # Handle different UOMs using the conversion factors
        if uom in CONCENTRATION_CONVERSION:
            return float(concentration) * CONCENTRATION_CONVERSION[uom]
        else:
            # Default: assume value is already in percent
            return float(concentration) * 0.01
    except (ValueError, TypeError):
        return None

def convert_eiq_units(eiq_value, application_rate, rate_uom, ai_concentration, concentration_uom, applications=1):
    """
    Prepare all units for EIQ calculation to ensure mathematical correctness.
    
    Args:
        eiq_value (float): Base EIQ value for active ingredient [EIQ/lb of AI]
        application_rate (float): Application rate in original units
        rate_uom (str): Unit of measure for application rate
        ai_concentration (float): Active ingredient concentration in original units
        concentration_uom (str): Unit of measure for AI concentration
        applications (int): Number of applications
        
    Returns:
        tuple: (standardized_eiq, standardized_rate, standardized_concentration)
            All values standardized for calculation in the base formula
    """
    # Convert application rate to standard unit (lbs/acre)
    std_rate = convert_application_rate(application_rate, rate_uom)
    
    # Convert AI concentration to decimal (0-1)
    std_concentration = convert_concentration_to_decimal(ai_concentration, concentration_uom)
    
    # EIQ value remains unchanged (already in EIQ/lb)
    std_eiq = eiq_value
    
    return (std_eiq, std_rate, std_concentration)

def convert_concentration_to_percent(concentration, uom):
    """
    Convert concentration to percentage based on unit of measure.
    
    Args:
        concentration (float): Concentration value
        uom (str): Unit of measure for concentration
        
    Returns:
        float or None: Concentration as percentage (0-100)
    """
    # Get decimal value and convert to percentage
    decimal_value = convert_concentration_to_decimal(concentration, uom)
    if decimal_value is not None:
        return decimal_value * 100
    return None