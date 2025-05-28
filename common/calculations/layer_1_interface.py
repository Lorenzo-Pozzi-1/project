"""
Unified EIQ Calculation Interface
Combines both layers into clean, easy-to-use functions for the UI.
Handles UOM standardization internally, exposes simple interfaces.
"""

from typing import List, Dict
from .layer_2_uom_std import EIQUOMStandardizer
from .layer_3_eiq_math import calculate_field_eiq_product, calculate_field_eiq_scenario

class EIQCalculator:
    """
    Main interface for EIQ calculations throughout the application.
    Handles UOM standardization internally and provides clean interfaces.
    """
    
    def __init__(self):
        self.standardizer = EIQUOMStandardizer()
    
    def calculate_product_field_eiq(self,
                                  active_ingredients: List[Dict],
                                  application_rate: float,
                                  application_rate_uom: str,
                                  applications: int = 1,
                                  user_preferences: dict = None) -> float:
        """
        Calculate Field EIQ for a product with multiple active ingredients.
        
        Args:
            active_ingredients: List of dicts with 'eiq', 'concentration', 'uom', 'name'
            application_rate: Product application rate
            application_rate_uom: UOM for application rate
            applications: Number of applications
            user_preferences: User preferences for UOM conversions
            
        Returns:
            Total Field EIQ [eiq/ha]
        """
        try:
            print(f"\nI have to calculate_product_field_EIQ")
            # Layer 1: Standardize inputs
            standardized = self.standardizer.standardize_product_inputs(
                active_ingredients=active_ingredients,
                application_rate=application_rate,
                application_rate_uom=application_rate_uom,
                applications=applications,
                user_preferences=user_preferences
            )
            
            # Layer 2: Pure calculation
            result = calculate_field_eiq_product(
                standardized_ais=standardized.active_ingredients,
                rate_per_ha=standardized.rate_per_ha,
                applications=standardized.applications
            )
            
            return result.field_eiq_per_ha
            
        except Exception as e:
            print(f"Layer 1.calculate_product_field_eiq: Error calculating product Field EIQ: {e}")
            return 0.0
    
    def calculate_scenario_field_eiq(self,
                                   applications: List[Dict],
                                   user_preferences: dict = None) -> float:
        """
        Calculate total Field EIQ for a scenario (multiple applications).
        
        Args:
            applications: List of application dicts with product and rate info
            user_preferences: User preferences for UOM conversions
            
        Returns:
            Total scenario Field EIQ [eiq/ha]
        """
        try:
            application_eiq_values = []
            
            for app in applications:
                # Extract application data
                product = app.get('product')
                if not product:
                    continue
                
                # Get active ingredients data
                active_ingredients = product.get_ai_data() if hasattr(product, 'get_ai_data') else []
                if not active_ingredients:
                    continue
                
                # Calculate EIQ for this application
                app_eiq = self.calculate_product_field_eiq(
                    active_ingredients=active_ingredients,
                    application_rate=app.get('rate', 0),
                    application_rate_uom=app.get('rate_uom', ''),
                    applications=1,  # Each application is counted once
                    user_preferences=user_preferences
                )
                
                application_eiq_values.append(app_eiq)
            
            # Sum all application EIQs
            scenario_result = calculate_field_eiq_scenario(application_eiq_values)
            return scenario_result.field_eiq_per_ha
            
        except Exception as e:
            print(f"Layer 1.calculate_scenario_field_eiq: Error calculating scenario Field EIQ: {e}")
            return 0.0

# Create singleton instance for global use
eiq_calculator = EIQCalculator()