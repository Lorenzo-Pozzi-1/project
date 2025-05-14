"""
Scenario model for the LORENZO POZZI Pesticide App.

This module defines the Scenario class which represents a complete
pesticide application scenario for comparison.
"""

import copy
from datetime import date
from data.season_plan_model import SeasonPlan

class Scenario:
    """
    Represents a pesticide application scenario for comparison.
    
    A scenario contains a full season plan with metadata and applications,
    along with additional properties for scenario management and comparison.
    """
    
    def __init__(self, name="New Scenario", season_plan=None, scenario_id=None):
        """
        Initialize a Scenario instance.
        
        Args:
            name (str): User-friendly name for the scenario
            season_plan (SeasonPlan): Season plan containing metadata and applications
            scenario_id (str): Unique identifier for the scenario, generated if None
        """
        import uuid
        
        self.name = name
        self.season_plan = season_plan or SeasonPlan()
        self.scenario_id = scenario_id or str(uuid.uuid4())
        self.is_baseline = False
        self.creation_date = date.today()
        self.last_modified = date.today()
        self.notes = ""
    
    def clone(self, new_name=None):
        """
        Create a copy of this scenario with a new name.
        
        Args:
            new_name (str): Name for the new scenario, defaults to "Copy of [original]"
            
        Returns:
            Scenario: New scenario instance with copied data
        """
        # Create default name if not provided
        if new_name is None:
            new_name = f"Copy of {self.name}"
            
        # Create deep copy of the season plan
        new_plan = copy.deepcopy(self.season_plan)
        
        # Create new scenario with copied data but new ID
        new_scenario = Scenario(
            name=new_name,
            season_plan=new_plan
        )
        
        # Copy notes but not baseline status
        new_scenario.notes = self.notes
        
        return new_scenario
    
    def mark_modified(self):
        """Mark the scenario as modified with current timestamp."""
        self.last_modified = date.today()
    
    def to_dict(self):
        """
        Convert scenario to dictionary representation.
        
        Returns:
            dict: Scenario data as dictionary
        """
        return {
            "name": self.name,
            "scenario_id": self.scenario_id,
            "is_baseline": self.is_baseline,
            "creation_date": self.creation_date.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "notes": self.notes,
            "season_plan": self.season_plan.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Scenario instance from dictionary data.
        
        Args:
            data (dict): Scenario data
        
        Returns:
            Scenario: New Scenario instance
        """
        # Create season plan from nested data
        season_plan = None
        if "season_plan" in data:
            season_plan = SeasonPlan.from_dict(data["season_plan"])
        
        # Create scenario with basic properties
        scenario = cls(
            name=data.get("name", "Unnamed Scenario"),
            season_plan=season_plan,
            scenario_id=data.get("scenario_id")
        )
        
        # Set additional properties
        scenario.is_baseline = data.get("is_baseline", False)
        scenario.notes = data.get("notes", "")
        
        # Convert date strings to date objects
        if "creation_date" in data and isinstance(data["creation_date"], str):
            try:
                scenario.creation_date = date.fromisoformat(data["creation_date"])
            except ValueError:
                scenario.creation_date = date.today()
                
        if "last_modified" in data and isinstance(data["last_modified"], str):
            try:
                scenario.last_modified = date.fromisoformat(data["last_modified"])
            except ValueError:
                scenario.last_modified = date.today()
        
        return scenario