"""
Main application window for the Pesticide App

This module defines the MainWindow class which serves as the container
for all pages in the application.
"""

import os, shutil
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QFrame, QWidget
from PySide6.QtCore import Signal
from data.product_repository import ProductRepository
from main_window.home_page import HomePage
from products_table.products_page import ProductsPage
from season_planner.season_planner_page import SeasonPlannerPage
from eiq_calculator.eiq_calculator_page import EiqCalculatorPage
from common.styles import YELLOW_BAR_STYLE

class MainWindow(QMainWindow):
    """
    Main application window that manages all pages.
    
    The MainWindow uses a QStackedWidget to switch between different pages
    of the application.
    """

    filters_changed = Signal() # Signal to notify when filters change

    def __init__(self, config=None):
        """Initialize the main window and configuration."""
        
        super().__init__()
        self.config = config or {}        
        self.setup_window()
        self.init_ui()
        self.apply_filters("Canada", "None of the above")
        
    def setup_window(self):
        """Set up the window properties."""
        
        self.setWindowTitle("LORENZO POZZI - Pesticide App")
        self.setMinimumSize(900, 700)
        # self.showMaximized()
                
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
        
        # Connect signal to page refresh methods
        self.filters_changed.connect(self.refresh_pages)
        
        # Connect the country_changed and region_changed signals to handler methods
        self.home_page.country_changed.connect(self.on_country_changed)
        self.home_page.region_changed.connect(self.on_region_changed)
        
        # Start with the home page
        self.stacked_widget.setCurrentIndex(0)

    def apply_filters(self, country, region):
        """Centralized method to apply filters to products."""
        # Set updating flag to prevent navigation during updates
        self.updating_products = True
            
        # Store the selected values
        self.selected_country = country
        self.selected_region = region
        
        # Apply filters to the repository
        repo = ProductRepository.get_instance()
        repo.set_filters(country, region)
        
        print(f"Filters applied - Country: {country}, Region: {region}")
        print(f"Filtered products count: {len(repo.get_filtered_products())}")
        
        # Notify pages to refresh their views
        self.filters_changed.emit()
        self.updating_products = False
    
    def on_country_changed(self, country):
        """Handle country change event."""
        self.apply_filters(country, "None of the above")

    def on_region_changed(self, region):
        """Handle region change event."""
        self.apply_filters(self.selected_country, region)

    def refresh_pages(self):
        """Refresh all pages to get product data up to date with filters."""
        self.eiq_calculator_page.refresh_product_data()
        self.products_page.refresh_product_data()
        # In the future add any other pages here

    def navigate_to_page(self, page_index):
        """Navigate to the specified page index."""
        
        if self.updating_products:
            print("Please wait, I'm updating the products data...")
            return
            
        if 0 <= page_index < self.stacked_widget.count():
            # Navigate to the page
            self.stacked_widget.setCurrentIndex(page_index)
    
    def go_home(self):
        """Navigate back to the home page."""
        self.stacked_widget.setCurrentIndex(0)
    
    def closeEvent(self, event):
        """Handle the close event, clean up __pycache__ directories."""
        try:
            # Find and remove all __pycache__ directories 
            app_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(app_dir)
            for dirpath, dirnames, _ in os.walk(root_dir):
                for dirname in dirnames:
                    if dirname == "__pycache__":
                        cache_path = os.path.join(dirpath, dirname)
                        try:
                            shutil.rmtree(cache_path)
                        except Exception:
                            pass
                
        except Exception as e:
            print(f"Error during cache cleanup: {e}")
        
        # Accept the close event
        event.accept()