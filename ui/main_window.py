"""
Main application window for the LORENZO POZZI Pesticide App

This module defines the MainWindow class which serves as the container
for all pages in the application.
Updated with McCain branding elements.
"""

from PySide6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QFrame, QWidget
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFontDatabase, QFont

from ui.home_page import HomePage
from ui.products_page import ProductsPage
from ui.season_planner import SeasonPlannerPage
from ui.eiq import EiqCalculatorPage
from ui.common.styles import YELLOW_BAR_STYLE

class MainWindow(QMainWindow):
    """
    Main application window that manages all pages.
    
    The MainWindow uses a QStackedWidget to switch between different pages
    of the application. McCain branding elements are applied.
    """
    def __init__(self, config=None):
        """Initialize the main window with configuration."""
        super().__init__()
        
        self.config = config or {}
        self.selected_country = None
        self.setup_window()
        self.init_fonts()
        self.init_ui()

        # Connect the region_changed signal to methods that need to be updated
        self.home_page.region_changed.connect(self.update_selected_country)
        self.home_page.region_changed.connect(self.products_page.update_region_filter)
        
    def setup_window(self):
        """Set up the window properties."""
        # Set window properties
        self.setWindowTitle("LORENZO POZZI Pesticide App")
        self.setMinimumSize(900, 700)
        
        # Set window icon (if available)
        try:
            self.setWindowIcon(QIcon("assets/icon.png"))
        except:
            pass  # No icon available, use default
    
    def init_fonts(self):
        """Initialize and load McCain brand fonts."""
        # Load brand fonts if available
        # This requires the fonts to be installed on the system or available in the assets folder
        
        # Attempt to load Red Hat Display for titles
        try:
            QFontDatabase.addApplicationFont("ui/common/RedHatDisplay-Black.ttf")
            QFontDatabase.addApplicationFont("ui/common/RedHatDisplay-Bold.ttf")
            QFontDatabase.addApplicationFont("ui/common/RedHatDisplay-Regular.ttf")
        except:
            print("Red Hat Display font not available, using fallback")
        
        # Attempt to load Montserrat for body text
        try:
            QFontDatabase.addApplicationFont("ui/common/Montserrat-Medium.ttf")
            QFontDatabase.addApplicationFont("ui/common/Montserrat-Regular.ttf")
        except:
            print("Montserrat font not available, using fallback")
            
        # Set Century Gothic for general text if available
        try:
            QFontDatabase.addApplicationFont("ui/common/GOTHIC.ttf")
        except:
            print("Century Gothic font not available, using fallback")
    
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
        # Now using the new modular EiqCalculatorPage
        self.eiq_calculator_page = EiqCalculatorPage(self)
        self.stacked_widget.addWidget(self.eiq_calculator_page)
        
        # Add McCain yellow bar at the bottom
        self.yellow_bar = QFrame()
        self.yellow_bar.setStyleSheet(YELLOW_BAR_STYLE)
        main_layout.addWidget(self.yellow_bar)
        
        # Start with the home page
        self.stacked_widget.setCurrentIndex(0)
    
    def update_selected_country(self, region):
        """Update the selected country when the signal is emitted."""
        self.selected_country = region
        print(f"MainWindow updated selected country to: {self.selected_country}")

    def navigate_to_page(self, page_index):
        """Navigate to the specified page index."""
        if 0 <= page_index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(page_index)
    
    def go_home(self):
        """Navigate back to the home page."""
        self.stacked_widget.setCurrentIndex(0)