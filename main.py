#!/usr/bin/env python3
"""
LORENZO POZZI Pesticide App - Main Application Entry Point

This module serves as the entry point for the App.
It initializes the application, sets up the main window, and starts the event loop.
"""

import os, sys
from PySide6.QtCore import QDir, QObject, QEvent
from PySide6.QtWidgets import QApplication
from common.config_utils import load_config
from data.product_repository import ProductRepository
from data.ai_repository import AIRepository
from main_page.main_window import MainWindow

# Clear the terminal screen
print("\033c", end="")

# Silence messages when resizing the window
os.environ['QT_LOGGING_RULES'] = '*=false' 

class ComboBoxWheelFilter(QObject):
    """Prevents QComboBox widgets from changing values when scrolling without clicking first."""
    def __init__(self):
        super().__init__()
        self.clicked_combos = set()  # Track which combo boxes have been clicked

    def eventFilter(self, obj, event):
        # Track combo boxes that have been clicked
        if event.type() in (QEvent.MouseButtonPress, QEvent.KeyPress):
            self.clicked_combos.add(obj)
        
        # Block wheel events for combo boxes that haven't been clicked
        elif event.type() == QEvent.Wheel and obj not in self.clicked_combos:
            return True  # Block the event
        
        # Reset clicked state when dropdown closes or focus is lost
        elif event.type() == QEvent.Hide and hasattr(obj, 'view'):
            self.clicked_combos.discard(obj)
        elif event.type() == QEvent.FocusOut:
            self.clicked_combos.discard(obj)
        
        # Let other events pass through
        return super().eventFilter(obj, event)

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
    
    # Improve QComboBox behavior to prevent accidental scrolling
    app.installEventFilter(ComboBoxWheelFilter())
    
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
    sys.exit(app.exec())

if __name__ == "__main__":
    main()