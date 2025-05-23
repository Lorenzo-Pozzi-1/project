"""
Data package for the LORENZO POZZI Pesticide App.

This package provides access to data models and repositories for the application.
All components are exported at the package level, allowing for clean imports like:

    from data import Product, Scenario, AIRepository, ProductRepository

Usage examples:
    # Import specific models
    from data import Product, ActiveIngredient, Scenario
    
    # Import repositories
    from data import ProductRepository, AIRepository
    
    # Get singleton instances
    product_repo = ProductRepository.get_instance()
    ai_repo = AIRepository.get_instance()
"""

# Re-export all model classes
from data.ai_model import ActiveIngredient
from data.product_model import Product
from data.application_model import Application
from data.scenario_model import Scenario

# Re-export repository classes
from data.ai_repository import AIRepository
from data.product_repository import ProductRepository
from data.UOM_repository import UOMRepository

# Define what gets imported with "from data import *"
__all__ = [
    # Models
    'ActiveIngredient',
    'Product',
    'Application',
    'Scenario',
    
    # Repositories
    'AIRepository',
    'ProductRepository',
    'UOMRepository'
]