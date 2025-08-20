"""
STIR placeholder page

This module defines the STIRPlaceholderPage class which serves as a
placeholder for the STIR (Soil Tillage Intensity Rating) feature.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from common.constants import get_margin_large, get_picture_size, get_spacing_large, get_spacing_medium
from common.styles import get_title_font, get_large_font, get_subtitle_font, INFO_TEXT_STYLE
from common.utils import resource_path
from common.widgets.header_frame_buttons import ContentFrame, create_button

class STIRPlaceholderPage(QWidget):
    """
    STIR placeholder page.
    
    This page serves as a placeholder for the STIR feature that will be
    implemented in the future.
    """
    
    def __init__(self, parent=None):
        """Initialize the STIR placeholder page."""
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

        # Create a layout for the entire header including back button
        header_main_layout = QVBoxLayout()
        
        # Top row with back button
        top_row_layout = QHBoxLayout()
        top_row_layout.setAlignment(Qt.AlignLeft)
        
        # Back button in top left
        back_button = create_button(
            text="← Back to Feature Selection", 
            style="white", 
            callback=self.go_back_to_feature_selection,
            parent=self
        )
        top_row_layout.addWidget(back_button)
        top_row_layout.addStretch()  # Push button to the left
        
        header_main_layout.addLayout(top_row_layout)
        
        # Logos and title row, centered together
        logos_title_layout = QHBoxLayout()
        logos_title_layout.setAlignment(Qt.AlignCenter)
        
        # Logo on the left
        left_logo_label = QLabel()
        pixmap = QPixmap(resource_path("main_page/logo_McCain.png"))
        left_logo_label.setPixmap(pixmap.scaled(get_picture_size(), get_picture_size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logos_title_layout.addWidget(left_logo_label)
        
        # Small spacing between logo and title
        logos_title_layout.addSpacing(get_spacing_medium())
        
        # Title in the center
        title_label = QLabel("STIR")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(get_title_font())
        logos_title_layout.addWidget(title_label)
        
        # Small spacing between title and logo
        logos_title_layout.addSpacing(get_spacing_medium())
        
        # Logo on the right
        right_logo_label = QLabel()
        right_logo_pixmap = QPixmap(resource_path("main_page/logo_NAAg.png"))
        right_logo_label.setPixmap(right_logo_pixmap.scaled(get_picture_size(), get_picture_size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logos_title_layout.addWidget(right_logo_label)
        
        # Add logos and title layout to header main layout
        header_main_layout.addLayout(logos_title_layout)
        
        # Add header main layout to header frame
        header_frame.layout.addLayout(header_main_layout)
        
        # Add header frame to main layout
        main_layout.addWidget(header_frame)
        
        # Add some spacing
        main_layout.addStretch(1)
        
        # Feature buttons section
        buttons_frame = ContentFrame()
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(get_spacing_large())
        
        # STIR Calculator button
        calculator_button = create_button(
            text="STIR Calculator",
            description="Calculate Soil Tillage Intensity Ratings\nCompare different tillage practices",
            style="feature",
            callback=self.navigate_to_stir_calculator,
            parent=self
        )
        buttons_layout.addWidget(calculator_button, 1)  # Add stretch factor of 1
        
        buttons_frame.layout.addLayout(buttons_layout)
        main_layout.addWidget(buttons_frame)
        
        # Add some spacing
        main_layout.addStretch(1)
        
        # Info frame about STIR
        info_frame = ContentFrame()
        info_frame.setStyleSheet(INFO_TEXT_STYLE)
        info_layout = QVBoxLayout()
                
        # STIR info title
        info_title = QLabel("About STIR")
        info_title.setFont(get_subtitle_font())
        info_title.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(info_title)
        
        # STIR description
        info_text = QLabel(
            "STIR (Soil Tillage Intensity Rating) evaluates the intensity of soil tillage practices<br>"
            "<b>Higher STIR values → More soil disturbance</b><br>"
            "STIR is a product of speed, tillage type, average depth, and surface soil disturbance"
        )
        info_text.setWordWrap(True)
        info_text.setFont(get_large_font())
        info_text.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(info_text)
        
        info_frame.layout.addLayout(info_layout)
        main_layout.addWidget(info_frame)
    
    def navigate_to_stir_calculator(self):
        """Navigate to the STIR calculator page."""
        self.parent.navigate_to_page(7)  # STIR calculator page will be at index 7
        
    def go_back_to_feature_selection(self):
        """Navigate back to the feature selection page."""
        self.parent.navigate_to_page(0)  # Feature selection page is at index 0
