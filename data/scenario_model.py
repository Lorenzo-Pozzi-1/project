"""
Scenario model for the LORENZO POZZI Pesticide App.

This module defines the Scenario class which represents a complete
pesticide application scenario for a season.
"""

import copy
from datetime import date

class Scenario:
    """
    Represents a pesticide application scenario.
    
    Stores information about a seasonal pesticide application plan including
    grower details, field information, and all planned applications.
    """
    
    def __init__(self, 
                 name="New Scenario",
                 crop_year=None,
                 grower_name=None,
                 field_name=None,
                 field_area=None,
                 field_area_uom="acre",
                 variety=None,
                 applications=None):
        """
        Initialize a Scenario instance.
        
        Args:
            name (str): User-friendly name for the scenario
            crop_year (int): Year of the crop/season
            grower_name (str): Name of the grower
            field_name (str): Name of the field
            field_area (float): Size of the field
            field_area_uom (str): Unit of measure for field area (default: ha)
            variety (str): Crop variety planted
            applications (list): List of Application objects
        """
        # Scenario name
        self.name = name
        
        # Field information
        self.crop_year = crop_year if crop_year is not None else date.today().year
        self.grower_name = grower_name or ""
        self.field_name = field_name or ""
        self.field_area = 0 if field_area is None else field_area  # Default to 0
        self.field_area_uom = field_area_uom or "acre"
        self.variety = variety or ""
        
        # Applications
        self.applications = applications if applications else []
        self.creation_date = date.today()
    
    def clone(self, new_name=None):
        """
        Create a copy of this scenario with a new name.
        
        Args:
            new_name (str): Name for the new scenario, defaults to "Copy of [original]"
            
        Returns:
            Scenario: New scenario instance with copied data
        """
        # Create default name if not provided
        if new_name is None:
            new_name = f"Copy of {self.name}"
            
        # Create deep copy of the applications
        new_applications = copy.deepcopy(self.applications)
        
        # Create new scenario with copied data
        new_scenario = Scenario(
            name=new_name,
            crop_year=self.crop_year,
            grower_name=self.grower_name,
            field_name=self.field_name,
            field_area=self.field_area,
            field_area_uom=self.field_area_uom,
            variety=self.variety,
            applications=new_applications
        )
        
        return new_scenario
    
    def add_application(self, application):
        """
        Add an application to the scenario.
        
        Args:
            application: Application object to add
        """
        self.applications.append(application)
    
    def remove_application(self, index):
        """
        Remove an application from the scenario.
        
        Args:
            index (int): Index of the application to remove
            
        Returns:
            bool: True if successful, False if index out of range
        """
        if 0 <= index < len(self.applications):
            self.applications.pop(index)
            return True
        return False
    
    def get_total_eiq(self):
        """
        Calculate the total Field EIQ for all applications in the scenario.
        
        Returns:
            float: Sum of all application EIQs
        """
        return sum(app.field_eiq for app in self.applications if app.field_eiq is not None)
    
    def to_dict(self):
        """
        Convert scenario to dictionary representation.
        
        Returns:
            dict: Scenario data as dictionary
        """
        return {
            # Scenario name
            "name": self.name,
            
            # Field information
            "crop_year": self.crop_year,
            "grower_name": self.grower_name,
            "field_name": self.field_name,
            "field_area": self.field_area,
            "field_area_uom": self.field_area_uom,
            "variety": self.variety,
            
            # Applications
            "applications": [app.to_dict() for app in self.applications],
            "creation_date": self.creation_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Scenario instance from dictionary data.
        
        Args:
            data (dict): Scenario data
        
        Returns:
            Scenario: New Scenario instance
        """
        from data.application_model import Application
        
        # Extract field area with safe default
        field_area = data.get("field_area")
        if field_area is None:
            field_area = 0
        
        # Create scenario with basic properties
        scenario = cls(
            name=data.get("name", "Unnamed Scenario"),
            crop_year=data.get("crop_year"),
            grower_name=data.get("grower_name", ""),
            field_name=data.get("field_name", ""),
            field_area=field_area,
            field_area_uom=data.get("field_area_uom", "acre"),
            variety=data.get("variety", "")
        )
        
        # Convert application dictionaries to Application objects
        if "applications" in data and isinstance(data["applications"], list):
            scenario.applications = [Application.from_dict(app_data) for app_data in data["applications"]]
        
        # Set creation date if provided
        if "creation_date" in data and isinstance(data["creation_date"], str):
            try:
                scenario.creation_date = date.fromisoformat(data["creation_date"])
            except ValueError:
                scenario.creation_date = date.today()
        
        return scenario