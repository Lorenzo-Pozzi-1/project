"""
Models for the Season Planner functionality.

This module defines data models and utilities shared between 
the scenario editor and comparison views.
"""

class Treatment:
    """
    Represents a single pesticide treatment application.
    
    A treatment can contain multiple products with their
    associated details and EIQ values.
    """
    def __init__(self, treatment_number=1):
        """Initialize a treatment instance."""
        self.treatment_number = treatment_number
        self.products = []  # List of products used in this treatment
        self.field_eiq = 0.0
    
    def add_product(self, product_type, product_name, active_ingredient_group):
        """Add a product to this treatment."""
        self.products.append({
            'type': product_type,
            'name': product_name,
            'active_ingredient_group': active_ingredient_group
        })
    
    def set_field_eiq(self, eiq_value):
        """Set the field EIQ for this treatment."""
        try:
            self.field_eiq = float(eiq_value)
        except (ValueError, TypeError):
            self.field_eiq = 0.0
    
    def get_product(self, index=0):
        """Get a product by index."""
        if 0 <= index < len(self.products):
            return self.products[index]
        return {'type': '', 'name': '', 'active_ingredient_group': ''}


class Scenario:
    """
    Represents a pesticide application scenario.
    
    A scenario contains metadata about the field and a collection
    of treatments that make up the application strategy.
    """
    def __init__(self, name="Scenario"):
        """Initialize a scenario instance."""
        self.name = name
        self.grower = ""
        self.field = ""
        self.variety = ""
        self.treatments = []  # List of Treatment objects
    
    def add_treatment(self):
        """Add a new treatment to this scenario."""
        treatment_number = len(self.treatments) + 1
        treatment = Treatment(treatment_number)
        self.treatments.append(treatment)
        return treatment
    
    def remove_treatment(self, index):
        """Remove a treatment by index."""
        if 0 <= index < len(self.treatments):
            self.treatments.pop(index)
    
    def get_total_eiq(self):
        """Calculate the total EIQ for all treatments."""
        return sum(treatment.field_eiq for treatment in self.treatments)
    
    def get_data_for_comparison(self):
        """Get scenario data formatted for comparison view."""
        return {
            "num_applications": len(self.treatments),
            "eiq_score": int(self.get_total_eiq()),
            "other_info": f"Field: {self.field}" if self.field else "No field specified"
        }