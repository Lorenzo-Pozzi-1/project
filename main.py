#!/usr/bin/env python3
"""
LORENZO POZZI Pesticide App - Main Application Entry Point

This module serves as the entry point for the App.
It initializes the application, sets up the main window, and starts the event loop.
"""

import os, sys
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QApplication, QComboBox, QDoubleSpinBox
from common import load_config, WheelProtectionFilter
from data import ProductRepository, AIRepository
from main_page import MainWindow

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
    app.setApplicationName("Pesticides App")
    
    # # Block scroll to change value for QComboBox and QDoubleSpinBox
    # scroll_filter = WheelProtectionFilter()
    # for widget_class in [QComboBox, QDoubleSpinBox]:
    #     original_init = widget_class.__init__
    #     def create_filtered_init(orig_init):
    #         def filtered_init(self, *args, **kwargs):
    #             orig_init(self, *args, **kwargs)
    #             self.installEventFilter(scroll_filter)
    #         return filtered_init
    #     widget_class.__init__ = create_filtered_init(original_init)

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