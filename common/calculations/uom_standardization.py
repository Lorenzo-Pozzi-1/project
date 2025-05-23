"""
UOM Standardization (1st Layer) for EIQ Calculations
Handles all unit conversions and dimensional analysis validation
"""

from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from data.repository_UOM import UOMRepository, CompositeUOM

@dataclass
class StandardizedEIQInputs:
    """Container for standardized EIQ calculation inputs"""
    rate_per_ha: float                    # [kg/ha] or [L/ha] 
    rate_unit_type: str                   # "weight" or "volume"
    ai_concentration_per_unit: float      # [kg/kg] or [kg/L]
    ai_eiq_per_kg: float                  # [eiq/kg]
    applications: int                     # dimensionless

@dataclass
class ProductStandardizedInputs:
    """Container for standardized product-level inputs"""
    rate_per_ha: float                    # [kg/ha] or [L/ha]
    rate_unit_type: str                   # "weight" or "volume" 
    active_ingredients: List[Dict]        # List of standardized AI data
    applications: int                     # dimensionless

class EIQUOMStandardizer:
    """
    Handles all UOM conversions and validations for EIQ calculations.
    Ensures dimensional analysis is correct before passing to calculation layer.
    """
    
    def __init__(self):
        self.uom_repo = UOMRepository.get_instance()
    
    def standardize_single_ai_inputs(self, 
                                   ai_eiq: float,
                                   ai_concentration: float, 
                                   ai_concentration_uom: str,
                                   application_rate: float,
                                   application_rate_uom: str,
                                   applications: int,
                                   user_preferences: dict = None) -> StandardizedEIQInputs:
        """
        Standardize all inputs for single AI EIQ calculation.
        
        Returns standardized inputs where dimensional analysis checks out:
        [kg/ha] × [kg/kg] × [eiq/kg] = [eiq/ha] OR
        [L/ha] × [kg/L] × [eiq/kg] = [eiq/ha]
        """
        
        # Step 1: Standardize application rate to [kg/ha] or [L/ha]
        rate_per_ha, rate_unit_type = self._standardize_application_rate(
            application_rate, application_rate_uom, user_preferences
        )
        
        # Step 2: Standardize AI concentration to match rate units
        ai_concentration_per_unit = self._standardize_ai_concentration(
            ai_concentration, ai_concentration_uom, rate_unit_type
        )
        
        # Step 3: Standardize EIQ to [eiq/kg] (Cornell is eiq/lb)
        ai_eiq_per_kg = self._standardize_ai_eiq(ai_eiq)
        
        # Step 4: Validate dimensional analysis
        self._validate_dimensional_analysis(rate_unit_type, ai_concentration_per_unit)
        
        return StandardizedEIQInputs(
            rate_per_ha=rate_per_ha,
            rate_unit_type=rate_unit_type,
            ai_concentration_per_unit=ai_concentration_per_unit,
            ai_eiq_per_kg=ai_eiq_per_kg,
            applications=applications
        )
    
    def standardize_product_inputs(self,
                                 active_ingredients: List[Dict],
                                 application_rate: float,
                                 application_rate_uom: str, 
                                 applications: int,
                                 user_preferences: dict = None) -> ProductStandardizedInputs:
        """
        Standardize inputs for product-level EIQ calculation.
        
        Args:
            active_ingredients: List of dicts with 'eiq', 'concentration', 'uom', 'name'
            application_rate: Product application rate
            application_rate_uom: UOM for application rate
            applications: Number of applications
            user_preferences: User preferences for conversions
            
        Returns:
            ProductStandardizedInputs with all AIs standardized consistently
        """
        
        # Step 1: Standardize application rate
        rate_per_ha, rate_unit_type = self._standardize_application_rate(
            application_rate, application_rate_uom, user_preferences
        )
        
        # Step 2: Standardize all active ingredients to match rate units
        standardized_ais = []
        for ai in active_ingredients:
            if not ai or ai.get('eiq') in [None, "--"] or ai.get('concentration') in [None, "--"]:
                continue
                
            try:
                standardized_ai = self.standardize_single_ai_inputs(
                    ai_eiq=float(ai['eiq']),
                    ai_concentration=float(ai['concentration']),
                    ai_concentration_uom=ai['uom'],
                    application_rate=application_rate,
                    application_rate_uom=application_rate_uom,
                    applications=1,  # Will be applied at product level
                    user_preferences=user_preferences
                )
                
                standardized_ais.append({
                    'name': ai.get('name', 'Unknown'),
                    'concentration_per_unit': standardized_ai.ai_concentration_per_unit,
                    'eiq_per_kg': standardized_ai.ai_eiq_per_kg
                })
                
            except Exception as e:
                print(f"Error standardizing AI {ai.get('name', 'unknown')}: {e}")
                continue
        
        return ProductStandardizedInputs(
            rate_per_ha=rate_per_ha,
            rate_unit_type=rate_unit_type,
            active_ingredients=standardized_ais,
            applications=applications
        )
    
    def _standardize_application_rate(self, 
                                    rate: float, 
                                    rate_uom: str, 
                                    user_preferences: dict = None) -> Tuple[float, str]:
        """
        Convert application rate to standard [kg/ha] or [L/ha].
        
        Returns:
            Tuple of (standardized_rate, unit_type) where unit_type is "weight" or "volume"
        """
        if not rate or not rate_uom:
            raise ValueError("Application rate and UOM are required")
        
        from_uom = CompositeUOM(rate_uom)
        
        # Determine target unit based on numerator type
        numerator_unit = self.uom_repo.get_base_unit(from_uom.numerator)
        if not numerator_unit:
            raise ValueError(f"Unknown unit in rate: {from_uom.numerator}")
        
        if numerator_unit.category == 'weight':
            target_uom = CompositeUOM("kg/ha")
            unit_type = "weight"
        elif numerator_unit.category == 'volume':
            target_uom = CompositeUOM("l/ha") 
            unit_type = "volume"
        else:
            raise ValueError(f"Application rate must be weight/area or volume/area, got: {rate_uom}")
        
        # Convert to standard rate
        standardized_rate = self.uom_repo.convert_composite_uom(
            rate, from_uom, target_uom, user_preferences
        )
        
        return standardized_rate, unit_type
    
    def _standardize_ai_concentration(self, 
                                    concentration: float, 
                                    concentration_uom: str, 
                                    target_rate_type: str) -> float:
        """
        Convert AI concentration to match the application rate units.
        
        Args:
            concentration: AI concentration value
            concentration_uom: UOM for concentration (%, g/L, lb/gal, etc.)
            target_rate_type: "weight" or "volume" to match application rate
            
        Returns:
            Standardized concentration as [kg/kg] or [kg/L]
        """
        if not concentration or not concentration_uom:
            raise ValueError("AI concentration and UOM are required")
        
        # Handle percentage
        if concentration_uom == '%':
            return concentration / 100.0  # Convert to decimal [kg/kg]
        
        from_uom = CompositeUOM(concentration_uom)
        
        # Determine target concentration UOM based on rate type
        if target_rate_type == "weight":
            target_uom = CompositeUOM("kg/kg")  # [kg AI / kg product]
        elif target_rate_type == "volume":
            target_uom = CompositeUOM("kg/l")   # [kg AI / L product]
        else:
            raise ValueError(f"Invalid rate type: {target_rate_type}")
        
        # Convert concentration
        standardized_concentration = self.uom_repo.convert_composite_uom(
            concentration, from_uom, target_uom
        )
        
        return standardized_concentration
    
    def _standardize_ai_eiq(self, ai_eiq: float) -> float:
        """
        Convert AI EIQ from Cornell units (eiq/lb) to standard (eiq/kg).
        
        Args:
            ai_eiq: EIQ value from Cornell database (eiq/lb)
            
        Returns:
            EIQ in standard units (eiq/kg)
        """
        if not ai_eiq:
            raise ValueError("AI EIQ value is required")
        
        # Cornell EIQ is per pound, convert to per kg
        return self.uom_repo.convert_base_unit(ai_eiq, 'lbs', 'kg')
    
    def _validate_dimensional_analysis(self, rate_unit_type: str, ai_concentration: float):
        """
        Validate that dimensional analysis will work correctly.
        
        Expected outcomes:
        - Weight rate: [kg/ha] × [kg/kg] × [eiq/kg] = [eiq/ha]
        - Volume rate: [L/ha] × [kg/L] × [eiq/kg] = [eiq/ha]
        """
        if rate_unit_type not in ["weight", "volume"]:
            raise ValueError(f"Invalid rate unit type: {rate_unit_type}")
        
        if ai_concentration <= 0:
            raise ValueError("AI concentration must be positive")
        
        # Additional validations could go here
        # For example, checking reasonable ranges for concentrations
        if rate_unit_type == "weight" and ai_concentration > 1.0:
            raise ValueError("Weight-based concentration cannot exceed 1.0 (100%)")