"""
UOM Converter for the LORENZO POZZI Pesticide App.

This module contains all the conversion logic and agricultural domain-specific
calculations for unit of measure operations.
"""

from typing import Dict
from common.widgets.tracer import calculation_tracer

class UOMConverter:
    """Handles all UOM conversion logic and agricultural calculations."""
    
    def __init__(self, repository):
        """Initialize converter with reference to repository for unit lookups."""
        self.repository = repository
    
    def convert_base_unit(self, value: float, from_uom: str, to_uom: str) -> float:
        """Convert between two base units of the same category."""
        from_unit = self.repository.get_base_unit(from_uom)
        to_unit = self.repository.get_base_unit(to_uom)
        
        if not from_unit or not to_unit:
            raise ValueError(f"Unknown unit: {from_uom} or {to_uom}")
        
        if from_unit.category != to_unit.category:
            raise ValueError(f"Cannot convert {from_uom} ({from_unit.category}) to {to_uom} ({to_unit.category})")
        
        # Convert to standard, then to target
        standard_value = value * from_unit.factor
        return standard_value / to_unit.factor
    
    def convert_composite_uom(self, value: float, from_uom, to_uom, 
                            user_preferences: dict = None) -> float:
        """Convert between composite UOMs, handling special cases with validation."""
        
        calculation_tracer.log_substep(f"Converting {value} {from_uom.original_string} → {to_uom.original_string}", level=3)
        
        try:
            # Validate physical state compatibility
            self._validate_physical_state_compatibility(from_uom, to_uom)

            # Handle concentration units
            if from_uom.is_concentration and to_uom.is_concentration:
                result = self._convert_concentration_composite(value, from_uom, to_uom)
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
            from data.repository_UOM import CompositeUOM
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
        
        from data.repository_UOM import CompositeUOM
        concentration_composite = CompositeUOM(concentration_uom)
        
        # For weight-based rates, concentration should be weight/weight
        if rate_unit_type == "weight":
            if not concentration_composite.is_concentration:
                return False
            # Check if it's weight/weight
            num_unit = self.repository.get_base_unit(concentration_composite.numerator)
            den_unit = self.repository.get_base_unit(concentration_composite.denominator)
            return (num_unit and den_unit and 
                   num_unit.category == 'weight' and den_unit.category == 'weight')
        
        # For volume-based rates, concentration should be weight/volume
        elif rate_unit_type == "volume":
            if not concentration_composite.is_concentration:
                return False
            # Check if it's weight/volume
            num_unit = self.repository.get_base_unit(concentration_composite.numerator)
            den_unit = self.repository.get_base_unit(concentration_composite.denominator)
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
        from data.repository_UOM import CompositeUOM
        rate_composite = CompositeUOM(rate_uom)
        numerator_unit = self.repository.get_base_unit(rate_composite.numerator)
        
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
    
    def _validate_physical_state_compatibility(self, from_uom, to_uom):
        """Validate that we're not converting between incompatible physical states."""
        
        # SPECIAL CASE: Allow seed treatment conversions (bidirectional)
        if self._needs_user_preferences(from_uom, to_uom):
            return  # Skip physical state validation for preference-based conversions
        
        # Get the numerator units (the "amount" part)
        from_num_unit = self.repository.get_base_unit(from_uom.numerator)
        to_num_unit = self.repository.get_base_unit(to_uom.numerator)
        
        if not from_num_unit or not to_num_unit:
            return  # Can't validate unknown units
        
        # Check if trying to convert between dry and liquid
        if from_num_unit.state == 'dry' and to_num_unit.state == 'liquid':
            raise ValueError(
                f"Cannot convert dry weight unit '{from_uom.numerator}' to liquid volume unit '{to_uom.numerator}'. "
                f"These represent different physical states and cannot be directly converted."
            )
        
        if from_num_unit.state == 'liquid' and to_num_unit.state == 'dry':
            raise ValueError(
                f"Cannot convert liquid volume unit '{from_uom.numerator}' to dry weight unit '{to_uom.numerator}'. "
                f"These represent different physical states and cannot be directly converted."
            )
        
        # Allow conversions within same state or involving 'no' state (area, length)
        return
    
    def _convert_concentration_composite(self, value: float, from_uom, to_uom) -> float:
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
    
    def _convert_rate(self, value: float, from_uom, to_uom, 
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
    
    def _needs_user_preferences(self, from_uom, to_uom) -> bool:
        """Check if conversion needs user preferences (row spacing, seeding rate)."""
        
        # Get denominator units
        from_denom_unit = self.repository.get_base_unit(from_uom.denominator) if from_uom.denominator else None
        to_denom_unit = self.repository.get_base_unit(to_uom.denominator) if to_uom.denominator else None
        
        if not from_denom_unit or not to_denom_unit:
            return False
        
        # Linear ↔ Area conversions need row spacing (bidirectional)
        if ((from_denom_unit.category == 'length' and to_denom_unit.category == 'area') or
            (from_denom_unit.category == 'area' and to_denom_unit.category == 'length')):
            return True
        
        # Seed weight ↔ Area conversions need seeding rate (bidirectional)
        if ((from_denom_unit.category == 'weight' and to_denom_unit.category == 'area') or
            (from_denom_unit.category == 'area' and to_denom_unit.category == 'weight')):
            return True
        
        return False
    
    def _convert_with_preferences(self, value: float, from_uom, to_uom,
                                 user_preferences: dict) -> float:
        """Convert using user preferences for row spacing and seeding rate."""
        if not user_preferences:
            raise ValueError("User preferences required for this conversion")
        
        # Determine conversion type based on denominator categories
        from_denom_unit = self.repository.get_base_unit(from_uom.denominator) if from_uom.denominator else None
        to_denom_unit = self.repository.get_base_unit(to_uom.denominator) if to_uom.denominator else None
        
        if not from_denom_unit or not to_denom_unit:
            raise ValueError(f"Unknown denominator units in conversion: {from_uom.original_string} to {to_uom.original_string}")
        
        # Linear to/from area conversion
        if ((from_denom_unit.category == 'length' and to_denom_unit.category == 'area') or
            (from_denom_unit.category == 'area' and to_denom_unit.category == 'length')):
            
            # Determine direction and call appropriate method
            if from_denom_unit.category == 'length':
                return self._convert_linear_to_area(value, from_uom, to_uom, user_preferences)
            else:
                return self._convert_area_to_linear(value, from_uom, to_uom, user_preferences)
        
        # Seed treatment to/from area conversion  
        elif ((from_denom_unit.category == 'weight' and to_denom_unit.category == 'area') or
              (from_denom_unit.category == 'area' and to_denom_unit.category == 'weight')):
            
            # Determine direction and call appropriate method
            if from_denom_unit.category == 'weight':
                return self._convert_seed_treatment_to_area(value, from_uom, to_uom, user_preferences)
            else:
                return self._convert_area_to_seed_treatment(value, from_uom, to_uom, user_preferences)
        
        raise ValueError(f"No preference-based conversion available for {from_uom.original_string} to {to_uom.original_string}")
    
    def _convert_linear_to_area(self, value: float, from_uom, to_uom,
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
    
    def _convert_area_to_linear(self, value: float, from_uom, to_uom,
                               user_preferences: dict) -> float:
        """
        Convert area rates to linear rates using row spacing.
        Reverse of _convert_linear_to_area.
        """
        calculation_tracer.log_substep("Converting area rate to linear rate", level=4)
        
        # Step 1: Get row spacing and convert to meters
        row_spacing = user_preferences.get('default_row_spacing', 34.0)
        row_spacing_unit = user_preferences.get('default_row_spacing_unit', 'inch')
        row_spacing_m = self.convert_base_unit(row_spacing, row_spacing_unit, 'm')
        calculation_tracer.log_substep(f"Step 1: Row spacing {row_spacing} {row_spacing_unit} = {row_spacing_m:.3f} m", level=5)
        
        # Step 2: Calculate meters of rows per hectare
        m_of_rows_per_ha = 10000.0 / row_spacing_m
        calculation_tracer.log_substep(f"Step 2: Meters of rows per hectare: {m_of_rows_per_ha:.1f} m/ha", level=5)
        
        # Step 3: Convert from area unit to ha if needed
        amount_per_ha = value
        if from_uom.denominator != 'ha':
            ha_factor = self.convert_base_unit(1.0, from_uom.denominator, 'ha')
            amount_per_ha *= ha_factor
            calculation_tracer.log_substep(f"Step 3: Area conversion {from_uom.denominator} → ha (×{ha_factor:.3f})", level=5)
        
        # Step 4: Convert amount/ha to amount/m
        amount_per_m = amount_per_ha / m_of_rows_per_ha
        calculation_tracer.log_substep(f"Step 4: {amount_per_ha:.3f} {from_uom.numerator}/ha = {amount_per_m:.3f} {from_uom.numerator}/m", level=5)
        
        # Step 5: Convert numerator unit if needed
        final_amount_per_m = amount_per_m
        if from_uom.numerator != to_uom.numerator:
            num_factor = self.convert_base_unit(1.0, from_uom.numerator, to_uom.numerator)
            final_amount_per_m *= num_factor
            calculation_tracer.log_substep(f"Step 5: Unit conversion {from_uom.numerator} → {to_uom.numerator} (×{num_factor:.3f})", level=5)
        
        # Step 6: Convert from standard linear rate (amount/m) to target linear unit
        if to_uom.denominator in ['100m', '1000ft']:
            # Handle special cases where denominator is not just a unit but a quantity
            if to_uom.denominator == '100m':
                final_result = final_amount_per_m * 100.0  # Convert from amount/m to amount/100m
            elif to_uom.denominator == '1000ft':
                feet_per_meter = self.convert_base_unit(1.0, 'm', 'ft')
                final_result = final_amount_per_m * (1000.0 * feet_per_meter)  # Convert from amount/m to amount/1000ft
        else:
            # Standard conversion for simple units
            meter_factor = self.convert_base_unit(1.0, 'm', to_uom.denominator)
            final_result = final_amount_per_m / meter_factor  # Inverse because it's in denominator
        
        calculation_tracer.log_conversion(value, from_uom.original_string, to_uom.original_string, f"{final_result:.3f}", level=4, is_last=True)
        return final_result
    
    def _convert_seed_treatment_to_area(self, value: float, from_uom, to_uom, user_preferences: dict) -> float:
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
        
        from data.repository_UOM import CompositeUOM        
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
        # Determine if application rate numerator is liquid or dry
        app_num_unit = self.repository.get_base_unit(from_uom.numerator)
        if not app_num_unit:
            raise ValueError(f"Unknown application rate unit: {from_uom.numerator}")
        
        # Convert application rate numerator to standard units
        if app_num_unit.state == 'liquid' or app_num_unit.category == 'volume':
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
    
    def _convert_area_to_seed_treatment(self, value: float, from_uom, to_uom, 
                                       user_preferences: dict) -> float:
        """
        Convert area rates to seed treatment rates using seeding rate.
        Reverse of _convert_seed_treatment_to_area.
        
        Args:
            value: Application rate value (e.g., 5.0 for "5 ml/ha")
            from_uom: Source UOM (e.g., "ml/ha", "kg/ha") 
            to_uom: Target UOM (e.g., "ml/cwt", "fl oz/100kg")
            user_preferences: User preferences containing seeding rate info
            
        Returns:
            Converted rate in target seed treatment units
            
        Formula:
            [amount/area] ÷ [seed_weight/area] = [amount/seed_weight]
            e.g., [ml/ha] ÷ [cwt/ha] = [ml/cwt]
        """
        calculation_tracer.log_substep("Converting area rate to seed treatment rate", level=4)
        
        # Step 1: Parse and standardize seeding rate to kg/ha
        seeding_rate = user_preferences.get('default_seeding_rate', 20)
        seeding_rate_unit = user_preferences.get('default_seeding_rate_unit', 'cwt/acre')
        
        from data.repository_UOM import CompositeUOM        
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
        
        # Step 2: Convert from area unit to ha if needed
        amount_per_ha = value
        if from_uom.denominator != 'ha':
            ha_factor = self.convert_base_unit(1.0, from_uom.denominator, 'ha')
            amount_per_ha *= ha_factor
            calculation_tracer.log_substep(f"Step 2: Area conversion {from_uom.denominator} → ha (×{ha_factor:.3f})", level=5)
        
        # Step 3: Apply reverse conversion formula
        # [amount/ha] ÷ [kg_seed/ha] = [amount/kg_seed]
        amount_per_kg_seed = amount_per_ha / seeding_rate_kg_per_ha
        calculation_tracer.log_substep(f"Step 3: {amount_per_ha:.3f} {from_uom.numerator}/ha ÷ {seeding_rate_kg_per_ha:.1f} kg/ha = {amount_per_kg_seed:.3f} {from_uom.numerator}/kg", level=5)
        
        # Step 4: Determine target application rate units
        # Check if target numerator is liquid or dry to maintain consistency
        target_num_unit = self.repository.get_base_unit(to_uom.numerator)
        if not target_num_unit:
            raise ValueError(f"Unknown target application rate unit: {to_uom.numerator}")
        
        # Convert numerator if needed (e.g., ml to fl oz, kg to g)
        final_amount_per_seed_unit = amount_per_kg_seed
        if from_uom.numerator != to_uom.numerator:
            num_factor = self.convert_base_unit(1.0, from_uom.numerator, to_uom.numerator)
            final_amount_per_seed_unit *= num_factor
            calculation_tracer.log_substep(f"Step 4a: Unit conversion {from_uom.numerator} → {to_uom.numerator} (×{num_factor:.3f})", level=5)
        
        # Step 5: Convert from kg seed weight to target seed weight unit
        if to_uom.denominator != 'kg':
            seed_weight_factor = self.convert_base_unit(1.0, 'kg', to_uom.denominator)
            final_amount_per_seed_unit *= seed_weight_factor
            calculation_tracer.log_substep(f"Step 4b: Seed weight conversion kg → {to_uom.denominator} (×{seed_weight_factor:.3f})", level=5)
        
        calculation_tracer.log_conversion(value, from_uom.original_string, to_uom.original_string, f"{final_amount_per_seed_unit:.3f}", level=4, is_last=True)
        return final_amount_per_seed_unit