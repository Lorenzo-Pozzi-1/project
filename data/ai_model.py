"""
Active ingredient model for the LORENZO POZZI Pesticide App.

This module defines the active ingredient class and related functionality.
"""

class ActiveIngredient:
    """Model representing an active ingredient with its mode of action classifications."""
    
    def __init__(self, name, ai_type=None, FRAC_group=None, HRAC_group=None, IRAC_group=None):
        self.name = name
        self.ai_type = ai_type
        self.FRAC_group = FRAC_group
        self.HRAC_group = HRAC_group
        self.IRAC_group = IRAC_group
    
    @classmethod
    def from_dict(cls, data):
        """Create an ActiveIngredient from a dictionary."""
        return cls(
            name=data.get("NAME"),
            ai_type=data.get("type"),
            FRAC_group=data.get("FRAC group code"),
            HRAC_group=data.get("HRAC group code"),
            IRAC_group=data.get("IRAC group code")
        )