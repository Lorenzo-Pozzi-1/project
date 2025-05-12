"""
Data models for the Season Planner.

This module defines the Treatment, Scenario, and Season classes.
"""

class Treatment:
    """Represents a single pesticide treatment in a scenario."""
    
    def __init__(self, date="", product=None, rate=0.0, rate_uom="", 
                 acres=0.0, application_method="", field_eiq=0.0):
        self.date = date
        self.product = product  # Product object or product name
        self.rate = rate
        self.rate_uom = rate_uom
        self.acres = acres
        self.application_method = application_method
        self.field_eiq = field_eiq
        self.active_groups = ""  # Will be populated based on product
    
    @property
    def product_name(self):
        """Get the product name, handling both string and Product object."""
        if hasattr(self.product, 'product_name'):
            return self.product.product_name
        return str(self.product) if self.product else ""


class Scenario:
    """Represents a scenario with field info and treatments."""
    
    def __init__(self, name="", grower="", field="", variety=""):
        self.name = name
        self.grower = grower
        self.field = field
        self.variety = variety
        self.treatments = []
        
    def add_treatment(self, treatment):
        """Add a treatment to this scenario."""
        self.treatments.append(treatment)
        
    def remove_treatment(self, index):
        """Remove a treatment by index."""
        if 0 <= index < len(self.treatments):
            del self.treatments[index]
    
    def move_treatment(self, from_index, to_index):
        """Move a treatment from one position to another."""
        if 0 <= from_index < len(self.treatments) and 0 <= to_index < len(self.treatments):
            treatment = self.treatments.pop(from_index)
            self.treatments.insert(to_index, treatment)
    
    @property
    def total_field_eiq(self):
        """Calculate the total Field EIQ for all treatments."""
        return sum(t.field_eiq for t in self.treatments)