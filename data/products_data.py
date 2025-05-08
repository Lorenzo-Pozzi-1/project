"""
Product data module for the LORENZO POZZI Pesticide App.

This module provides utility functions for initializing product data from CSV.
All data access should go through the ProductRepository.
"""

import os, csv
from data.product_repository import ProductRepository

# Paths to data files
CSV_FILE = os.path.join("data", "NEW_products.csv")

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
                cleaned_row = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items() if k is not None}                
                product_data.append(cleaned_row)
        
        return product_data
    
    except (IOError, csv.Error) as e:
        print(f"Error reading CSV file: {e}")
        return []


def initialize_database():
    """
    Initialize the product repository if it doesn't have data.
    
    Returns:
        bool: True if initialization was performed, False if not needed
    """
    # Get the repository instance
    repo = ProductRepository.get_instance()
    
    # Check if repository already has products
    if repo.get_all_products():
        return False
    
    # Force a refresh from CSV
    return repo.refresh_from_csv()


def refresh_from_csv():
    """
    Refresh the product repository from the CSV file.
    
    Returns:
        bool: True if successful, False otherwise
    """
    repo = ProductRepository.get_instance()
    return repo.refresh_from_csv()