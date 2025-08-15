"""
STIR Scenario model for the PestIQ App.

This module defines the STIRScenario class which represents a complete
tillage operation scenario for a field/rotation.
"""

from typing import List, Optional
from .model_operation import Operation


class STIRScenario:
    """
    Represents a STIR tillage scenario.
    
    Stores information about a tillage plan including
    scenario name and all planned operations.
    """
    
    def __init__(self, 
                 name: str = "New STIR Scenario",
                 operations: Optional[List[Operation]] = None):
        """
        Initialize a STIRScenario instance.
        
        Args:
            name (str): User-friendly name for the scenario
            operations (list): List of Operation objects
        """
        self.name = name
        self.operations = operations if operations else []
    
    def add_operation(self, operation: Operation) -> None:
        """
        Add an operation to the scenario.
        
        Args:
            operation: Operation object to add
        """
        self.operations.append(operation)
    
    def remove_operation(self, index: int) -> bool:
        """
        Remove an operation from the scenario.
        
        Args:
            index (int): Index of the operation to remove
            
        Returns:
            bool: True if successful, False if index out of range
        """
        if 0 <= index < len(self.operations):
            self.operations.pop(index)
            return True
        return False
    
    def get_total_stir(self) -> float:
        """
        Calculate the total STIR value for all operations in the scenario.
        
        Returns:
            float: Sum of all operation STIR values
        """
        return sum(op.stir_value for op in self.operations if op.stir_value is not None)
    
    def clone(self) -> 'STIRScenario':
        """
        Create a copy of this scenario with a new name.
            
        Returns:
            STIRScenario: New scenario instance with copied data
        """
        # Copy operations using the Operation model's to_dict/from_dict methods for deep cloning
        new_operations = []
        for op in self.operations:
            op_dict = op.to_dict()
            new_op = Operation.from_dict(op_dict)
            new_operations.append(new_op)
        
        # Create new scenario with copied data
        new_scenario = STIRScenario(
            name=f"Copy of {self.name}",
            operations=new_operations
        )
        
        return new_scenario
    
    def to_dict(self) -> dict:
        """
        Convert scenario to dictionary representation.
        
        Returns:
            dict: Scenario data as dictionary
        """
        return {
            "name": self.name,
            "operations": [op.to_dict() for op in self.operations],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'STIRScenario':
        """
        Create a STIRScenario instance from dictionary data.
        
        Args:
            data (dict): Scenario data
        
        Returns:
            STIRScenario: New STIRScenario instance
        """
        # Create scenario with basic properties
        scenario = cls(name=data.get("name", "Unnamed STIR Scenario"))
        
        # Convert operation dictionaries to Operation objects
        if "operations" in data and isinstance(data["operations"], list):
            scenario.operations = [Operation.from_dict(op_data) for op_data in data["operations"]]
        
        return scenario
    
    def get_operations_count(self) -> int:
        """
        Get the number of operations in this scenario.
        
        Returns:
            int: Number of operations
        """
        return len(self.operations)
    
    def is_empty(self) -> bool:
        """
        Check if this scenario is empty (no operations).
        
        Returns:
            bool: True if no operations, False otherwise
        """
        return len(self.operations) == 0