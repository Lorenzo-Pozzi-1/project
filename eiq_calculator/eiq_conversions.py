"""
EIQ Unit Conversion Utilities for the LORENZO POZZI Pesticide App.

This module provides conversion functions for application rates, 
active ingredient concentrations, and other units used in EIQ calculations.
"""

# Application rate conversion factors to kg/ha or l/ha (! incoherent when multiplied by [EIQ/lb of AI] !)
APPLICATION_RATE_CONVERSION = {    # CHECK WITH PAPER NOTES AND UPDATE, MANAGE SEEDS AND AMMOUNT/LENGTH 
    # Imperial
    "lbs/acre"   : 1.121,     # to kg/ha
    "oz/acre"    : 70.05,     # to kg/ha
    "fl oz/acre" : 0.0730778, # to l/ha
    "pt/acre"    : 1.16924,   # to l/ha
    "qt/acre"    : 2.33849,   # to l/ha
    "gal/acre"   : 11.2336,   # to l/ha
    
    # Metric
    "kg/ha": 1,     # to kg/ha
    "g/ha" : 0.001, # to kg/ha
    "l/ha" : 1,     # to l/ha
    "ml/ha": 0.001, # to l/ha

    # silly
    "fl oz/100 gal": 0.0, # CHECK
    "ml/acre"      : 0.00247105, # to l/ha
    
    # Seed treatments
    "fl oz/cwt" : 0.0, # CHECK
    "oz/cwt"    : 0.0, # CHECK
    "g/cwt"     : 0.0, # CHECK
    "lb/cwt"    : 0.0, # CHECK
    "ml/100 kg" : 0.0, # CHECK
    "oz/100 gal": 0.0, # CHECK-----

    # Linear
    "fl oz/1000 ft": 0.0, # CHECK
    "ml/100 m"     : 0.0, # CHECK
    "oz/1000 ft"   : 0.0, # CHECK
}

# AI concentration conversion factors to metric
CONCENTRATION_CONVERSION = {
    "%"     : 0.0, # CHECK
    "g/l"   : 0.0, # CHECK
    "lb/gal": 0.0, # CHECK
    "cgu/ml": 0.0  # CHECK
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