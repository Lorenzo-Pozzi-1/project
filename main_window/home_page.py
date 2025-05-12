"""
Home page for the LORENZO POZZI Pesticide App

This module defines the HomePage class which serves as the main navigation
screen for the application.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame
from PySide6.QtCore import Qt, Signal
from common.styles import get_title_font, get_body_font, get_subtitle_font, MARGIN_LARGE, SPACING_LARGE
from common.widgets import FeatureButton, ContentFrame

class HomePage(QWidget):
    """
    Home page with country selection and feature navigation buttons.
    
    This page serves as the main entry point for users to access the
    various features of the application.
    """
    
    country_changed = Signal(str)
    region_changed = Signal(str)
    
    def __init__(self, parent=None):
        """Initialize the home page."""
        super().__init__(parent)
        self.parent = parent
        self.initializing = True  # Flag to avoid multiple filtering during setup
        self.setup_ui()
        self.initializing = False  # Setup complete
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        main_layout.setSpacing(SPACING_LARGE)
        
        # Title
        title_label = QLabel("McCain Pesticides App")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(get_title_font())
        main_layout.addWidget(title_label)
        
        # country and region selection area
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.NoFrame)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setAlignment(Qt.AlignCenter)
        
        # Country selection
        country_label = QLabel("Select country:")
        country_label.setFont(get_body_font())
        
        self.country_combo = QComboBox()
        self.country_combo.setFont(get_body_font())
        self.country_combo.addItems(["Canada", "United States"])
        self.country_combo.setMinimumWidth(200)
        self.country_combo.setCurrentIndex(0)
        self.country_combo.currentIndexChanged.connect(self.on_country_changed)
        
        filter_layout.addWidget(country_label)
        filter_layout.addWidget(self.country_combo)
        
        # Add spacing between dropdowns
        filter_layout.addSpacing(20)
        
        # Region selection
        region_label = QLabel("Select region:")
        region_label.setFont(get_body_font())
        
        self.region_combo = QComboBox()
        self.region_combo.setFont(get_body_font())
        self.region_combo.addItem("None of the above")
        self.region_combo.setMinimumWidth(200)
        self.region_combo.setCurrentIndex(0)
        self.region_combo.currentIndexChanged.connect(self.on_region_changed)
        
        self.update_regions_dropdown()
        
        filter_layout.addWidget(region_label)
        filter_layout.addWidget(self.region_combo)
        
        main_layout.addWidget(filter_frame)
        
        # Buttons area
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Create the main feature buttons
        self.products_button = FeatureButton(
            "Products List and Comparison",
            "View and compare products with quick fact sheets"
        )
        self.products_button.clicked.connect(lambda: self.parent.navigate_to_page(1))
        
        self.season_planner_button = FeatureButton(
            "EIQ Season Planner",
            "Plan applications\nCompare scenarios\nImport and work from previous years plans"
        )
        self.season_planner_button.clicked.connect(lambda: self.parent.navigate_to_page(2))
        
        self.eiq_calculator_button = FeatureButton(
            "EIQ Calculator",
            "Calculate Environmental Impact Quotients\nCompare EIQ of different applications\nCalculate your seasonal EIQ"
        )
        self.eiq_calculator_button.clicked.connect(lambda: self.parent.navigate_to_page(3))
        
        buttons_layout.addWidget(self.products_button)
        buttons_layout.addWidget(self.season_planner_button)
        buttons_layout.addWidget(self.eiq_calculator_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Add a spacer before the info frames for better proportions
        main_layout.addStretch(1)
        
        # Warning section in its own frame
        warning_frame = ContentFrame()
        warning_layout = QVBoxLayout()
        
        warning_title = QLabel("! ALWAYS CHECK LABELS !") 
        warning_title.setFont(get_subtitle_font(size=20))
        warning_title.setStyleSheet("color: red; font-weight: bold; background-color: #FFEEEE; padding: 5px;")
        warning_title.setAlignment(Qt.AlignCenter)
        warning_layout.addWidget(warning_title)
        
        warning_frame.layout.addLayout(warning_layout)
        main_layout.addWidget(warning_frame)
        
        # Add spacing between frames
        main_layout.addSpacing(5)
        
        # EIQ info section
        info_frame = ContentFrame()
        info_layout = QVBoxLayout()
        
        # EIQ info title
        info_title = QLabel("About Environmental Impact Quotient (EIQ)")
        info_title.setFont(get_subtitle_font())
        info_layout.addWidget(info_title)
        
        # Improved EIQ description with better formatting and concise information
        info_text = QLabel(
            "<b>Environmental Impact Quotient (EIQ)</b>, developed by the <b>NYSIPM Program at Cornell University</b>, "
            "provides a standardized assessment of pesticide environmental impact.<br><br>"
            "<b>EIQ evaluates three main components:</b><br>"
            "- <b>Farm worker risk</b> (applicator + harvester exposure)<br>"
            "- <b>Consumer risk</b> (food residue + groundwater effects)<br>"
            "- <b>Ecological risk</b> (fish, birds, bees, and beneficial insects)<br><br>"
            "Higher scores indicate greater environmental impact. The <b>Field Use EIQ</b> (= EIQ × %AI × Rate) "
            "adjusts for real-world application conditions, supporting sustainable pest management decisions."
            "\n\n CONCISE EXPLANATION EIQ MOLECULE vs EIQ FIELD USE"
        )

        info_text.setWordWrap(True)
        info_text.setFont(get_body_font())
        info_layout.addWidget(info_text)
        
        info_frame.layout.addLayout(info_layout)
        main_layout.addWidget(info_frame)

        # Reduce spacing between frames
        main_layout.addSpacing(5)

    def on_country_changed(self, _):
        """Handle country selection change."""
        if self.initializing:
            return  # Skip during initialization      
        country = self.country_combo.currentText()
        print(f"Country changed to: {country}")
        
        # Update the region dropdown based on the selected country
        old_block_state = self.region_combo.blockSignals(True)  # Block signals temporarily to prevent cascading events  
        self.update_regions_dropdown() # Update regions dropdown based on selected country
        self.region_combo.setCurrentIndex(0) # Reset region selection to "None of the above" 
        region = self.region_combo.currentText() # Get the new region value after reset
        self.region_combo.blockSignals(old_block_state) # Restore original signal blocking state
        self.country_changed.emit(country) # Emit signal for the country change
        
        # Also update the region in the parent window to ensure synchronization
        if self.parent and hasattr(self.parent, 'selected_region'):
            self.parent.selected_region = region
    
    def update_regions_dropdown(self):
        """Update regions dropdown based on selected country."""
        # Store current selection if any
        current_region = self.region_combo.currentText()
        
        # Clear the dropdown
        self.region_combo.clear()
        self.region_combo.addItem("None of the above")
        
        # Get the selected country
        country = self.country_combo.currentText()
        
        # Add regions based on selected country
        if country == "United States":
            self.region_combo.addItems(["Washington", "Idaho", "Wisconsin", "Maine"])
        elif country == "Canada":
            self.region_combo.addItems(["New Brunswick", "Prince Edward Island", "Alberta", "Manitoba", "Quebec", "Saskatchewan"])
        
        # Try to restore previous selection if it's still available
        index = self.region_combo.findText(current_region)
        if index >= 0:
            self.region_combo.setCurrentIndex(index)
        else:
            self.region_combo.setCurrentIndex(0)  # Default to "None of the above"
    
    def on_region_changed(self, index):
        """Handle region selection change."""
        if self.initializing:
            return  # Skip during initialization
                
        region = self.region_combo.currentText()
        print(f"Region changed to: {region}")
        
        # Emit signal with selected region - MainWindow will handle filtering
        self.region_changed.emit(region)
