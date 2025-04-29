"""
Product model for the LORENZO POZZI Pesticide App.

This module defines the Product class and related functionality.
Updated to support multiple active ingredients and detailed EIQ data.
Adapted for the NEW_products.csv format.
"""


class Product:
    """
    Represents a pesticide product.
    
    Stores information about a pesticide product including country, region, name, active ingredients,
    EIQ values, application rates, and safety intervals.
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
                 ai1_eiq=None,
                 ai2=None,
                 ai2_concentration=None,
                 ai2_concentration_uom=None,
                 ai2_eiq=None,
                 ai3=None,
                 ai3_concentration=None,
                 ai3_concentration_uom=None,
                 ai3_eiq=None,
                 ai4=None,
                 ai4_concentration=None,
                 ai4_concentration_uom=None,
                 ai4_eiq=None):
        """
        Initialize a Product instance.
        
        Args:
            country (str): Country where the product is registered
            region (str): Geographic region where the product is registered
            product_type (str): Product type (e.g., Herbicide)
            product_name (str): Product name
            producer_name (str): Manufacturer/producer name
            regulator_number (str): Registration/regulation number
            application_method (str): Recommended application method
            label_minimum_rate (float): Minimum application rate per label
            label_maximum_rate (float): Maximum application rate per label
            rate_uom (str): Unit of measure for application rates
            formulation (str): Product formulation type
            min_days_between_applications (int): Minimum days between applications
            rei_hours (int): Restricted Entry Interval in hours
            phi_days (int): Pre-Harvest Interval in days
            ai1 (str): First active ingredient name
            ai1_concentration (float): Concentration of first active ingredient
            ai1_concentration_uom (str): Unit of measure for first active ingredient concentration
            ai1_eiq (float): EIQ value for first active ingredient
            ai2 (str): Second active ingredient name (if applicable)
            ai2_concentration (float): Concentration of second active ingredient
            ai2_concentration_uom (str): Unit of measure for second active ingredient concentration
            ai2_eiq (float): EIQ value for second active ingredient
            ai3 (str): Third active ingredient name (if applicable)
            ai3_concentration (float): Concentration of third active ingredient
            ai3_concentration_uom (str): Unit of measure for third active ingredient concentration
            ai3_eiq (float): EIQ value for third active ingredient
            ai4 (str): Fourth active ingredient name (if applicable)
            ai4_concentration (float): Concentration of fourth active ingredient
            ai4_concentration_uom (str): Unit of measure for fourth active ingredient concentration
            ai4_eiq (float): EIQ value for fourth active ingredient
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
        self.ai1_eiq = self._convert_to_float(ai1_eiq)
        
        # Active ingredient 2 (if present)
        self.ai2 = ai2
        self.ai2_concentration = self._convert_to_float(ai2_concentration)
        self.ai2_concentration_uom = ai2_concentration_uom
        self.ai2_eiq = self._convert_to_float(ai2_eiq)
        
        # Active ingredient 3 (if present)
        self.ai3 = ai3
        self.ai3_concentration = self._convert_to_float(ai3_concentration)
        self.ai3_concentration_uom = ai3_concentration_uom
        self.ai3_eiq = self._convert_to_float(ai3_eiq)
        
        # Active ingredient 4 (if present)
        self.ai4 = ai4
        self.ai4_concentration = self._convert_to_float(ai4_concentration)
        self.ai4_concentration_uom = ai4_concentration_uom
        self.ai4_eiq = self._convert_to_float(ai4_eiq)
    
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
    
    @property
    def eiq_total(self):
        """Calculate the total EIQ based on all active ingredients."""
        total_eiq = 0
        
        # For each active ingredient, if present, add its contribution to total EIQ
        if self.ai1 and self.ai1_eiq is not None and self.ai1_concentration is not None:
            total_eiq += self.ai1_eiq * (self.ai1_concentration / 100)
            
        if self.ai2 and self.ai2_eiq is not None and self.ai2_concentration is not None:
            total_eiq += self.ai2_eiq * (self.ai2_concentration / 100)
            
        if self.ai3 and self.ai3_eiq is not None and self.ai3_concentration is not None:
            total_eiq += self.ai3_eiq * (self.ai3_concentration / 100)
            
        if self.ai4 and self.ai4_eiq is not None and self.ai4_concentration is not None:
            total_eiq += self.ai4_eiq * (self.ai4_concentration / 100)
            
        return total_eiq if total_eiq > 0 else None
    
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
            "min rate": self.label_minimum_rate,
            "max rate": self.label_maximum_rate,
            "rate UOM": self.rate_uom,
            "min days between applications": self.min_days_between_applications,
            "REI (h)": self.rei_hours,
            "PHI (d)": self.phi_days,
            "AI1": self.ai1,
            "[AI1]": self.ai1_concentration,
            "[AI1]UOM": self.ai1_concentration_uom,
            "AI1 eiq": self.ai1_eiq,
            "AI2": self.ai2,
            "[AI2]": self.ai2_concentration,
            "[AI2]UOM": self.ai2_concentration_uom,
            "AI2 eiq": self.ai2_eiq,
            "AI3": self.ai3,
            "[AI3]": self.ai3_concentration,
            "[AI3]UOM": self.ai3_concentration_uom,
            "AI3 eiq": self.ai3_eiq,
            "AI4": self.ai4,
            "[AI4]": self.ai4_concentration,
            "[AI4]UOM": self.ai4_concentration_uom,
            "AI4 eiq": self.ai4_eiq,
            "Formulation": self.formulation
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
            label_minimum_rate=data.get("min rate"),
            label_maximum_rate=data.get("max rate"),
            rate_uom=data.get("rate UOM"),
            formulation=data.get("Formulation"),
            min_days_between_applications=data.get("min days between applications"),
            rei_hours=data.get("REI (h)"),
            phi_days=data.get("PHI (d)"),
            ai1=data.get("AI1"),
            ai1_concentration=data.get("[AI1]"),
            ai1_concentration_uom=data.get("[AI1]UOM"),
            ai1_eiq=data.get("AI1 eiq"),
            ai2=data.get("AI2"),
            ai2_concentration=data.get("[AI2]"),
            ai2_concentration_uom=data.get("[AI2]UOM"),
            ai2_eiq=data.get("AI2 eiq"),
            ai3=data.get("AI3"),
            ai3_concentration=data.get("[AI3]"),
            ai3_concentration_uom=data.get("[AI3]UOM"),
            ai3_eiq=data.get("AI3 eiq"),
            ai4=data.get("AI4"),
            ai4_concentration=data.get("[AI4]"),
            ai4_concentration_uom=data.get("[AI4]UOM"),
            ai4_eiq=data.get("AI4 eiq")
        )