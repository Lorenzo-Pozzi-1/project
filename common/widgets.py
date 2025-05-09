"""
Common custom widgets for the LORENZO POZZI Pesticide App

This module provides reusable custom widgets used throughout the application.
"""

from PySide6.QtCore import Qt, Signal, QRect, QPointF
from PySide6.QtGui import QColor, QBrush, QPainter, QPen, QLinearGradient
from PySide6.QtWidgets import QPushButton, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QSizePolicy, QWidget, QSpacerItem
from common.styles import FEATURE_BUTTON_STYLE, SECONDARY_BUTTON_STYLE, get_title_font, get_body_font, MARGIN_MEDIUM, SPACING_MEDIUM

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
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(get_title_font(size=20))
        layout.addWidget(self.title_label)
        
        # Add a spacer to balance the layout
        layout.addItem(QSpacerItem(150, 0))


class FeatureButton(QPushButton):
    """
    A custom button for feature selection on the home page.
    
    Has a title, description, and consistent styling.
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
        
        # Title
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


class ContentFrame(QFrame):
    """
    A styled frame for content sections.
    
    Provides consistent styling for content areas throughout the app.
    """
    def __init__(self, parent=None):
        """Initialize the frame."""
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
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


class ScoreBar(QWidget):
    """A color gradient bar for displaying field EIQ scores from Low to High."""
    
    def __init__(self, parent=None, low_threshold=33.3, high_threshold=66.6):
        """
        Initialize the scorebar widget.
        
        Args:
            parent: Parent widget
            low_threshold: Threshold for low/medium values
            high_threshold: Threshold for medium/high values
        """
        super().__init__(parent)
        
        # Set default values
        self.min_value = 0
        self.max_value = 100
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.current_value = 0
        self.label_text = ""
        self.title_text = "Field EIQ score:"
        
        # Colors - define once and reuse
        self.low_color = QColor("#77DD77")  # Pastel green
        self.medium_color = QColor("#FFF275")  # Pastel yellow
        self.high_color = QColor("#FF6961")  # Pastel red
        self.border_color = QColor("#CCCCCC") # Light gray
        self.text_color = QColor("#333333") # Dark gray
        
        # Category colors - defined once
        self.category_text_colors = {
            "Low": QColor("#1E8449"), # Dark green
            "Medium": QColor("#B7950B"), # Dark yellow
            "High": QColor("#B03A2E"), # Dark red
            "EXTREME": QColor("#B03A2E") # Dark red
        }
        
        # Set minimum size
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
        self.current_value = value
        self.label_text = label_text
        self.update()
    
    def get_score_level(self):
        """Get the field EIQ score level based on the current value."""
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
        painter = QPainter()
        if not painter.begin(self):  # Explicitly call begin and check for success
            return  # Don't proceed if begin fails
        
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Calculate the dimensions
            rect = self.rect()
            margin = 10
            bar_width = rect.width() - (margin * 2)
            bar_height = 20  # Fixed height
            bar_x = rect.x() + margin
            
            # Draw the title
            title_font = get_body_font(size=14, bold=True)
            painter.setFont(title_font)
            painter.setPen(QPen(self.text_color, 1))
            
            title_rect = QRect(bar_x, margin, bar_width, 25)
            painter.drawText(title_rect, Qt.AlignCenter, self.title_text)
            
            # Position the bar below the title
            bar_y = title_rect.bottom() + 15
            bar_rect = QRect(bar_x, bar_y, bar_width, bar_height)
            
            # Create gradient
            gradient = QLinearGradient(bar_rect.topLeft(), bar_rect.topRight())
            gradient.setColorAt(0.0, self.low_color)
            gradient.setColorAt(0.5, self.medium_color)
            gradient.setColorAt(1.0, self.high_color)
            
            # Draw gradient bar
            painter.fillRect(bar_rect, gradient)
            painter.setPen(QPen(self.border_color, 1))
            painter.drawRect(bar_rect)
            
            # Draw ticks and labels - reuse formatting for consistency
            self._draw_ticks_and_labels(painter, bar_x, bar_y, bar_width, bar_height)
            
            # Handle the marker and text display if we have a valid value
            if self.current_value > 0:
                self._draw_marker_and_text(painter, bar_x, bar_y, bar_width, bar_height)
        
        finally:
            painter.end()  # Always call end() to properly clean up
    
    def _draw_ticks_and_labels(self, painter, bar_x, bar_y, bar_width, bar_height):
        """Draw the tick marks and labels on the bar."""
        painter.setPen(QPen(QColor(160, 160, 160, 120), 1))
        painter.setFont(get_body_font(size=8))
        
        # Define tick positions and labels
        ticks = [
            (0, "0"),
            (self.low_threshold / self.max_value, f"{self.low_threshold:.1f}"),
            (self.high_threshold / self.max_value, f"{self.high_threshold:.1f}"),
            (1.0, "100")
        ]
        
        for relative_pos, label in ticks:
            x_pos = bar_x + relative_pos * bar_width
            painter.drawLine(x_pos, bar_y + bar_height, x_pos, bar_y + bar_height + 3)
            painter.drawText(QRect(x_pos - 15, bar_y + bar_height + 4, 30, 12), Qt.AlignCenter, label)
    
    def _draw_marker_and_text(self, painter, bar_x, bar_y, bar_width, bar_height):
        """Draw the position marker and text label."""
        score_level = self.get_score_level()
        
        # Cap the marker position at the end of the bar
        marker_value = min(self.current_value, self.max_value) 
        marker_x = bar_x + (marker_value / self.max_value) * bar_width
        
        # Draw triangle marker
        triangle_width = 10
        triangle_height = 8
        
        points = [
            QPointF(marker_x, bar_y + bar_height),  # Top point
            QPointF(marker_x - triangle_width/2, bar_y + bar_height + triangle_height),  # Bottom left
            QPointF(marker_x + triangle_width/2, bar_y + bar_height + triangle_height)   # Bottom right
        ]
        
        # Draw filled triangle
        painter.setBrush(QBrush(QColor("#333333")))
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.drawPolygon(points)
        
        # Set color based on field EIQ score level
        text_color = self.category_text_colors.get(score_level, self.category_text_colors["High"])
        
        # Draw the field EIQ score level text
        painter.setFont(get_body_font(size=15, bold=True))
        painter.setPen(QPen(text_color, 1))
        
        text_y = bar_y + bar_height + triangle_height + 5
        text_width = 120
        
        # Keep text within widget bounds
        text_x = max(bar_x, min(marker_x - text_width/2, bar_x + bar_width - text_width))
        
        level_rect = QRect(text_x, text_y, text_width, 20)
        painter.drawText(level_rect, Qt.AlignCenter, score_level)