"""
Season Planner page for the LORENZO POZZI Pesticide App.

This module defines the SeasonPlannerPage class which provides functionality
for planning and managing seasonal pesticide applications.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from common.styles import MARGIN_LARGE, SPACING_MEDIUM, get_title_font, get_body_font
from common.widgets import HeaderWithBackButton, ContentFrame


class SeasonPlannerPage(QWidget):
    """
    Season Planner page for managing seasonal application plans.
    
    This page allows users to create, edit, and compare seasonal pesticide
    application plans to help reduce EIQ impact.
    """
    
    def __init__(self, parent=None):
        """Initialize the season planner page."""
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        main_layout.setSpacing(SPACING_MEDIUM)
        
        # Header with back button
        header = HeaderWithBackButton("Season Planner")
        header.back_clicked.connect(self.parent.go_home)
        main_layout.addWidget(header)
        
        # Content frame for the main content
        content_frame = ContentFrame()
        content_layout = QVBoxLayout()
        
        # Placeholder content - we'll replace this with actual functionality
        title_label = QLabel("Season Planner")
        title_label.setFont(get_title_font(size=18))
        title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title_label)
        
        description_label = QLabel(
            "This feature will allow you to plan and manage seasonal pesticide applications "
            "across multiple fields, tracking cumulative EIQ impact and optimizing your "
            "pesticide program for both efficacy and environmental impact."
        )
        description_label.setFont(get_body_font())
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(description_label)
        
        # Add the content layout to the content frame
        content_frame.layout.addLayout(content_layout)
        
        # Add the content frame to the main layout
        main_layout.addWidget(content_frame)
        
        # Add stretch to push content to the top
        main_layout.addStretch(1)
    
    def refresh_product_data(self):
        """
        Refresh product data based on the filtered products.
        
        This method will be called when filtered data changes in the main window.
        For now, it's a placeholder that will be implemented with actual functionality.
        """
        # This is a placeholder that will be implemented with actual functionality
        pass