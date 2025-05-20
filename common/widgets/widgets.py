"""
Common custom widgets for the LORENZO POZZI Pesticide App

This module provides reusable custom widgets used throughout the application.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QWidget, QSpacerItem
from common.styles import *

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
        self.home_button = create_button(text="Home", style='secondary', callback=self.back_clicked.emit)
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
        self.layout.setContentsMargins(MARGIN_SMALL, MARGIN_SMALL, MARGIN_SMALL, MARGIN_SMALL)
        self.layout.setSpacing(SPACING_MEDIUM)


def create_button(text=None, description=None, style='primary', callback=None, parent=None):
    """
    Create a button with consistent styling.
    
    Args:
        text (str): Button text
        description (str): Optional description for feature buttons
        style (str): Button style ('primary', 'secondary', 'special', 'feature', 'remove')
        callback (callable): Function to call when button is clicked
        parent (QWidget): Parent widget
        
    Returns:
        QPushButton: Styled button
    """
    button = QPushButton(parent)
    button.setCursor(Qt.PointingHandCursor)

    # Apply the appropriate style based on the style parameter
    if style == 'primary':
        button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        button.setText(text)
    elif style == 'secondary':
        button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        button.setText(text)
    elif style == 'special':
        button.setStyleSheet(SPECIAL_BUTTON_STYLE)
        button.setText(text)
    elif style == 'feature':
        button.setStyleSheet(FEATURE_BUTTON_STYLE)
        
        # Create a layout for the button content
        layout = QVBoxLayout(button)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Add title and description
        title = QLabel(text)
        title.setAlignment(Qt.AlignCenter)
        title.setFont(get_subtitle_font())
        layout.addWidget(title) 
        description = QLabel(description)
        description.setAlignment(Qt.AlignCenter)
        description.setFont(get_body_font())
        layout.addWidget(description)
                    
    elif style == 'remove':
        button.setStyleSheet(REMOVE_BUTTON_STYLE)
        button.setText("×")
        button.setFixedSize(30, 30)  # Set a fixed size for the button
    
    # Set minimum dimensions for regular buttons (not for remove buttons)
    if style == 'feature':
        button.setMinimumSize(FEATURE_BUTTON_SIZE, FEATURE_BUTTON_SIZE)
    elif style != 'remove':
        button.setMinimumSize(BUTTON_MIN_WIDTH, BUTTON_MIN_HEIGHT)
    
    # Connect callback if provided
    if callback:
        button.clicked.connect(callback)
        
    return button
