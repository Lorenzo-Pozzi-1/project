#!/usr/bin/env python3
"""
LORENZO POZZI Pesticide App - Main Application Entry Point

This module serves as the entry point for the LORENZO POZZI Pesticide App.
It initializes the application, sets up the main window, and starts the event loop.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDir

# Import the MainWindow from the UI module
from ui.main_window import MainWindow

# Import utility functions
from utils.config import load_config

# Clear the terminal screen for a clean start
print("\033c", end="")

# Set the environment variable for Qt logging rules to suppress debug messages
os.environ['QT_LOGGING_RULES'] = '*=false'

def setup_environment():
    """Setup the application environment."""
        
    # Set the current working directory to the application's directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    QDir.setCurrent(app_dir)


def main():
    """Main application entry point."""
    # Setup the environment
    setup_environment()
    
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Set application style and properties
    app.setStyle("Fusion")
    app.setApplicationName("Lorenzo Pozzi Pesticide App")
    app.setOrganizationName("Lorenzo Pozzi")
    
    # Load application configuration
    config = load_config()
    
    # Create and show the main window
    window = MainWindow(config)
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()