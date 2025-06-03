"""
Product Repository for the LORENZO POZZI Pesticide App.

This module provides a centralized repository for accessing and filtering 
product data, with CSV loading and caching for performance optimization.
"""

import csv
from typing import List, Optional
from data.model_product import Product
from common import resource_path

products_csv = resource_path("data/csv_products.csv")

class ProductRepository:
    """
    Centralized repository for product data.
    
    This class is responsible for loading, filtering, and providing
    access to product data throughout the application.
    """
    
    _instance = None  # Singleton instance
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = ProductRepository()
        return cls._instance
    
    def __init__(self):
        """Initialize the repository."""
        self.csv_file = products_csv
        
        # Cache storage
        self._all_products = None  # List of all Product objects
        self._filtered_products = None  # Currently filtered products
        self._current_country = None  # Current country filter
        self._current_region = None  # Current region filter
        
    def get_all_products(self) -> List[Product]:
        """Get all products, loading from CSV if needed."""
        if self._all_products is None:
            self._load_products()
        return self._all_products
    
    def get_filtered_products(self) -> List[Product]:
        """Get filtered products based on current country/region."""
        if self._filtered_products is None:
            self.apply_filters(self._current_country, self._current_region)
        return self._filtered_products
    
    def set_filters(self, country: Optional[str], region: Optional[str]) -> None:
        """Set country and region filters and update filtered products."""
        if country != self._current_country or region != self._current_region:
            self._current_country = country
            self._current_region = region
            self._filtered_products = None  # Invalidate cache
    
    def apply_filters(self, country: Optional[str], region: Optional[str]) -> List[Product]:
        """Apply filters and return filtered products."""
        products = self.get_all_products()
        
        # If no country filter, return all products
        if not country or country == "None of these":
            self._filtered_products = products
            return products
        
        # Start with country filter
        filtered = [p for p in products if p.country == country]
        
        # Grouped Canadian regions
        east_CA = ["Quebec", "Prince Edward Island", "New Brunswick"]
        west_CA = ["Saskatchewan", "Manitoba"]
        
        # Apply region filter if specified
        if region and region != "None of these":
            if region in east_CA and country == "Canada":
                # For these regions, include products from all three Eastern Canada regions
                filtered = [p for p in filtered if (p.region in east_CA) or not p.region]
            elif region in west_CA and country == "Canada":
                # For these regions, include products from both Prairie provinces
                filtered = [p for p in filtered if (p.region in west_CA) or not p.region]
            else:
                # Standard filtering for other regions
                filtered = [p for p in filtered if p.region == region or not p.region]
        
        self._filtered_products = filtered
        return filtered
    
    def _load_products(self) -> None:
        """Load all products from the CSV file."""
        try:
            with open(self.csv_file, 'r', newline='', encoding='cp1252') as csvfile:
                reader = csv.DictReader(csvfile)
                cleaned_rows = [
                    {k.strip(): v.strip() if isinstance(v, str) else v 
                     for k, v in row.items() if k is not None}
                    for row in reader
                ]
                
            self._all_products = [Product.from_dict(row) for row in cleaned_rows]
            
        except Exception as e:
            print(f"Error loading product data: {e}")
            self._all_products = []
    
    def refresh_from_csv(self) -> bool:
        """Refresh data from CSV and invalidate caches."""
        try:
            self._all_products = None
            self._filtered_products = None
            self.get_all_products()  # Reload data
            return True
        except Exception as e:
            print(f"Error refreshing from CSV: {e}")
            return False
    
    @staticmethod
    def csv_to_dict(csv_file):
        """
        Convert CSV file to a list of dictionaries.
        
        Args:
            csv_file (str): Path to the CSV file
        
        Returns:
            list: List of dictionaries with product data
        """
        try:
            with open(csv_file, 'r', newline='', encoding='cp1252') as file:
                reader = csv.DictReader(file, quotechar='"', skipinitialspace=True)
                return [
                    {k.strip(): v.strip() if isinstance(v, str) else v 
                     for k, v in row.items() if k is not None}
                    for row in reader
                ]
        
        except (IOError, csv.Error) as e:
            print(f"Error reading CSV file: {e}")
            return []