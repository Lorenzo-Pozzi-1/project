"""
Season Plan model for the LORENZO POZZI Pesticide App.

This module defines the SeasonPlan class which represents a complete
seasonal pesticide application plan for a specific field.
"""

from datetime import date


class SeasonPlan:
    """
    Represents a seasonal pesticide application plan.
    
    Stores information about a field's seasonal plan including crop year,
    grower details, field information, and all planned applications.
    """
    
    def __init__(self, 
                crop_year=None,
                grower_name=None,
                field_name=None,
                field_area=None,
                field_area_uom="acre",
                variety=None,
                applications=None):
        """
        Initialize a SeasonPlan instance.
        
        Args:
            crop_year (int): Year of the crop/season
            grower_name (str): Name of the grower
            field_name (str): Name of the field
            field_area (float): Size of the field
            field_area_uom (str): Unit of measure for field area (default: acre)
            variety (str): Potato variety planted
            applications (list): List of Application objects
        """
        # Set default crop year to current year if not provided
        self.crop_year = crop_year if crop_year is not None else date.today().year
        self.grower_name = grower_name or ""
        self.field_name = field_name or ""
        self.field_area = 0 if field_area is None else field_area  # Default to 0
        self.field_area_uom = field_area_uom
        self.variety = variety or ""
        self.applications = applications if applications else []
        
        # Additional metadata
        self.creation_date = date.today()
        self.last_modified = date.today()
    
    def add_application(self, application):
        """
        Add an application to the season plan.
        
        Args:
            application: Application object to add
        """
        self.applications.append(application)
        self.last_modified = date.today()
    
    def remove_application(self, index):
        """
        Remove an application from the season plan.
        
        Args:
            index (int): Index of the application to remove
            
        Returns:
            bool: True if successful, False if index out of range
        """
        if 0 <= index < len(self.applications):
            self.applications.pop(index)
            self.last_modified = date.today()
            return True
        return False
    
    def get_total_eiq(self):
        """
        Calculate the total Field EIQ for all applications in the plan.
        
        Returns:
            float: Sum of all application EIQs
        """
        return sum(app.field_eiq for app in self.applications if app.field_eiq is not None)
    
    def to_dict(self):
        """
        Convert season plan to dictionary representation.
        
        Returns:
            dict: Season plan data as dictionary
        """
        return {
            "crop_year": self.crop_year,
            "grower_name": self.grower_name,
            "field_name": self.field_name,
            "field_area": self.field_area,
            "field_area_uom": self.field_area_uom,
            "variety": self.variety,
            "applications": [app.to_dict() for app in self.applications],
            "creation_date": self.creation_date.isoformat(),
            "last_modified": self.last_modified.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a SeasonPlan instance from dictionary data.
        
        Args:
            data (dict): Season plan data
        
        Returns:
            SeasonPlan: New SeasonPlan instance
        """
        from data.application_model import Application
        
        plan = cls(
            crop_year=data.get("crop_year"),
            grower_name=data.get("grower_name"),
            field_name=data.get("field_name"),
            field_area=data.get("field_area"),
            field_area_uom=data.get("field_area_uom"),
            variety=data.get("variety")
        )
        
        # Convert application dictionaries to Application objects
        if "applications" in data and isinstance(data["applications"], list):
            plan.applications = [Application.from_dict(app_data) for app_data in data["applications"]]
        
        # Convert date strings to date objects
        if "creation_date" in data and isinstance(data["creation_date"], str):
            try:
                plan.creation_date = date.fromisoformat(data["creation_date"])
            except ValueError:
                plan.creation_date = date.today()
                
        if "last_modified" in data and isinstance(data["last_modified"], str):
            try:
                plan.last_modified = date.fromisoformat(data["last_modified"])
            except ValueError:
                plan.last_modified = date.today()
        
        return plan