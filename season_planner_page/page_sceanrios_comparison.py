"""
Scenarios Comparison Page for the Season Planner.

Placeholder page that displays a preview image for the upcoming
scenarios comparison feature.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from common import HeaderWithHomeButton, get_margin_large, resource_path


class ScenariosComparisonPage(QWidget):
    """
    Placeholder page for scenarios comparison feature.
    
    Displays a full-window preview image until the actual
    comparison functionality is implemented.
    """
    
    def __init__(self, parent=None):
        """Initialize the scenarios comparison page."""
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        
        # Header with back button
        header = HeaderWithHomeButton("Scenarios Comparison - Coming Soon")
        header.back_clicked.connect(self.go_back)
        main_layout.addWidget(header)
        
        # Image display (full remaining space)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        
        # Load and display the placeholder image
        image_path = resource_path(r"C:\Users\LORPOZZI\Downloads\Screenshot 2025-06-05 083452.png")
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap)
        
        main_layout.addWidget(self.image_label, 1)  # Give it all remaining space
    
    def go_back(self):
        """Navigate back to the scenarios manager page."""
        if self.parent:
            # Navigate back to season planner page
            self.parent.navigate_to_page(2)