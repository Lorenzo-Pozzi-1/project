#!/usr/bin/env python3
"""
LORENZO POZZI EIQ & STIR App - Main Application Entry Point

This module serves as the entry point for the App.
It initializes the application, sets up the main window, and starts the event loop.
"""

import os, sys
from PySide6.QtCore import QDir, QTimer
from PySide6.QtWidgets import QApplication, QComboBox, QDoubleSpinBox
from common.utils import load_config
from data.repository_AI import AIRepository
from data.repository_product import ProductRepository
from main_page.window_main import MainWindow

# Silence messages when resizing the window
os.environ['QT_LOGGING_RULES'] = '*=false' 

def main() -> int:
    """Main application entry point."""
    
    # Clear the terminal screen
    print("\033c", end="")
    
    # Set the current directory as working directory 
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    QDir.setCurrent(app_dir)
    
    # Create the Qt application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("EIQ & STIR App")
    
    # Load application configuration
    config = load_config()
    
    # Initialize products and active ingredients repositories
    product_repo = ProductRepository.get_instance()
    product_repo.get_all_products()
    ai_repo = AIRepository.get_instance()
    ai_repo.get_all_ingredients()

    # Create and show the main window
    window = MainWindow(config)
    window.show()

    # Start the application event loop
    return sys.exit(app.exec())

if __name__ == "__main__":
    main()