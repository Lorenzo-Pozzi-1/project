"""
Rotation model for STIR calculations.

This module defines the Rotation class which represents a multi-year
crop rotation with seasons and their tillage operations.
"""

from typing import List, Optional, Dict, Any
from .model_season import Season


class Rotation:
    """
    Represents a multi-year crop rotation for STIR calculations.
    
    Stores information about a rotation including its name and
    all seasons (crop years) within the rotation.
    """
    
    def __init__(self, 
                 name: str = "New Rotation",
                 seasons: Optional[List[Season]] = None):
        """
        Initialize a Rotation instance.
        
        Args:
            name (str): User-friendly name for the rotation
            seasons (list): List of Season objects in this rotation
        """
        self.name = name
        self.seasons = seasons if seasons else []
    
    def add_season(self, season: Season) -> None:
        """
        Add a season to the rotation.
        
        Args:
            season: Season object to add
        """
        self.seasons.append(season)
    
    def remove_season(self, index: int) -> bool:
        """
        Remove a season from the rotation.
        
        Args:
            index (int): Index of the season to remove
            
        Returns:
            bool: True if successful, False if index out of range
        """
        if 0 <= index < len(self.seasons):
            self.seasons.pop(index)
            return True
        return False
    
    def move_season(self, from_index: int, to_index: int) -> bool:
        """
        Move a season from one position to another.
        
        Args:
            from_index (int): Current index of the season
            to_index (int): Target index for the season
            
        Returns:
            bool: True if successful, False if indices out of range
        """
        if (0 <= from_index < len(self.seasons) and 
            0 <= to_index < len(self.seasons)):
            season = self.seasons.pop(from_index)
            self.seasons.insert(to_index, season)
            return True
        return False
    
    def get_season_by_year(self, crop_year: int) -> Optional[Season]:
        """
        Get a season by its crop year.
        
        Args:
            crop_year (int): Year to search for
            
        Returns:
            Season object if found, None otherwise
        """
        for season in self.seasons:
            if season.crop_year == crop_year:
                return season
        return None
    
    def get_total_stir_all_seasons(self) -> float:
        """
        Calculate the total STIR value for all seasons in the rotation.
        
        Returns:
            float: Sum of all season STIR values
        """
        return sum(season.get_total_stir() for season in self.seasons)
    
    def get_average_annual_stir(self) -> float:
        """
        Calculate the average annual STIR value for the rotation.
        
        Returns:
            float: Average STIR per year (0 if no seasons)
        """
        if not self.seasons:
            return 0.0
        
        total_stir = self.get_total_stir_all_seasons()
        return total_stir / len(self.seasons)
    
    def get_rotation_years(self) -> int:
        """
        Get the number of years in the rotation.
        
        Returns:
            int: Number of seasons/years in rotation
        """
        return len(self.seasons)
    
    def get_crops_sequence(self) -> List[str]:
        """
        Get the sequence of crops in the rotation.
        
        Returns:
            List[str]: Ordered list of crop names by year
        """
        # Sort seasons by crop year to ensure correct sequence
        sorted_seasons = sorted(self.seasons, key=lambda s: s.crop_year)
        return [season.crop for season in sorted_seasons]
    
    def get_crop_years_range(self) -> tuple:
        """
        Get the range of crop years in the rotation.
        
        Returns:
            tuple: (min_year, max_year) or (None, None) if no seasons
        """
        if not self.seasons:
            return (None, None)
        
        years = [season.crop_year for season in self.seasons]
        return (min(years), max(years))
    
    def sort_seasons_by_year(self) -> None:
        """Sort seasons by crop year (in-place)."""
        self.seasons.sort(key=lambda s: s.crop_year)
    
    def validate_rotation(self) -> List[str]:
        """
        Validate the rotation and return list of warnings/errors.
        
        Returns:
            List[str]: List of validation messages (empty if valid)
        """
        warnings = []
        
        # Check for duplicate years
        years = [season.crop_year for season in self.seasons]
        if len(years) != len(set(years)):
            warnings.append("Warning: Duplicate crop years found in rotation")
        
        # Check for missing seasons between years
        if len(years) > 1:
            sorted_years = sorted(years)
            for i in range(len(sorted_years) - 1):
                if sorted_years[i+1] - sorted_years[i] > 1:
                    warnings.append(f"Warning: Gap between years {sorted_years[i]} and {sorted_years[i+1]}")
        
        return warnings
    
    def clone(self) -> 'Rotation':
        """
        Create a copy of this rotation with a new name.
            
        Returns:
            Rotation: New rotation instance with copied data
        """
        # Deep copy all seasons
        new_seasons = []
        for season in self.seasons:
            new_seasons.append(season.clone())
        
        # Create new rotation with copied data
        new_rotation = Rotation(
            name=f"Copy of {self.name}",
            seasons=new_seasons
        )
        
        return new_rotation
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert rotation to dictionary representation.
        
        Returns:
            dict: Rotation data as dictionary
        """
        return {
            "name": self.name,
            "seasons": [season.to_dict() for season in self.seasons],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rotation':
        """
        Create Rotation instance from dictionary.
        
        Args:
            data: Dictionary containing rotation data
            
        Returns:
            Rotation: New Rotation instance
        """
        seasons = []
        for season_data in data.get("seasons", []):
            seasons.append(Season.from_dict(season_data))
        
        return cls(
            name=data.get("name", "New Rotation"),
            seasons=seasons
        )
    
    def __str__(self) -> str:
        """Return string representation of the rotation."""
        year_range = self.get_crop_years_range()
        if year_range[0] is not None:
            return f"{self.name} ({year_range[0]}-{year_range[1]}) - {len(self.seasons)} years"
        else:
            return f"{self.name} - Empty rotation"
    
    def __repr__(self) -> str:
        """Return detailed string representation of the rotation."""
        return (f"Rotation(name='{self.name}', seasons={len(self.seasons)}, "
                f"avg_stir={self.get_average_annual_stir():.2f})")
