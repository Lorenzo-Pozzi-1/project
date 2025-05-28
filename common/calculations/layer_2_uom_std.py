"""
UOM Standardization (1st Layer) for EIQ Calculations
Handles all unit conversions and dimensional analysis validation
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from common.widgets.tracer import calculation_tracer
from data.repository_UOM import UOMRepository, CompositeUOM

@dataclass
class StandardizedEIQInputs:
    """Container for standardized EIQ calculation inputs"""
    rate_per_ha: float                    # [kg/ha]  or [l/ha] 
    rate_unit_type: str                   # "weight" or "volume"
    ai_concentration_per_unit: float      # [kg/kg]  or [kg/l]
    ai_eiq_per_kg: float                  # [eiq/kg]
    applications: int                     # dimensionless

@dataclass
class ProductStandardizedInputs:
    """Container for standardized product-level inputs"""
    rate_per_ha: float              # [kg/ha]  or [l/ha]
    rate_unit_type: str             # "weight" or "volume" 
    active_ingredients: List[Dict]  # List of standardized AI data
    applications: int               # dimensionless

class EIQUOMStandardizer:
    """
    Handles all UOM conversions and validations for EIQ calculations.
    Ensures dimensional analysis is correct before passing to calculation layer.
    """
    
    def __init__(self):
        # Initialize UOM repository
        self.uom_repo = UOMRepository.get_instance()
    
    def standardize_single_ai_inputs(self, 
                                   ai_eiq: float,
                                   ai_concentration: float, 
                                   ai_concentration_uom: str,
                                   application_rate: float,
                                   application_rate_uom: str,
                                   applications: int,
                                   user_preferences: dict = None,
                                   # NEW: Optional pre-standardized rate parameters
                                   pre_standardized_rate: float = None,
                                   pre_standardized_rate_type: str = None) -> StandardizedEIQInputs:
        """
        Standardize all inputs for single AI EIQ calculation.
        
        Args:
            ai_eiq: Active ingredient EIQ (Cornell units - eiq/lb)
            ai_concentration: AI concentration in product  
            ai_concentration_uom: UOM for concentration (%, g/l, lb/gal, etc.)
            application_rate: Product application rate (used only if not pre-standardized)
            application_rate_uom: UOM for application rate (used only if not pre-standardized)
            applications: Number of applications
            user_preferences: User preferences for UOM conversions
            pre_standardized_rate: Already converted rate in [kg/ha] or [l/ha] (optional)
            pre_standardized_rate_type: Type of pre-standardized rate ("weight" or "volume")
            
        Returns:
            StandardizedEIQInputs with all values in standard units
        """
        
        calculation_tracer.log(f"\n\tI have to standardize_single_ai_inputs (AI EIQ={ai_eiq}, [AI]={ai_concentration} {ai_concentration_uom})")
        
        # Step 1: Handle application rate - use pre-standardized if available
        if pre_standardized_rate is not None and pre_standardized_rate_type is not None:
            calculation_tracer.log(f"\n\tSTEP 1 - Standardizing app. rate\n\t\tUsing pre-standardized rate: {pre_standardized_rate} {"kg/ha" if pre_standardized_rate_type == "weight" else "l/ha"}\n\tDONE")
            rate_per_ha = pre_standardized_rate
            rate_unit_type = pre_standardized_rate_type
        else:
            calculation_tracer.log(f"\tNo pre-standardized rate provided, converting: {application_rate} {application_rate_uom}")
            calculation_tracer.log("\tSTEP 1 - Standardizing application rate")
            rate_per_ha, rate_unit_type = self._standardize_application_rate(
                application_rate, application_rate_uom, user_preferences
            )
            calculation_tracer.log(f"\tApplication rate standardized to {rate_per_ha} with unit type '{rate_unit_type}'")
        
        # Step 2: Standardize AI concentration to match rate units
        calculation_tracer.log("\n\tSTEP 2 - Standardizing AI concentration to match rate units")
        ai_concentration_per_unit = self._standardize_ai_concentration(
            ai_concentration, ai_concentration_uom, rate_unit_type
        )
        calculation_tracer.log(f"\tDONE! AI concentration standardized to {ai_concentration_per_unit} {"kg/kg" if pre_standardized_rate_type == "weight" else "kg/l"}")
        
        # Step 3: Standardize EIQ to [eiq/kg] (Cornell is eiq/lb)
        calculation_tracer.log("\n\tSTEP 3 - Standardizing AI EIQ from Cornell units")
        ai_eiq_per_kg = self._standardize_ai_eiq(ai_eiq)
        calculation_tracer.log(f"\tAI EIQ standardized to {ai_eiq_per_kg:.2f} eiq/kg")
        
        # Step 4: Validate dimensional analysis
        calculation_tracer.log("\n\tSTEP 4 - Validating dimensional analysis")
        self._validate_dimensional_analysis(rate_unit_type, ai_concentration_per_unit)
        calculation_tracer.log("\tDimensional analysis validation passed")
        
        result = StandardizedEIQInputs(
            rate_per_ha=rate_per_ha,
            rate_unit_type=rate_unit_type,
            ai_concentration_per_unit=ai_concentration_per_unit,
            ai_eiq_per_kg=ai_eiq_per_kg,
            applications=applications
        )
        calculation_tracer.log(f"\tReturning standardized inputs: rate={result.rate_per_ha}, type={result.rate_unit_type}")
        return result
    
    def standardize_product_inputs(self,
                                 active_ingredients: List[Dict],
                                 application_rate: float,
                                 application_rate_uom: str, 
                                 applications: int,
                                 user_preferences: dict = None) -> ProductStandardizedInputs:
        """
        Standardize inputs for product-level EIQ calculation.
        
        Args:
            active_ingredients: List of dicts with 'eiq', 'concentration', 'uom', 'name'
            application_rate: Product application rate
            application_rate_uom: UOM for application rate
            applications: Number of applications
            user_preferences: User preferences for conversions
            
        Returns:
            ProductStandardizedInputs with all AIs standardized consistently
        """
        
        calculation_tracer.log(f"\nI first have to standardize_product_inputs ({applications} applications with {len(active_ingredients)} AIs at {application_rate} {application_rate_uom})")
        
        # Step 1: Standardize application rate ONCE at product level
        calculation_tracer.log("\n  STEP 1 - Standardizing product application rate...\n")
        rate_per_ha, rate_unit_type = self._standardize_application_rate(
            application_rate, application_rate_uom, user_preferences
        )
        calculation_tracer.log(f"\n  COMPLETE! Product application rate standardized to {rate_per_ha} {'kg/ha' if rate_unit_type == 'weight' else 'l/ha'}")
        
        # Step 2: Standardize all active ingredients using the pre-standardized rate
        calculation_tracer.log("\n  STEP 2 - Standardizing all active ingredients using pre-standardized rate...")
        standardized_ais = []
        for i, ai in enumerate(active_ingredients):
            calculation_tracer.log(f"\n  Processing AI {i+1}/{len(active_ingredients)}: {ai.get('name', 'Unknown')}")
            
            if not ai or ai.get('eiq') in [None, "--"] or ai.get('concentration') in [None, "--"]:
                calculation_tracer.log(f"Skipping AI {ai.get('name', 'Unknown')} due to missing data")
                continue
                
            try:
                # Pass pre-standardized rate to avoid redundant conversion
                standardized_ai = self.standardize_single_ai_inputs(
                    ai_eiq=float(ai['eiq']),
                    ai_concentration=float(ai['concentration']),
                    ai_concentration_uom=ai['uom'],
                    application_rate=application_rate,  # Original values still passed for signature compatibility
                    application_rate_uom=application_rate_uom,
                    applications=1,  # Will be applied at product level
                    user_preferences=user_preferences,
                    pre_standardized_rate=rate_per_ha,
                    pre_standardized_rate_type=rate_unit_type
                )
                
                ai_data = {
                    'name': ai.get('name', 'Unknown'),
                    'concentration_per_unit': standardized_ai.ai_concentration_per_unit,
                    'eiq_per_kg': standardized_ai.ai_eiq_per_kg
                }
                standardized_ais.append(ai_data)
                calculation_tracer.log(f"\n  DONE! I have Successfully standardized AI {ai.get('name', 'Unknown')}")
                
            except Exception as e:
                calculation_tracer.log(f"Error standardizing AI {ai.get('name', 'unknown')}: {e}")
                continue
        
        result = ProductStandardizedInputs(
            rate_per_ha=rate_per_ha,
            rate_unit_type=rate_unit_type,
            active_ingredients=standardized_ais,
            applications=applications
        )
        calculation_tracer.log(f"\nI have standardized the product inputs (with {len(standardized_ais)} standardized AIs)")
        return result
    
    def _standardize_application_rate(self, 
                                    rate: float, 
                                    rate_uom: str, 
                                    user_preferences: dict = None) -> Tuple[float, str]:
        """
        Convert application rate to standard [kg/ha] or [l/ha].
        
        Returns:
            Tuple of (standardized_rate, unit_type) where unit_type is "weight" or "volume"
        """
        
        if not rate or not rate_uom:
            raise ValueError("Application rate and UOM are required")
        
        from_uom = CompositeUOM(rate_uom) # Parse the UOM into numerator / denominator
        
        # Determine target unit (kg or l) based on numerator type
        numerator_unit = self.uom_repo.get_base_unit(from_uom.numerator)
        if not numerator_unit:
            raise ValueError(f"Unknown unit in rate: {from_uom.numerator}")
                
        if numerator_unit.category == 'weight':
            target_uom = CompositeUOM("kg/ha")
            unit_type = "weight"
        elif numerator_unit.category == 'volume':
            target_uom = CompositeUOM("l/ha") 
            unit_type = "volume"
        else:
            raise ValueError(f"Application rate must be weight/area or volume/area, got: {rate_uom}")
        
        # Convert to standard rate
        calculation_tracer.log(f"\tI have to _standardize_application_rate: Converting {rate} from {from_uom.original_string} to {target_uom.original_string}... ",)
        standardized_rate = self.uom_repo.convert_composite_uom(
            rate, from_uom, target_uom, user_preferences
        )
        calculation_tracer.log(f"\tStandardization complete - {rate} {rate_uom} = {standardized_rate} {target_uom.original_string}")
        
        return standardized_rate, unit_type
    
    def _standardize_ai_concentration(self, concentration: float, concentration_uom: str, target_rate_type: str) -> float:
        """
        Convert AI concentration to match the application rate units.
        
        Args:
            concentration: AI concentration value
            concentration_uom: UOM for concentration (%, g/l, lb/gal, etc.)
            target_rate_type: "weight" or "volume" to match application rate
            
        Returns:
            Standardized concentration as [kg/kg] or [kg/l]
        """
        calculation_tracer.log(f"\t\t_standardize_ai_concentration from {concentration} {concentration_uom} ({target_rate_type} based)")
        
        if not concentration or not concentration_uom:
            raise ValueError("AI concentration and UOM are required")
        
        # Handle percentage - works with both weight and volume (THIS MAY CREATE CALCULATION ERRORS WHEN LABEL % IS VOLUME/VOLUME)
        if concentration_uom == '%':
            result = concentration / 100.0  # Convert to decimal [kg/kg]
            calculation_tracer.log(f"\t\tL2 - _standardize_ai_concentration: Converting percentage - {concentration}% = {result} (decimal)")
            return result
        
        from_uom = CompositeUOM(concentration_uom) # Parse the UOM into numerator / denominator
        
        # Determine target concentration UOM based on rate type
        if target_rate_type == "weight":
            target_uom = CompositeUOM("kg/kg")  # [kg AI / kg product]
        elif target_rate_type == "volume":
            target_uom = CompositeUOM("kg/l")   # [kg AI / l product]
        else:
            raise ValueError(f"Invalid rate type: {target_rate_type}")
        
        # Check if the conversion is physically possible (wet vs dry, can't mix them)
        if from_uom.is_concentration:
            # Check if source and target are compatible
            from_is_weight_per_volume = self._is_weight_per_volume(from_uom)
            from_is_weight_per_weight = self._is_weight_per_weight(from_uom)
            
            if from_is_weight_per_volume and target_rate_type == "weight":
                # e.g. cannot convert lb/gal to kg/kg - this is physically impossible
                raise ValueError(
                    f"Cannot convert {concentration_uom} (weight/volume) to weight/weight concentration. "
                    f"Product with {concentration_uom} concentration must use volume-based application rates."
                )
            
            if from_is_weight_per_weight and target_rate_type == "volume":
                # Could convert kg/kg to kg/l, but would need product density - not implemented yet
                # For now, assume similar density to water (1 kg/l)
                calculation_tracer.log(f"\t\tL2 - _standardize_ai_concentration: WARNING! Converting concentration from {concentration_uom} to kg/l assuming density ~1 kg/l")
        
        # Convert concentration
        try:
            calculation_tracer.log(f"\t\t_standardize_ai_concentration: from {concentration} {from_uom.original_string} to {target_uom.original_string}")
            standardized_concentration = self.uom_repo.convert_composite_uom(
                concentration, from_uom, target_uom
            )
            calculation_tracer.log(f"\t\tConversion complete - {concentration} {concentration_uom} = {standardized_concentration} {target_uom.original_string}")
            return standardized_concentration
        except Exception as e:
            calculation_tracer.log(f"Conversion failed with error: {e}")
            raise ValueError(
                f"\tL2._standardize_ai_concentration: Cannot convert concentration from {concentration_uom} to {target_uom.original_string}: {e}"
            )
    
    def _standardize_ai_eiq(self, ai_eiq: float) -> float:
        """
        Convert AI EIQ from Cornell units (eiq/lb) to standard (eiq/kg). 0s and None values are handled gracefully.
        
        Args:
            ai_eiq: EIQ value from Cornell (eiq/lb)
            
        Returns:
            EIQ in standard units (eiq/kg)
        """
        calculation_tracer.log(f"\t\tI have to _standardize_ai_eiq: from {ai_eiq:.2f} (eiq/lb) to standard (eiq/kg)")
        
        if ai_eiq is None:
            calculation_tracer.log("\t\tL2 - _standardize_ai_eiq: WARNING! Missing AI eiq value, calculating assuming it is 0.")
            return 0.0
        
        if ai_eiq == 0:
            calculation_tracer.log("\t\tL2 - _standardize_ai_eiq: AI EIQ is 0, returning 0.0")
            return 0.0
        
        # Cornell EIQ is per pound, convert to per kg
        conversion_factor = self.uom_repo.convert_base_unit(1,'lb','kg')
        result = ai_eiq / conversion_factor
        calculation_tracer.log(f"\t\tDONE! {result:.2f} eiq/kg")
        return result
    
    def _validate_dimensional_analysis(self, rate_unit_type: str, ai_concentration: float):
        """
        Validate that dimensional analysis will work correctly.
        
        Expected outcomes:
        - Weight rate: [kg/ha] x [kg/kg] x [eiq/kg] = [eiq/ha]
        - Volume rate: [l/ha]  x [kg/l]  x [eiq/kg] = [eiq/ha]
        """
        calculation_tracer.log(f"\t\t_validate_dimensional_analysis for rate type '{rate_unit_type}' with concentration {ai_concentration}: ", end="")
        
        if rate_unit_type not in ["weight", "volume"]:
            raise ValueError(f"Invalid rate unit type: {rate_unit_type}")
        
        if ai_concentration <= 0:
            calculation_tracer.log(f"\t\tL2 - _validate_dimensional_analysis: ERROR - AI concentration {ai_concentration} must be positive")
            raise ValueError("AI concentration must be positive")
        
        # Additional validations could go here
        # For example, checking reasonable ranges for concentrations
        if rate_unit_type == "weight" and ai_concentration > 1.0:
            calculation_tracer.log(f"\t\tL2 - _validate_dimensional_analysis: ERROR - Weight-based concentration {ai_concentration} cannot exceed 1.0 (100%)")
            raise ValueError("Layer2._validate_dimensional_analysis: Weight-based concentration cannot exceed 1.0 (100%)")
        
        calculation_tracer.log("passed")
        
    def _is_weight_per_volume(self, uom: CompositeUOM) -> bool:
        """Check if UOM is weight per volume (like lb/gal, g/l)."""
        
        if not uom.is_concentration:
            calculation_tracer.log("\t\tL2 - _is_weight_per_volume: UOM is not a concentration, returning False")
            return False
        
        num_unit = self.uom_repo.get_base_unit(uom.numerator)
        den_unit = self.uom_repo.get_base_unit(uom.denominator)
        
        is_weight_per_volume = (num_unit and den_unit and num_unit.category == 'weight' and den_unit.category == 'volume')
        calculation_tracer.log(f"\t\t\t{uom.original_string} _is_weight_per_volume? {is_weight_per_volume}")
        return is_weight_per_volume
    
    def _is_weight_per_weight(self, uom: CompositeUOM) -> bool:
        """Check if UOM is weight per weight (like g/kg, %)."""
        
        if uom.numerator == '%':
            calculation_tracer.log("\t\t\tL2 - _is_weight_per_weight: UOM is percentage, returning True")
            return True
            
        if not uom.is_concentration:
            return False
        
        num_unit = self.uom_repo.get_base_unit(uom.numerator)
        den_unit = self.uom_repo.get_base_unit(uom.denominator)
        
        is_weight_per_weight = (num_unit and den_unit and num_unit.category == 'weight' and den_unit.category == 'weight')
        calculation_tracer.log(f"\t\t\t{uom.original_string} _is_weight_per_weight? {is_weight_per_weight}")
        return is_weight_per_weight