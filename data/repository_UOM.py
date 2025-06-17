"""
UOM Repository for the LORENZO POZZI Pesticide App.

This module provides the public interface for unit of measure operations,
delegating complex conversion logic to the UOM converter.
"""

import csv
from typing import Optional, Dict
from dataclasses import dataclass
from common.utils import resource_path
from data.converter_UOM import UOMConverter

UOM_CSV = resource_path("data/csv_UOM.csv")

@dataclass
class BaseUnit:
    """Represents a fundamental unit of measure."""
    uom: str       # e.g., kg, l, ha
    category: str  # weight, volume, area, length
    state: str     # dry, liquid, no
    factor: float  # conversion factor to standard unit
    standard: str  # standard unit for this category

class CompositeUOM:
    """Represents a composite unit X/Y (like kg/ha, ml/100m, etc.)."""
    
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
        return self._check_if_concentration()
    
    def _check_if_concentration(self) -> bool:
        """Internal method to check if this represents a concentration."""
        # Handle special cases first
        if self.denominator is None:
            return self.numerator in ['%', 'g/l', 'lb/gal']
        
        # For compound units, check categories - need repository instance
        from data.repository_UOM import UOMRepository
        repo = UOMRepository.get_instance()
        num_unit = repo.get_base_unit(self.numerator)
        den_unit = repo.get_base_unit(self.denominator)
        
        if num_unit and den_unit:
            return ((num_unit.category == 'weight' and den_unit.category == 'volume') or 
                    (num_unit.category == 'weight' and den_unit.category == 'weight'))
        return False

class UOMRepository:
    """Repository for base units and composite UOM operations with EIQ capabilities."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = UOMRepository()
        return cls._instance
    
    def __init__(self):
        self.csv_file = UOM_CSV
        self._base_units: Dict[str, BaseUnit] = {}
        self._converter = None  # Will be initialized after loading units
        self._load_base_units()
        self._initialize_converter()
    
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
            from common.widgets.tracer import calculation_tracer
            calculation_tracer.log_substep(f"Error loading base units: {e}", level=1)
            self._base_units = {}
    
    def _initialize_converter(self):
        """Initialize the converter after base units are loaded."""
        self._converter = UOMConverter(self)
    
    def get_base_unit(self, uom: str) -> Optional[BaseUnit]:
        """Get a base unit by name."""
        return self._base_units.get(uom.lower())
    
    def convert_base_unit(self, value: float, from_uom: str, to_uom: str) -> float:
        """Convert between two base units of the same category."""
        return self._converter.convert_base_unit(value, from_uom, to_uom)
    
    def convert_composite_uom(self, value: float, from_uom: CompositeUOM, to_uom: CompositeUOM, 
                            user_preferences: dict = None) -> float:
        """Convert between composite UOMs, handling special cases with validation."""
        return self._converter.convert_composite_uom(value, from_uom, to_uom, user_preferences)
    
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
        return self._converter.convert_concentration(value, from_uom, to_uom)
    
    def validate_concentration_units(self, concentration_uom: str, rate_unit_type: str) -> bool:
        """
        Validate that concentration units are compatible with rate units.
        
        Args:
            concentration_uom: Concentration UOM (%, g/l, etc.)
            rate_unit_type: "weight" or "volume"
            
        Returns:
            bool: True if compatible, False otherwise
        """
        return self._converter.validate_concentration_units(concentration_uom, rate_unit_type)
    
    def get_rate_compatibility_info(self, rate_uom: str) -> Dict:
        """
        Get information about rate UOM compatibility and requirements.
        
        Args:
            rate_uom: Application rate UOM
            
        Returns:
            Dict with compatibility information
        """
        return self._converter.get_rate_compatibility_info(rate_uom)
    
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
        return self._converter.validate_eiq_calculation_inputs(
            rate, rate_uom, ai_concentration, ai_concentration_uom, ai_eiq
        )