#!/usr/bin/env python3
"""
LORENZO POZZI Pesticide App - Main Application Entry Point

This module serves as the entry point for the App.
It initializes the application, sets up the main window, and starts the event loop.
"""

import os
import sys
from typing import Any, Dict, Set, Callable
from PySide6.QtCore import QDir, QObject, QEvent
from PySide6.QtWidgets import QApplication, QComboBox, QDoubleSpinBox
from common import load_config
from data import ProductRepository, AIRepository
from main_page import MainWindow

# Silence messages when resizing the window
os.environ['QT_LOGGING_RULES'] = '*=false' 

class WheelProtectionFilter(QObject):
    """Prevents widgets from changing values when scrolling without clicking first."""
    
    def __init__(self) -> None:
        super().__init__()
        self.clicked_widgets: Set[QObject] = set()  # Track which widgets have been clicked

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
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

def main() -> int:
    """Main application entry point."""
    
    # Clear the terminal screen
    print("\033c", end="")

    # Set the current directory as working directory 
    app_dir: str = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    QDir.setCurrent(app_dir)
    
    # Create the Qt application
    app: QApplication = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Pesticides App")
    
    # Prevent accidental scrolling value changes
    wheel_filter: WheelProtectionFilter = WheelProtectionFilter()
    
    # Store original initialization methods
    original_combo_init: Callable = QComboBox.__init__
    
    # Monkey-patch combo box initialization
    def filtered_combo_init(self: QComboBox, *args: Any, **kwargs: Any) -> None:
        original_combo_init(self, *args, **kwargs)
        self.installEventFilter(wheel_filter)
    
    QComboBox.__init__ = filtered_combo_init
    
    # Store original spinbox initialization
    original_spinbox_init: Callable = QDoubleSpinBox.__init__
    
    # Monkey-patch spinbox initialization
    def filtered_spinbox_init(self: QDoubleSpinBox, *args: Any, **kwargs: Any) -> None:
        original_spinbox_init(self, *args, **kwargs)
        self.installEventFilter(wheel_filter)
    
    QDoubleSpinBox.__init__ = filtered_spinbox_init

    # Load application configuration
    config: Dict[str, Any] = load_config()
    
    # Initialize products and active ingredients repositories
    product_repo: ProductRepository = ProductRepository.get_instance()
    product_repo.get_all_products()
    ai_repo: AIRepository = AIRepository.get_instance()
    ai_repo.get_all_ingredients()
    
    # Create and show the main window
    window: MainWindow = MainWindow(config)
    window.show()
    
    # Start the application event loop
    return sys.exit(app.exec())

if __name__ == "__main__":
    main()