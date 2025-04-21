"""
Product model for the LORENZO POZZI Pesticide App.

This module defines the Product class and related functionality.
Updated to support multiple active ingredients and detailed EIQ data.
"""


class Product:
    """
    Represents a pesticide product.
    
    Stores information about a pesticide product including region, name, active ingredients,
    EIQ values, application rates, and safety intervals.
    """
    
    def __init__(self, 
                 region=None,
                 product_type=None,
                 product_name=None,
                 producer_name=None,
                 regulator_number=None,
                 application_method=None,
                 label_minimum_rate=None,
                 label_maximum_rate=None,
                 label_suggested_rate=None,
                 rate_uom=None,
                 number_of_ai=0,
                 ai1=None,
                 ai1_eiq=None,
                 ai1_group=None,
                 ai1_concentration_percent=None,  # Updated column name
                 ai2=None,
                 ai2_eiq=None,
                 ai2_group=None,
                 ai2_concentration_percent=None,  # Updated column name
                 ai3=None,
                 ai3_eiq=None,
                 ai3_group=None,
                 ai3_concentration_percent=None,  # Updated column name
                 ai4=None,
                 ai4_eiq=None,
                 ai4_group=None,
                 ai4_concentration_percent=None,  # Updated column name
                 eiq_total=None,
                 min_days_between_applications=None,
                 rei_hours=None,
                 phi_days=None):
        """
        Initialize a Product instance.
        
        Args:
            region (str): Geographic region where the product is registered
            product_type (str): Product type (e.g., Herbicide)
            product_name (str): Product name
            producer_name (str): Manufacturer/producer name
            regulator_number (str): Registration/regulation number
            application_method (str): Recommended application method
            label_minimum_rate (float): Minimum application rate per label
            label_maximum_rate (float): Maximum application rate per label
            label_suggested_rate (float): Suggested application rate
            rate_uom (str): Unit of measure for application rates
            number_of_ai (int): Number of active ingredients
            ai1 (str): First active ingredient name
            ai1_eiq (float): EIQ value for first active ingredient
            ai1_group (str): Group/classification for first active ingredient
            ai1_concentration_percent (float): Concentration of first active ingredient
            ai2 (str): Second active ingredient name (if applicable)
            ai2_eiq (float): EIQ value for second active ingredient
            ai2_group (str): Group/classification for second active ingredient
            ai2_concentration_percent (float): Concentration of second active ingredient
            ai3 (str): Third active ingredient name (if applicable)
            ai3_eiq (float): EIQ value for third active ingredient
            ai3_group (str): Group/classification for third active ingredient
            ai3_concentration_percent (float): Concentration of third active ingredient
            ai4 (str): Fourth active ingredient name (if applicable)
            ai4_eiq (float): EIQ value for fourth active ingredient
            ai4_group (str): Group/classification for fourth active ingredient
            ai4_concentration_percent (float): Concentration of fourth active ingredient
            eiq_total (float): Total EIQ value for the product
            min_days_between_applications (int): Minimum days between applications
            rei_hours (int): Restricted Entry Interval in hours
            phi_days (int): Pre-Harvest Interval in days
        """
        self.region = region
        
        # Use product type directly from data without validation/forcing to predefined list
        self.product_type = product_type
            
        self.product_name = product_name
        self.producer_name = producer_name
        self.regulator_number = regulator_number
        self.application_method = application_method
        
        # Application rates
        self.label_minimum_rate = self._convert_to_float(label_minimum_rate)
        self.label_maximum_rate = self._convert_to_float(label_maximum_rate)
        self.label_suggested_rate = self._convert_to_float(label_suggested_rate)
        self.rate_uom = rate_uom
        
        # Number of active ingredients
        self.number_of_ai = int(number_of_ai) if number_of_ai else 0
        
        # Active ingredient 1 (primary)
        self.ai1 = ai1
        self.ai1_eiq = self._convert_to_float(ai1_eiq)
        self.ai1_group = ai1_group
        self.ai1_concentration_percent = self._convert_to_float(ai1_concentration_percent)  # Updated parameter name
        
        # Active ingredient 2 (if present)
        self.ai2 = ai2
        self.ai2_eiq = self._convert_to_float(ai2_eiq)
        self.ai2_group = ai2_group
        self.ai2_concentration_percent = self._convert_to_float(ai2_concentration_percent)  # Updated parameter name
        
        # Active ingredient 3 (if present)
        self.ai3 = ai3
        self.ai3_eiq = self._convert_to_float(ai3_eiq)
        self.ai3_group = ai3_group
        self.ai3_concentration_percent = self._convert_to_float(ai3_concentration_percent)  # Updated parameter name
        
        # Active ingredient 4 (if present)
        self.ai4 = ai4
        self.ai4_eiq = self._convert_to_float(ai4_eiq)
        self.ai4_group = ai4_group
        self.ai4_concentration_percent = self._convert_to_float(ai4_concentration_percent)  # Updated parameter name
        
        # Overall EIQ and application intervals
        self.eiq_total = self._convert_to_float(eiq_total)
        self.min_days_between_applications = self._convert_to_int(min_days_between_applications)
        self.rei_hours = self._convert_to_int(rei_hours)
        self.phi_days = self._convert_to_int(phi_days)
    
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
        """Get display name with primary active ingredient."""
        if self.ai1:
            return f"{self.product_name} ({self.ai1})"
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
    
    def calculate_field_eiq(self, rate=None, applications=1):
        """
        Calculate the Field EIQ for this product.
        
        Args:
            rate (float): Application rate (uses suggested rate if not provided)
            applications (int): Number of applications
        
        Returns:
            float: Calculated Field EIQ or None if calculation not possible
        """
        if self.eiq_total is None:
            return None
            
        # Use provided rate or default to suggested rate
        if rate is None:
            rate = self.label_suggested_rate
            
        if rate is None:
            return None
            
        # Simple field EIQ calculation
        return self.eiq_total * rate * applications
    
    def to_dict(self):
        """
        Convert product to dictionary representation.
        
        Returns:
            dict: Product data as dictionary
        """
        return {
            "region": self.region,
            "type": self.product_type,
            "name": self.product_name,
            "producer": self.producer_name,
            "regulator number": self.regulator_number,
            "application method": self.application_method,
            "min rate": self.label_minimum_rate,
            "max rate": self.label_maximum_rate,
            "suggested rate": self.label_suggested_rate,
            "rate UOM": self.rate_uom,
            "number of AI": self.number_of_ai,
            "AI1": self.ai1,
            "AI1 eiq": self.ai1_eiq,
            "AI1 group": self.ai1_group,
            "AI1 %": self.ai1_concentration_percent,
            "AI2": self.ai2,
            "AI2 eiq": self.ai2_eiq,
            "AI2 group": self.ai2_group,
            "AI2 %": self.ai2_concentration_percent,
            "AI3": self.ai3,
            "AI3 eiq": self.ai3_eiq,
            "AI3 group": self.ai3_group,
            "AI3 %": self.ai3_concentration_percent,
            "AI4": self.ai4,
            "AI4 eiq": self.ai4_eiq,
            "AI4 group": self.ai4_group,
            "AI4 %": self.ai4_concentration_percent,
            "eiq total": self.eiq_total,
            "min days between applications": self.min_days_between_applications,
            "REI (hours)": self.rei_hours,
            "PHI (days)": self.phi_days
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
            region=data.get("region"),
            product_type=data.get("type"),
            product_name=data.get("name"),
            producer_name=data.get("producer"),
            regulator_number=data.get("regulator number"),
            application_method=data.get("application method"),
            label_minimum_rate=data.get("min rate"),
            label_maximum_rate=data.get("max rate"),
            label_suggested_rate=data.get("suggested rate"),
            rate_uom=data.get("rate UOM"),
            number_of_ai=data.get("number of AI"),
            ai1=data.get("AI1"),
            ai1_eiq=data.get("AI1 eiq"),
            ai1_group=data.get("AI1 group"),
            ai1_concentration_percent=data.get("AI1 %"),
            ai2=data.get("AI2"),
            ai2_eiq=data.get("AI2 eiq"),
            ai2_group=data.get("AI2 group"),
            ai2_concentration_percent=data.get("AI2 %"),
            ai3=data.get("AI3"),
            ai3_eiq=data.get("AI3 eiq"),
            ai3_group=data.get("AI3 group"),
            ai3_concentration_percent=data.get("AI3 %"),
            ai4=data.get("AI4"),
            ai4_eiq=data.get("AI4 eiq"),
            ai4_group=data.get("AI4 group"),
            ai4_concentration_percent=data.get("AI4 %"),
            eiq_total=data.get("eiq total"),
            min_days_between_applications=data.get("min days between applications"),
            rei_hours=data.get("REI (hours)"),
            phi_days=data.get("PHI (days)")
        )