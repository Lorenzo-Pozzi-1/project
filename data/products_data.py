"""
Product data module for the LORENZO POZZI Pesticide App.

This module provides functions to load and manage product data.
The data can be initialized from a CSV file and is stored in JSON format.
Updated to support the new product model with multiple active ingredients and EIQ data.
"""

import os
import json
import csv
from models.product import Product

# Paths to data files
DB_FILE = os.path.join("data", "products.json")
CSV_FILE = os.path.join("data", "products.csv")

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
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Clean the row keys to handle potential whitespace in headers
                cleaned_row = {k.strip(): v for k, v in row.items()}
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
                with open(DB_FILE, 'w') as file:
                    json.dump(product_data, file, indent=4)
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
        with open(DB_FILE, 'w') as file:
            json.dump(product_data, file, indent=4)
        
        return True
    
    except Exception as e:
        print(f"Error refreshing database from CSV: {e}")
        return False


def export_to_csv():
    """
    Export the current product database to a CSV file.
    
    This is useful for making changes to the database and then exporting
    for editing in a spreadsheet application.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load current products
        products = load_products()
        
        if not products:
            print("No products to export")
            return False
        
        # Convert to dictionaries
        product_dicts = [product.to_dict() for product in products]
        
        # Get fieldnames from the first product
        fieldnames = list(product_dicts[0].keys())
        
        # Write to CSV
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(product_dicts)
        
        return True
    
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False


def load_products():
    """
    Load all products from the database.
    
    Returns:
        list: List of Product objects
    """
    # Ensure database exists
    initialize_database()
    
    try:
        products = []
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                product = Product.from_dict(row)
                products.append(product)
        return products
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading product data: {e}")
        return []


def save_products(products):
    """
    Save products to the database.
    
    Args:
        products (list): List of Product objects
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert products to dictionaries
        product_data = [product.to_dict() for product in products]
        
        # Save to database file
        with open(DB_FILE, 'w') as file:
            json.dump(product_data, file, indent=4)
        
        return True
    except IOError as e:
        print(f"Error saving product data: {e}")
        return False


def add_product(product):
    """
    Add a new product to the database.
    
    Args:
        product (Product): Product to add
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Load existing products
    products = load_products()
    
    # Add new product
    products.append(product)
    
    # Save updated products
    return save_products(products)


def update_product(product_name, updated_product):
    """
    Update an existing product in the database.
    
    Args:
        product_name (str): Name of product to update
        updated_product (Product): Updated product data
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Load existing products
    products = load_products()
    
    # Find and update the product
    for i, product in enumerate(products):
        if product.product_name == product_name:
            products[i] = updated_product
            return save_products(products)
    
    # Product wasn't found
    return False


def delete_product(product_name):
    """
    Delete a product from the database.
    
    Args:
        product_name (str): Name of product to delete
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Load existing products
    products = load_products()
    
    # Find and remove the product
    for i, product in enumerate(products):
        if product.product_name == product_name:
            del products[i]
            return save_products(products)
    
    # Product wasn't found
    return False


def get_product_by_name(product_name):
    """
    Get a specific product by name.
    
    Args:
        product_name (str): Name of product to retrieve
    
    Returns:
        Product: The requested product or None if not found
    """
    products = load_products()
    
    for product in products:
        if product.product_name == product_name:
            return product
    
    return None


def get_products_by_type(product_type):
    """
    Get all products of a specific type.
    
    Args:
        product_type (str): Type to filter by (e.g., "Herbicides")
    
    Returns:
        list: List of Product objects of the specified type
    """
    products = load_products()
    return [product for product in products if product.product_type == product_type]


def get_products_by_active_ingredient(active_ingredient):
    """
    Get all products containing a specific active ingredient.
    
    Args:
        active_ingredient (str): Active ingredient to filter by
    
    Returns:
        list: List of Product objects containing the specified active ingredient
    """
    products = load_products()
    return [product for product in products if active_ingredient in product.active_ingredients]


def get_products_by_region(region):
    """
    Get all products registered in a specific region.
    
    Args:
        region (str): Region to filter by
    
    Returns:
        list: List of Product objects for the specified region
    """
    products = load_products()
    return [product for product in products if product.region == region]
