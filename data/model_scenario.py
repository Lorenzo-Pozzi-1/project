"""
Scenario model for the LORENZO POZZI EIQ App.

This module defines the Scenario class which represents a complete
pesticide application scenario for a season.
"""

from datetime import date
from data.model_application import Application

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
        self.field_area = 1 if field_area is None else field_area  # Default to 1
        self.field_area_uom = field_area_uom or "acre"
        self.variety = variety or ""
        
        # Applications
        self.applications = applications if applications else []
    
    def clone(self):
        """
        Create a copy of this scenario with a new name.
            
        Returns:
            Scenario: New scenario instance with copied data
        """
        # Copy applications using the Application model's to_dict/from_dict methods for deep cloning
        new_applications = []
        for app in self.applications:
            app_dict = app.to_dict()
            new_app = Application.from_dict(app_dict)
            new_applications.append(new_app)
        
        # Create new scenario with copied data
        new_scenario = Scenario(
            name=f"Copy of {self.name}",
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
        Calculate the area-weighted Field EIQ for all applications in the scenario.
        
        Returns:
            float: Area-weighted EIQ for the scenario
        """
        if not self.applications or self.field_area <= 0:
            return 0.0
        
        # Use the standardizer to convert areas to hectares for calculation
        try:
            from common.calculations.layer_2_uom_std import EIQUOMStandardizer
            standardizer = EIQUOMStandardizer()
            
            # Prepare application data for standardization
            app_data = []
            for app in self.applications:
                app_data.append({
                    'area': getattr(app, 'area', 0) if hasattr(app, 'area') else 0
                })
            
            # Standardize areas to hectares
            standardized_apps, field_area_ha = standardizer.standardize_scenario_areas(
                app_data, self.field_area, self.field_area_uom
            )
            
            # Calculate area-weighted EIQ using standardized areas
            total_eiq_units = 0.0
            for i, app in enumerate(self.applications):
                if app.field_eiq is not None and app.field_eiq >= 0:
                    standardized_area = standardized_apps[i]['area'] if i < len(standardized_apps) else 0
                    total_eiq_units += app.field_eiq * standardized_area
                    
            return total_eiq_units / field_area_ha if field_area_ha > 0 else 0.0
            
        except Exception:
            # Fallback to simple area calculation if standardization fails
            total_eiq_units = 0.0
            for app in self.applications:
                if app.field_eiq is not None and app.field_eiq >= 0 and hasattr(app, 'area') and app.area is not None and app.area >= 0:
                    total_eiq_units += app.field_eiq * app.area
                    
            return total_eiq_units / self.field_area if self.field_area > 0 else 0.0
    
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
        
        return scenario