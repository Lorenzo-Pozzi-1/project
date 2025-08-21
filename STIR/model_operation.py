"""
Operation model for STIR calculations.

This module defines the Operation class which represents a field operation
(tillage, planting, harvesting, etc.) with all necessary parameters for
STIR calculation.
"""

from typing import Optional, Dict, Any


class Operation:
    """
    Represents a field operation for STIR calculations.
    
    Stores information about a single field operation including timing,
    machine details, and operational parameters needed for STIR calculation.
    """
    
    def __init__(self,
                 operation_group: str = "pre-plant",  # "pre-plant", "in-season", "harvest"
                 machine_name: str = "",
                 depth: float = 0.0,
                 depth_uom: str = "cm",
                 speed: float = 0.0,
                 speed_uom: str = "km/h",
                 surface_area_disturbed: float = 100.0,  # Percentage (0-100)
                 number_of_passes: int = 1,
                 tillage_type_factor: float = 0.0,  # Tillage intensity factor
                 machine_rotates: bool = False,  # Whether machine has rotating components
                 stir_value: Optional[float] = None):
        """
        Initialize an Operation.
        
        Args:
            operation_group: Type of operation ("pre-plant", "in-season", "harvest")
            machine_name: Name of the machine/implement used
            depth: Working depth of the operation
            depth_uom: Unit of measure for depth (e.g., "cm", "in")
            speed: Operating speed
            speed_uom: Unit of measure for speed (e.g., "km/h", "mph")
            surface_area_disturbed: Percentage of surface area disturbed (0-100)
            number_of_passes: Number of times the operation is performed
            tillage_type_factor: Tillage intensity factor (1.0=Inversion+mixing, 0.8=Mixing+someinversion, 
                               0.7=Mixing only, 0.4=Lifting+fracturing, 0.15=Compression)
            machine_rotates: Whether the machine has rotating/powered components (True/False)
            stir_value: Calculated STIR value (if None, will be calculated)
        """
        self.operation_group = operation_group
        self.machine_name = machine_name
        self.depth = depth
        self.depth_uom = depth_uom
        self.speed = speed
        self.speed_uom = speed_uom
        self.surface_area_disturbed = surface_area_disturbed
        self.number_of_passes = number_of_passes
        self.tillage_type_factor = tillage_type_factor
        self.machine_rotates = machine_rotates
        self.stir_value = stir_value
    
    def load_machine_defaults(self, machine_name: str) -> bool:
        """
        Load default parameters from a machine.
        
        Args:
            machine_name: Name of the machine to load defaults from
            
        Returns:
            bool: True if machine found and defaults loaded, False otherwise
        """
        try:
            from .repository_machine import MachineRepository
            
            repo = MachineRepository.get_instance()
            machine = repo.get_machine_by_name(machine_name)
            
            if machine:
                self.machine_name = machine.name
                self.depth = machine.depth
                self.depth_uom = machine.depth_uom
                self.speed = machine.speed
                self.speed_uom = machine.speed_uom
                self.surface_area_disturbed = machine.surface_area_disturbed
                self.tillage_type_factor = machine.tillage_type_factor
                self.machine_rotates = machine.rotates
                return True
            
            return False
            
        except Exception:
            return False
    
    def calculate_stir(self) -> float:
        """
        Calculate the STIR value for this operation.
        
        Uses different formulas based on whether the machine rotates:
        - For rotating machines: STIR = (tillage type factor x 3.25) x (speed [km/h] x 0.5) x (depth [cm]) x (surface area disturbed [%])
        - For non-rotating machines: STIR = (tillage type factor x 3.25) x (speed [km/h] x 0.5) x (depth [cm]) x (surface area disturbed [%])
        
        Note: Currently using the same formula for both - will be updated with specific formulas later.
        
        Returns:
            Calculated STIR value
        """
        # Convert units to standard values if needed
        depth_cm = self._convert_depth_to_cm()
        speed_kmh = self._convert_speed_to_kmh()
        surface_fraction = self.surface_area_disturbed / 100.0
        
        # Calculate STIR using different formulas based on machine rotation
        if self.machine_rotates:
            # Formula for rotating machines (placeholder - same as current)
            stir = (self.tillage_type_factor * 3.25) * (speed_kmh * 0.5) * depth_cm * surface_fraction
        else:
            # Formula for non-rotating machines (placeholder - same as current)
            stir = (self.tillage_type_factor * 3.25) * (speed_kmh * 0.5) * depth_cm * surface_fraction
        
        # Apply number of passes
        total_stir = stir * self.number_of_passes
        
        self.stir_value = round(total_stir)
        return self.stir_value
    
    def _convert_depth_to_cm(self) -> float:
        """Convert depth to centimeters."""
        if self.depth_uom.lower() == 'inch':
            return self.depth * 2.54
        elif self.depth_uom.lower() == 'cm':
            return self.depth
        else:
            # Default to cm
            return self.depth
    
    def _convert_speed_to_kmh(self) -> float:
        """Convert speed to km/h."""
        if self.speed_uom.lower() == 'mph':
            return self.speed * 1.60934
        elif self.speed_uom.lower() == 'km/h':
            return self.speed
        else:
            # Default to km/h
            return self.speed
    
    def get_depth_in_unit(self, target_uom: str) -> float:
        """Get depth converted to the specified unit."""
        depth_cm = self._convert_depth_to_cm()
        
        if target_uom.lower() == 'inch':
            return depth_cm / 2.54
        elif target_uom.lower() == 'cm':
            return depth_cm
        else:
            # Default to cm
            return depth_cm
    
    def get_speed_in_unit(self, target_uom: str) -> float:
        """Get speed converted to the specified unit."""
        speed_kmh = self._convert_speed_to_kmh()
        
        if target_uom.lower() == 'mph':
            return speed_kmh / 1.60934
        elif target_uom.lower() == 'km/h':
            return speed_kmh
        else:
            # Default to km/h
            return speed_kmh
    
    def clone(self) -> 'Operation':
        """
        Create a copy of this operation.
        
        Returns:
            New Operation instance with the same parameters
        """
        return Operation(
            operation_group=self.operation_group,
            machine_name=self.machine_name,
            depth=self.depth,
            depth_uom=self.depth_uom,
            speed=self.speed,
            speed_uom=self.speed_uom,
            surface_area_disturbed=self.surface_area_disturbed,
            number_of_passes=self.number_of_passes,
            tillage_type_factor=self.tillage_type_factor,
            stir_value=self.stir_value
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert operation to dictionary for serialization.
        
        Returns:
            Dictionary representation of the operation
        """
        return {
            'operation_group': self.operation_group,
            'machine_name': self.machine_name,
            'depth': self.depth,
            'depth_uom': self.depth_uom,
            'speed': self.speed,
            'speed_uom': self.speed_uom,
            'surface_area_disturbed': self.surface_area_disturbed,
            'number_of_passes': self.number_of_passes,
            'tillage_type_factor': self.tillage_type_factor,
            'machine_rotates': self.machine_rotates,
            'stir_value': self.stir_value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Operation':
        """
        Create Operation from dictionary.
        
        Args:
            data: Dictionary containing operation data
            
        Returns:
            Operation instance created from dictionary data
        """
        return cls(
            operation_group=data.get('operation_group', 'pre-plant'),
            machine_name=data.get('machine_name', ''),
            depth=data.get('depth', 0.0),
            depth_uom=data.get('depth_uom', 'cm'),
            speed=data.get('speed', 0.0),
            speed_uom=data.get('speed_uom', 'km/h'),
            surface_area_disturbed=data.get('surface_area_disturbed', 100.0),
            number_of_passes=data.get('number_of_passes', 1),
            tillage_type_factor=data.get('tillage_type_factor', 0.0),
            machine_rotates=data.get('machine_rotates', False),
            stir_value=data.get('stir_value')
        )
    
    def __str__(self) -> str:
        """String representation of the operation."""
        return f"{self.machine_name}: {self.operation_group.title()}, STIR: {self.calculate_stir()}"

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (f"Operation(group='{self.operation_group}', machine='{self.machine_name}', "
                f"depth={self.depth}{self.depth_uom}, speed={self.speed}{self.speed_uom}, "
                f"passes={self.number_of_passes}, tillage_factor={self.tillage_type_factor}, "
                f"stir={self.stir_value})")