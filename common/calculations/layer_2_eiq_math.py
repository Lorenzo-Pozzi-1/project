"""
Pure EIQ Calculation Functions (2nd Layer)
Only accepts standardized inputs, performs mathematical calculations only.
No UOM handling - all inputs must be pre-standardized.
"""

from typing import List, Dict
from dataclasses import dataclass

@dataclass
class EIQResult:
    """Container for EIQ calculation results"""
    field_eiq_per_ha: float
    breakdown: Dict = None  # Optional detailed breakdown

def calculate_field_eiq_single_ai(ai_concentration_per_unit: float,
                                ai_eiq_per_kg: float,  
                                rate_per_ha: float,
                                applications: int) -> float:
    """
    Calculate Field EIQ for a single active ingredient.
    
    All inputs must be in standardized units:
    - ai_concentration_per_unit: [kg AI/kg product] or [kg AI/L product]
    - ai_eiq_per_kg: [eiq/kg AI]
    - rate_per_ha: [kg product/ha] or [L product/ha] 
    - applications: dimensionless
    
    Formula: [kg/ha] × [kg/kg] × [eiq/kg] × applications = [eiq/ha]
             [L/ha] × [kg/L] × [eiq/kg] × applications = [eiq/ha]
    
    Returns:
        Field EIQ per hectare [eiq/ha]
    """
    if any(val <= 0 for val in [ai_concentration_per_unit, ai_eiq_per_kg, rate_per_ha]):
        return 0.0
    
    if applications <= 0:
        return 0.0
    
    # Pure mathematical calculation - units already validated
    field_eiq = rate_per_ha * ai_concentration_per_unit * ai_eiq_per_kg * applications
    
    return field_eiq

def calculate_field_eiq_product(standardized_ais: List[Dict],
                              rate_per_ha: float, 
                              applications: int) -> EIQResult:
    """
    Calculate Field EIQ for a product with multiple active ingredients.
    
    Args:
        standardized_ais: List of dicts with standardized AI data:
            - 'concentration_per_unit': [kg AI/kg product] or [kg AI/L product]
            - 'eiq_per_kg': [eiq/kg AI]
            - 'name': AI name (for breakdown)
        rate_per_ha: [kg product/ha] or [L product/ha]
        applications: dimensionless
        
    Returns:
        EIQResult with total field EIQ and optional breakdown
    """
    if not standardized_ais or rate_per_ha <= 0:
        return EIQResult(field_eiq_per_ha=0.0)
    
    total_field_eiq = 0.0
    breakdown = {}
    
    for ai in standardized_ais:
        ai_field_eiq = calculate_field_eiq_single_ai(
            ai_concentration_per_unit=ai['concentration_per_unit'],
            ai_eiq_per_kg=ai['eiq_per_kg'],
            rate_per_ha=rate_per_ha,
            applications=applications
        )
        
        total_field_eiq += ai_field_eiq
        breakdown[ai.get('name', 'Unknown')] = ai_field_eiq
    
    return EIQResult(
        field_eiq_per_ha=total_field_eiq,
        breakdown=breakdown
    )

def calculate_field_eiq_application(product_eiq_result: EIQResult) -> float:
    """
    Calculate Field EIQ for a single application.
    
    This is essentially a pass-through function for consistency in the hierarchy,
    but could be extended for application-specific adjustments.
    
    Args:
        product_eiq_result: Result from calculate_field_eiq_product
        
    Returns:
        Field EIQ per hectare [eiq/ha]
    """
    return product_eiq_result.field_eiq_per_ha

def calculate_field_eiq_scenario(application_eiq_values: List[float]) -> EIQResult:
    """
    Calculate total Field EIQ for a scenario (multiple applications).
    
    Args:
        application_eiq_values: List of Field EIQ values [eiq/ha] from individual applications
        
    Returns:
        EIQResult with total scenario EIQ and breakdown by application
    """
    if not application_eiq_values:
        return EIQResult(field_eiq_per_ha=0.0)
    
    total_scenario_eiq = sum(eiq for eiq in application_eiq_values if eiq > 0)
    
    breakdown = {
        f'Application {i+1}': eiq 
        for i, eiq in enumerate(application_eiq_values) 
        if eiq > 0
    }
    
    return EIQResult(
        field_eiq_per_ha=total_scenario_eiq,
        breakdown=breakdown
    )

# Convenience function for backward compatibility
def format_eiq_result(field_eiq: float) -> str:
    """Format EIQ results for display."""
    if field_eiq <= 0:
        return "0.00"
    return f"{field_eiq:.2f}"

def get_impact_category(field_eiq: float) -> tuple:
    """Get the impact category and color based on Field EIQ value."""
    if field_eiq < 33.3:
        return "Low Environmental Impact", "#E6F5E6"  # Light green
    elif field_eiq < 66.6:
        return "Moderate Environmental Impact", "#FFF5E6"  # Light yellow
    else:
        return "High Environmental Impact", "#F5E6E6"  # Light red