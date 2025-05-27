"""
UOM Standardization (1st Layer) for EIQ Calculations
Handles all unit conversions and dimensional analysis validation
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
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
        print("Layer 1 - __init__: Initializing EIQUOMStandardizer with UOM repository")
    
    def standardize_single_ai_inputs(self, 
                                   ai_eiq: float,
                                   ai_concentration: float, 
                                   ai_concentration_uom: str,
                                   application_rate: float,
                                   application_rate_uom: str,
                                   applications: int,
                                   user_preferences: dict = None) -> StandardizedEIQInputs:
        """
        Standardize all inputs for single AI EIQ calculation.
        
        Returns standardized inputs where dimensional analysis checks out:
        [kg/ha] x [kg/kg] x [eiq/kg] = [eiq/ha] OR [l/ha] x [kg/l] x [eiq/kg] = [eiq/ha]
        """
        
        print(f"Layer 1 - standardize_single_ai_inputs: Starting standardization with AI EIQ={ai_eiq}, concentration={ai_concentration} {ai_concentration_uom}, rate={application_rate} {application_rate_uom}, applications={applications}")
        
        # Step 1: Standardize application rate to [kg/ha] or [l/ha]
        print("Layer 1 - standardize_single_ai_inputs: Step 1 - Standardizing application rate")
        rate_per_ha, rate_unit_type = self._standardize_application_rate(
            application_rate, application_rate_uom, user_preferences
        )
        print(f"Layer 1 - standardize_single_ai_inputs: Application rate standardized to {rate_per_ha} with unit type '{rate_unit_type}'")
        
        # Step 2: Standardize AI concentration to match rate units
        print("Layer 1 - standardize_single_ai_inputs: Step 2 - Standardizing AI concentration to match rate units")
        ai_concentration_per_unit = self._standardize_ai_concentration(
            ai_concentration, ai_concentration_uom, rate_unit_type
        )
        print(f"Layer 1 - standardize_single_ai_inputs: AI concentration standardized to {ai_concentration_per_unit}")
        
        # Step 3: Standardize EIQ to [eiq/kg] (Cornell is eiq/lb)
        print("Layer 1 - standardize_single_ai_inputs: Step 3 - Standardizing AI EIQ from Cornell units")
        ai_eiq_per_kg = self._standardize_ai_eiq(ai_eiq)
        print(f"Layer 1 - standardize_single_ai_inputs: AI EIQ standardized to {ai_eiq_per_kg} eiq/kg")
        
        # Step 4: Validate dimensional analysis
        print("Layer 1 - standardize_single_ai_inputs: Step 4 - Validating dimensional analysis")
        self._validate_dimensional_analysis(rate_unit_type, ai_concentration_per_unit)
        print("Layer 1 - standardize_single_ai_inputs: Dimensional analysis validation passed")
        
        result = StandardizedEIQInputs(
            rate_per_ha=rate_per_ha,
            rate_unit_type=rate_unit_type,
            ai_concentration_per_unit=ai_concentration_per_unit,
            ai_eiq_per_kg=ai_eiq_per_kg,
            applications=applications
        )
        print(f"Layer 1 - standardize_single_ai_inputs: Returning standardized inputs: rate={result.rate_per_ha}, type={result.rate_unit_type}, concentration={result.ai_concentration_per_unit}, eiq={result.ai_eiq_per_kg}")
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
        
        print(f"Layer 1 - standardize_product_inputs: Starting product standardization with {len(active_ingredients)} active ingredients, rate={application_rate} {application_rate_uom}, applications={applications}")
        
        # Step 1: Standardize application rate
        print("Layer 1 - standardize_product_inputs: Step 1 - Standardizing product application rate")
        rate_per_ha, rate_unit_type = self._standardize_application_rate(
            application_rate, application_rate_uom, user_preferences
        )
        print(f"Layer 1 - standardize_product_inputs: Product application rate standardized to {rate_per_ha} with unit type '{rate_unit_type}'")
        
        # Step 2: Standardize all active ingredients to match rate units
        print("Layer 1 - standardize_product_inputs: Step 2 - Standardizing all active ingredients")
        standardized_ais = []
        for i, ai in enumerate(active_ingredients):
            print(f"Layer 1 - standardize_product_inputs: Processing AI {i+1}/{len(active_ingredients)}: {ai.get('name', 'Unknown')}")
            
            if not ai or ai.get('eiq') in [None, "--"] or ai.get('concentration') in [None, "--"]:
                print(f"Layer 1 - standardize_product_inputs: Skipping AI {ai.get('name', 'Unknown')} due to missing data")
                continue
                
            try:
                print(f"Layer 1 - standardize_product_inputs: Calling standardize_single_ai_inputs for AI {ai.get('name', 'Unknown')}")
                standardized_ai = self.standardize_single_ai_inputs(
                    ai_eiq=float(ai['eiq']),
                    ai_concentration=float(ai['concentration']),
                    ai_concentration_uom=ai['uom'],
                    application_rate=application_rate,
                    application_rate_uom=application_rate_uom,
                    applications=1,  # Will be applied at product level
                    user_preferences=user_preferences
                )
                
                ai_data = {
                    'name': ai.get('name', 'Unknown'),
                    'concentration_per_unit': standardized_ai.ai_concentration_per_unit,
                    'eiq_per_kg': standardized_ai.ai_eiq_per_kg
                }
                standardized_ais.append(ai_data)
                print(f"Layer 1 - standardize_product_inputs: Successfully standardized AI {ai.get('name', 'Unknown')}: concentration={ai_data['concentration_per_unit']}, eiq={ai_data['eiq_per_kg']}")
                
            except Exception as e:
                print(f"Layer 1 - standardize_product_inputs: Error standardizing AI {ai.get('name', 'unknown')}: {e}")
                continue
        
        result = ProductStandardizedInputs(
            rate_per_ha=rate_per_ha,
            rate_unit_type=rate_unit_type,
            active_ingredients=standardized_ais,
            applications=applications
        )
        print(f"Layer 1 - standardize_product_inputs: Returning product inputs with {len(standardized_ais)} standardized AIs")
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
        print(f"Layer 1 - _standardize_application_rate: Converting rate {rate} {rate_uom} to standard units")
        
        if not rate or not rate_uom:
            raise ValueError("Application rate and UOM are required")
        
        print(f"Layer 1 - _standardize_application_rate: Parsing composite UOM from '{rate_uom}'")
        from_uom = CompositeUOM(rate_uom) # Parse the UOM into numerator / denominator
        print(f"Layer 1 - _standardize_application_rate: Parsed UOM - numerator: {from_uom.numerator}, denominator: {from_uom.denominator}")
        
        # Determine target unit (kg or l) based on numerator type
        print(f"Layer 1 - _standardize_application_rate: Getting base unit for numerator '{from_uom.numerator}'")
        numerator_unit = self.uom_repo.get_base_unit(from_uom.numerator)
        if not numerator_unit:
            raise ValueError(f"Unknown unit in rate: {from_uom.numerator}")
        
        print(f"Layer 1 - _standardize_application_rate: Numerator unit category is '{numerator_unit.category}'")
        
        if numerator_unit.category == 'weight':
            target_uom = CompositeUOM("kg/ha")
            unit_type = "weight"
            print("Layer 1 - _standardize_application_rate: Target unit determined as kg/ha (weight-based)")
        elif numerator_unit.category == 'volume':
            target_uom = CompositeUOM("l/ha") 
            unit_type = "volume"
            print("Layer 1 - _standardize_application_rate: Target unit determined as l/ha (volume-based)")
        else:
            raise ValueError(f"Application rate must be weight/area or volume/area, got: {rate_uom}")
        
        # Convert to standard rate
        print(f"Layer 1 - _standardize_application_rate: Converting {rate} from {from_uom.original_string} to {target_uom.original_string}")
        standardized_rate = self.uom_repo.convert_composite_uom(
            rate, from_uom, target_uom, user_preferences
        )
        print(f"Layer 1 - _standardize_application_rate: Conversion complete - {rate} {rate_uom} = {standardized_rate} {target_uom.original_string}")
        
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
        print(f"Layer 1 - _standardize_ai_concentration: Converting concentration {concentration} {concentration_uom} to match rate type '{target_rate_type}'")
        
        if not concentration or not concentration_uom:
            raise ValueError("AI concentration and UOM are required")
        
        # Handle percentage - works with both weight and volume (THIS MAY CREATE CALCULATION ERRORS WHEN LABEL % IS VOLUME/VOLUME)
        if concentration_uom == '%':
            result = concentration / 100.0  # Convert to decimal [kg/kg]
            print(f"Layer 1 - _standardize_ai_concentration: Converting percentage - {concentration}% = {result} (decimal)")
            return result
        
        print(f"Layer 1 - _standardize_ai_concentration: Parsing composite UOM from '{concentration_uom}'")
        from_uom = CompositeUOM(concentration_uom) # Parse the UOM into numerator / denominator
        print(f"Layer 1 - _standardize_ai_concentration: Parsed concentration UOM - numerator: {from_uom.numerator}, denominator: {from_uom.denominator}")
        
        # Determine target concentration UOM based on rate type
        if target_rate_type == "weight":
            target_uom = CompositeUOM("kg/kg")  # [kg AI / kg product]
            print("Layer 1 - _standardize_ai_concentration: Target concentration unit set to kg/kg (weight-based)")
        elif target_rate_type == "volume":
            target_uom = CompositeUOM("kg/l")   # [kg AI / l product]
            print("Layer 1 - _standardize_ai_concentration: Target concentration unit set to kg/l (volume-based)")
        else:
            raise ValueError(f"Invalid rate type: {target_rate_type}")
        
        # Check if the conversion is physically possible (wet vs dry, can't mix them)
        if from_uom.is_concentration:
            print("Layer 1 - _standardize_ai_concentration: Checking physical compatibility of concentration units")
            # Check if source and target are compatible
            from_is_weight_per_volume = self._is_weight_per_volume(from_uom)
            from_is_weight_per_weight = self._is_weight_per_weight(from_uom)
            print(f"Layer 1 - _standardize_ai_concentration: Source is weight/volume: {from_is_weight_per_volume}, weight/weight: {from_is_weight_per_weight}")
            
            if from_is_weight_per_volume and target_rate_type == "weight":
                # e.g. cannot convert lb/gal to kg/kg - this is physically impossible
                raise ValueError(
                    f"Cannot convert {concentration_uom} (weight/volume) to weight/weight concentration. "
                    f"Product with {concentration_uom} concentration must use volume-based application rates."
                )
            
            if from_is_weight_per_weight and target_rate_type == "volume":
                # Could convert kg/kg to kg/l, but would need product density - not implemented yet
                # For now, assume similar density to water (1 kg/l)
                print(f"Layer 1 - _standardize_ai_concentration: WARNING! Converting concentration from {concentration_uom} to kg/l assuming density ~1 kg/l")
        
        # Convert concentration
        try:
            print(f"Layer 1 - _standardize_ai_concentration: Converting {concentration} from {from_uom.original_string} to {target_uom.original_string}")
            standardized_concentration = self.uom_repo.convert_composite_uom(
                concentration, from_uom, target_uom
            )
            print(f"Layer 1 - _standardize_ai_concentration: Conversion complete - {concentration} {concentration_uom} = {standardized_concentration} {target_uom.original_string}")
            return standardized_concentration
        except Exception as e:
            print(f"Layer 1 - _standardize_ai_concentration: Conversion failed with error: {e}")
            raise ValueError(
                f"Layer 1._standardize_ai_concentration: Cannot convert concentration from {concentration_uom} to {target_uom.original_string}: {e}"
            )
    
    def _standardize_ai_eiq(self, ai_eiq: float) -> float:
        """
        Convert AI EIQ from Cornell units (eiq/lb) to standard (eiq/kg). 0s and None values are handled gracefully.
        
        Args:
            ai_eiq: EIQ value from Cornell (eiq/lb)
            
        Returns:
            EIQ in standard units (eiq/kg)
        """
        print(f"Layer 1 - _standardize_ai_eiq: Converting AI EIQ {ai_eiq} from Cornell units (eiq/lb) to standard (eiq/kg)")
        
        if ai_eiq is None:
            print("Layer 1 - _standardize_ai_eiq: WARNING! Missing AI eiq value, calculating assuming it is 0.")
            return 0.0
        
        if ai_eiq == 0:
            print("Layer 1 - _standardize_ai_eiq: AI EIQ is 0, returning 0.0")
            return 0.0
        
        # Cornell EIQ is per pound, convert to per kg
        print("Layer 1 - _standardize_ai_eiq: Converting from lb to kg using UOM repository")
        result = self.uom_repo.convert_base_unit(ai_eiq, 'lb', 'kg')
        print(f"Layer 1 - _standardize_ai_eiq: Conversion complete - {ai_eiq} eiq/lb = {result} eiq/kg")
        return result
    
    def _validate_dimensional_analysis(self, rate_unit_type: str, ai_concentration: float):
        """
        Validate that dimensional analysis will work correctly.
        
        Expected outcomes:
        - Weight rate: [kg/ha] x [kg/kg] x [eiq/kg] = [eiq/ha]
        - Volume rate: [l/ha]  x [kg/l]  x [eiq/kg] = [eiq/ha]
        """
        print(f"Layer 1 - _validate_dimensional_analysis: Validating dimensional analysis for rate type '{rate_unit_type}' with concentration {ai_concentration}")
        
        if rate_unit_type not in ["weight", "volume"]:
            raise ValueError(f"Invalid rate unit type: {rate_unit_type}")
        
        if ai_concentration <= 0:
            print(f"Layer 1 - _validate_dimensional_analysis: ERROR - AI concentration {ai_concentration} must be positive")
            raise ValueError("AI concentration must be positive")
        
        # Additional validations could go here
        # For example, checking reasonable ranges for concentrations
        if rate_unit_type == "weight" and ai_concentration > 1.0:
            print(f"Layer 1 - _validate_dimensional_analysis: ERROR - Weight-based concentration {ai_concentration} cannot exceed 1.0 (100%)")
            raise ValueError("Layer1._validate_dimensional_analysis: Weight-based concentration cannot exceed 1.0 (100%)")
        
        print("Layer 1 - _validate_dimensional_analysis: All dimensional analysis checks passed")
        
    def _is_weight_per_volume(self, uom: CompositeUOM) -> bool:
        """Check if UOM is weight per volume (like lb/gal, g/l)."""
        print(f"Layer 1 - _is_weight_per_volume: Checking if {uom.original_string} is weight per volume")
        
        if not uom.is_concentration:
            print("Layer 1 - _is_weight_per_volume: UOM is not a concentration, returning False")
            return False
        
        num_unit = self.uom_repo.get_base_unit(uom.numerator)
        den_unit = self.uom_repo.get_base_unit(uom.denominator)
        
        is_weight_per_volume = (num_unit and den_unit and num_unit.category == 'weight' and den_unit.category == 'volume')
        print(f"Layer 1 - _is_weight_per_volume: Result for {uom.original_string}: {is_weight_per_volume}")
        return is_weight_per_volume
    
    def _is_weight_per_weight(self, uom: CompositeUOM) -> bool:
        """Check if UOM is weight per weight (like g/kg, %)."""
        print(f"Layer 1 - _is_weight_per_weight: Checking if {uom.original_string} is weight per weight")
        
        if uom.numerator == '%':
            print("Layer 1 - _is_weight_per_weight: UOM is percentage, returning True")
            return True
            
        if not uom.is_concentration:
            print("Layer 1 - _is_weight_per_weight: UOM is not a concentration, returning False")
            return False
        
        num_unit = self.uom_repo.get_base_unit(uom.numerator)
        den_unit = self.uom_repo.get_base_unit(uom.denominator)
        
        is_weight_per_weight = (num_unit and den_unit and num_unit.category == 'weight' and den_unit.category == 'weight')
        print(f"Layer 1 - _is_weight_per_weight: Result for {uom.original_string}: {is_weight_per_weight}")
        return is_weight_per_weight