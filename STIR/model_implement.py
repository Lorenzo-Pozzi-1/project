"""
Implement model for custom machine creation.

This module defines the Implement class which represents individual implements
that can be combined to create custom machines.
"""

from typing import Dict, Any


class Implement:
    """
    Represents an individual implement that can be part of a custom machine.
    
    Stores information about an implement including its tillage characteristics.
    """
    
    def __init__(self,
                 name: str = "",
                 tillage_type_factor: float = 0.0,
                 picture: str = ""):
        """
        Initialize an Implement.
        
        Args:
            name: Name of the implement
            tillage_type_factor: Tillage intensity factor for this implement
            picture: Filename of the implement picture (e.g., "chisel.png")
        """
        self.name = name
        self.tillage_type_factor = tillage_type_factor
        self.picture = picture
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert implement to dictionary representation.
        
        Returns:
            dict: Implement data as dictionary
        """
        return {
            "name": self.name,
            "tillage_type_factor": self.tillage_type_factor,
            "picture": self.picture
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Implement':
        """
        Create Implement instance from dictionary.
        
        Args:
            data: Dictionary containing implement data
            
        Returns:
            Implement: New Implement instance
        """
        return cls(
            name=data.get("name", ""),
            tillage_type_factor=data.get("tillage_type_factor", 0.0),
            picture=data.get("picture", "")
        )
    
    def __str__(self) -> str:
        """Return string representation of the implement."""
        return f"Implement: {self.name} (factor: {self.tillage_type_factor})"
    
    def __repr__(self) -> str:
        """Return detailed string representation of the implement."""
        return (f"Implement(name='{self.name}', "
                f"tillage_factor={self.tillage_type_factor})")


# Hardcoded tillage type options as per USDA standards
TILLAGE_TYPE_OPTIONS = [
    (1.0, "1.0 = Inversion + mixing"),
    (0.8, "0.8 = Mixing + some inversion"),
    (0.7, "0.7 = Mixing only"),
    (0.4, "0.4 = Lifting + fracturing"),
    (0.15, "0.15 = Compression")
]


def load_implements_from_csv(csv_file_path: str) -> list['Implement']:
    """
    Load implements from CSV file.
    
    Args:
        csv_file_path: Path to the CSV file containing implement data
        
    Returns:
        List of Implement objects
    """
    import csv
    implements = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    name = row.get('name', '').strip()
                    if not name:
                        continue
                        
                    implement = Implement(
                        name=name,
                        tillage_type_factor=float(row.get('tillage_type_factor', 0.0)),
                        picture=row.get('picture', '').strip()
                    )
                    implements.append(implement)
                    
                except (ValueError, TypeError) as e:
                    print(f"Warning: Skipping invalid implement row: {row}. Error: {e}")
                    continue
                    
    except FileNotFoundError:
        print(f"Warning: Could not find implements file: {csv_file_path}")
    except Exception as e:
        print(f"Error loading implements: {str(e)}")
    
    return implements
