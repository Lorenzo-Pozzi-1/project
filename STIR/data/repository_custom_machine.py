"""
Repository for managing custom machines data.

This module provides functionality to read, write, and manage custom machines
stored in CSV format.
"""

import csv
import os
from typing import List, Optional
from .model_custom_machine import CustomMachine, CustomMachineTool
from common.utils import resource_path


class CustomMachineRepository:
    """Repository for managing custom machines stored in CSV format."""
    
    _instance = None  # Singleton instance
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = CustomMachineRepository()
        return cls._instance
    
    def __init__(self, csv_file: str = "csv_custom_machines.csv"):
        """
        Initialize the repository.
        
        Args:
            csv_file: Name of the CSV file containing custom machines data
        """
        self.csv_file = csv_file
        self.csv_path = resource_path(f"STIR/data/{csv_file}")
    
    def load_all(self) -> List[CustomMachine]:
        """
        Load all custom machines from the CSV file.
        
        Returns:
            List[CustomMachine]: List of all custom machines
        """
        machines = []
        
        if not os.path.exists(self.csv_path):
            return machines
        
        try:
            with open(self.csv_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        machine = CustomMachine.from_dict(row)
                        machines.append(machine)
                    except Exception as e:
                        print(f"Error loading custom machine from row: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error reading custom machines CSV: {e}")
        
        return machines
    
    def save_all(self, machines: List[CustomMachine]) -> bool:
        """
        Save all custom machines to the CSV file.
        
        Args:
            machines: List of CustomMachine objects to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as file:
                if not machines:
                    # Write header only if no machines
                    writer = csv.writer(file)
                    writer.writerow(self._get_fieldnames())
                    return True
                
                # Write data
                fieldnames = self._get_fieldnames()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                
                for machine in machines:
                    writer.writerow(machine.to_dict())
                    
            return True
            
        except Exception as e:
            print(f"Error saving custom machines CSV: {e}")
            return False
    
    def add_machine(self, machine: CustomMachine) -> bool:
        """
        Add a new custom machine to the repository.
        
        Args:
            machine: CustomMachine to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        machines = self.load_all()
        machines.append(machine)
        return self.save_all(machines)
    
    def update_machine(self, old_name: str, updated_machine: CustomMachine) -> bool:
        """
        Update an existing custom machine in the repository.
        
        Args:
            old_name: Name of the machine to update
            updated_machine: Updated CustomMachine object
            
        Returns:
            bool: True if successful, False if machine not found
        """
        machines = self.load_all()
        
        for i, machine in enumerate(machines):
            if machine.name == old_name:
                machines[i] = updated_machine
                return self.save_all(machines)
        
        return False
    
    def delete_machine(self, name: str) -> bool:
        """
        Delete a custom machine from the repository.
        
        Args:
            name: Name of the machine to delete
            
        Returns:
            bool: True if successful, False if machine not found
        """
        machines = self.load_all()
        original_count = len(machines)
        
        machines = [machine for machine in machines if machine.name != name]
        
        if len(machines) < original_count:
            return self.save_all(machines)
        
        return False
    
    def find_by_name(self, name: str) -> Optional[CustomMachine]:
        """
        Find a custom machine by name.
        
        Args:
            name: Name of the machine to find
            
        Returns:
            CustomMachine: The machine if found, None otherwise
        """
        machines = self.load_all()
        
        for machine in machines:
            if machine.name == name:
                return machine
        
        return None
    
    def get_machine_by_name(self, name: str) -> Optional[CustomMachine]:
        """
        Get a custom machine by name (alias for find_by_name).
        
        Args:
            name: Name of the machine to find
            
        Returns:
            CustomMachine: The machine if found, None otherwise
        """
        return self.find_by_name(name)
    
    def get_machine_names(self) -> List[str]:
        """
        Get a list of all custom machine names.
        
        Returns:
            List[str]: List of machine names
        """
        machines = self.load_all()
        return [machine.name for machine in machines]
    
    def _get_fieldnames(self) -> List[str]:
        """Get the fieldnames for the CSV file."""
        fieldnames = ["name", "speed", "speed_uom", "picture", "notes"]
        
        # Add tool fields (10 tools max)
        for i in range(1, 11):
            tool_prefix = f"tool{i}_"
            fieldnames.extend([
                f"{tool_prefix}name",
                f"{tool_prefix}rotates",
                f"{tool_prefix}depth", 
                f"{tool_prefix}depth_uom",
                f"{tool_prefix}surface_area_disturbed",
                f"{tool_prefix}tillage_type_factor"
            ])
        
        return fieldnames
    
    def export_to_csv(self, export_path: str) -> bool:
        """
        Export custom machines to a specified CSV file.
        
        Args:
            export_path: Path where to export the CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        machines = self.load_all()
        
        try:
            with open(export_path, 'w', newline='', encoding='utf-8') as file:
                fieldnames = self._get_fieldnames()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                
                for machine in machines:
                    writer.writerow(machine.to_dict())
                    
            return True
            
        except Exception as e:
            print(f"Error exporting custom machines: {e}")
            return False
    
    def import_from_csv(self, import_path: str, replace_existing: bool = False) -> bool:
        """
        Import custom machines from a CSV file.
        
        Args:
            import_path: Path to the CSV file to import
            replace_existing: If True, replace all existing machines; if False, append
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            imported_machines = []
            
            with open(import_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        machine = CustomMachine.from_dict(row)
                        imported_machines.append(machine)
                    except Exception as e:
                        print(f"Error importing machine from row: {e}")
                        continue
            
            if replace_existing:
                return self.save_all(imported_machines)
            else:
                existing_machines = self.load_all()
                all_machines = existing_machines + imported_machines
                return self.save_all(all_machines)
                
        except Exception as e:
            print(f"Error importing custom machines: {e}")
            return False
