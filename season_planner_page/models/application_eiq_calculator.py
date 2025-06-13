"""
Application EIQ Calculator for the Season Planner.

Handles EIQ calculations including estimation for applications with missing AI data.
"""

from typing import List
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
            
            # Get validation state to determine calculation method
            validation = self._validator.validate_application(app)
            
            if validation.state == ValidationState.VALID:
                # Standard EIQ calculation with complete AI data
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
            print(f"Error calculating EIQ for {app.product_name}: {e}")
            return 0.0
    
    def calculate_all_eiq_values(self, applications: List[Application]) -> None:
        """
        Calculate EIQ for all applications using a two-pass approach.
        
        Pass 1: Calculate EIQ for VALID applications (complete AI data)
        Pass 2: Calculate estimated EIQ for VALID_ESTIMATED applications
        """
        try:
            # Pass 1: Calculate EIQ for VALID applications
            for app in applications:
                validation = self._validator.validate_application(app)
                if validation.state == ValidationState.VALID:
                    app.field_eiq = self.calculate_application_eiq(app)
                else:
                    app.field_eiq = 0.0
            
            # Pass 2: Calculate estimated EIQ for VALID_ESTIMATED applications
            for app in applications:
                validation = self._validator.validate_application(app)
                if validation.state == ValidationState.VALID_ESTIMATED:
                    app.field_eiq = self.calculate_application_eiq(app, applications)
                    
        except Exception as e:
            print(f"Error in calculate_all_eiq_values(): {e}")
    
    def get_total_eiq(self, applications: List[Application]) -> float:
        """Calculate total EIQ for all applications."""
        try:
            total_eiq = 0.0
            for app in applications:
                if app.field_eiq and app.field_eiq > 0:
                    total_eiq += app.field_eiq
            return total_eiq
        except Exception as e:
            print(f"Error calculating total EIQ: {e}")
            return 0.0
    
    def _calculate_average_eiq_for_estimation(self, applications: List[Application]) -> float:
        """
        Calculate average EIQ from applications that have valid EIQ calculations.
        Only includes applications with ValidationState.VALID (complete AI data).
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
                
                # Only include VALID applications (with complete AI data) in the average
                if validation.state == ValidationState.VALID:
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
                            if eiq > 0:
                                valid_eiq_values.append(eiq)
                        except Exception:
                            continue
            
            if valid_eiq_values:
                return sum(valid_eiq_values) / len(valid_eiq_values)
            else:
                # No valid EIQ values available, return a conservative default
                return 50.0  # Conservative default EIQ value
                
        except Exception as e:
            print(f"Error calculating average EIQ: {e}")
            return 50.0
    
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
            print(f"Error in _find_product(): {e}")
            return None