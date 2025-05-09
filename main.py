#!/usr/bin/env python3
"""
LORENZO POZZI Pesticide App - Main Application Entry Point

This module serves as the entry point for the App.
It initializes the application, sets up the main window, and starts the event loop.
"""

import os, sys
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QApplication
from common.config_utils import load_config
from data.product_repository import ProductRepository
from data.ai_repository import AIRepository
from main_window.main_window import MainWindow

# Clear the terminal screen
print("\033c", end="")

# Silence messages when resiszing the window
os.environ['QT_LOGGING_RULES'] = '*=false' 

def main():
    """Main application entry point."""
    
    # Set the current directory as working directory 
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    QDir.setCurrent(app_dir)
    
    # Create the Qt application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Pesticides App")
    app.setOrganizationName("Lorenzo Pozzi")
    
    # Load application configuration
    config = load_config()
    
    # Initialize repositories
    product_repo = ProductRepository.get_instance()
    product_repo.get_all_products()  # Load products data
    ai_repo = AIRepository.get_instance()
    ai_repo.get_all_ingredients()  # Load AI data
    
    # Create and show the main window
    window = MainWindow(config)
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()