"""
Application EIQ Calculator for the Season Planner.

Handles EIQ calculations including estimation for applications with missing AI data.
"""

from typing import List
from PySide6.QtWidgets import QMessageBox
from data.model_application import Application
from data.repository_product import ProductRepository
from common.calculations.layer_1_interface import eiq_calculator
from .application_validator import ApplicationValidator, ValidationState


class ApplicationEIQCalculator:
    """
    Calculator for application EIQ values with support for estimation.
    
    Handles both direct EIQ calculation from AI data and estimated EIQ
    calculation using averages from other valid applications.
    """
    
    def __init__(self, user_preferences: dict = None):
        """Initialize the EIQ calculator."""
        self._products_repo = ProductRepository.get_instance()
        self._validator = ApplicationValidator()
        self._user_preferences = user_preferences or {}
    
    def calculate_application_eiq(self, app: Application, all_applications: List[Application] = None) -> float:
        """
        Calculate EIQ for a single application.
        
        Args:
            app: Application to calculate EIQ for
            all_applications: All applications (needed for average calculation)
            
        Returns:
            float: Calculated or estimated EIQ value
        """
        try:
            # Check if we have all required data
            if not app.product_name or not app.rate or not app.rate_uom:
                return 0.0

            product = self._find_product(app.product_name)
            if not product:
                return 0.0

            # Skip EIQ calculation for adjuvants
            if self._is_adjuvant_or_biological(product):
                return 0.0

            # Get validation state to determine calculation method
            validation = self._validator.validate_application(app)
            
            if validation.state in [ValidationState.VALID, ValidationState.RATE_ISSUES, ValidationState.INVALID_DATA]:
                # Standard EIQ calculation with complete AI data (include RATE_ISSUES and INVALID_DATA)
                ai_data = product.get_ai_data()
                if ai_data:
                    return eiq_calculator.calculate_product_field_eiq(
                        active_ingredients=ai_data,
                        application_rate=app.rate,
                        application_rate_uom=app.rate_uom,
                        applications=1,
                        user_preferences=self._user_preferences
                    )
            
            elif validation.state == ValidationState.VALID_ESTIMATED:
                # Use estimated EIQ (average of other valid applications)
                if all_applications:
                    return self._calculate_average_eiq_for_estimation(all_applications)
                else:
                    return 50.0  # Default fallback
            
            return 0.0
            
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error calculating EIQ for {app.product_name}: {e}")
            return 0.0

    def _is_adjuvant_or_biological(self, product) -> bool:
        """
        Check if a product is an adjuvant or a biological based on product type or application method.

        Args:
            product: Product object to check
            
        Returns:
            bool: True if product is an adjuvant or biological, False otherwise
        """
        if not product:
            return False
        
        # Check product type
        if hasattr(product, 'product_type') and product.product_type:
            if product.product_type.lower() == "adjuvant" or product.product_type.lower() == "biological":
                return True
                
        # Check application method
        if hasattr(product, 'application_method') and product.application_method:
            if product.application_method.lower() == "adjuvant":
                return True

        return False
    
    def calculate_all_eiq_values(self, applications: List[Application]) -> None:
        """
        Calculate EIQ for all applications using a two-pass approach.
        
        Pass 1: Calculate EIQ for VALID, RATE_ISSUES and INVALID_DATA applications (complete AI data)
        Pass 2: Calculate estimated EIQ for VALID_ESTIMATED applications
        """
        try:
            # Pass 1: Calculate EIQ for VALID, RATE_ISSUES and INVALID_DATA applications
            for app in applications:
                validation = self._validator.validate_application(app)
                if validation.state in [ValidationState.VALID, ValidationState.RATE_ISSUES, ValidationState.INVALID_DATA]:
                    app.field_eiq = self.calculate_application_eiq(app)
                else:
                    app.field_eiq = 0.0
            
            # Pass 2: Calculate estimated EIQ for VALID_ESTIMATED applications
            for app in applications:
                validation = self._validator.validate_application(app)
                if validation.state == ValidationState.VALID_ESTIMATED:
                    app.field_eiq = self.calculate_application_eiq(app, applications)
                    
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error in ApplicationEIQCalculator.calculate_all_eiq_values() method: {e}")

    def get_total_eiq(self, applications: List[Application], field_area: float = None, field_area_uom: str = "acre") -> float:
        """Calculate area-weighted EIQ for all applications."""
        try:
            if not applications:
                return 0.0
                
            # If no field area provided, try to calculate simple sum as fallback
            if field_area is None or field_area <= 0:
                total_eiq = 0.0
                for app in applications:
                    if app.field_eiq and app.field_eiq > 0:
                        total_eiq += app.field_eiq
                return total_eiq
            
            # Use the standardizer to convert areas to hectares
            from common.calculations.layer_2_uom_std import EIQUOMStandardizer
            standardizer = EIQUOMStandardizer()
            
            # Prepare application data for standardization
            app_data = []
            for app in applications:
                app_data.append({
                    'area': getattr(app, 'area', 0) if hasattr(app, 'area') else 0
                })
            
            # Standardize areas to hectares
            standardized_apps, field_area_ha = standardizer.standardize_scenario_areas(
                app_data, field_area, field_area_uom, self._user_preferences
            )
            
            # Calculate area-weighted EIQ using standardized areas
            total_eiq_units = 0.0
            for i, app in enumerate(applications):
                if app.field_eiq and app.field_eiq > 0:
                    standardized_area = standardized_apps[i]['area'] if i < len(standardized_apps) else 0
                    total_eiq_units += app.field_eiq * standardized_area
                    
            return total_eiq_units / field_area_ha if field_area_ha > 0 else 0.0
            
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error calculating total EIQ: {e}")
            return 0.0
    
    def _calculate_average_eiq_for_estimation(self, applications: List[Application]) -> float:
        """
        Calculate average EIQ from applications that have valid EIQ calculations.
        Includes applications with ValidationState.VALID, ValidationState.RATE_ISSUES and ValidationState.INVALID_DATA.
        Excludes fumigations (applications with EIQ >= 1000) from the average calculation.
        """
        try:
            valid_eiq_values = []
            
            for app in applications:
                if not app.product_name or not app.rate or not app.rate_uom:
                    continue
                
                product = self._find_product(app.product_name)
                if not product:
                    continue
                
                # Get validation state to determine if this should be included in average
                validation = self._validator.validate_application(app)
                
                # Include VALID, RATE_ISSUES and INVALID_DATA applications in the average
                if validation.state in [ValidationState.VALID, ValidationState.RATE_ISSUES, ValidationState.INVALID_DATA]:
                    ai_data = product.get_ai_data()
                    if ai_data:
                        try:
                            eiq = eiq_calculator.calculate_product_field_eiq(
                                active_ingredients=ai_data,
                                application_rate=app.rate,
                                application_rate_uom=app.rate_uom,
                                applications=1,
                                user_preferences=self._user_preferences
                            )
                            # Exclude EIQ values >= 1000 (fumigations) from average calculation
                            if eiq > 0 and eiq < 1000:
                                valid_eiq_values.append(eiq)
                        except Exception:
                            continue
            
            if valid_eiq_values:
                return sum(valid_eiq_values) / len(valid_eiq_values)
            else:
                # No valid EIQ values available, return a default
                return 30.0  # Default EIQ value
                
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error calculating average EIQ: {e}")
            return 30.0
    
    def _find_product(self, product_name: str):
        """Find a product by name in the filtered products list."""
        try:
            if not product_name:
                return None
            
            filtered_products = self._products_repo.get_filtered_products()
            for product in filtered_products:
                if product.product_name == product_name:
                    return product
            return None
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error in ApplicationEIQCalculator._find_product() method: {e}")
            return None