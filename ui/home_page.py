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
    MARGIN_LARGE, SPACING_LARGE
)
from ui.common.widgets import FeatureButton, ContentFrame


class HomePage(QWidget):
    """
    Home page with region selection and feature navigation buttons.
    
    This page serves as the main entry point for users to access the
    various features of the application.
    """
    
    region_changed = Signal(str)
    
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
        
        # Region selection area
        region_frame = QFrame()
        region_frame.setFrameShape(QFrame.NoFrame)
        region_layout = QHBoxLayout(region_frame)
        region_layout.setAlignment(Qt.AlignCenter)
        
        region_label = QLabel("Select Region:")
        region_label.setFont(get_body_font(size=12))
        
        self.region_combo = QComboBox()
        self.region_combo.setFont(get_body_font(size=12))
        self.region_combo.addItems([
            "CA", "USA"
        ])
        self.region_combo.setMinimumWidth(200)
        self.region_combo.setCurrentIndex(0)
        self.region_combo.currentIndexChanged.connect(self.on_region_changed)
        
        region_layout.addWidget(region_label)
        region_layout.addWidget(self.region_combo)
        
        main_layout.addWidget(region_frame)
        
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
            "Season Planner",
            "Plan applications, compare scenarios, import and work from previous years plans"
        )
        self.season_planner_button.clicked.connect(lambda: self.parent.navigate_to_page(2))
        
        self.eiq_calculator_button = FeatureButton(
            "EIQ Calculator",
            "Calculate Environmental Impact Quotients, compare EIQ of different applications, calculate your seasonal EIQ"
        )
        self.eiq_calculator_button.clicked.connect(lambda: self.parent.navigate_to_page(3))
        
        buttons_layout.addWidget(self.products_button)
        buttons_layout.addWidget(self.season_planner_button)
        buttons_layout.addWidget(self.eiq_calculator_button)
        
        main_layout.addLayout(buttons_layout)
        
        # EIQ info section at the bottom
        info_frame = ContentFrame()
        info_layout = QVBoxLayout()
        
        info_title = QLabel("About Environmental Impact Quotient (EIQ)")
        info_title.setFont(get_subtitle_font(size=16))
        info_layout.addWidget(info_title)
        
        info_text = QLabel(
            "<b>Environmental Impact Quotient (EIQ)</b>, developed by the <b>NYSIPM Program at Cornell University</b>, is a tool used to assess the potential risks of pesticide active ingredients. "
            "It generates a single numerical score reflecting environmental and human health impacts.<br><br>"
            "<b>EIQ evaluates:</b><br>"
            "- <b>Farm worker risk</b> (toxicity + exposure)<br>"
            "- <b>Consumer risk</b> (residue on food)<br>"
            "- <b>Ecological risk</b> (effects on birds, bees, fish, etc.)<br><br>"
            "Higher scores = higher impact. Users can also calculate a <b>Field Use Rating</b>, which adjusts for application rate and frequency. "
            "The EIQ supports <b>sustainable, low-impact pest management</b> decisions in agriculture."
        )

        info_text.setWordWrap(True)
        info_text.setFont(get_body_font())
        info_layout.addWidget(info_text)
        
        info_frame.layout.addLayout(info_layout)
        
        # Add a spacer before the info frame
        main_layout.addStretch(1)
        main_layout.addWidget(info_frame)
    
    def on_region_changed(self, index):
        """Handle region selection change."""
        # In the future, this could update application-wide settings
        # or trigger region-specific data loading
        region = self.region_combo.currentText()
        print(f"Region changed to: {region}")

        self.region_changed.emit(region)