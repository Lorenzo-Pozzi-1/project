"""
Machine model for STIR calculations.

This module defines the Machine class which represents a tillage machine/implement
with default operational parameters.
"""

from typing import Dict, Any


class Machine:
    """
    Represents a tillage machine/implement for STIR calculations.
    
    Stores information about a machine including its default operational
    parameters that can be used to initialize operations.
    """
    
    def __init__(self,
                 name: str = "",
                 depth: float = 0.0,
                 depth_uom: str = "cm",
                 speed: float = 0.0,
                 speed_uom: str = "km/h",
                 surface_area_disturbed: float = 100.0,
                 tillage_type_factor: float = 0.7):
        """
        Initialize a Machine.
        
        Args:
            name: Name of the machine/implement
            depth: Default working depth
            depth_uom: Unit of measure for depth (e.g., "cm", "in")
            speed: Default operating speed
            speed_uom: Unit of measure for speed (e.g., "km/h", "mph")
            surface_area_disturbed: Default percentage of surface area disturbed (0-100)
            tillage_type_factor: Default tillage intensity factor (1.0=Inversion+mixing, 
                               0.8=Mixing+some inversion, 0.7=Mixing only, 0.4=Lifting+fracturing, 
                               0.15=Compression)
        """
        self.name = name
        self.depth = depth
        self.depth_uom = depth_uom
        self.speed = speed
        self.speed_uom = speed_uom
        self.surface_area_disturbed = surface_area_disturbed
        self.tillage_type_factor = tillage_type_factor
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert machine to dictionary representation.
        
        Returns:
            dict: Machine data as dictionary
        """
        return {
            "name": self.name,
            "depth": self.depth,
            "depth_uom": self.depth_uom,
            "speed": self.speed,
            "speed_uom": self.speed_uom,
            "surface_area_disturbed": self.surface_area_disturbed,
            "tillage_type_factor": self.tillage_type_factor
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Machine':
        """
        Create Machine instance from dictionary.
        
        Args:
            data: Dictionary containing machine data
            
        Returns:
            Machine: New Machine instance
        """
        return cls(
            name=data.get("name", ""),
            depth=data.get("depth", 0.0),
            depth_uom=data.get("depth_uom", "cm"),
            speed=data.get("speed", 0.0),
            speed_uom=data.get("speed_uom", "km/h"),
            surface_area_disturbed=data.get("surface_area_disturbed", 100.0),
            tillage_type_factor=data.get("tillage_type_factor", 0.7)
        )
    
    def create_default_operation(self, operation_group: str = "pre-plant"):
        """
        Create an Operation with this machine's default parameters.
        
        Args:
            operation_group: Type of operation ("pre-plant", "in-season", "harvest")
            
        Returns:
            Operation: New Operation instance with machine defaults
        """
        from .model_operation import Operation
        
        return Operation(
            operation_group=operation_group,
            machine_name=self.name,
            depth=self.depth,
            depth_uom=self.depth_uom,
            speed=self.speed,
            speed_uom=self.speed_uom,
            surface_area_disturbed=self.surface_area_disturbed,
            tillage_type_factor=self.tillage_type_factor
        )
    
    def __str__(self) -> str:
        """Return string representation of the machine."""
        return f"Machine: {self.name}"
    
    def __repr__(self) -> str:
        """Return detailed string representation of the machine."""
        return (f"Machine(name='{self.name}', depth={self.depth}, "
                f"speed={self.speed}, tillage_factor={self.tillage_type_factor})")
