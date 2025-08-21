"""
Machine Repository for STIR calculations.

This module provides a centralized repository for accessing and filtering 
machine data, with CSV loading and caching for performance optimization.
"""

import csv
import os
from PySide6.QtWidgets import QMessageBox
from typing import List, Optional
from .model_machine import Machine
from common.utils import resource_path

machines_csv = resource_path("STIR/csv_machines.csv")

class MachineRepository:
    """
    Centralized repository for machine data.
    
    This class is responsible for loading, filtering, and providing
    access to machine data throughout the application.
    """
    
    _instance = None  # Singleton instance
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = MachineRepository()
        return cls._instance
    
    def __init__(self):
        """Initialize the repository."""
        self.csv_file = machines_csv
        
        # Cache storage
        self._all_machines = None  # List of all Machine objects
        
    def get_all_machines(self) -> List[Machine]:
        """Get all machines, loading from CSV if needed."""
        if self._all_machines is None:
            self._load_machines()
        return self._all_machines
    
    def get_machine_by_name(self, name: str) -> Optional[Machine]:
        """
        Get a specific machine by name.
        
        Args:
            name: Name of the machine to find
            
        Returns:
            Machine object if found, None otherwise
        """
        machines = self.get_all_machines()
        for machine in machines:
            if machine.name == name:
                return machine
        return None
    
    def get_machine_names(self) -> List[str]:
        """
        Get list of all machine names.
        
        Returns:
            List of machine names
        """
        machines = self.get_all_machines()
        return [machine.name for machine in machines]
    
    def _load_machines(self):
        """Load machine data from CSV file."""
        try:
            self._all_machines = []
            
            # Load standard machines
            self._load_machines_from_file(self.csv_file)
            
            # Load custom machines
            custom_machines_csv = resource_path("STIR/csv_custom_machines.csv")
            self._load_machines_from_file(custom_machines_csv, is_custom=True)
                        
        except Exception as e:
            QMessageBox.critical(
                None,
                "Error Loading Machines",
                f"An error occurred while loading machines: {str(e)}"
            )
            self._all_machines = []
    
    def _load_machines_from_file(self, file_path: str, is_custom: bool = False):
        """Load machines from a specific CSV file."""
        try:
            if not os.path.exists(file_path):
                if is_custom:
                    # Custom machines file doesn't exist yet, that's OK
                    return
                else:
                    raise FileNotFoundError(f"Could not find machines file: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8-sig') as file:  # Handle BOM
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        # Skip empty rows
                        name = row.get('name', '').strip()
                        if not name:
                            continue
                            
                        machine = Machine(
                            name=name,
                            depth=float(row.get('depth', 0)),
                            depth_uom=row.get('depth_uom', 'cm').strip(),
                            speed=float(row.get('speed', 0)),
                            speed_uom=row.get('speed_uom', 'km/h').strip(),
                            surface_area_disturbed=float(row.get('surface_area_disturbed', 100)),
                            tillage_type_factor=float(row.get('tillage_type_factor', 0.7)),
                            picture=row.get('picture', '').strip(),
                            rotates=str(row.get('rotates', 'FALSE')).upper() == 'TRUE'
                        )
                        self._all_machines.append(machine)
                        
                    except (ValueError, TypeError) as e:
                        # Skip invalid rows and continue (only if name is not empty)
                        if row.get('name', '').strip():
                            print(f"Warning: Skipping invalid machine row: {row}. Error: {e}")
                        continue
                        
        except FileNotFoundError:
            if not is_custom:
                QMessageBox.critical(
                    None,
                    "File Not Found",
                    f"Could not find machines file: {file_path}"
                )
        except Exception as e:
            print(f"Error loading machines from {file_path}: {str(e)}")
    
    def reload_data(self):
        """Force reload of machine data from CSV."""
        self._all_machines = None
        self.get_all_machines()
    
    def get_machines_count(self) -> int:
        """Get total number of machines."""
        return len(self.get_all_machines())
