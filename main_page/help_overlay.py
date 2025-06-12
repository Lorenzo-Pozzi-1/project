"""
Simple help dialog system for the Pesticide App.

This module provides a help dialog that displays screenshots and instructions
based on the current page index.
"""

import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QScrollArea, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from common import get_medium_font, get_large_font, resource_path

class HelpDialog(QDialog):
    """Simple help dialog that shows page-specific screenshots and instructions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Help")
        self.setModal(True)
        # Make dialog maximized instead of fixed size
        self.setWindowState(self.windowState() | Qt.WindowMaximized)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.content_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        
        layout.addWidget(scroll_area)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        close_button.setFont(get_medium_font())
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
    def show_help_for_page(self, page_index):
        """Show help content for the specified page."""
        # Clear existing content
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)
        
        # Get content for this page
        page_data = self.get_page_data(page_index)
        
        if not page_data:
            # Show "no help available" message
            no_help_label = QLabel("No help content available for this page.")
            no_help_label.setAlignment(Qt.AlignCenter)
            no_help_label.setFont(get_large_font())
            self.content_layout.addWidget(no_help_label)
            self.show()
            return
        
        # Add title
        title_label = QLabel(page_data["title"])
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(get_large_font())
        title_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        self.content_layout.addWidget(title_label)
        
        # Add screenshot if it exists - use resource_path
        screenshot_path = resource_path(f"help/{page_data['screenshot']}")
        if os.path.exists(screenshot_path):
            screenshot_label = QLabel()
            pixmap = QPixmap(screenshot_path)
            # Scale image to fit dialog width while maintaining aspect ratio
            # Increase scale for maximized window
            scaled_pixmap = pixmap.scaledToWidth(1200, Qt.SmoothTransformation)
            screenshot_label.setPixmap(scaled_pixmap)
            screenshot_label.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(screenshot_label)
        
        # Add instructions
        instructions_label = QLabel(page_data["instructions"])
        instructions_label.setWordWrap(True)
        instructions_label.setFont(get_medium_font())
        instructions_label.setAlignment(Qt.AlignLeft)
        instructions_label.setStyleSheet("margin-top: 15px; line-height: 1.4;")
        self.content_layout.addWidget(instructions_label)
        
        # Show the dialog
        self.show()
        
    def get_page_data(self, page_index):
        """Get help data for a specific page."""
        help_data = {
            0: {  # Home page
                "title": "Home Page - Navigation and Preferences",
                "screenshot": "home_page.png",
                "instructions": """
                <b>1. Country and Region:</b> Select your location to filter products available in your area.<br><br>
                <b>2. Row Spacing and Seeding Rate:</b> Set your default field parameters for calculations.<br><br>
                <b>3. Save Button:</b> Save your preferences to persist between sessions.<br><br>
                <b>4. Products List:</b> Browse and compare all available pesticide products.<br><br>
                <b>5. EIQ Calculator:</b> Calculate environmental impact for single applications.<br><br>
                <b>6. Season Planner:</b> Plan entire seasons and compare treatment scenarios.
                """
            },
            1: {  # Products page
                "title": "Products List and Comparison",
                "screenshot": "products_page.png", 
                "instructions": """
                <b>1. Search Box:</b> Type to filter products by name or active ingredient.<br><br>
                <b>2. Table Headers:</b> Click column headers to sort by that criteria.<br><br>
                <b>3. Product Rows:</b> Double-click any row to view detailed information and fact sheets.<br><br>
                <b>4. Filters:</b> Products are automatically filtered based on your country/region selection.
                """
            },
            2: {  # Season planner
                "title": "EIQ Season Planner",
                "screenshot": "season_planner_page.png",
                "instructions": """
                <b>1. Scenario Management:</b> Create new scenarios or load existing ones.<br><br>
                <b>2. Add Applications:</b> Click "Add Row" to add pesticide applications to your plan.<br><br>
                <b>3. Application Details:</b> For each row, select product, rate, timing, and target area.<br><br>
                <b>4. EIQ Totals:</b> View cumulative environmental impact across all applications.<br><br>
                <b>5. Compare Scenarios:</b> Save multiple scenarios to compare treatment strategies.
                """
            },
            3: {  # EIQ Calculator
                "title": "EIQ Calculator",
                "screenshot": "calculator_page.png",
                "instructions": """
                <b>1. Product Selection:</b> Choose a pesticide product from the dropdown menu.<br><br>
                <b>2. Application Rate:</b> Enter the rate you plan to apply the product.<br><br>
                <b>3. Application Area:</b> Specify the area you're treating.<br><br>
                <b>4. Results:</b> View the calculated Field Use EIQ and impact breakdown.<br><br>
                <b>5. Risk Categories:</b> See impacts on farm workers, consumers, and ecology.
                """
            }
        }
        
        return help_data.get(page_index)


def add_help_button_to_main_window(main_window):
    """Add a help button to the main window's yellow bar."""
    
    # Create help button
    help_button = QPushButton("?")
    help_button.setStyleSheet("""
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 15px;
            width: 30px;
            height: 30px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
    """)
    help_button.setToolTip("Show help for this page")
    
    # Create the dialog (but don't show it yet)
    help_dialog = HelpDialog(main_window)
    
    def show_help():
        """Show help for the current page."""
        current_page = main_window.stacked_widget.currentIndex()
        help_dialog.show_help_for_page(current_page)
    
    help_button.clicked.connect(show_help)
    
    # Add button to the yellow bar (insert at the beginning)
    yellow_bar_layout = main_window.yellow_bar.layout()
    yellow_bar_layout.insertWidget(0, help_button)
    
    return help_button, help_dialog