"""
Pure EIQ Calculation Functions (Layer 3).
Only accepts standardized inputs, performs mathematical calculations only.
No UOM handling - all inputs must be pre-standardized.
"""

from typing import List, Dict
from common.widgets.tracer import calculation_tracer
from dataclasses import dataclass

@dataclass
class EIQResult:
    """Container for EIQ calculation results"""
    field_eiq_per_ha: float
    breakdown: Dict = None  # More info on individual components if needed

def calculate_field_eiq_single_ai(ai_concentration_per_unit: float,
                                ai_eiq_per_kg: float,  
                                rate_per_ha: float,
                                applications: int) -> float:
    """
    Calculate Field EIQ for a single active ingredient.
    
    All inputs must be in standardized units:
    - ai_concentration_per_unit: [kg AI/kg product] or [kg AI/l product]
    - ai_eiq_per_kg: [eiq/kg AI]
    - rate_per_ha: [kg product/ha] or [l product/ha] 
    - applications: dimensionless number of applications
    
    Formula: [kg/ha] x [kg/kg] x [eiq/kg] x applications = [eiq/ha]
          or [l/ha]  x [kg/l]  x [eiq/kg] x applications = [eiq/ha]
    
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
            - 'concentration_per_unit': [kg AI/kg product] or [kg AI/l product]
            - 'eiq_per_kg': [eiq/kg AI]
            - 'name': AI name (for breakdown)
        rate_per_ha: [kg product/ha] or [l product/ha]
        applications: dimensionless number of applications
        
    Returns:
        EIQResult with total field EIQ and breakdown
    """
    if not standardized_ais or rate_per_ha <= 0:
        return EIQResult(field_eiq_per_ha=0.0)
    
    total_field_eiq = 0.0
    breakdown = {}
    
    # Calculate for each AI and log the formula
    for ai in standardized_ais:
        ai_field_eiq = calculate_field_eiq_single_ai(
            ai_concentration_per_unit=ai['concentration_per_unit'],
            ai_eiq_per_kg=ai['eiq_per_kg'],
            rate_per_ha=rate_per_ha,
            applications=applications
        )
        
        calculation_tracer.log_calculation_formula(
            ai['name'], f"{rate_per_ha:.1f}", f"{ai['concentration_per_unit']:.4f}",
            f"{ai['eiq_per_kg']:.1f}", applications, f"{ai_field_eiq:.1f}"
        )
        
        total_field_eiq += ai_field_eiq
        breakdown[ai.get('name', 'Unknown')] = ai_field_eiq
    
    # Log total if multiple AIs
    calculation_tracer.log_total_calculation(breakdown, total_field_eiq)
    
    return EIQResult(
        field_eiq_per_ha=total_field_eiq,
        breakdown=breakdown
    )

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
    
    valid_eiq_values = [eiq for eiq in application_eiq_values if eiq >= 0]
    total_scenario_eiq = sum(valid_eiq_values)
    
    # Log scenario calculation if multiple applications
    if len(valid_eiq_values) > 1:
        calculation_tracer.log_step("Scenario Total")
        total_parts = " + ".join([f"{eiq:.1f}" for eiq in valid_eiq_values])
        calculation_tracer.log_substep(f"Total: {total_parts} = {total_scenario_eiq:.1f} eiq/ha", level=1, is_last=True)
    
    breakdown = {
        f'Application {i+1}': eiq 
        for i, eiq in enumerate(application_eiq_values) 
        if eiq >= 0
    }
    
    return EIQResult(
        field_eiq_per_ha=total_scenario_eiq,
        breakdown=breakdown
    )