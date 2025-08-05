"""
Feature Selection page for the LORENZO POZZI EIQ App

This module defines the FeatureSelectionPage class which serves as the initial
screen where users choose between EIQ and STIR features.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from common.constants import get_margin_large, get_picture_size, get_spacing_large, get_spacing_medium
from common.styles import get_title_font, get_large_font
from common.utils import resource_path
from common.widgets.header_frame_buttons import ContentFrame, create_button

class FeatureSelectionPage(QWidget):
    """
    Feature selection page where users choose between EIQ and STIR.
    
    This page serves as the initial entry point for users to select
    which feature they want to use.
    """
    
    def __init__(self, parent=None):
        """Initialize the feature selection page."""
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(get_margin_large(), get_margin_large(), get_margin_large(), get_margin_large())
        main_layout.setSpacing(get_spacing_large())
        
        # Header with logos and title in its own ContentFrame
        header_frame = ContentFrame()
        
        # Logos and title row, centered together
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignCenter)
        
        # Logo on the left
        left_logo_label = QLabel()
        pixmap = QPixmap(resource_path("main_page/logo_McCain.png"))
        left_logo_label.setPixmap(pixmap.scaled(get_picture_size(), get_picture_size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        top_layout.addWidget(left_logo_label)
        
        # Small spacing between logo and title
        top_layout.addSpacing(get_spacing_medium())
        
        # Title in the center
        title_label = QLabel("RegenAg App")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(get_title_font())
        top_layout.addWidget(title_label)
        
        # Small spacing between title and logo
        top_layout.addSpacing(get_spacing_medium())
        
        # Logo on the right
        right_logo_label = QLabel()
        right_logo_pixmap = QPixmap(resource_path("main_page/logo_NAAg.png"))
        right_logo_label.setPixmap(right_logo_pixmap.scaled(get_picture_size(), get_picture_size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        top_layout.addWidget(right_logo_label)
        
        # Add top layout to header frame
        header_frame.layout.addLayout(top_layout)
        
        # Add header frame to main layout
        main_layout.addWidget(header_frame)
        
        # Add some spacing
        main_layout.addStretch(1)
                
        # Feature selection buttons
        buttons_frame = ContentFrame()
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(get_spacing_large())
        
        # EIQ button
        eiq_button = create_button(
            text="EIQ", 
            description="Environmental Impact Quotients\nAssess and compare pesticides' environmental impacts", 
            style="feature", 
            callback=self.navigate_to_eiq,
            parent=self
        )
        buttons_layout.addWidget(eiq_button, 1)  # Add stretch factor of 1
        
        # STIR button
        stir_button = create_button(
            text="STIR", 
            description="Soil Tillage Intensity Rating\nAssess soil disturbance", 
            style="feature", 
            callback=self.navigate_to_stir,
            parent=self
        )
        buttons_layout.addWidget(stir_button, 1)  # Add stretch factor of 1
        
        buttons_frame.layout.addLayout(buttons_layout)
        main_layout.addWidget(buttons_frame)
        
        # Add more spacing at the bottom
        main_layout.addStretch(1)
    
    def navigate_to_eiq(self):
        """Navigate to the EIQ home page."""
        self.parent.navigate_to_page(1)  # EIQ home page will be at index 1
    
    def navigate_to_stir(self):
        """Navigate to the STIR placeholder page."""
        self.parent.navigate_to_page(6)  # STIR page will be at index 6
