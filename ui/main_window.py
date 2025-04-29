"""
Main application window for the LORENZO POZZI Pesticide App

This module defines the MainWindow class which serves as the container
for all pages in the application.
"""

import os
import shutil
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QFrame, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFontDatabase

from ui.home_page import HomePage
from ui.products_page.products_page import ProductsPage
from ui.season_planner.season_planner_page import SeasonPlannerPage
from ui.eiq.eiq_calculator_page import EiqCalculatorPage
from ui.common.styles import YELLOW_BAR_STYLE, setup_app_palette
from data.products_data import DB_FILE  # Import the database file path


class MainWindow(QMainWindow):
    """
    Main application window that manages all pages.
    
    The MainWindow uses a QStackedWidget to switch between different pages
    of the application.
    """
    def __init__(self, config=None):
        """Initialize the main window with configuration."""
        super().__init__()
        
        self.config = config or {}
        self.selected_country = None
        self.setup_window()
        self.init_fonts()
        self.init_ui()

        # Connect the country_changed signal to methods that need to be updated
        self.home_page.country_changed.connect(self.update_selected_country)
        self.home_page.country_changed.connect(self.products_page.update_country_filter)
        
        # Set initial country value (after the connections are established)
        initial_country = self.home_page.country_combo.currentText()
        self.update_selected_country(initial_country)
        self.products_page.update_country_filter(initial_country)
        
    def setup_window(self):
        """Set up the window properties."""
        # Set window properties
        self.setWindowTitle("LORENZO POZZI Pesticide App")
        self.setMinimumSize(900, 700)
        
        # Set window icon (if available)
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
    
    def init_fonts(self):
        """Initialize and load fonts for titles."""
        # Load Red Hat Display fonts
        font_paths = [
            os.path.join(os.path.dirname(__file__), "common", "RedHatDisplay-Black.ttf"),
            os.path.join(os.path.dirname(__file__), "common", "RedHatDisplay-Bold.ttf"),
            os.path.join(os.path.dirname(__file__), "common", "RedHatDisplay-Regular.ttf")
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                QFontDatabase.addApplicationFont(font_path)
    
    def init_ui(self):
        """Initialize the UI components."""
        # Create central widget to hold the layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create stacked widget to manage different pages
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create and add the home page (index 0)
        self.home_page = HomePage(self)
        self.stacked_widget.addWidget(self.home_page)
        
        # Create and add the products page (index 1)
        self.products_page = ProductsPage(self)
        self.stacked_widget.addWidget(self.products_page)
        
        # Create and add the season planner page (index 2)
        self.season_planner_page = SeasonPlannerPage(self)
        self.stacked_widget.addWidget(self.season_planner_page)
        
        # Create and add the EIQ calculator page (index 3)
        self.eiq_calculator_page = EiqCalculatorPage(self)
        self.stacked_widget.addWidget(self.eiq_calculator_page)
        
        # Add yellow bar at the bottom
        self.yellow_bar = QFrame()
        self.yellow_bar.setStyleSheet(YELLOW_BAR_STYLE)
        main_layout.addWidget(self.yellow_bar)
        
        # Start with the home page
        self.stacked_widget.setCurrentIndex(0)
    
    def update_selected_country(self, country):
        """Update the selected country when the signal is emitted."""
        self.selected_country = country
        print(f"MainWindow updated selected country to: {self.selected_country}")

    def navigate_to_page(self, page_index):
        """Navigate to the specified page index."""
        if 0 <= page_index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(page_index)
    
    def go_home(self):
        """Navigate back to the home page."""
        self.stacked_widget.setCurrentIndex(0)
    
    def closeEvent(self, event):
        """
        Handle the close event for the main window.
        
        This is called when the application is being closed.
        It deletes the products.json file and cleans up __pycache__ directories.
        """
        # Clean up the products.json file
        try:
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
                print(f"Successfully deleted {DB_FILE}")
        except Exception as e:
            print(f"Error deleting products.json file: {e}")
        
        # Clean up all __pycache__ directories - Windows compatible approach
        try:
            # Start at the root directory of the application
            app_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(app_dir)  # Go up one level to get the project root
            
            # Track deleted files for reporting
            deleted_files = 0
            total_files = 0
            
            # Walk through all directories
            for dirpath, dirnames, filenames in os.walk(root_dir):
                if os.path.basename(dirpath) == "__pycache__":
                    for file in filenames:
                        total_files += 1
                        if file.endswith('.pyc') or file.endswith('.pyo'):
                            try:
                                os.remove(os.path.join(dirpath, file))
                                deleted_files += 1
                            except Exception:
                                pass
                    
                    # Try to remove the directory if empty
                    try:
                        remaining_files = os.listdir(dirpath)
                        if not remaining_files:
                            os.rmdir(dirpath)
                    except Exception:
                        pass
            
            if deleted_files > 0:
                print(f"Cleanup complete: Deleted {deleted_files} of {total_files} cached Python files")
        except Exception as e:
            print(f"Error during cache cleanup: {e}")
        
        # Accept the close event
        event.accept()