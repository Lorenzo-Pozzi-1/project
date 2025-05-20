#!/usr/bin/env python3
"""
LORENZO POZZI Pesticide App - Main Application Entry Point

This module serves as the entry point for the App.
It initializes the application, sets up the main window, and starts the event loop.
"""

import os, sys
from PySide6.QtCore import QDir, QObject, QEvent
from PySide6.QtWidgets import QApplication, QComboBox
from E_common import load_config
from G_data import ProductRepository, AIRepository
from A_main_page import MainWindow

# Clear the terminal screen
print("\033c", end="")

# Silence messages when resizing the window
os.environ['QT_LOGGING_RULES'] = '*=false' 

class WheelProtectionFilter(QObject):
    """Prevents widgets from changing values when scrolling without clicking first."""
    def __init__(self):
        super().__init__()
        self.clicked_widgets = set()  # Track which widgets have been clicked

    def eventFilter(self, obj, event):
        # Track widgets that have been clicked
        if event.type() in (QEvent.MouseButtonPress, QEvent.KeyPress):
            self.clicked_widgets.add(obj)
        
        # Block wheel events for widgets that haven't been clicked
        elif event.type() == QEvent.Wheel and obj not in self.clicked_widgets:
            return True  # Block the event
        
        # Reset clicked state when dropdown closes or focus is lost
        elif event.type() == QEvent.Hide and hasattr(obj, 'view'):
            self.clicked_widgets.discard(obj)
        elif event.type() == QEvent.FocusOut:
            self.clicked_widgets.discard(obj)
        
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
    
    # Prevent accidental scrolling value changes
    wheel_filter = WheelProtectionFilter()
    original_combo_init = QComboBox.__init__
    def filtered_combo_init(self, *args, **kwargs):
        original_combo_init(self, *args, **kwargs)
        self.installEventFilter(wheel_filter)
    QComboBox.__init__ = filtered_combo_init
    # original_spinbox_init = QDoubleSpinBox.__init__
    # def filtered_spinbox_init(self, *args, **kwargs):
    #     original_spinbox_init(self, *args, **kwargs)
    #     self.installEventFilter(wheel_filter)
    # QDoubleSpinBox.__init__ = filtered_spinbox_init
    
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