"""
UOM Repository and Composite UOM System for the LORENZO POZZI Pesticide App.

This module provides a compositional approach to unit of measure handling
with enhanced concentration conversion capabilities for EIQ calculations.
"""

import csv
from typing import Optional, Dict
from dataclasses import dataclass
from common import resource_path
from common.widgets.tracer import calculation_tracer

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
        
        # For compound units, check categories
        repo = UOMRepository.get_instance()
        num_unit = repo.get_base_unit(self.numerator)
        den_unit = repo.get_base_unit(self.denominator)
        
        if num_unit and den_unit:
            return ((num_unit.category == 'weight' and den_unit.category == 'volume') or 
                    (num_unit.category == 'weight' and den_unit.category == 'weight'))
        return False

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
            calculation_tracer.log_substep(f"Error loading base units: {e}", level=1)
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
        
        calculation_tracer.log_substep(f"Converting {value} {from_uom.original_string} → {to_uom.original_string}", level=3)
        
        try:
            # Validate physical state compatibility
            self._validate_physical_state_compatibility(from_uom, to_uom)

            # Handle concentration units
            if from_uom.is_concentration and to_uom.is_concentration:
                result = self._convert_concentration(value, from_uom, to_uom)
                return result
            
            # IMPORTANT: Check for special conversions (user preferences) FIRST
            if self._needs_user_preferences(from_uom, to_uom):
                calculation_tracer.log_substep("Requires user preferences (row spacing/seeding rate)", level=4)
                result = self._convert_with_preferences(value, from_uom, to_uom, user_preferences)
                return result
            
            # Handle standard rate conversions (only if not needing user preferences)
            if from_uom.is_rate and to_uom.is_rate:
                calculation_tracer.log_substep("Standard rate conversion", level=4)
                result = self._convert_rate(value, from_uom, to_uom, user_preferences)
                return result
            
            # If we get here, the conversion is not supported
            if from_uom.is_concentration and to_uom.is_rate:
                raise ValueError(f"Cannot convert concentration unit '{from_uom.original_string}' to rate unit '{to_uom.original_string}'")
            elif from_uom.is_rate and to_uom.is_concentration:
                raise ValueError(f"Cannot convert rate unit '{from_uom.original_string}' to concentration unit '{to_uom.original_string}'")
            else:
                raise ValueError(f"Unsupported conversion: {from_uom.original_string} to {to_uom.original_string}")
                
        except ValueError as e:
            # Re-raise ValueError with more context
            raise ValueError(f"Unit conversion error: {str(e)}")
        except Exception as e:
            # Handle other exceptions
            raise ValueError(f"Unexpected error during unit conversion from {from_uom.original_string} to {to_uom.original_string}: {str(e)}")
    
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
        
        # Try using the base composite UOM conversion
        try:
            from_composite = CompositeUOM(from_uom)
            to_composite = CompositeUOM(to_uom)
            return self.convert_composite_uom(value, from_composite, to_composite)
        except Exception as e:
            raise ValueError(f"repo. Cannot convert concentration from {from_uom} to {to_uom}: {e}")
    
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
    
    def _validate_physical_state_compatibility(self, from_uom: CompositeUOM, to_uom: CompositeUOM):
        """Validate that we're not converting between incompatible physical states."""
        # Get the numerator units (the "amount" part)
        from_num_unit = self.get_base_unit(from_uom.numerator)
        to_num_unit = self.get_base_unit(to_uom.numerator)
        
        if not from_num_unit or not to_num_unit:
            return  # Can't validate unknown units
        
        # Check if trying to convert between dry and wet
        if from_num_unit.state == 'dry' and to_num_unit.state == 'wet':
            raise ValueError(
                f"Cannot convert dry weight unit '{from_uom.numerator}' to liquid volume unit '{to_uom.numerator}'. "
                f"These represent different physical states and cannot be directly converted."
            )
        
        if from_num_unit.state == 'wet' and to_num_unit.state == 'dry':
            raise ValueError(
                f"Cannot convert liquid volume unit '{from_uom.numerator}' to dry weight unit '{to_uom.numerator}'. "
                f"These represent different physical states and cannot be directly converted."
            )
        
        # Allow conversions within same state or involving 'no' state (area, length)
        return
    
    def _convert_concentration(self, value: float, from_uom: CompositeUOM, to_uom: CompositeUOM) -> float:
        """Convert concentration units to standard units."""
        calculation_tracer.log_substep(f"Converting concentration: {value} {from_uom.original_string} → {to_uom.original_string}", level=4)
        
        # Handle percentage conversion
        if from_uom.numerator == '%':
            calculation_tracer.log_substep("Converting from percentage", level=5)
            return value / 100.0  # Convert percentage to decimal
        
        # Handle other concentration conversions directly using base unit conversion
        try:
            # Convert numerator (amount units: g to kg, lb to kg, etc.)
            num_factor = self.convert_base_unit(1.0, from_uom.numerator, to_uom.numerator)
            
            # Convert denominator if different (volume units: l to l, gal to l, etc.)
            if from_uom.denominator and to_uom.denominator:
                den_factor = self.convert_base_unit(1.0, from_uom.denominator, to_uom.denominator)
            else:
                den_factor = 1.0
            
            # For concentrations: multiply by numerator factor, divide by denominator factor
            result = value * num_factor / den_factor
            calculation_tracer.log_substep(f"Concentration conversion result: {result:.4f}", level=5)
            return result
            
        except Exception as e:
            calculation_tracer.log_substep(f"Concentration conversion error: {e}", level=5)
            raise ValueError(f"Cannot convert concentration from {from_uom.original_string} to {to_uom.original_string}: {e}")
    
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
        if from_uom.denominator in ['100m', '1000ft', 'm', 'ft'] and \
           to_uom.denominator in ['ha', 'acre']:
            return True
        
        # Seed treatments like kg/cwt need seeding rate
        if from_uom.denominator in ['cwt', '100kg'] and to_uom.denominator in ['ha', 'acre']:
            return True
        
        return False
    
    def _convert_with_preferences(self, value: float, from_uom: CompositeUOM, to_uom: CompositeUOM,
                                 user_preferences: dict) -> float:
        """Convert using user preferences for row spacing and seeding rate."""
        if not user_preferences:
            raise ValueError("User preferences required for this conversion")
        
        # Linear to area conversion (amount/length → amount/ha)
        if from_uom.denominator in ['100m', '1000ft', 'm', 'ft']:
            return self._convert_linear_to_area(value, from_uom, to_uom, user_preferences)
        
        # Seed treatment conversion (amount/cwt → amount/ha)
        elif from_uom.denominator in ['cwt', '100kg']:
            return self._convert_seed_treatment_to_area(value, from_uom, to_uom, user_preferences)
        
        raise ValueError(f"No preference-based conversion available for {from_uom.original_string} to {to_uom.original_string}")
    
    def _convert_linear_to_area(self, value: float, from_uom: CompositeUOM, to_uom: CompositeUOM,
                            user_preferences: dict) -> float:
        """
        Convert linear rates to area rates using row spacing.
        """
        calculation_tracer.log_substep("Converting linear rate to area rate", level=4)
        
        # Step 1: Convert to standard linear rate (amount/m)
        # First convert the denominator part to meters
        if from_uom.denominator in ['100m', '1000ft']:
            # Handle special cases where denominator is not just a unit but a quantity
            if from_uom.denominator == '100m':
                amount_per_m = value / 100.0  # Convert from amount/100m to amount/m
            elif from_uom.denominator == '1000ft':
                feet_per_meter = self.convert_base_unit(1.0, 'm', 'ft')
                amount_per_m = value / (1000.0 * feet_per_meter)  # Convert from amount/1000ft to amount/m
        else:
            # Standard conversion for simple units
            meter_factor = self.convert_base_unit(1.0, from_uom.denominator, 'm')
            amount_per_m = value * meter_factor  # Inverse because it's in denominator
        
        calculation_tracer.log_substep(f"Step 1: {value} {from_uom.original_string} = {amount_per_m:.3f} {from_uom.numerator}/m", level=5)
        
        # Step 2: Get row spacing and convert to meters
        row_spacing = user_preferences.get('default_row_spacing', 34.0)
        row_spacing_unit = user_preferences.get('default_row_spacing_unit', 'inch')
        row_spacing_m = self.convert_base_unit(row_spacing, row_spacing_unit, 'm')
        calculation_tracer.log_substep(f"Step 2: Row spacing {row_spacing} {row_spacing_unit} = {row_spacing_m:.3f} m", level=5)

        # Step 3: Calculate rows per meter and meters of rows per hectare
        m_of_rows_per_ha = 10000.0 / row_spacing_m
        calculation_tracer.log_substep(f"Step 3: Meters of rows per hectare: {m_of_rows_per_ha:.1f} m/ha", level=5)
        
        # Step 4: Convert amount/m to amount/ha
        amount_per_ha = amount_per_m * m_of_rows_per_ha
        calculation_tracer.log_substep(f"Step 4: {amount_per_ha:.3f} {from_uom.numerator}/ha", level=5)
        
        # Step 5: Convert numerator to match target unit if needed
        if from_uom.numerator != to_uom.numerator:
            num_factor = self.convert_base_unit(1.0, from_uom.numerator, to_uom.numerator)
            amount_per_ha *= num_factor
            calculation_tracer.log_substep(f"Step 5: Unit conversion {from_uom.numerator} → {to_uom.numerator} (×{num_factor:.3f})", level=5)
        
        # Step 6: Convert to target area unit if needed
        if to_uom.denominator != 'ha':
            area_factor = self.convert_base_unit(1.0, 'ha', to_uom.denominator)
            amount_per_ha *= area_factor
            calculation_tracer.log_substep(f"Step 6: Area conversion ha → {to_uom.denominator} (×{area_factor:.3f})", level=5)
        
        calculation_tracer.log_conversion(value, from_uom.original_string, to_uom.original_string, f"{amount_per_ha:.3f}", level=4, is_last=True)
        return amount_per_ha
    
    def _convert_seed_treatment_to_area(self, value: float, from_uom: CompositeUOM, to_uom: CompositeUOM, user_preferences: dict) -> float:
        """
        Convert seed treatment rates to area rates using seeding rate.
        
        Args:
            value: Application rate value (e.g., 5.0 for "5 ml/cwt")
            from_uom: Source UOM (e.g., "ml/cwt", "fl oz/100kg") 
            to_uom: Target UOM (e.g., "l/ha", "kg/ha")
            user_preferences: User preferences containing seeding rate info
            
        Returns:
            Converted rate in target area units
            
        Formula:
            [amount/seed_weight] x [seed_weight/area] = [amount/area]
            e.g., [ml/cwt] x [cwt/ha] = [ml/ha] → [l/ha]
        """
        calculation_tracer.log_substep("Converting seed treatment rate to area rate", level=4)
        
        # Step 1: Parse and standardize seeding rate to kg/ha
        seeding_rate = user_preferences.get('default_seeding_rate', 20)
        seeding_rate_unit = user_preferences.get('default_seeding_rate_unit', 'cwt/acre')
                
        # Parse seeding rate UOM
        seeding_uom = CompositeUOM(seeding_rate_unit)
        
        # Convert seeding rate to kg/ha
        seeding_rate_kg_per_ha = seeding_rate
        
        # Convert numerator to kg
        if seeding_uom.numerator != 'kg':
            kg_factor = self.convert_base_unit(1.0, seeding_uom.numerator, 'kg')
            seeding_rate_kg_per_ha *= kg_factor
        
        # Convert denominator to ha  
        if seeding_uom.denominator != 'ha':
            ha_factor = self.convert_base_unit(1.0, seeding_uom.denominator, 'ha')
            seeding_rate_kg_per_ha /= ha_factor
        
        calculation_tracer.log_substep(f"Step 1: Seeding rate {seeding_rate} {seeding_rate_unit} = {seeding_rate_kg_per_ha:.1f} kg/ha", level=5)
        
        # Step 2: Standardize application rate to standard units per kg of seed
        # Determine if application rate numerator is wet or dry
        app_num_unit = self.get_base_unit(from_uom.numerator)
        if not app_num_unit:
            raise ValueError(f"Unknown application rate unit: {from_uom.numerator}")
        
        # Convert application rate numerator to standard units
        if app_num_unit.state == 'wet' or app_num_unit.category == 'volume':
            # Convert to liters per kg of seed (l/kg)
            target_app_numerator = 'l'
            standard_app_rate = self.convert_base_unit(value, from_uom.numerator, 'l')
        else:
            # Convert to kg per kg of seed (kg/kg) 
            target_app_numerator = 'kg'
            standard_app_rate = self.convert_base_unit(value, from_uom.numerator, 'kg')
        
        # Convert application rate denominator to kg (seed weight)
        if from_uom.denominator != 'kg':
            seed_kg_factor = self.convert_base_unit(1.0, from_uom.denominator, 'kg')
            standard_app_rate /= seed_kg_factor
        
        calculation_tracer.log_substep(f"Step 2: App rate {value} {from_uom.original_string} = {standard_app_rate:.3f} {target_app_numerator}/kg", level=5)
        
        # Step 3: Apply conversion formula
        # [amount/kg_seed] x [kg_seed/ha] = [amount/ha]
        amount_per_ha = standard_app_rate * seeding_rate_kg_per_ha
        
        # Step 4: Convert to target UOM if needed
        final_result = amount_per_ha
        
        # Convert numerator if needed (e.g., l to ml, kg to g)
        if to_uom.numerator != target_app_numerator:
            num_factor = self.convert_base_unit(1.0, target_app_numerator, to_uom.numerator)
            final_result *= num_factor
            calculation_tracer.log_substep(f"Step 4a: Unit conversion {target_app_numerator} → {to_uom.numerator} (×{num_factor:.3f})", level=5)
        
        # Convert denominator if needed (e.g., ha to acre)
        if to_uom.denominator != 'ha':
            den_factor = self.convert_base_unit(1.0, 'ha', to_uom.denominator)
            final_result *= den_factor
            calculation_tracer.log_substep(f"Step 4b: Area conversion ha → {to_uom.denominator} (×{den_factor:.3f})", level=5)
        
        calculation_tracer.log_conversion(value, from_uom.original_string, to_uom.original_string, f"{final_result:.3f}", level=4, is_last=True)
        return final_result