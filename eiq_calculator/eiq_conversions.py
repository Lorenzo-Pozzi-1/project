"""
Enhanced EIQ Unit Conversion Utilities for the LORENZO POZZI Pesticide App.

This module provides improved conversion functions for application rates, 
active ingredient concentrations, and other units used in EIQ calculations.
Uses a single unified data structure for UOM classification and conversion factors.
"""

# Unified UOM data structure
# Each UOM has its category and conversion factor to the standard unit for that category
UOM_DATA = {
    # Weight-based application rates (standard: kg/ha)
    "lbs/acre": {"category": "weight", "factor": 1.12085, "standard": "kg/ha"},  # 1 [lb/acre] = 1.12085 [kg/ha]
    "oz/acre": {"category": "weight", "factor": 0.070053, "standard": "kg/ha"},  # 1 [oz/acre] = 0.070053 [kg/ha]
    "kg/ha": {"category": "weight", "factor": 1.0, "standard": "kg/ha"},         # Already in standard unit
    "g/ha": {"category": "weight", "factor": 0.001, "standard": "kg/ha"},        # 1 [g/ha] = 0.001 [kg/ha]
    
    # Volume-based application rates (standard: l/ha)
    "fl oz/acre": {"category": "volume", "factor": 0.073078, "standard": "l/ha"},  # 1 [fl oz/acre] = 0.073078 [l/ha]
    "pt/acre": {"category": "volume", "factor": 1.16924, "standard": "l/ha"},      # 1 [pt/acre] = 1.16924 [l/ha]
    "qt/acre": {"category": "volume", "factor": 2.33849, "standard": "l/ha"},      # 1 [qt/acre] = 2.33849 [l/ha]
    "gal/acre": {"category": "volume", "factor": 9.35396, "standard": "l/ha"},     # 1 [gal/acre] = 9.35396 [l/ha]
    "l/ha": {"category": "volume", "factor": 1.0, "standard": "l/ha"},             # Already in standard unit
    "ml/ha": {"category": "volume", "factor": 0.001, "standard": "l/ha"},          # 1 [ml/ha] = 0.001 [l/ha]
    "ml/acre": {"category": "volume", "factor": 0.00247105, "standard": "l/ha"},   # 1 [ml/acre] = 0.00247105 [l/ha]
    
    # Miscellaneous (this is for a seed treatment product that gives concntration to reach in a solution in which the seeds should be soaked)
    "fl oz/100 gal": {"category": "misc", "factor": 0.0, "standard": "misc"},  # Placeholder
    
    # Seed treatments (standard: kg/100kg seed)
    "fl oz/cwt": {"category": "seed", "factor": 0.0, "standard": "kg/100kg"},  # Placeholder
    "oz/cwt": {"category": "seed", "factor": 0.0, "standard": "kg/100kg"},     # Placeholder
    "g/cwt": {"category": "seed", "factor": 0.0, "standard": "kg/100kg"},      # Placeholder
    "lb/cwt": {"category": "seed", "factor": 0.0, "standard": "kg/100kg"},     # Placeholder
    "ml/100 kg": {"category": "seed", "factor": 0.0, "standard": "kg/100kg"},  # Placeholder
    "oz/100 gal": {"category": "seed", "factor": 0.0, "standard": "kg/100kg"}, # Placeholder
    
    # Linear application rates for 34-inch row spacing
    "fl oz/1000 ft": {"category": "linear", "factor": 1.123939, "standard": "l/ha"},  # 15.380 [fl oz/acre per fl oz/1000 ft] * 0.073078 [l/ha per fl oz/acre] = 1.123939 [l/ha per fl oz/1000 ft]
    "ml/100 m": {"category": "linear", "factor": 0.115824, "standard": "l/ha"},       # 1 [ml/100 m] = 0.115824 [l/ha]
    "oz/1000 ft": {"category": "linear", "factor": 1.077415, "standard": "kg/ha"},    # 15.380 [oz/acre per oz/1000 ft] * 0.070053 [kg/ha per oz/acre] = 1.077415 [kg/ha per oz/1000 ft]
    
    # Concentration units (all convert to decimal 0-1)
    "%": {"category": "concentration", "factor": 0.01, "standard": "decimal"},           # 1% = 0.01 [kg/kg] or [l/l]
    "g/l": {"category": "concentration", "factor": 0.001, "standard": "decimal"},        # 1 [g/l] = 0.001 [kg/l]
    "lb/gal": {"category": "concentration", "factor": 0.119826, "standard": "decimal"},  # 1 [lb/gal] = 0.119826 [kg/l]
    "g/kg": {"category": "concentration", "factor": 0.001, "standard": "decimal"},       # 1 [g/kg] = 0.001 [kg/kg]
    "cfu/ml": {"category": "concentration", "factor": 0.0, "standard": "decimal"},       # Placeholder for a biological product that gives CFU/ml
}

# For backward compatibility, create APPLICATION_RATE_CONVERSION from the unified structure
APPLICATION_RATE_CONVERSION = {uom: data["factor"] for uom, data in UOM_DATA.items() 
                              if data["category"] in ["weight", "volume", "seed", "linear"]}

# Create CONCENTRATION_CONVERSION from the unified structure
CONCENTRATION_CONVERSION = {uom: data["factor"] for uom, data in UOM_DATA.items() 
                          if data["category"] == "concentration"}

# UOM classification functions
def get_uom_category(uom):
    """
    Get the category of a unit of measure.
    
    Args:
        uom (str): Unit of measure
        
    Returns:
        str: Category ("weight", "volume", "seed", "linear", "concentration", or None)
    """
    if uom is None:
        return None
        
    uom_lower = uom.lower()
    
    # Check if the UOM is directly in our data structure
    for key, data in UOM_DATA.items():
        if key.lower() == uom_lower:
            return data["category"]
            
    # Special case for percentage notation
    if "%" in uom_lower:
        return "concentration"
        
    return None

def is_weight_uom(uom):
    """Determine if the UOM is weight-based."""
    return get_uom_category(uom) == "weight"

def is_volume_uom(uom):
    """Determine if the UOM is volume-based."""
    return get_uom_category(uom) == "volume"

def is_seed_treatment_uom(uom):
    """Determine if the UOM is for seed treatments."""
    return get_uom_category(uom) == "seed"

def is_linear_uom(uom):
    """Determine if the UOM is for linear applications."""
    return get_uom_category(uom) == "linear"

def is_concentration_uom(uom):
    """Determine if the UOM is for concentration."""
    return get_uom_category(uom) == "concentration"

def get_standard_unit(uom):
    """
    Get the standard unit for a given UOM's category.
    
    Args:
        uom (str): Source unit of measure
        
    Returns:
        str: Standard unit for the category, or None if not found
    """
    if uom is None:
        return None
        
    uom_lower = uom.lower()
    
    for key, data in UOM_DATA.items():
        if key.lower() == uom_lower:
            return data["standard"]
            
    return None

def get_conversion_factor(uom):
    """
    Get the conversion factor for a unit of measure.
    
    Args:
        uom (str): Unit of measure
        
    Returns:
        float: Conversion factor to standard unit, or None if not found
    """
    if uom is None:
        return None
        
    uom_lower = uom.lower()
    
    for key, data in UOM_DATA.items():
        if key.lower() == uom_lower:
            return data["factor"]
            
    # Special case for percentage notation
    if "%" in uom_lower:
        return 0.01  # 1% = 0.01 decimal
            
    return None

# Conversion functions for application rates
def convert_application_rate(rate, from_uom, to_uom=None):
    """
    Convert application rate from one unit to another.
    
    Args:
        rate (float): Application rate value
        from_uom (str): Source unit of measure
        to_uom (str): Target unit of measure (if None, converts to standard unit)
        
    Returns:
        float: Converted application rate
    """
    if rate is None or from_uom is None:
        return None
    
    # Get category and standard unit for source UOM
    category = get_uom_category(from_uom)
    if category is None:
        return rate  # Unknown UOM, return unchanged
        
    # Find the standard unit for this category
    standard_unit = None
    for key, data in UOM_DATA.items():
        if data["category"] == category and key.lower() == from_uom.lower():
            standard_unit = data["standard"]
            break
    
    # If standard unit not found, or no target unit specified, use the standard unit for the category
    if to_uom is None:
        if standard_unit is None:
            return rate  # Can't determine standard unit, return unchanged
        to_uom = standard_unit
    
    # If source and target are the same, return unchanged
    if from_uom.lower() == to_uom.lower():
        return rate
    
    # Get conversion factors
    from_factor = get_conversion_factor(from_uom)
    to_factor = get_conversion_factor(to_uom)
    
    if from_factor is None or to_factor is None:
        return rate  # Unknown conversion factor, return unchanged
    
    # Convert to standard unit, then to target unit
    try:
        standard_value = rate * from_factor
        result = standard_value / to_factor
        return result
    except (ValueError, TypeError, ZeroDivisionError) as e:
        print(f"Error converting application rate: {e}")
        return rate

# Concentration conversion functions
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
        # Convert concentration to float
        concentration_float = float(concentration)
        
        # Get conversion factor
        factor = get_conversion_factor(uom)
        
        if factor is not None:
            return concentration_float * factor
        
        # Default behavior for unknown UOMs: if it contains "%", treat as percentage
        if uom and "%" in uom:
            return concentration_float * 0.01
            
        # Otherwise return as is
        return concentration_float
            
    except (ValueError, TypeError):
        return None

def convert_concentration_to_percent(concentration, uom):
    """
    Convert concentration to percentage (0-100) based on unit of measure.
    
    Args:
        concentration (float): Concentration value
        uom (str): Unit of measure for concentration
        
    Returns:
        float or None: Concentration as percentage (0-100)
    """
    decimal = convert_concentration_to_decimal(concentration, uom)
    if decimal is not None:
        return decimal * 100
    return None

# EIQ conversion functions
def convert_eiq_to_metric(eiq_value):
    """
    Convert Cornell EIQ (EIQ/lb) to metric EIQ (EIQ/kg).
    
    Args:
        eiq_value (float): EIQ value in EIQ/lb
        
    Returns:
        float: EIQ value in EIQ/kg
    """
    if eiq_value is None:
        return None
        
    # 1 lb = 0.453592 kg, so EIQ/kg = EIQ/lb ÷ 0.453592
    try:
        return float(eiq_value) / 0.453592
    except (ValueError, TypeError):
        return None

# Provide convert_eiq_units for backward compatibility
def convert_eiq_units(eiq_value, application_rate, rate_uom, ai_concentration, concentration_uom, applications=1):
    """
    Prepare all units for EIQ calculation to ensure mathematical correctness.
    
    This function is maintained for backward compatibility and uses the improved
    standardization function internally.
    
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
    # Use the new standardization function
    return standardize_eiq_calculation(
        eiq_value, application_rate, rate_uom, ai_concentration, concentration_uom)

# Main standardization function
# Update in standardize_eiq_calculation function:

def standardize_eiq_calculation(eiq_value, application_rate, rate_uom, ai_concentration, concentration_uom):
    """
    Standardize all values for consistent EIQ calculation based on application type.
    
    Args:
        eiq_value (float): Cornell EIQ value (EIQ/lb of AI)
        application_rate (float): Application rate value
        rate_uom (str): Unit of measure for application rate
        ai_concentration (float): AI concentration value 
        concentration_uom (str): Unit of measure for concentration
        
    Returns:
        tuple: (standardized_eiq, standardized_rate, standardized_concentration)
              All values standardized for calculation in the base formula
    """
    # Determine application category
    category = get_uom_category(rate_uom)
    
    # Convert application rate to standard unit based on category
    if category == "weight":
        std_rate = convert_application_rate(application_rate, rate_uom, "kg/ha")
    elif category == "volume":
        std_rate = convert_application_rate(application_rate, rate_uom, "l/ha")
    elif category == "seed":
        std_rate = convert_application_rate(application_rate, rate_uom, "kg/100kg")
    elif category == "linear":
        # For linear measures, check if volume or weight based
        if "fl" in rate_uom.lower() or "ml" in rate_uom.lower():
            std_rate = convert_application_rate(application_rate, rate_uom, "l/ha")
        else:
            std_rate = convert_application_rate(application_rate, rate_uom, "kg/ha")
    else:
        # Unknown application type, use as is
        std_rate = application_rate
        print(f"Unknown application rate unit: {rate_uom}. Using original value.")
    
    # For all cases, convert concentration to decimal
    std_concentration = convert_concentration_to_decimal(ai_concentration, concentration_uom)
    
    # Convert Cornell EIQ from EIQ/lb to EIQ/kg for all cases
    std_eiq = convert_eiq_to_metric(eiq_value)
    
    return std_eiq, std_rate, std_concentration