"""
Common custom widgets for the LORENZO POZZI Pesticide App

This module provides reusable custom widgets used throughout the application.
"""

import math

from PySide6.QtCore import Qt, Signal, QSize, QRect, QRectF, QPointF
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QPen, QLinearGradient
from PySide6.QtWidgets import (
    QPushButton, QLabel, QFrame, QVBoxLayout, QHBoxLayout, 
    QSizePolicy, QWidget, QTableWidget, QTableWidgetItem, QSpacerItem
)

from ui.common.styles import (
    PRIMARY_COLOR, WHITE, FEATURE_BUTTON_STYLE, PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE, get_title_font, get_body_font, 
    MARGIN_MEDIUM, SPACING_MEDIUM
)

class HeaderWithBackButton(QWidget):
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
        
        # Back button
        self.back_button = QPushButton("Back to Home")
        self.back_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.back_button.setMaximumWidth(150)
        self.back_button.clicked.connect(self.back_clicked.emit)
        layout.addWidget(self.back_button)
        
        # Title without yellow period
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(get_title_font(size=20))
        layout.addWidget(self.title_label)
        
        # Add a spacer to balance the layout
        layout.addItem(QSpacerItem(150, 0))


class FeatureButton(QPushButton):
    """
    A custom button for feature selection on the home page.
    
    Features a title, description, and consistent styling.
    """
    def __init__(self, title, description, parent=None):
        """Initialize with the given title and description."""
        super().__init__(parent)
        self.title = title
        self.description = description
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        self.setMinimumSize(150, 150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(FEATURE_BUTTON_STYLE)
        
        # Create layout for button contents
        layout = QVBoxLayout(self)
        layout.setContentsMargins(MARGIN_MEDIUM, MARGIN_MEDIUM, MARGIN_MEDIUM, MARGIN_MEDIUM)
        layout.setSpacing(SPACING_MEDIUM)
        
        # Title without yellow period
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(get_title_font(size=14))
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Description label
        desc_label = QLabel(self.description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(get_body_font())
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)


class ColorCodedTableItem(QTableWidgetItem):
    """
    A table item that can be color-coded based on its value.
    
    Useful for EIQ scores and other numeric values that have thresholds.
    """
    def __init__(self, value, low_threshold=15, high_threshold=30, 
                 low_color=QColor(200, 255, 200), 
                 medium_color=QColor(255, 255, 200),
                 high_color=QColor(255, 200, 200)):
        """
        Initialize with value and thresholds.
        
        Args:
            value: The numeric value to display
            low_threshold: Values below this are considered "low"
            high_threshold: Values above this are considered "high"
            low_color: Background color for low values
            medium_color: Background color for medium values
            high_color: Background color for high values
        """
        if isinstance(value, (int, float)):
            display_value = f"{value:.1f}"
        else:
            display_value = str(value)
            
        super().__init__(display_value)
        
        self.setTextAlignment(Qt.AlignCenter)
        
        # Apply color coding based on thresholds
        try:
            value_float = float(value)
            if value_float < low_threshold:
                self.setBackground(QBrush(low_color))
            elif value_float < high_threshold:
                self.setBackground(QBrush(medium_color))
            else:
                self.setBackground(QBrush(high_color))
        except (ValueError, TypeError):
            # If value can't be converted to float, don't apply color
            pass


class ContentFrame(QFrame):
    """
    A styled frame for content sections.
    
    Provides consistent styling for content areas throughout the app.
    """
    def __init__(self, parent=None):
        """Initialize the frame."""
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)  # Changed from StyledPanel to NoFrame
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
                border-radius: 6px;
            }
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)


class ToxicityBar(QWidget):
    """A color gradient bar displaying toxicity levels from Low to High."""
    
    def __init__(self, parent=None, low_threshold=33.3, high_threshold=66.6):
        """
        Initialize the toxicity bar widget.
        
        Args:
            parent: Parent widget
            low_threshold: Threshold for low/medium values
            high_threshold: Threshold for medium/high values
        """
        super().__init__(parent)
        
        # Set default values
        self.min_value = 0
        self.max_value = 100
        self.low_threshold = low_threshold  # Store the provided threshold
        self.high_threshold = high_threshold  # Store the provided threshold
        self.current_value = 0
        self.label_text = ""
        self.title_text = "Toxicity level:"
        
        # Colors
        self.low_color = QColor("#77DD77")  # Pastel green
        self.medium_color = QColor("#FFF275")  # Pastel yellow
        self.high_color = QColor("#FF6961")  # Pastel red
        self.border_color = QColor("#CCCCCC")
        self.text_color = QColor("#333333")
        
        # Category colors - darker versions for text
        self.low_text_color = QColor("#1E8449")
        self.medium_text_color = QColor("#B7950B")
        self.high_text_color = QColor("#B03A2E")
        self.extreme_text_color = QColor("#B03A2E")
        
        # Set minimum size - increased height to make room for text
        self.setMinimumSize(200, 140)
        
        # Simple layout with just margins
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        self.setLayout(layout)
    
    def set_value(self, value, label_text=""):
        """
        Set the value and optional text label for the bar.
        
        Args:
            value: Value to display on the bar
            label_text: Text to display below the bar
        """
        # Store the original value (even if >100)
        self.current_value = value
        self.label_text = label_text
        
        # Update the widget
        self.update()
    
    def get_toxicity_level(self):
        """Get the toxicity level based on the current value."""
        if self.current_value > 100:
            return "EXTREME"
        elif self.current_value < self.low_threshold:
            return "Low"
        elif self.current_value < self.high_threshold:
            return "Medium"
        else:
            return "High"
    
    def paintEvent(self, event):
        """Paint the gradient bar and all other elements."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate the dimensions
        rect = self.rect()
        margin = 10
        bar_width = rect.width() - (margin * 2)  # Margin on both sides
        bar_height = 20  # Fixed height
        
        bar_x = rect.x() + margin
        
        # Draw the title
        title_font = get_body_font(size=14, bold=True)
        painter.setFont(title_font)
        painter.setPen(QPen(self.text_color, 1))
        
        title_rect = QRect(bar_x, margin, bar_width, 25)
        painter.drawText(title_rect, Qt.AlignCenter, self.title_text)
        
        # Position the bar below the title (with fixed position)
        bar_y = title_rect.bottom() + 15
        
        bar_rect = QRect(bar_x, bar_y, bar_width, bar_height)
        
        # Create gradient
        gradient = QLinearGradient(bar_rect.topLeft(), bar_rect.topRight())
        gradient.setColorAt(0.0, self.low_color)
        gradient.setColorAt(0.5, self.medium_color)
        gradient.setColorAt(1.0, self.high_color)
        
        # Draw gradient bar
        painter.fillRect(bar_rect, gradient)
        
        # Draw border
        painter.setPen(QPen(self.border_color, 1))
        painter.drawRect(bar_rect)
        
        # Draw small ticks with faint labels
        painter.setPen(QPen(QColor(160, 160, 160, 120), 1))  # Light gray, semi-transparent
        painter.setFont(get_body_font(size=8))  # Small font
        
        # Low tick (0)
        low_x = bar_x
        painter.drawLine(low_x, bar_y + bar_height, low_x, bar_y + bar_height + 3)
        painter.drawText(QRect(low_x - 15, bar_y + bar_height + 4, 30, 12), Qt.AlignCenter, "0")
        
        # Low-Medium threshold tick (33.3)
        low_med_x = bar_x + (self.low_threshold / self.max_value) * bar_width
        painter.drawLine(low_med_x, bar_y + bar_height, low_med_x, bar_y + bar_height + 3)
        
        # Format the threshold value with one decimal place
        low_med_text = f"{self.low_threshold:.1f}"
        painter.drawText(QRect(low_med_x - 15, bar_y + bar_height + 4, 30, 12), Qt.AlignCenter, low_med_text)
        
        # Medium-High threshold tick (66.6)
        med_high_x = bar_x + (self.high_threshold / self.max_value) * bar_width
        painter.drawLine(med_high_x, bar_y + bar_height, med_high_x, bar_y + bar_height + 3)
        
        # Format the threshold value with one decimal place
        med_high_text = f"{self.high_threshold:.1f}"
        painter.drawText(QRect(med_high_x - 15, bar_y + bar_height + 4, 30, 12), Qt.AlignCenter, med_high_text)
        
        # High-end tick (100)
        high_x = bar_x + bar_width
        painter.drawLine(high_x, bar_y + bar_height, high_x, bar_y + bar_height + 3)
        painter.drawText(QRect(high_x - 15, bar_y + bar_height + 4, 30, 12), Qt.AlignCenter, "100")
        
        # Handle the marker and text display
        if self.current_value > 0:
            # Get current toxicity level
            toxicity_level = self.get_toxicity_level()
            
            # If the value is greater than 100, cap the marker position at the end of the bar
            marker_value = min(self.current_value, self.max_value) 
            marker_x = bar_x + (marker_value / self.max_value) * bar_width
            
            # Draw triangle marker below the bar pointing upwards
            triangle_width = 10
            triangle_height = 8
            
            # Set up triangle coordinates
            points = [
                (marker_x, bar_y + bar_height),  # Top point
                (marker_x - triangle_width/2, bar_y + bar_height + triangle_height),  # Bottom left
                (marker_x + triangle_width/2, bar_y + bar_height + triangle_height)   # Bottom right
            ]
            
            # Draw filled triangle
            painter.setBrush(QBrush(QColor("#333333")))
            painter.setPen(QPen(QColor("#333333"), 1))
            
            # Create QPointF objects for the polygon
            polygon_points = [QPointF(x, y) for x, y in points]
            painter.drawPolygon(polygon_points)
            
            # Set color based on toxicity level
            if toxicity_level == "Low":
                text_color = self.low_text_color
            elif toxicity_level == "Medium":
                text_color = self.medium_text_color
            elif toxicity_level == "EXTREME":
                text_color = self.extreme_text_color
            else:  # High
                text_color = self.high_text_color
            
            # Draw the bold toxicity level text centered under the marker
            painter.setFont(get_body_font(size=15, bold=True))
            painter.setPen(QPen(text_color, 1))
            
            # Position the text under the triangle - move it up compared to previous version
            text_y = bar_y + bar_height + triangle_height + 5
            text_width = 120  # Increased width for "EXTREMELY TOXIC"
            
            # Ensure text stays within bounds of the widget
            text_x = max(bar_x, min(marker_x - text_width/2, bar_x + bar_width - text_width))
            
            # Draw the toxicity level
            level_rect = QRect(text_x, text_y, text_width, 20)
            painter.drawText(level_rect, Qt.AlignCenter, toxicity_level)