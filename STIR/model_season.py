"""
Season model for STIR calculations.

This module defines the Season class which represents a single crop year
with all tillage operations for that season.
"""

from datetime import date
from typing import List, Optional, Dict, Any
from .model_operation import Operation


class Season:
    """
    Represents a single crop season for STIR calculations.
    
    Stores information about a crop year including the crop planted
    and all tillage operations performed during that season.
    """
    
    def __init__(self, 
                 name: str = "New Season",
                 crop_year: Optional[int] = None,
                 crop: str = "",
                 operations: Optional[List[Operation]] = None):
        """
        Initialize a Season instance.
        
        Args:
            name (str): User-friendly name for the season
            crop_year (int): Year of the crop/season (defaults to current year)
            crop (str): Name of the crop planted this season
            operations (list): List of Operation objects for this season
        """
        self.name = name
        self.crop_year = crop_year if crop_year is not None else date.today().year
        self.crop = crop
        self.operations = operations if operations else []
    
    def add_operation(self, operation: Operation) -> None:
        """
        Add an operation to the season.
        
        Args:
            operation: Operation object to add
        """
        self.operations.append(operation)
    
    def remove_operation(self, index: int) -> bool:
        """
        Remove an operation from the season.
        
        Args:
            index (int): Index of the operation to remove
            
        Returns:
            bool: True if successful, False if index out of range
        """
        if 0 <= index < len(self.operations):
            self.operations.pop(index)
            return True
        return False
    
    def move_operation(self, from_index: int, to_index: int) -> bool:
        """
        Move an operation from one position to another.
        
        Args:
            from_index (int): Current index of the operation
            to_index (int): Target index for the operation
            
        Returns:
            bool: True if successful, False if indices out of range
        """
        if (0 <= from_index < len(self.operations) and 
            0 <= to_index < len(self.operations)):
            operation = self.operations.pop(from_index)
            self.operations.insert(to_index, operation)
            return True
        return False
    
    def get_total_stir(self) -> float:
        """
        Calculate the total STIR value for all operations in the season.
        
        Returns:
            float: Sum of all operation STIR values
        """
        return sum(op.stir_value for op in self.operations if op.stir_value is not None)
    
    def get_operations_by_group(self, group: str) -> List[Operation]:
        """
        Get all operations of a specific group.
        
        Args:
            group (str): Operation group ("pre-plant", "in-season", "harvest")
            
        Returns:
            List[Operation]: Operations in the specified group
        """
        return [op for op in self.operations if op.operation_group == group]
    
    def get_operation_groups(self) -> List[str]:
        """
        Get all unique operation groups in this season.
        
        Returns:
            List[str]: List of operation group names
        """
        groups = set(op.operation_group for op in self.operations)
        return sorted(list(groups))
    
    def clone(self) -> 'Season':
        """
        Create a copy of this season with a new name.
            
        Returns:
            Season: New season instance with copied data
        """
        # Copy operations using the Operation model's to_dict/from_dict methods for deep cloning
        new_operations = []
        for op in self.operations:
            op_dict = op.to_dict()
            new_op = Operation.from_dict(op_dict)
            new_operations.append(new_op)
        
        # Create new season with copied data
        new_season = Season(
            name=f"Copy of {self.name}",
            crop_year=self.crop_year,
            crop=self.crop,
            operations=new_operations
        )
        
        return new_season
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert season to dictionary representation.
        
        Returns:
            dict: Season data as dictionary
        """
        return {
            "name": self.name,
            "crop_year": self.crop_year,
            "crop": self.crop,
            "operations": [op.to_dict() for op in self.operations],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Season':
        """
        Create Season instance from dictionary.
        
        Args:
            data: Dictionary containing season data
            
        Returns:
            Season: New Season instance
        """
        operations = []
        for op_data in data.get("operations", []):
            operations.append(Operation.from_dict(op_data))
        
        return cls(
            name=data.get("name", "New Season"),
            crop_year=data.get("crop_year"),
            crop=data.get("crop", ""),
            operations=operations
        )
    
    def __str__(self) -> str:
        """Return string representation of the season."""
        return f"{self.name} ({self.crop_year}) - {self.crop}"
    
    def __repr__(self) -> str:
        """Return detailed string representation of the season."""
        return (f"Season(name='{self.name}', crop_year={self.crop_year}, "
                f"crop='{self.crop}', operations={len(self.operations)})")
