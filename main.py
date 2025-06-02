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
    
    # Block scroll to change value for QComboBox and QDoubleSpinBox
    wheel_filter = WheelProtectionFilter()

    original_combo_init = QComboBox.__init__
    def filtered_combo_init(self, *args, **kwargs) -> None:
        original_combo_init(self, *args, **kwargs)
        self.installEventFilter(wheel_filter)
    QComboBox.__init__ = filtered_combo_init
    
    original_spinbox_init = QDoubleSpinBox.__init__
    def filtered_spinbox_init(self, *args, **kwargs) -> None:
        original_spinbox_init(self, *args, **kwargs)
        self.installEventFilter(wheel_filter)
    QDoubleSpinBox.__init__ = filtered_spinbox_init

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