"""
Product model for the LORENZO POZZI Pesticide App.

This module defines the Product class and related functionality.
Updated to support multiple active ingredients without EIQ data in the product.
"""

from data.ai_repository import AIRepository
from math_module import convert_concentration_to_percent

class Product:
    """
    Represents a pesticide product.
    
    Stores information about a pesticide product including country, region, name, active ingredients,
    application rates, and safety intervals.
    """
    
    def __init__(self, 
                 country=None,
                 region=None,
                 product_type=None,
                 product_name=None,
                 producer_name=None,
                 regulator_number=None,
                 application_method=None,
                 label_minimum_rate=None,
                 label_maximum_rate=None,
                 rate_uom=None,
                 formulation=None,
                 min_days_between_applications=None,
                 rei_hours=None,
                 phi_days=None,
                 ai1=None,
                 ai1_concentration=None,
                 ai1_concentration_uom=None,
                 ai2=None,
                 ai2_concentration=None,
                 ai2_concentration_uom=None,
                 ai3=None,
                 ai3_concentration=None,
                 ai3_concentration_uom=None,
                 ai4=None,
                 ai4_concentration=None,
                 ai4_concentration_uom=None):
        """
        Initialize a Product instance.
        
        Args:
            country (str): Country where the product is registered
            region (str): region where the product standard applies
            product_type (str): Product type (e.g., Herbicide)
            product_name (str): Product name
            producer_name (str): Manufacturer/producer name
            regulator_number (str): Registration/regulation number
            application_method (str): Recommended application method
            formulation (str): Product formulation (liquid/dry)
            label_minimum_rate (float): Minimum application rate as per label
            label_maximum_rate (float): Maximum application rate as per label
            rate_uom (str): Unit of measure for application rates
            min_days_between_applications (int): Minimum days between applications
            rei_hours (int): Restricted Entry Interval in hours
            phi_days (int): Pre-Harvest Interval in days
            ai1 (str): First active ingredient name
            ai1_concentration (float): Concentration of first active ingredient
            ai1_concentration_uom (str): Unit of measure for first active ingredient concentration
            ai2 (str): Second active ingredient name (if applicable)
            ai2_concentration (float): Concentration of second active ingredient
            ai2_concentration_uom (str): Unit of measure for second active ingredient concentration
            ai3 (str): Third active ingredient name (if applicable)
            ai3_concentration (float): Concentration of third active ingredient
            ai3_concentration_uom (str): Unit of measure for third active ingredient concentration
            ai4 (str): Fourth active ingredient name (if applicable)
            ai4_concentration (float): Concentration of fourth active ingredient
            ai4_concentration_uom (str): Unit of measure for fourth active ingredient concentration
        """
        self.country = country
        self.region = region
        self.product_type = product_type
        self.product_name = product_name
        self.producer_name = producer_name
        self.regulator_number = regulator_number
        self.application_method = application_method
        self.formulation = formulation
        
        # Application rates
        self.label_minimum_rate = self._convert_to_float(label_minimum_rate)
        self.label_maximum_rate = self._convert_to_float(label_maximum_rate)
        self.rate_uom = rate_uom
        
        # Application intervals and safety periods
        self.min_days_between_applications = self._convert_to_int(min_days_between_applications)
        self.rei_hours = self._convert_to_int(rei_hours)
        self.phi_days = self._convert_to_int(phi_days)
        
        # Active ingredients
        for idx in range(1, 5):  # Process AI1 through AI4
            name_attr = f"ai{idx}"
            conc_attr = f"ai{idx}_concentration"
            uom_attr = f"ai{idx}_concentration_uom"
            
            setattr(self, name_attr, locals()[name_attr])
            setattr(self, conc_attr, self._convert_to_float(locals()[conc_attr]))
            setattr(self, uom_attr, locals()[uom_attr])
    
    def _convert_to_float(self, value):
        """Convert a value to float, handling None and empty strings."""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _convert_to_int(self, value):
        """Convert a value to int, handling None and empty strings."""
        if value is None or value == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _get_ai_info(self, idx):
        """Get active ingredient information for the given index.
        
        Args:
            idx (int): The index of the active ingredient (1-4)
            
        Returns:
            tuple: (name, concentration, uom) or (None, None, None) if not present
        """
        name = getattr(self, f"ai{idx}", None)
        if not name:
            return None, None, None
            
        concentration = getattr(self, f"ai{idx}_concentration", None)
        uom = getattr(self, f"ai{idx}_concentration_uom", None)
        
        return name, concentration, uom
    
    @property
    def display_name(self):
        """Get display name with all active ingredients."""
        ingredients = self.active_ingredients
        if ingredients:
            ai_text = ", ".join(ingredients)
            return f"{self.product_name} ({ai_text})"
        return self.product_name
    
    @property
    def active_ingredients(self):
        """Get a list of all active ingredients in the product."""
        ingredients = []
        for idx in range(1, 5):  # Process AI1 through AI4
            name, _, _ = self._get_ai_info(idx)
            if name:
                ingredients.append(name)
        return ingredients
    
    @property
    def number_of_ai(self):
        """Calculate the number of active ingredients."""
        return sum(1 for idx in range(1, 5) if getattr(self, f"ai{idx}", None))
    
    def to_dict(self):
        """
        Convert product to dictionary representation.
        
        Returns:
            dict: Product data as dictionary
        """
        return {
            "country": self.country,
            "region": self.region,
            "type": self.product_type,
            "reg. #": self.regulator_number,
            "name": self.product_name,
            "producer": self.producer_name,
            "use": self.application_method,
            "formulation": self.formulation,
            "min rate": self.label_minimum_rate,
            "max rate": self.label_maximum_rate,
            "rate UOM": self.rate_uom,
            "m.d.b.a.": self.min_days_between_applications,
            "REI (h)": self.rei_hours,
            "PHI (d)": self.phi_days,
            "AI1": self.ai1,
            "[AI1]": self.ai1_concentration,
            "[AI1]UOM": self.ai1_concentration_uom,
            "AI2": self.ai2,
            "[AI2]": self.ai2_concentration,
            "[AI2]UOM": self.ai2_concentration_uom,
            "AI3": self.ai3,
            "[AI3]": self.ai3_concentration,
            "[AI3]UOM": self.ai3_concentration_uom,
            "AI4": self.ai4,
            "[AI4]": self.ai4_concentration,
            "[AI4]UOM": self.ai4_concentration_uom
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Product instance from dictionary data.
        
        Args:
            data (dict): Product data
        
        Returns:
            Product: New Product instance
        """
        return cls(
            country=data.get("country"),
            region=data.get("region"),
            product_type=data.get("type"),
            product_name=data.get("name"),
            producer_name=data.get("producer"),
            regulator_number=data.get("regulator number"),
            application_method=data.get("application method"),
            formulation=data.get("formulation"),
            label_minimum_rate=data.get("min rate"),
            label_maximum_rate=data.get("max rate"),
            rate_uom=data.get("rate UOM"),
            min_days_between_applications=data.get("min days between applications"),
            rei_hours=data.get("REI (h)"),
            phi_days=data.get("PHI (d)"),
            ai1=data.get("AI1"),
            ai1_concentration=data.get("[AI1]"),
            ai1_concentration_uom=data.get("[AI1]UOM"),
            ai2=data.get("AI2"),
            ai2_concentration=data.get("[AI2]"),
            ai2_concentration_uom=data.get("[AI2]UOM"),
            ai3=data.get("AI3"),
            ai3_concentration=data.get("[AI3]"),
            ai3_concentration_uom=data.get("[AI3]UOM"),
            ai4=data.get("AI4"),
            ai4_concentration=data.get("[AI4]"),
            ai4_concentration_uom=data.get("[AI4]UOM")
        )
    
    def get_ai_groups(self):
        """
        Get mode of action groups for all active ingredients in the product.
        
        Returns:
            list: List of dictionaries with AI names and their MoA groups
        """
        
        ai_repo = AIRepository.get_instance()
        return [ai_repo.get_moa_groups(ai_name) for ai_name in self.active_ingredients if ai_name]
    
    def get_ai_eiq(self, ai_name):
        """
        Get the EIQ value for a specific active ingredient in the product.
        
        Args:
            ai_name (str): Name of the active ingredient to look up
            
        Returns:
            float or None: EIQ value if found, None otherwise
        """
        
        ai_repo = AIRepository.get_instance()
        return ai_repo.get_ai_eiq(ai_name)
        
    def get_ai_data(self):
        """
        Get all active ingredients data with their EIQ values from the repository.
        
        Returns:
            list: List of dictionaries with name, eiq, percent for each AI
        """
        
        ai_repo = AIRepository.get_instance()
        ai_data = []
        
        # Process all active ingredients in a loop
        for idx in range(1, 5):  # Process AI1 through AI4
            name, concentration, uom = self._get_ai_info(idx)
            if not name:
                continue
                
            eiq = ai_repo.get_ai_eiq(name)
            percent = convert_concentration_to_percent(concentration, uom)
            
            if eiq is not None and percent is not None:
                ai_data.append({
                    'name': name,
                    'eiq': eiq,
                    'percent': percent
                })
        
        return ai_data