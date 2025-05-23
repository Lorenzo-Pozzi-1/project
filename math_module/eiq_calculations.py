"""
EIQ Calculation Functions for the LORENZO POZZI Pesticide App.

This module provides functions for calculating Environmental Impact Quotients
(EIQ) for pesticide products and applications with proper unit of measure handling.
"""

from data.UOM_repository import UOMRepository, CompositeUOM

def calculate_field_eiq(ai_eiq, ai_percent, rate, unit, applications=1, user_preferences=None):
    """
    Calculate Field EIQ based on product data and application parameters.
    
    Args:
        ai_eiq (float): Active ingredient EIQ value (Cornell EIQ/lb)
        ai_percent (float): Active ingredient percentage (0-100)
        rate (float): Application rate
        unit (str): Unit of measure for rate
        applications (int): Number of applications
        user_preferences (dict): User preferences for conversions
        
    Returns:
        float: Field EIQ value
    """
    try:
        repo = UOMRepository.get_instance()
        from_uom = CompositeUOM(unit)
        
        # Determine target standard unit based on the type of application
        if from_uom.numerator and repo.get_base_unit(from_uom.numerator):
            num_unit = repo.get_base_unit(from_uom.numerator)
            if num_unit.category == 'weight':
                target_uom = CompositeUOM("kg/ha")
            elif num_unit.category == 'volume':
                target_uom = CompositeUOM("l/ha")
            else:
                # Fallback
                target_uom = CompositeUOM("kg/ha")
        else:
            target_uom = CompositeUOM("kg/ha")
        
        # Convert rate to standard units
        std_rate = repo.convert_composite_uom(rate, from_uom, target_uom, user_preferences)
        
        # Convert EIQ to metric (EIQ/kg)
        std_eiq = repo.convert_base_unit(ai_eiq, 'lbs', 'kg')  # Cornell EIQ is per pound
        
        # Convert percentage to decimal
        ai_decimal = ai_percent / 100.0
        
        # Calculate Field EIQ: (EIQ/kg) × (decimal) × (kg/ha or l/ha) × applications
        field_eiq = std_eiq * ai_decimal * std_rate * applications
        return field_eiq
    
    except (ValueError, ZeroDivisionError, TypeError) as e:
        print(f"Error calculating Field EIQ: {e}")
        return 0.0

def calculate_product_field_eiq(active_ingredients, rate, unit, applications=1, user_preferences=None):
    """
    Calculate total Field EIQ for a product with multiple active ingredients.
    
    Args:
        active_ingredients (list): List of dictionaries with 'eiq', 'percent', and 'name' keys
        rate (float): Application rate
        unit (str): Unit of measure for rate
        applications (int): Number of applications
        user_preferences (dict): User preferences for row spacing, seeding rate, etc.
        
    Returns:
        float: Total Field EIQ value for the product
    """
    if not active_ingredients:
        return 0.0
    
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
            
            # Calculate individual AI's field EIQ using the new system
            # Note: applications=1 here since we apply it at the end for the total
            ai_field_eiq = calculate_field_eiq(
                ai_eiq, percent_value, rate, unit, applications=1, user_preferences=user_preferences
            )
            total_field_eiq += ai_field_eiq
            
        except (ValueError, TypeError) as e:
            print(f"Error calculating EIQ for active ingredient {ai.get('name', 'unknown')}: {e}")
            # Skip this ingredient but continue with others
            continue
    
    # Apply number of applications to the total
    return total_field_eiq * applications

def format_eiq_result(field_eiq):
    """
    Format EIQ results for display.
    
    Args:
        field_eiq (float): Field EIQ value
        
    Returns:
        string: result eiq/ha formatted
    """
    if field_eiq <= 0:
        return "0.00"
    
    return f"{field_eiq:.2f}"

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