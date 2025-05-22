"""
UOM Repository and Composite UOM System for the LORENZO POZZI Pesticide App.

This module provides a compositional approach to unit of measure handling.
"""

import csv
from typing import Optional, Dict
from dataclasses import dataclass
from common import resource_path

UOM_CSV = resource_path("data/base_units.csv")

@dataclass
class BaseUnit:
    """Represents a fundamental unit of measure."""
    uom: str
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
        """Check if this is a rate (has denominator)."""
        return self.denominator is not None
    
    @property
    def is_concentration(self) -> bool:
        """Check if this is a concentration (mass/volume or similar)."""
        if not self.is_rate:
            return self.numerator in ['%', 'g/l', 'lb/gal', 'g/kg']
        
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
        
        if not self.is_rate:
            if self.numerator == '%':
                return 'decimal'
            return self.numerator
        
        num_unit = repo.get_base_unit(self.numerator)
        den_unit = repo.get_base_unit(self.denominator)
        
        if num_unit and den_unit:
            return f"{num_unit.standard}/{den_unit.standard}"
        
        return self.original_string

class UOMRepository:
    """Repository for base units and composite UOM operations."""
    
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
            raise ValueError(f"Cannot convert {from_unit.category} to {to_unit.category}")
        
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
        
        # Handle other concentration conversions
        # Implementation details...
        return value
    
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
        4. Apply: [amount/m] × [m of rows/ha] = [amount/ha]
        """
        # Step 1: Convert to standard linear rate (amount/m)
        amount_per_m = self.convert_base_unit(value, from_uom.denominator, 'm')
        
        # Step 2: Get row spacing and convert to meters
        row_spacing = user_preferences.get('default_row_spacing', 34.0)
        row_spacing_unit = user_preferences.get('default_row_spacing_unit', 'inches')
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
        Formula: [amount/cwt seed] × [cwt seed/ha] = [amount/ha]
        """
        # Get seeding rate
        seeding_rate = user_preferences.get('default_seeding_rate', 2000)
        seeding_rate_unit = user_preferences.get('default_seeding_rate_unit', 'kg/ha')
        
        # Parse seeding rate unit (e.g., "kg/ha" → numerator="kg", denominator="ha")
        seeding_uom = CompositeUOM(seeding_rate_unit)
        
        # Convert seeding rate to cwt/ha
        seeding_rate_cwt_per_ha = self.convert_base_unit(seeding_rate, seeding_uom.numerator, 'cwt')
        if seeding_uom.denominator != 'ha':
            seeding_rate_cwt_per_ha = self.convert_base_unit(seeding_rate_cwt_per_ha, seeding_uom.denominator, 'ha')
        
        # Apply conversion: [amount/cwt] × [cwt/ha] = [amount/ha]
        amount_per_ha = value * seeding_rate_cwt_per_ha
        
        # Convert to target area unit if needed
        if to_uom.denominator != 'ha':
            amount_per_ha = self.convert_base_unit(amount_per_ha, 'ha', to_uom.denominator)
        
        return amount_per_ha

# Updated conversion functions for backward compatibility
def convert_application_rate(rate: float, from_uom: str, to_uom: str, 
                           user_preferences: dict = None) -> float:
    """Convert application rates using the new system."""
    repo = UOMRepository.get_instance()
    from_composite = CompositeUOM(from_uom)
    to_composite = CompositeUOM(to_uom)
    
    return repo.convert_composite_uom(rate, from_composite, to_composite, user_preferences)

def convert_concentration_to_percent(concentration: float, uom: str) -> float:
    """Convert concentration to percentage."""
    composite_uom = CompositeUOM(uom)
    percent_uom = CompositeUOM('%')
    
    repo = UOMRepository.get_instance()
    return repo.convert_composite_uom(concentration, composite_uom, percent_uom) * 100