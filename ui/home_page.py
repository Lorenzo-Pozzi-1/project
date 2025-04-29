"""
Home page for the LORENZO POZZI Pesticide App

This module defines the HomePage class which serves as the main navigation
screen for the application.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QFrame, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.common.styles import (
    get_title_font, get_body_font, get_subtitle_font, PRIMARY_COLOR, 
    MARGIN_LARGE, SPACING_LARGE, SECONDARY_COLOR, YELLOW_BAR_STYLE
)
from ui.common.widgets import FeatureButton, ContentFrame


class HomePage(QWidget):
    """
    Home page with country selection and feature navigation buttons.
    
    This page serves as the main entry point for users to access the
    various features of the application.
    """
    
    country_changed = Signal(str)
    
    def __init__(self, parent=None):
        """Initialize the home page."""
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        main_layout.setSpacing(SPACING_LARGE)
        
        # Title
        title_label = QLabel("LORENZO POZZI Pesticide App")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(get_title_font(size=24))
        main_layout.addWidget(title_label)
        
        # country selection area
        country_frame = QFrame()
        country_frame.setFrameShape(QFrame.NoFrame)
        country_layout = QHBoxLayout(country_frame)
        country_layout.setAlignment(Qt.AlignCenter)
        
        country_label = QLabel("Select country:")
        country_label.setFont(get_body_font(size=12))
        
        self.country_combo = QComboBox()
        self.country_combo.setFont(get_body_font(size=12))
        self.country_combo.addItems([
            "Canada", "United States"
        ])
        self.country_combo.setMinimumWidth(200)
        self.country_combo.setCurrentIndex(0)
        self.country_combo.currentIndexChanged.connect(self.on_country_changed)
        
        country_layout.addWidget(country_label)
        country_layout.addWidget(self.country_combo)
        
        main_layout.addWidget(country_frame)
        
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
        
        # Warning section and EIQ info section at the bottom
        info_frame = ContentFrame()
        info_layout = QVBoxLayout()
        
        # Warning title - make it more visible with improved styling
        warning_title = QLabel("! Always check products' labels !") 
        warning_title.setFont(get_subtitle_font(size=20))  # Reduced size for better proportions
        warning_title.setStyleSheet("color: red; font-weight: bold; background-color: #FFEEEE; border: 2px solid red; border-radius: 5px; padding: 5px;")
        warning_title.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(warning_title)
        
        # Add some space between warning and EIQ info
        info_layout.addSpacing(15)
        
        # EIQ info title
        info_title = QLabel("About Environmental Impact Quotient (EIQ)")
        info_title.setFont(get_subtitle_font(size=16))
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
        )

        info_text.setWordWrap(True)
        info_text.setFont(get_body_font())
        info_layout.addWidget(info_text)
        
        info_frame.layout.addLayout(info_layout)
        
        # Add a spacer before the info frame for better proportions
        main_layout.addStretch(1)
        main_layout.addWidget(info_frame)
    
    def on_country_changed(self, index):
        """Handle country selection change."""
        country = self.country_combo.currentText()
        print(f"country changed to: {country}")
        self.country_changed.emit(country)  # Emit signal with selected country