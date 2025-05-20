"""
Active ingredient Repository for the LORENZO POZZI Pesticide App.

This module provides a centralized repository for accessing active ingredients
classification data.
"""

import csv
import os
from typing import Dict, Optional, Tuple
from G_data.ai_model import ActiveIngredient

class AIRepository:
    """Repository for active ingredient information including mode of action groups."""
    
    _instance = None  # Singleton instance
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = AIRepository()
        return cls._instance
    
    def __init__(self):
        """Initialize the repository."""
        self.csv_file = os.path.join("data", "active_ingredients.csv")
        
        # Cache storage
        self._all_ingredients = {}  # Dictionary of all ActiveIngredient objects by name
        self._name_to_ai_map = {}  # Mapping of name variations to standardized names
    
    def get_all_ingredients(self) -> Dict[str, ActiveIngredient]:
        """Get all active ingredients, loading from CSV if needed."""
        if not self._all_ingredients:
            self._load_ingredients()
        return self._all_ingredients
    
    def _get_standardized_ai(self, ai_name: str) -> Tuple[Optional[str], Optional[ActiveIngredient]]:
        """Get standardized AI name and object if it exists.
        
        Args:
            ai_name: The name of the active ingredient
            
        Returns:
            tuple: (standardized_name, ai_object) or (None, None) if not found
        """
        if not self._all_ingredients:
            self._load_ingredients()
            
        # Try to find the AI using normalized name mapping
        ai_name_lower = ai_name.lower()
        if ai_name_lower in self._name_to_ai_map:
            std_name = self._name_to_ai_map[ai_name_lower]
            return std_name, self._all_ingredients.get(std_name)
            
        return None, None
    
    def get_moa_groups(self, ai_name: str) -> str:
        """
        Get formatted mode of action groups for an active ingredient.
        
        Args:
            ai_name: The name of the active ingredient
            
        Returns:
            str: Formatted mode of action groups (e.g., "FRAC: 7, HRAC: A")
        """
        _, ai = self._get_standardized_ai(ai_name)
        
        if ai:
            groups = []
            if ai.FRAC_group:
                groups.append(f"FRAC: {ai.FRAC_group}")
            if ai.HRAC_group:
                groups.append(f"HRAC: {ai.HRAC_group}")
            if ai.IRAC_group:
                groups.append(f"IRAC: {ai.IRAC_group}")
            
            return ", ".join(groups) if groups else ""
                
        return ""
    
    def get_ai_eiq(self, ai_name: str) -> Optional[float]:
        """
        Get the EIQ value for an active ingredient.
        
        Args:
            ai_name: The name of the active ingredient
            
        Returns:
            float or None: EIQ value if found, None otherwise
        """
        _, ai = self._get_standardized_ai(ai_name)
        
        if ai and ai.eiq is not None:
            try:
                return float(ai.eiq)
            except (ValueError, TypeError):
                return None
                
        return None
    
    def _load_ingredients(self) -> None:
        """Load all active ingredients from the CSV file."""
        try:
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Clean row data
                    cleaned_row = {k.strip(): v.strip() if isinstance(v, str) else v 
                                  for k, v in row.items() if k is not None}
                    
                    ai = ActiveIngredient.from_dict(cleaned_row)
                    self._all_ingredients[ai.name] = ai
            
            self._build_name_mapping()
            
        except Exception as e:
            print(f"Error loading active ingredient data: {e}")
            self._all_ingredients = {}
    
    def _build_name_mapping(self) -> None:
        """Build a mapping of name variations to standardized names."""
        self._name_to_ai_map = {name.lower(): name for name in self._all_ingredients.keys()}