"""
Product Repository for the LORENZO POZZI Pesticide App.

This module provides a centralized repository for accessing and filtering 
product data, with CSV loading and caching for performance optimization.
"""

import csv
import os
from typing import List, Optional
from data.product_model import Product

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
        self.csv_file = os.path.join("data", "NEW_products.csv")
        
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
        filtered = []
        
        if country and country != "None of the above":
            if region and region != "None of the above":
                # Filter by both country and region
                filtered = [p for p in products if p.country == country and 
                           (p.region == region or not p.region)]
            else:
                # Filter by country only
                filtered = [p for p in products if p.country == country]
        else:
            # No country filter, show all products
            filtered = products
        
        self._filtered_products = filtered
        return filtered
    
    def _load_products(self) -> None:
        """Load all products from the CSV file."""
        products = []
        
        try:
            with open(self.csv_file, 'r', newline='', encoding='cp1252') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Clean row data
                    cleaned_row = {k.strip(): v.strip() if isinstance(v, str) else v 
                                   for k, v in row.items() if k is not None}
                    product = Product.from_dict(cleaned_row)
                    products.append(product)
            
            self._all_products = products
            
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
    
    def get_product_by_name(self, product_name):
        """
        Get a specific product by name.
        
        Args:
            product_name (str): Name of product to retrieve
        
        Returns:
            Product: The requested product or None if not found
        """
        products = self.get_all_products()
        
        for product in products:
            if product.product_name == product_name:
                return product
        
        return None
    
    @staticmethod
    def csv_to_dict(csv_file):
        """
        Convert CSV file to a list of dictionaries.
        
        Args:
            csv_file (str): Path to the CSV file
        
        Returns:
            list: List of dictionaries with product data
        """
        product_data = []
        
        try:
            # Use cp1252 encoding for the NEW_products.csv file
            with open(csv_file, 'r', newline='', encoding='cp1252') as file:
                # Explicitly set quoting parameters to handle strings with commas
                reader = csv.DictReader(file, quotechar='"', skipinitialspace=True)
                for row in reader:
                    # Clean the row keys to handle potential whitespace in headers
                    cleaned_row = {k.strip(): v.strip() if isinstance(v, str) else v 
                                  for k, v in row.items() if k is not None}
                    product_data.append(cleaned_row)
            
            return product_data
        
        except (IOError, csv.Error) as e:
            print(f"Error reading CSV file: {e}")
            return []