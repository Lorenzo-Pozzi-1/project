"""
Data models for the Season Planner of the LORENZO POZZI Pesticide App.

This module defines the data models for representing seasons, applications,
and related entities used in the Season Planner module.
"""

import datetime
import uuid
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Union


@dataclass
class Product:
    """Represents a product used in an application."""
    name: str
    type: str = ""
    active_ingredient: str = ""
    ai_percentage: float = 0.0
    eiq_value: float = 0.0
    application_rate: float = 0.0
    rate_unit: str = "kg/ha"
    
    def calculate_field_eiq(self, area: float = 1.0) -> float:
        """
        Calculate field EIQ for this product.
        
        Args:
            area: Area in hectares or acres (depending on rate_unit)
            
        Returns:
            Field EIQ value
        """
        if self.eiq_value <= 0 or self.ai_percentage <= 0 or self.application_rate <= 0:
            return 0.0
            
        # Convert AI percentage to decimal (0-1)
        ai_decimal = self.ai_percentage / 100.0
        
        # Calculate Field EIQ
        field_eiq = self.eiq_value * ai_decimal * self.application_rate * area
        return field_eiq


@dataclass
class Application:
    """Represents a single pesticide application event."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    date: datetime.date = field(default_factory=datetime.date.today)
    products: List[Product] = field(default_factory=list)
    notes: str = ""
    field_name: str = ""
    area: float = 1.0  # Area in hectares or acres
    area_unit: str = "ha"  # 'ha' for hectares, 'acre' for acres
    application_method: str = ""
    
    def add_product(self, product: Product) -> None:
        """Add a product to this application."""
        self.products.append(product)
    
    def remove_product(self, index: int) -> Optional[Product]:
        """Remove a product by index."""
        if 0 <= index < len(self.products):
            return self.products.pop(index)
        return None
    
    def calculate_total_field_eiq(self) -> float:
        """Calculate total field EIQ for all products in this application."""
        return sum(product.calculate_field_eiq(self.area) for product in self.products)


@dataclass
class Season:
    """Represents a growing season with multiple applications."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Season"
    year: int = field(default_factory=lambda: datetime.date.today().year)
    grower: str = ""
    farm: str = ""
    crop: str = ""
    variety: str = ""
    applications: List[Application] = field(default_factory=list)
    notes: str = ""
    
    def add_application(self, application: Application) -> None:
        """Add an application to this season."""
        self.applications.append(application)
    
    def remove_application(self, index: int) -> Optional[Application]:
        """Remove an application by index."""
        if 0 <= index < len(self.applications):
            return self.applications.pop(index)
        return None
    
    def calculate_season_eiq(self) -> float:
        """Calculate total EIQ for the entire season."""
        return sum(app.calculate_total_field_eiq() for app in self.applications)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert season to dictionary for serialization."""
        # Use dataclasses.asdict but handle datetime objects
        result = asdict(self)
        
        # Convert datetime objects to strings
        for i, app in enumerate(result['applications']):
            app['date'] = app['date'].isoformat()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Season':
        """Create a Season instance from dictionary data."""
        # Convert string dates back to datetime objects
        applications = []
        for app_data in data.get('applications', []):
            # Convert date string to datetime.date
            if 'date' in app_data and isinstance(app_data['date'], str):
                try:
                    app_data['date'] = datetime.date.fromisoformat(app_data['date'])
                except ValueError:
                    # Fallback to today if date parsing fails
                    app_data['date'] = datetime.date.today()
            
            # Create Product objects
            products = []
            for prod_data in app_data.get('products', []):
                products.append(Product(**prod_data))
            
            app_data['products'] = products
            applications.append(Application(**app_data))
        
        # Update the applications list in the data
        data['applications'] = applications
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert season to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Season':
        """Create a Season instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class SeasonStorage:
    """Utility class for saving and loading seasons."""
    
    @staticmethod
    def save_season(season: Season, file_path: str) -> bool:
        """
        Save a season to a file.
        
        Args:
            season: The Season object to save
            file_path: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'w') as f:
                f.write(season.to_json())
            return True
        except Exception as e:
            print(f"Error saving season: {e}")
            return False
    
    @staticmethod
    def load_season(file_path: str) -> Optional[Season]:
        """
        Load a season from a file.
        
        Args:
            file_path: Path to the season file
            
        Returns:
            Loaded Season or None if loading failed
        """
        try:
            with open(file_path, 'r') as f:
                json_data = f.read()
            return Season.from_json(json_data)
        except Exception as e:
            print(f"Error loading season: {e}")
            return None
    
    @staticmethod
    def list_saved_seasons(directory: str) -> List[Dict[str, str]]:
        """
        List all saved seasons in a directory.
        
        Args:
            directory: Directory to search for season files
            
        Returns:
            List of dictionaries with season file information
        """
        import os
        import glob
        
        seasons = []
        
        try:
            # Search for JSON files
            pattern = os.path.join(directory, "*.json")
            for file_path in glob.glob(pattern):
                try:
                    # Try to load minimal info without loading the whole season
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    seasons.append({
                        'file_path': file_path,
                        'name': data.get('name', 'Unnamed Season'),
                        'year': data.get('year', ''),
                        'grower': data.get('grower', ''),
                        'crop': data.get('crop', '')
                    })
                except Exception:
                    # Skip files that can't be properly loaded
                    continue
        except Exception as e:
            print(f"Error listing seasons: {e}")
        
        return seasons