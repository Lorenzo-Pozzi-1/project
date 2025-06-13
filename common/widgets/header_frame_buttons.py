"""
Common custom widgets for the LORENZO POZZI Pesticide App

This module provides reusable custom widgets used throughout the application.
"""

from math import floor
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QWidget, QSpacerItem

from common.constants import get_button_min_height, get_button_min_width, get_feature_button_size, get_margin_medium, get_margin_small, get_spacing_medium, get_spacing_small
from common.styles import FEATURE_BUTTON_STYLE, FRAME_STYLE, REMOVE_BUTTON_STYLE, TINY_BUTTON_STYLE, UOM_BUTTON_STYLE, get_large_font, get_small_font, get_subtitle_font, get_title_font


class HeaderWithHomeButton(QWidget):
    """
    A header widget with a title and back button.
    
    This widget is used at the top of pages to provide a consistent navigation.
    """
    back_clicked = Signal()  # Signal emitted when back button is clicked
    
    def __init__(self, title, parent=None):
        """Initialize with the given title."""
        super().__init__(parent)
        self.title = title
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Home button
        self.home_button = create_button(text="Home", style='white', callback=self.back_clicked.emit)
        self.home_button.setFixedWidth(75)
        layout.addWidget(self.home_button)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(get_title_font(size=20))
        layout.addWidget(self.title_label)
        
        # Add a spacer to balance the layout
        layout.addItem(QSpacerItem(150, 0))


class ContentFrame(QFrame):
    """
    A styled frame for content sections.
    
    Provides consistent styling for content areas throughout the app.
    """
    def __init__(self, parent=None):
        """Initialize the frame."""
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet(FRAME_STYLE)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(get_margin_small(), get_margin_small(), get_margin_small(), get_margin_small())
        self.layout.setSpacing(get_spacing_medium())


def create_button(text=None, description=None, style='yellow', callback=None, parent=None) -> QPushButton:
    """
    Create a button with consistent styling.
    
    Args:
        text (str): Button text
        description (str): Optional description for feature buttons
        style (str): Button style ('yellow', 'white', 'special', 'feature', 'remove', 'tiny', 'UOM)
        callback (callable): Function to call when button is clicked
        parent (QWidget): Parent widget
        
    Returns:
        QPushButton: Styled button
    """
    button = QPushButton(parent)
    button.setCursor(Qt.PointingHandCursor)
    
    # Apply style and content based on button type
    if style in ('yellow', 'white', 'special'):
        # Standard buttons share the same structure
        button.setStyleSheet(globals().get(f"{style.upper()}_BUTTON_STYLE"))
        button.setText(text)
        button.setFont(get_small_font())
        button.setMinimumSize(get_button_min_width(), get_button_min_height())
    
    elif style == 'feature':
        # Feature button with title and description
        button.setStyleSheet(FEATURE_BUTTON_STYLE)
        button.setMinimumSize(get_feature_button_size(), get_feature_button_size())
        
        # Create layout for the feature button content
        layout = QVBoxLayout(button)
        layout.setContentsMargins(get_margin_medium(), get_margin_medium(), get_margin_medium(), get_margin_medium())
        layout.setSpacing(get_spacing_small())
        
        # Add title label
        title_label = QLabel(text)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(get_subtitle_font())
        layout.addWidget(title_label)
        
        # Add description label
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(get_large_font())
        layout.addWidget(desc_label)
    
    elif style == 'remove':
        # Remove button (small "X" button)
        button.setStyleSheet(REMOVE_BUTTON_STYLE)
        button.setText("×")
        button.setFixedSize(30, 30)

    elif style == 'tiny':
        # Tiny button for the terminal
        button.setStyleSheet(TINY_BUTTON_STYLE)
        button.setText(text)
        button.setFont(get_small_font())
        button.setFixedSize(30, 20)
    
    elif style == 'UOM':
        # Tiny button for the terminal
        button.setStyleSheet(UOM_BUTTON_STYLE)
        button.setText(text)
        button.setFont(get_small_font())
        button.setFixedSize(30, 20)

    # Connect callback if provided
    if callback:
        button.clicked.connect(callback)
    
    return button
