"""
Enhanced EIQ Calculation Functions for the LORENZO POZZI Pesticide App.

This module provides improved functions for calculating Environmental Impact Quotients
(EIQ) for pesticide products and applications with proper unit of measure handling.
"""

from eiq_calculator.eiq_conversions import standardize_eiq_calculation, get_uom_category

def calculate_field_eiq(ai_eiq, ai_percent, rate, unit, applications=1):
    """
    Calculate Field EIQ based on product data and application parameters.
    
    This function uses standardized conversion to ensure proper UOM handling.
    
    Args:
        ai_eiq (float): Active ingredient EIQ value (Cornell EIQ/lb)
        ai_percent (float): Active ingredient percentage (0-100)
        rate (float): Application rate
        unit (str): Unit of measure for rate
        applications (int): Number of applications
        
    Returns:
        float: Field EIQ value
    """
    try:
        # Use standardization function to get consistent units
        std_eiq, std_rate, _ = standardize_eiq_calculation(
            ai_eiq, rate, unit, ai_percent, "%")
        
        # Convert percentage to decimal (0-1)
        ai_decimal = ai_percent / 100.0
        
        # Calculate Field EIQ with standardized units
        # This gives us: (kg/ha or l/ha) × (decimal) × (EIQ/kg) × applications
        field_eiq = std_eiq * ai_decimal * std_rate * applications
        return field_eiq
    
    except (ValueError, ZeroDivisionError, TypeError) as e:
        print(f"Error calculating Field EIQ: {e}")
        return 0.0

def calculate_product_field_eiq(active_ingredients, rate, unit, applications=1):
    """
    Calculate total Field EIQ for a product with multiple active ingredients.
    
    Args:
        active_ingredients (list): List of dictionaries with 'eiq', 'percent', and 'name' keys
        rate (float): Application rate
        unit (str): Unit of measure for rate
        applications (int): Number of applications
        
    Returns:
        float: Total Field EIQ value for the product
    """
    if not active_ingredients:
        return 0.0
    
    # Verify we have a valid rate unit
    category = get_uom_category(unit)
    if category not in ["weight", "volume", "seed", "linear"]:
        print(f"Warning: Unknown application rate unit type: {unit}")
    
    # Sum contributions from all active ingredients
    total_field_eiq = 0.0
    
    for ai in active_ingredients:
        # Skip AIs with missing data
        if not ai or 'eiq' not in ai or 'percent' not in ai:
            continue
            
        # Handle case where eiq or percent might be stored as strings or have "--" placeholder
        if ai['eiq'] == "--" or ai['percent'] == "--":
            continue
            
        try:
            # Convert values to float if stored as string
            ai_eiq = float(ai['eiq']) if isinstance(ai['eiq'], str) else ai['eiq']
            
            # Handle percent that might be stored with "%" suffix
            percent_str = str(ai['percent'])
            percent_value = float(percent_str.replace('%', '')) if '%' in percent_str else float(ai['percent'])
            
            # Calculate individual AI's field EIQ using our standardized function
            ai_field_eiq = calculate_field_eiq(ai_eiq, percent_value, rate, unit)
            total_field_eiq += ai_field_eiq
            
        except (ValueError, TypeError) as e:
            print(f"Error calculating EIQ for active ingredient {ai.get('name', 'unknown')}: {e}")
            # Skip this ingredient but continue with others
            continue
    
    # Apply number of applications
    return total_field_eiq * applications

def format_eiq_result(field_eiq):
    """
    Format EIQ results for display, including per-ha values only.
    
    Args:
        field_eiq (float): Field EIQ value
        
    Returns:
        str: Formatted string with per-ha values
    """
    if field_eiq <= 0:
        return "0.00 /ha"
        
    # Standard calculation already gives per-ha values
    return f"{field_eiq:.2f} /ha"

def get_impact_category(field_eiq):
    """
    Get the impact category and color based on Field EIQ value.
    
    Args:
        field_eiq (float): Field EIQ value
        
    Returns:
        tuple: (rating, color) where rating is a string and color is a hex code
    """
    if field_eiq < 33.3:
        return "Low Environmental Impact", "#E6F5E6"  # Light green
    elif field_eiq < 66.6:
        return "Moderate Environmental Impact", "#FFF5E6"  # Light yellow
    else:
        return "High Environmental Impact", "#F5E6E6"  # Light red