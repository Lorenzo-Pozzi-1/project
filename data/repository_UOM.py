"""
UOM Repository and Composite UOM System for the LORENZO POZZI Pesticide App.

This module provides a compositional approach to unit of measure handling
with enhanced concentration conversion capabilities for EIQ calculations.
"""

import csv
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from common import resource_path

UOM_CSV = resource_path("data/csv_UOM.csv")

@dataclass
class BaseUnit:
    """Represents a fundamental unit of measure."""
    uom: str       # e.g., kg, l, ha
    category: str  # weight, volume, area, length
    state: str     # dry, wet, no
    factor: float  # conversion factor to standard unit
    standard: str  # standard unit for this category

class CompositeUOM:
    """Represents a composite unit like kg/ha, ml/100m, etc."""
    
    def __init__(self, uom_string: str):
        """Parse a UOM string like 'kg/ha' or 'ml/100 m'."""
        self.original_string = uom_string
        self.numerator = None
        self.denominator = None
        self._parse_uom_string(uom_string)
    
    def _parse_uom_string(self, uom_string: str):
        """Parse compound UOM string into numerator and denominator."""
        if '/' in uom_string:
            num_str, den_str = uom_string.split('/', 1)
            self.numerator = num_str.strip()
            self.denominator = den_str.strip()
        else:
            # Simple unit (like % for concentration)
            self.numerator = uom_string.strip()
            self.denominator = None
    
    @property
    def is_rate(self) -> bool:
        """Check if this is a rate (has a denominator and is not a concentration)."""
        # Basic check if it has a denominator
        has_denom = self.denominator is not None
        
        # For proper rate identification, ensure it's not a concentration
        if has_denom:
            is_conc = self._check_if_concentration()
            return not is_conc
        
        return False
    
    @property
    def is_concentration(self) -> bool:
        """Check if this is a concentration (mass/volume or similar)."""
        if self.denominator is None:
            return self.numerator in ['%', 'g/l', 'lb/gal']
        
        return self._check_if_concentration()
    
    def _check_if_concentration(self) -> bool:
        """Internal method to check if this represents a concentration."""
        # Handle special cases first
        if self.denominator is None:
            return self.numerator in ['%', 'g/l', 'lb/gal']
        
        # For compound units, check categories
        repo = UOMRepository.get_instance()
        num_unit = repo.get_base_unit(self.numerator)
        den_unit = repo.get_base_unit(self.denominator)
        
        if num_unit and den_unit:
            return (num_unit.category == 'weight' and den_unit.category == 'volume') or \
                   (num_unit.category == 'weight' and den_unit.category == 'weight')
        return False
    
    def get_standard_form(self) -> str:
        """Get the standard form of this UOM."""
        repo = UOMRepository.get_instance()
        
        if self.denominator is None:
            if self.numerator == '%':
                return 'decimal'
            return self.numerator
        
        num_unit = repo.get_base_unit(self.numerator)
        den_unit = repo.get_base_unit(self.denominator)
        
        if num_unit and den_unit:
            return f"{num_unit.standard}/{den_unit.standard}"
        
        return self.original_string

class UOMRepository:
    """Repository for base units and composite UOM operations with enhanced EIQ capabilities."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = UOMRepository()
        return cls._instance
    
    def __init__(self):
        self.csv_file = UOM_CSV
        self._base_units: Dict[str, BaseUnit] = {}
        self._load_base_units()
        
        # Enhanced concentration conversion mappings for EIQ calculations
        self._concentration_conversion_map = {
            # Standard concentration conversions
            ('g/l', 'kg/l'): 0.001,
            ('lb/gal', 'kg/l'): 0.119826,  # 1 lb/gal = 0.119826 kg/l
            ('g/kg', 'kg/kg'): 0.001,
            ('mg/kg', 'kg/kg'): 0.000001,
            ('ppm', 'kg/kg'): 0.000001,  # ppm by weight
            ('oz/gal', 'kg/l'): 0.007489,  # 1 oz/gal = 0.007489 kg/l
        }
    
    def _load_base_units(self):
        """Load base units from CSV."""
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    unit = BaseUnit(
                        uom=row['UOM'].strip(),
                        category=row['category'].strip(),
                        state=row['state'].strip(),
                        factor=float(row['factor']),
                        standard=row['standard'].strip()
                    )
                    self._base_units[unit.uom.lower()] = unit
        except Exception as e:
            print(f"Error loading base units: {e}")
            self._base_units = {}
    
    def get_base_unit(self, uom: str) -> Optional[BaseUnit]:
        """Get a base unit by name."""
        return self._base_units.get(uom.lower())
    
    def convert_base_unit(self, value: float, from_uom: str, to_uom: str) -> float:
        """Convert between two base units of the same category."""
        from_unit = self.get_base_unit(from_uom)
        to_unit = self.get_base_unit(to_uom)
        
        if not from_unit or not to_unit:
            raise ValueError(f"Unknown unit: {from_uom} or {to_uom}")
        
        if from_unit.category != to_unit.category:
            raise ValueError(f"Cannot convert {from_uom} ({from_unit.category}) to {to_uom} ({to_unit.category})")
        
        # Convert to standard, then to target
        standard_value = value * from_unit.factor
        return standard_value / to_unit.factor
    
    def convert_composite_uom(self, value: float, from_uom: CompositeUOM, to_uom: CompositeUOM, 
                             user_preferences: dict = None) -> float:
        """Convert between composite UOMs, handling special cases with validation."""
        
        # Validate physical state compatibility
        self._validate_physical_state_compatibility(from_uom, to_uom)
        
        # Handle concentration units
        if from_uom.is_concentration and to_uom.is_concentration:
            return self._convert_concentration(value, from_uom, to_uom)
        
        # Handle rate conversions
        if from_uom.is_rate and to_uom.is_rate:
            return self._convert_rate(value, from_uom, to_uom, user_preferences)
        
        # Handle special conversions (e.g., linear to area rates)
        if self._needs_user_preferences(from_uom, to_uom):
            return self._convert_with_preferences(value, from_uom, to_uom, user_preferences)
        
        raise ValueError(f"Cannot convert {from_uom.original_string} to {to_uom.original_string}")
    
    # ========================
    # ENHANCED EIQ METHODS
    # ========================
    
    def convert_concentration(self, 
                            value: float, 
                            from_uom: str, 
                            to_uom: str) -> float:
        """
        Convert concentration units with special handling for EIQ calculations.
        
        Args:
            value: Concentration value to convert
            from_uom: Source UOM (%, g/l, lb/gal, etc.)
            to_uom: Target UOM (kg/kg, kg/l)
            
        Returns:
            Converted concentration value
        """
        # Handle percentage conversion
        if from_uom == '%':
            if to_uom in ['kg/kg', 'decimal']:
                return value / 100.0
            else:
                raise ValueError(f"Cannot convert % to {to_uom}")
        
        # Handle direct conversions
        conversion_key = (from_uom.lower(), to_uom.lower())
        if conversion_key in self._concentration_conversion_map:
            return value * self._concentration_conversion_map[conversion_key]
        
        # Try using the base composite UOM conversion
        try:
            from_composite = CompositeUOM(from_uom)
            to_composite = CompositeUOM(to_uom)
            return self.convert_composite_uom(value, from_composite, to_composite)
        except Exception as e:
            raise ValueError(f"Cannot convert concentration from {from_uom} to {to_uom}: {e}")
    
    def validate_concentration_units(self, concentration_uom: str, rate_unit_type: str) -> bool:
        """
        Validate that concentration units are compatible with rate units.
        
        Args:
            concentration_uom: Concentration UOM (%, g/l, etc.)
            rate_unit_type: "weight" or "volume"
            
        Returns:
            bool: True if compatible, False otherwise
        """
        if concentration_uom == '%':
            return True  # Percentage works with both weight and volume
        
        concentration_composite = CompositeUOM(concentration_uom)
        
        # For weight-based rates, concentration should be weight/weight
        if rate_unit_type == "weight":
            if not concentration_composite.is_concentration:
                return False
            # Check if it's weight/weight
            num_unit = self.get_base_unit(concentration_composite.numerator)
            den_unit = self.get_base_unit(concentration_composite.denominator)
            return (num_unit and den_unit and 
                   num_unit.category == 'weight' and den_unit.category == 'weight')
        
        # For volume-based rates, concentration should be weight/volume
        elif rate_unit_type == "volume":
            if not concentration_composite.is_concentration:
                return False
            # Check if it's weight/volume
            num_unit = self.get_base_unit(concentration_composite.numerator)
            den_unit = self.get_base_unit(concentration_composite.denominator)
            return (num_unit and den_unit and 
                   num_unit.category == 'weight' and den_unit.category == 'volume')
        
        return False
    
    def get_rate_compatibility_info(self, rate_uom: str) -> Dict:
        """
        Get information about rate UOM compatibility and requirements.
        
        Args:
            rate_uom: Application rate UOM
            
        Returns:
            Dict with compatibility information
        """
        rate_composite = CompositeUOM(rate_uom)
        numerator_unit = self.get_base_unit(rate_composite.numerator)
        
        if not numerator_unit:
            return {"valid": False, "error": f"Unknown unit: {rate_composite.numerator}"}
        
        if numerator_unit.category == 'weight':
            return {
                "valid": True,
                "rate_type": "weight",
                "compatible_concentration_types": ["weight/weight", "percentage"],
                "standard_rate_uom": "kg/ha",
                "standard_concentration_uom": "kg/kg"
            }
        elif numerator_unit.category == 'volume':
            return {
                "valid": True,
                "rate_type": "volume",
                "compatible_concentration_types": ["weight/volume", "percentage"],
                "standard_rate_uom": "l/ha",
                "standard_concentration_uom": "kg/l"
            }
        else:
            return {
                "valid": False,
                "error": f"Rate must be weight/area or volume/area, got: {numerator_unit.category}/area"
            }
    
    def validate_eiq_calculation_inputs(self, 
                                      rate: float,
                                      rate_uom: str,
                                      ai_concentration: float,
                                      ai_concentration_uom: str,
                                      ai_eiq: float) -> Dict:
        """
        Comprehensive validation of EIQ calculation inputs.
        
        Args:
            rate: Application rate value
            rate_uom: Application rate UOM
            ai_concentration: AI concentration value
            ai_concentration_uom: AI concentration UOM
            ai_eiq: AI EIQ value
            
        Returns:
            Dict with validation results and any errors
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate rate
        if rate <= 0:
            validation_result["errors"].append("Application rate must be positive")
            validation_result["valid"] = False
        
        # Validate rate UOM
        rate_info = self.get_rate_compatibility_info(rate_uom)
        if not rate_info["valid"]:
            validation_result["errors"].append(rate_info["error"])
            validation_result["valid"] = False
        else:
            # Validate concentration compatibility with rate
            if not self.validate_concentration_units(ai_concentration_uom, rate_info["rate_type"]):
                validation_result["errors"].append(
                    f"Concentration UOM '{ai_concentration_uom}' not compatible with "
                    f"{rate_info['rate_type']}-based rate '{rate_uom}'"
                )
                validation_result["valid"] = False
        
        # Validate AI concentration
        if ai_concentration <= 0:
            validation_result["errors"].append("AI concentration must be positive")
            validation_result["valid"] = False
        
        # Validate concentration ranges
        if ai_concentration_uom == '%' and ai_concentration > 100:
            validation_result["errors"].append("Percentage concentration cannot exceed 100%")
            validation_result["valid"] = False
        elif ai_concentration_uom == '%' and ai_concentration > 50:
            validation_result["warnings"].append("High concentration (>50%) - please verify")
        
        # Validate AI EIQ
        if ai_eiq <= 0:
            validation_result["errors"].append("AI EIQ must be positive")
            validation_result["valid"] = False
        elif ai_eiq > 200:
            validation_result["warnings"].append("Very high EIQ value (>200) - please verify")
        
        return validation_result
    
    def get_conversion_path_info(self, 
                               from_rate_uom: str,
                               from_concentration_uom: str,
                               user_preferences: dict = None) -> Dict:
        """
        Get information about the conversion path for EIQ calculations.
        Useful for debugging and user feedback.
        
        Args:
            from_rate_uom: Source rate UOM
            from_concentration_uom: Source concentration UOM
            user_preferences: User preferences for conversions
            
        Returns:
            Dict with conversion path information
        """
        try:
            rate_info = self.get_rate_compatibility_info(from_rate_uom)
            if not rate_info["valid"]:
                return {"valid": False, "error": rate_info["error"]}
            
            conversion_info = {
                "valid": True,
                "rate_conversion": {
                    "from": from_rate_uom,
                    "to": rate_info["standard_rate_uom"],
                    "requires_user_preferences": self._needs_user_preferences_for_rate(from_rate_uom)
                },
                "concentration_conversion": {
                    "from": from_concentration_uom,
                    "to": rate_info["standard_concentration_uom"]
                },
                "eiq_conversion": {
                    "from": "eiq/lb (Cornell)",
                    "to": "eiq/kg"
                },
                "final_units": "eiq/ha"
            }
            
            return conversion_info
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def _needs_user_preferences_for_rate(self, rate_uom: str) -> bool:
        """Check if rate conversion requires user preferences."""
        rate_composite = CompositeUOM(rate_uom)
        
        # Linear rates need row spacing
        if rate_composite.denominator and rate_composite.denominator in ['100 m', '1000 ft', 'm', 'ft']:
            return True
        
        # Seed treatments need seeding rate
        if rate_composite.denominator == 'cwt':
            return True
        
        return False
    
    # ========================
    # ORIGINAL METHODS (PRESERVED)
    # ========================
    
    def _validate_physical_state_compatibility(self, from_uom: CompositeUOM, to_uom: CompositeUOM):
        """Validate that we're not converting between incompatible physical states."""
        # Get the numerator units (the "amount" part)
        from_num_unit = self.get_base_unit(from_uom.numerator)
        to_num_unit = self.get_base_unit(to_uom.numerator)
        
        if not from_num_unit or not to_num_unit:
            return  # Can't validate unknown units
        
        # Check if trying to convert between dry and wet
        if from_num_unit.state == 'dry' and to_num_unit.state == 'wet':
            raise ValueError(f"Cannot convert dry weight ({from_uom.numerator}) to liquid volume ({to_uom.numerator})")
        
        if from_num_unit.state == 'wet' and to_num_unit.state == 'dry':
            raise ValueError(f"Cannot convert liquid volume ({from_uom.numerator}) to dry weight ({to_uom.numerator})")
        
        # Allow conversions within same state or involving 'no' state (area, length)
        return
    
    def _convert_concentration(self, value: float, from_uom: CompositeUOM, to_uom: CompositeUOM) -> float:
        """Convert concentration units."""
        if from_uom.numerator == '%':
            return value / 100.0  # Convert percentage to decimal
        
        # Handle other concentration conversions using enhanced method
        return self.convert_concentration(value, from_uom.original_string, to_uom.original_string)
    
    def _convert_rate(self, value: float, from_uom: CompositeUOM, to_uom: CompositeUOM, 
                     user_preferences: dict = None) -> float:
        """Convert rate units (amount/area, amount/length, etc.)."""
        
        # Special case: if user preferences are needed, delegate to that function
        if self._needs_user_preferences(from_uom, to_uom):
            return self._convert_with_preferences(value, from_uom, to_uom, user_preferences)
        
        # Standard rate conversion: convert numerator and denominator separately
        try:
            # Convert numerator (1 unit from → 1 unit to)
            num_factor = self.convert_base_unit(1.0, from_uom.numerator, to_uom.numerator)
            
            # Convert denominator (1 unit from → 1 unit to)  
            den_factor = self.convert_base_unit(1.0, from_uom.denominator, to_uom.denominator)
            
            # For rates: multiply by numerator factor, divide by denominator factor
            return value * num_factor / den_factor
            
        except ValueError as e:
            raise ValueError(f"Cannot convert rate {from_uom.original_string} to {to_uom.original_string}: {e}")
    
    def _needs_user_preferences(self, from_uom: CompositeUOM, to_uom: CompositeUOM) -> bool:
        """Check if conversion needs user preferences (row spacing, seeding rate)."""
        # Linear rates like ml/100m need row spacing to convert to area rates
        if from_uom.denominator in ['100 m', '1000 ft', 'm', 'ft'] and \
           to_uom.denominator in ['ha', 'acre']:
            return True
        
        # Seed treatments like kg/cwt need seeding rate
        if from_uom.denominator == 'cwt' and to_uom.denominator in ['ha', 'acre']:
            return True
        
        return False
    
    def _convert_with_preferences(self, value: float, from_uom: CompositeUOM, to_uom: CompositeUOM,
                                 user_preferences: dict) -> float:
        """Convert using user preferences for row spacing and seeding rate."""
        if not user_preferences:
            raise ValueError("User preferences required for this conversion")
        
        # Linear to area conversion (amount/length → amount/ha)
        if from_uom.denominator in ['100 m', '1000 ft', 'm', 'ft']:
            return self._convert_linear_to_area(value, from_uom, to_uom, user_preferences)
        
        # Seed treatment conversion (amount/cwt → amount/ha)
        elif from_uom.denominator == 'cwt':
            return self._convert_seed_treatment_to_area(value, from_uom, to_uom, user_preferences)
        
        raise ValueError(f"No preference-based conversion available for {from_uom.original_string} to {to_uom.original_string}")
    
    def _convert_linear_to_area(self, value: float, from_uom: CompositeUOM, to_uom: CompositeUOM,
                               user_preferences: dict) -> float:
        """
        Convert linear rates to area rates using row spacing.
        Formula: [amount/length] → [amount/ha]
        
        Steps:
        1. Convert to [amount/m]
        2. Convert row spacing to [rows/m] 
        3. Convert to [m of rows/ha] (assuming 100m rows and 10,000 m²/ha)
        4. Apply: [amount/m] x [m of rows/ha] = [amount/ha]
        """
        # Step 1: Convert to standard linear rate (amount/m)
        amount_per_m = self.convert_base_unit(value, from_uom.denominator, 'm')
        
        # Step 2: Get row spacing and convert to meters
        row_spacing = user_preferences.get('default_row_spacing', 34.0)
        row_spacing_unit = user_preferences.get('default_row_spacing_unit', 'inch')
        row_spacing_m = self.convert_base_unit(row_spacing, row_spacing_unit, 'm')
        
        # Step 3: Calculate rows per meter and meters of rows per hectare
        rows_per_m = 1.0 / row_spacing_m  # [rows/m]
        m_per_ha = 10000  # [m²/ha]
        row_length_m = 100  # assume 100m rows
        rows_per_ha = m_per_ha / (row_spacing_m * row_length_m)  # [rows/ha]
        m_of_rows_per_ha = rows_per_ha * row_length_m  # [m of rows/ha]
        
        # Step 4: Convert amount/m to amount/ha
        amount_per_ha = amount_per_m * m_of_rows_per_ha
        
        # Step 5: Convert to target area unit if needed
        if to_uom.denominator != 'ha':
            amount_per_ha = self.convert_base_unit(amount_per_ha, 'ha', to_uom.denominator)
        
        return amount_per_ha
    
    def _convert_seed_treatment_to_area(self, value: float, from_uom: CompositeUOM, to_uom: CompositeUOM,
                                       user_preferences: dict) -> float:
        """
        Convert seed treatment rates to area rates using seeding rate.
        Formula: [amount/cwt seed] x [cwt seed/ha] = [amount/ha]
        """
        # Get seeding rate
        seeding_rate = user_preferences.get('default_seeding_rate', 25)
        seeding_rate_unit = user_preferences.get('default_seeding_rate_unit', 'cwt/acre')
        
        # Parse seeding rate unit (e.g., "kg/ha" → numerator="kg", denominator="ha")
        seeding_uom = CompositeUOM(seeding_rate_unit)
        
        # Convert seeding rate to cwt/ha
        seeding_rate_cwt_per_ha = self.convert_base_unit(seeding_rate, seeding_uom.numerator, 'cwt')
        if seeding_uom.denominator != 'ha':
            seeding_rate_cwt_per_ha = self.convert_base_unit(seeding_rate_cwt_per_ha, seeding_uom.denominator, 'ha')
        
        # Apply conversion: [amount/cwt] x [cwt/ha] = [amount/ha]
        amount_per_ha = value * seeding_rate_cwt_per_ha
        
        # Convert to target area unit if needed
        if to_uom.denominator != 'ha':
            amount_per_ha = self.convert_base_unit(amount_per_ha, 'ha', to_uom.denominator)
        
        return amount_per_ha

def convert_concentration_to_percent(concentration: float, uom: str) -> float:
    """Convert concentration to percentage."""
    composite_uom = CompositeUOM(uom)
    percent_uom = CompositeUOM('%')
    
    repo = UOMRepository.get_instance()
    return repo.convert_composite_uom(concentration, composite_uom, percent_uom) * 100