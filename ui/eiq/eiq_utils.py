"""
EIQ Utilities for the LORENZO POZZI Pesticide App.

This module provides common utilities for EIQ calculations across different components.
"""

from data.products_data import load_products, get_product_by_name

# Unit conversion factors for EIQ calculations
UNIT_CONVERSION = {
    "quarts/acre": 2.0,    # Assumption: 1 quart = 2 pounds
    "pints/acre": 1.0,     # Assumption: 1 pint = 1 pound
    "fl oz/acre": 1/16.0,  # 16 fl oz = 1 pound
    "oz/acre": 1/16.0,     # 16 oz = 1 pound
    "lbs/acre": 1.0,
    "kg/ha": 0.892         # 1 kg/ha = 0.892 lbs/acre
}

def get_products_from_csv():
    """
    Load products from CSV data.
    If CSV data is not available, return an empty list.
    """
    try:
        products = load_products()
        return products
    except Exception as e:
        print(f"Error loading products from CSV: {e}")
        return []

def get_product_display_names():
    """
    Get a list of product display names from CSV data.
    """
    products = get_products_from_csv()
    if products:
        # Use display_name property if available
        return ["Select a product..."] + [p.display_name for p in products]

def get_product_info(product_name):
    """
    Get product information from CSV
    
    Args:
        product_name (str): Name of the product
        
    Returns:
        dict: Product data containing ai1_eiq, ai_percent, etc.
    """
    # First try to get product from CSV
    product = get_product_by_name(product_name.split(" (")[0])
    
    if product:
        # Now using AI1 EIQ instead of base EIQ
        ai1_eiq = product.ai1_eiq if product.ai1_eiq is not None else 0.0
        
        # Updated from ai1_concentration to ai1_concentration_percent
        ai_percent = product.ai1_concentration_percent if product.ai1_concentration_percent is not None else 0.0
        
        if product.label_suggested_rate is not None:
            rate = product.label_suggested_rate
        elif product.label_minimum_rate is not None:
            rate = product.label_minimum_rate
        else:
            rate = 0.0
            
        unit = product.rate_uom or "lbs/acre"
        
        return {
            "ai1_eiq": ai1_eiq,
            "ai_percent": ai_percent,
            "default_rate": rate,
            "default_unit": unit
        }
    
    # Default values if product not found
    return {
        "ai1_eiq": 0.0,
        "ai_percent": 0.0,
        "default_rate": 0.0,
        "default_unit": "lbs/acre"
    }

def calculate_field_eiq(ai1_eiq, ai_percent, rate, unit, applications=1):
    """
    Calculate Field EIQ based on product data and application parameters.
    
    Args:
        ai1_eiq (float): AI1 EIQ value
        ai_percent (float): Active ingredient percentage (0-100)
        rate (float): Application rate
        unit (str): Unit of measure for rate
        applications (int): Number of applications
        
    Returns:
        float: Field EIQ value
    """
    try:
        # Convert to decimal
        ai_decimal = ai_percent / 100.0
        
        # Convert rate to pounds/acre based on unit
        if unit in UNIT_CONVERSION:
            rate_in_pounds = rate * UNIT_CONVERSION[unit]
        else:
            # Default if unit not recognized
            rate_in_pounds = rate
        
        # Calculate Field EIQ
        field_eiq = ai1_eiq * ai_decimal * rate_in_pounds * applications
        return field_eiq
    
    except (ValueError, ZeroDivisionError, TypeError) as e:
        print(f"Error calculating Field EIQ: {e}")
        return 0.0

def get_impact_category(field_eiq):
    """
    Get the impact category and color based on Field EIQ value.
    
    Args:
        field_eiq (float): Field EIQ value
        
    Returns:
        tuple: (rating, color) where rating is a string and color is a hex code
    """
    if field_eiq < 20:
        return "Low Environmental Impact", "#E6F5E6"  # Light green
    elif field_eiq < 40:
        return "Moderate Environmental Impact", "#FFF5E6"  # Light yellow
    else:
        return "High Environmental Impact", "#F5E6E6"  # Light red