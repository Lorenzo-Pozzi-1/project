"""
Product model for the LORENZO POZZI Pesticide App.

This module defines the Product class and related functionality.
Updated to support multiple active ingredients without EIQ data in the product.
"""

from math_module.eiq_conversions import convert_concentration_to_percent

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
        
        # Active ingredient 1 (primary)
        self.ai1 = ai1
        self.ai1_concentration = self._convert_to_float(ai1_concentration)
        self.ai1_concentration_uom = ai1_concentration_uom
        
        # Active ingredient 2 (if present)
        self.ai2 = ai2
        self.ai2_concentration = self._convert_to_float(ai2_concentration)
        self.ai2_concentration_uom = ai2_concentration_uom
        
        # Active ingredient 3 (if present)
        self.ai3 = ai3
        self.ai3_concentration = self._convert_to_float(ai3_concentration)
        self.ai3_concentration_uom = ai3_concentration_uom
        
        # Active ingredient 4 (if present)
        self.ai4 = ai4
        self.ai4_concentration = self._convert_to_float(ai4_concentration)
        self.ai4_concentration_uom = ai4_concentration_uom
    
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
        if self.ai1:
            ingredients.append(self.ai1)
        if self.ai2:
            ingredients.append(self.ai2)
        if self.ai3:
            ingredients.append(self.ai3)
        if self.ai4:
            ingredients.append(self.ai4)
        return ingredients
    
    @property
    def number_of_ai(self):
        """Calculate the number of active ingredients."""
        count = 0
        if self.ai1:
            count += 1
        if self.ai2:
            count += 1
        if self.ai3:
            count += 1
        if self.ai4:
            count += 1
        return count
    
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
            "regulator number": self.regulator_number,
            "name": self.product_name,
            "producer": self.producer_name,
            "application method": self.application_method,
            "formulation": self.formulation,
            "min rate": self.label_minimum_rate,
            "max rate": self.label_maximum_rate,
            "rate UOM": self.rate_uom,
            "min days between applications": self.min_days_between_applications,
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
        from data.ai_repository import AIRepository
        
        ai_repo = AIRepository.get_instance()
        ai_groups = []
        
        # Process all active ingredients
        for ai_name in self.active_ingredients:
            if not ai_name:
                continue
                
            groups = ai_repo.get_moa_groups(ai_name)
            ai_groups.append(groups)
        
        return ai_groups
    
    def get_ai_eiq(self, ai_name):
        """
        Get the EIQ value for a specific active ingredient in the product.
        
        Args:
            ai_name (str): Name of the active ingredient to look up
            
        Returns:
            float or None: EIQ value if found, None otherwise
        """
        from data.ai_repository import AIRepository
        
        ai_repo = AIRepository.get_instance()
        return ai_repo.get_ai_eiq(ai_name)
        
    def get_ai_data(self):
        """
        Get all active ingredients data with their EIQ values from the repository.
        
        Returns:
            list: List of dictionaries with name, eiq, percent for each AI
        """
        from data.ai_repository import AIRepository
        
        ai_repo = AIRepository.get_instance()
        ai_data = []
        
        # Check AI1
        if self.ai1:
            eiq = ai_repo.get_ai_eiq(self.ai1)
            percent = convert_concentration_to_percent(self.ai1_concentration, self.ai1_concentration_uom)
            if eiq is not None and percent is not None:
                ai_data.append({
                    'name': self.ai1,
                    'eiq': eiq,
                    'percent': percent
                })
        
        # Check AI2
        if self.ai2:
            eiq = ai_repo.get_ai_eiq(self.ai2)
            percent = convert_concentration_to_percent(self.ai2_concentration, self.ai2_concentration_uom)
            if eiq is not None and percent is not None:
                ai_data.append({
                    'name': self.ai2,
                    'eiq': eiq,
                    'percent': percent
                })
        
        # Check AI3
        if self.ai3:
            eiq = ai_repo.get_ai_eiq(self.ai3)
            percent = convert_concentration_to_percent(self.ai3_concentration, self.ai3_concentration_uom)
            if eiq is not None and percent is not None:
                ai_data.append({
                    'name': self.ai3,
                    'eiq': eiq,
                    'percent': percent
                })
        
        # Check AI4
        if self.ai4:
            eiq = ai_repo.get_ai_eiq(self.ai4)
            percent = convert_concentration_to_percent(self.ai4_concentration, self.ai4_concentration_uom)
            if eiq is not None and percent is not None:
                ai_data.append({
                    'name': self.ai4,
                    'eiq': eiq,
                    'percent': percent
                })
        
        return ai_data