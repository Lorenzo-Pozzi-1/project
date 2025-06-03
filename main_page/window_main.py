"""
Main application window for the Pesticide App

This module defines the MainWindow class which serves as the container
for all pages in the application.
"""

import os, shutil
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QHBoxLayout, QFrame, QWidget, QLabel
from PySide6.QtCore import Signal, Qt
from common import CalculationTraceDialog, load_config, create_button, YELLOW_BAR_STYLE
from data import ProductRepository
from main_page.page_home import HomePage
from products_page import ProductsPage
from season_planner_page import ScenariosManagerPage
from eiq_calculator_page import EiqCalculatorPage

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
        self.apply_config_preferences()
        self.trace_dialog = None
        
    def setup_window(self):
        """Set up the window properties."""
        
        self.setWindowTitle("Pesticide App - Internship project of Lorenzo Pozzi")
        self.setMinimumSize(900, 700)
        self.showMaximized()
                
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
        
        # Create and add the scenarios manager page (index 2)
        self.scenarios_manager_page = ScenariosManagerPage(self)
        self.stacked_widget.addWidget(self.scenarios_manager_page)
        
        # Create and add the EIQ calculator page (index 3)
        self.eiq_calculator_page = EiqCalculatorPage(self)
        self.stacked_widget.addWidget(self.eiq_calculator_page)
        
        # Add yellow bar at the bottom with tracer button and author info
        self.yellow_bar = QFrame()  # Bar
        self.yellow_bar.setStyleSheet(YELLOW_BAR_STYLE)
        yellow_bar_layout = QHBoxLayout(self.yellow_bar)
        yellow_bar_layout.setContentsMargins(10, 2, 10, 2)

        self.trace_button = create_button(text="</>", style="tiny", callback=self.show_calculation_trace)  # Button
        self.trace_button.setToolTip("Show calculation trace")
        self.trace_button.clicked.connect(self.show_calculation_trace)
        yellow_bar_layout.addWidget(self.trace_button)

        yellow_bar_layout.addStretch()  # Add stretch to push author label to the right

        author_label = QLabel("Developed by: lorenzo.pozzi@mccain.ca")  # Author info
        author_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        yellow_bar_layout.addWidget(author_label)
        
        main_layout.addWidget(self.yellow_bar)
        
        # Connect signal to page refresh methods
        self.filters_changed.connect(self.refresh_pages)
        
        # Connect the home page signals to handler methods
        self.home_page.country_changed.connect(self.on_country_changed)
        self.home_page.region_changed.connect(self.on_region_changed)
        self.home_page.preferences_changed.connect(self.apply_config_preferences)
        
        # Start with the home page
        self.stacked_widget.setCurrentIndex(0)

    def apply_filters(self, country, region):
        """Centralized method to apply filters to products."""
        # Set updating flag to prevent navigation during updates
        self.updating_products = True
            
        # Store the selected values
        self.selected_country = country
        self.selected_region = region
        
        # Apply filters to the products repository
        products_repo = ProductRepository.get_instance()
        products_repo.set_filters(country, region)
                
        # Notify pages to refresh their views
        self.filters_changed.emit()
        self.updating_products = False
    
    def on_country_changed(self, country):
        """Handle country change event."""
        self.apply_filters(country, "None of these")

    def on_region_changed(self, region):
        """Handle region change event."""
        self.apply_filters(self.selected_country, region)

    def refresh_pages(self):
        """Refresh all pages to get product data up to date with filters."""
        self.eiq_calculator_page.refresh_product_data()
        self.products_page.refresh_product_data()
        self.scenarios_manager_page.refresh_product_data()
        # in the future add any new page that needs to be refreshed

    def navigate_to_page(self, page_index):
        """Enhanced navigation with WIP warnings."""
        # warning for demo rollout
        if page_index == 2:  # Season Planner
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Work in Progress", 
                "WORK IN PROGRESS!\n\nExplore and try the functionalities but be aware that they might present errors or change in the future!", 
                QMessageBox.Ok)
        # end of warning    
        self.stacked_widget.setCurrentIndex(page_index)

    def apply_config_preferences(self):
        """Apply user preferences from config."""
        # Get user preferences from config
        config = load_config()
        user_preferences = config.get("user_preferences", {})
        
        # Apply country and region preferences
        default_country = user_preferences.get("default_country", "Canada")
        default_region = user_preferences.get("default_region", "None of these")
        
        # Set in home page UI
        self.home_page.set_country_region(default_country, default_region)
        
        # Load other preferences into the home page
        self.home_page.load_preferences()
        
        # Apply filters
        self.apply_filters(default_country, default_region)

    def show_calculation_trace(self):
        """Show the calculation trace dialog."""
        # Check if dialog already exists and is visible
        if self.trace_dialog is not None and self.trace_dialog.isVisible():
            # Just bring it to front and focus it
            self.trace_dialog.raise_()
            self.trace_dialog.activateWindow()
            return
        
        # Create new dialog if none exists or previous one was closed
        self.trace_dialog = CalculationTraceDialog(self)
        self.trace_dialog.show()

    def closeEvent(self, event):
        """Handle the close event, clean up __pycache__ directories."""

        # If we're on the home page, check for unsaved preferences
        if self.stacked_widget.currentIndex() == 0 and self.home_page.preferences_row.has_unsaved_changes:
            if not self.home_page.check_unsaved_preferences():
                event.ignore()  # Cancel closing if the user cancelled
                return
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