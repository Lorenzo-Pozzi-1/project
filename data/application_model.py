"""
Application model for the LORENZO POZZI Pesticide App.

This module defines the Application class which represents a single 
pesticide application within a season plan.
"""

class Application:
    """
    Represents a single pesticide application.
    
    Stores information about a pesticide application including the date, product,
    rate, application method, and calculated EIQ impact.
    """
    
    def __init__(self, 
                 application_date=None,
                 product_type=None,
                 product_name=None,
                 rate=None,
                 rate_uom=None,
                 area=None,
                 application_method=None,
                 ai_groups=None,
                 field_eiq=None):
        """
        Initialize an Application instance.
        
        Args:
            application_date (str): Date of application
            product_type (str): Type of product applied
            product_name (str): Name of the product applied
            rate (float): Application rate
            rate_uom (str): Unit of measure for application rate
            area (float): Area treated
            application_method (str): Method of application
            ai_groups (list): Active ingredient groups used (for resistance management)
            field_eiq (float): Calculated field EIQ for this application
        """
        self.application_date = application_date if application_date else None
        self.product_type = product_type
        self.product_name = product_name
        self.rate = rate
        self.rate_uom = rate_uom
        self.area = area
        self.application_method = application_method
        self.ai_groups = ai_groups if ai_groups else []
        self.field_eiq = field_eiq
    
    def to_dict(self):
        """
        Convert application to dictionary representation.
        
        Returns:
            dict: Application data as dictionary
        """
        return {
            "application_date": self.application_date,
            "product_type": self.product_type,
            "product_name": self.product_name,
            "rate": self.rate,
            "rate_uom": self.rate_uom,
            "area": self.area,
            "application_method": self.application_method,
            "ai_groups": self.ai_groups,
            "field_eiq": self.field_eiq
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create an Application instance from dictionary data.
        
        Args:
            data (dict): Application data
        
        Returns:
            Application: New Application instance
        """
        app = cls()
        
        # Convert date string to date object if needed
        app.application_date = data.get("application_date")
        app.product_type = data.get("product_type")
        app.product_name = data.get("product_name")
        app.rate = data.get("rate")
        app.rate_uom = data.get("rate_uom")
        app.area = data.get("area")
        app.application_method = data.get("application_method")
        app.ai_groups = data.get("ai_groups", [])
        app.field_eiq = data.get("field_eiq")
        
        return app