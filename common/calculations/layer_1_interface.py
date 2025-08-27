"""
Unified EIQ Calculation Interface
Combines both layers into clean, easy-to-use functions for the other modules to call.
Handles UOM standardization internally, exposes simple interfaces.
"""

from typing import List, Dict
from common.widgets.tracer import calculation_tracer
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
            # Determine product name for header
            product_name = "Product Calculation"
            if active_ingredients and len(active_ingredients) > 0:
                first_ai = active_ingredients[0].get('name', 'Unknown')
                if len(active_ingredients) == 1:
                    product_name = f"Product with {first_ai}"
                else:
                    product_name = f"Product with {first_ai} + {len(active_ingredients)-1} others"
            
            # Start structured logging
            # calculation_tracer.log_header(f"EIQ CALCULATION FOR {product_name}")
            
            # Step 1: Product Information
            calculation_tracer.log_step("Product Information")
            calculation_tracer.log_ai_list(active_ingredients)
            calculation_tracer.log_application_info(application_rate, application_rate_uom, applications)
            
            # Step 2: Unit Standardization
            calculation_tracer.log_step("Unit Standardization")
            calculation_tracer.set_suppress_redundant(True)
            standardized = self.standardizer.standardize_product_inputs(
                active_ingredients=active_ingredients,
                application_rate=application_rate,
                application_rate_uom=application_rate_uom,
                applications=applications,
                user_preferences=user_preferences
            )
            calculation_tracer.set_suppress_redundant(False)
            
            # Step 3: Field EIQ Calculation
            calculation_tracer.log_step("Field EIQ Calculation")
            
            result = calculate_field_eiq_product(
                standardized_ais=standardized.active_ingredients,
                rate_per_ha=standardized.rate_per_ha,
                applications=standardized.applications
            )

            calculation_tracer.log_result("TOTAL FIELD EIQ", f"{result.field_eiq_per_ha:.1f}", "eiq/ha")
            calculation_tracer.calculation_complete()
            return result.field_eiq_per_ha
            
        except Exception as e:
            calculation_tracer.log(f"Error calculating product Field EIQ: {e}")
            calculation_tracer.calculation_complete()
            return 0.0
    
    def calculate_scenario_field_eiq(self,
                                   applications: List[Dict],
                                   field_area: float,
                                   field_area_uom: str = "acre",
                                   user_preferences: dict = None) -> float:
        """
        Calculate area-weighted Field EIQ for a scenario (multiple applications).
        
        Args:
            applications: List of application dicts with product, rate, and area info
            field_area: Total field area for calculating weighted average
            field_area_uom: Unit of measure for field and application areas
            user_preferences: User preferences for UOM conversions
            
        Returns:
            Area-weighted scenario Field EIQ [eiq/ha]
        """
        try:
            calculation_tracer.log_header(f"AREA-WEIGHTED SCENARIO EIQ CALCULATION ({len(applications)} applications)")
            
            # Step 1: Standardize all areas to hectares
            standardized_apps, field_area_ha = self.standardizer.standardize_scenario_areas(
                applications, field_area, field_area_uom, user_preferences
            )
            
            application_data = []
            
            for i, app in enumerate(standardized_apps):
                calculation_tracer.log_step(f"Application {i+1}")
                
                # Extract application data
                product = app.get('product')
                if not product:
                    calculation_tracer.log_substep("No product specified", level=1, is_last=True)
                    continue
                
                # Get active ingredients data
                active_ingredients = product.get_ai_data() if hasattr(product, 'get_ai_data') else []
                if not active_ingredients:
                    calculation_tracer.log_substep("No active ingredients found", level=1, is_last=True)
                    continue
                
                # Calculate EIQ for this application
                app_eiq = self.calculate_product_field_eiq(
                    active_ingredients=active_ingredients,
                    application_rate=app.get('rate', 0),
                    application_rate_uom=app.get('rate_uom', ''),
                    applications=1,  # Each application is counted once
                    user_preferences=user_preferences
                )
                
                # Get standardized application area (now in hectares)
                app_area_ha = app.get('area', 0)
                
                application_data.append({
                    'field_eiq': app_eiq,
                    'area': app_area_ha
                })
                
                calculation_tracer.log_result(f"Application {i+1} EIQ", f"{app_eiq:.1f}", "eiq/ha", level=1)
                calculation_tracer.log_result(f"Application {i+1} Area (standardized)", f"{app_area_ha:.4f}", "ha", level=1)
                calculation_tracer.add_blank_line()
            
            # Calculate area-weighted scenario EIQ
            scenario_result = calculate_field_eiq_scenario(application_data, field_area_ha)
            calculation_tracer.log_result("Field Area (standardized)", f"{field_area_ha:.4f}", "ha")
            calculation_tracer.log_result("Area-Weighted Scenario EIQ", f"{scenario_result.field_eiq_per_ha:.1f}", "eiq/ha")
            calculation_tracer.calculation_complete()
            return scenario_result.field_eiq_per_ha
            
        except Exception as e:
            calculation_tracer.log(f"Error calculating scenario Field EIQ: {e}")
            calculation_tracer.calculation_complete()
            return 0.0

# Create singleton instance for global use
eiq_calculator = EIQCalculator()