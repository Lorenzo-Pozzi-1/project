"""
Product data module for the LORENZO POZZI Pesticide App.

This module provides functions to load and manage product data.
The data can be initialized from a CSV file and is stored in JSON format.
Updated to work with NEW_products.csv format.
"""

import os, json, csv

# Paths to data files
CSV_FILE = os.path.join("data", "NEW_products.csv")
DB_FILE = os.path.join("data", "products.json")
FILTERED_DB_FILE = os.path.join("data", "filtered_products.json")

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
    Initialize the product database if it doesn't exist.
    
    Tries to load from CSV file.
    Creates the data directory and populates it with product data.
    
    Returns:
        bool: True if initialization was performed, False if not needed
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    
    # Check if database file exists
    if not os.path.exists(DB_FILE):
        # Try to load from CSV first
        if os.path.exists(CSV_FILE):
            product_data = csv_to_dict(CSV_FILE)
            
            if product_data:
                # Create database with CSV data
                with open(DB_FILE, 'w', encoding='utf-8') as file:
                    json.dump(product_data, file, indent=4, ensure_ascii=False)
                return True
    
    return False


def refresh_from_csv():
    """
    Refresh the product database from the CSV file.
    
    This allows updating the database when the CSV file changes.
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(CSV_FILE):
        print(f"CSV file not found: {CSV_FILE}")
        return False
    
    try:
        # Load data from CSV
        product_data = csv_to_dict(CSV_FILE)
        
        if not product_data:
            print("No data found in CSV file")
            return False
        
        # Save to database file
        with open(DB_FILE, 'w', encoding='utf-8') as file:
            json.dump(product_data, file, indent=4, ensure_ascii=False)
        
        return True
    
    except Exception as e:
        print(f"Error refreshing database from CSV: {e}")
        return False