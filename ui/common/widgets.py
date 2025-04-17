"""
Common custom widgets for the LORENZO POZZI Pesticide App

This module provides reusable custom widgets used throughout the application.
"""

import math

from PySide6.QtCore import Qt, Signal, QSize, QRect, QRectF, QPointF
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QPen
from PySide6.QtWidgets import (
    QPushButton, QLabel, QFrame, QVBoxLayout, QHBoxLayout, 
    QSizePolicy, QWidget, QTableWidget, QTableWidgetItem, QSpacerItem
)

from ui.common.styles import (
    PRIMARY_COLOR, WHITE, FEATURE_BUTTON_STYLE, PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE, get_title_font, get_body_font, 
    MARGIN_MEDIUM, SPACING_MEDIUM
)

from PySide6.QtWidgets import (
    QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
)
from PySide6.QtCore import Qt

from ui.common.styles import (
    PRIMARY_COLOR, SECONDARY_COLOR, FEATURE_BUTTON_STYLE,
    get_title_font, get_body_font, MARGIN_MEDIUM, SPACING_MEDIUM
)

from PySide6.QtWidgets import (
    QPushButton, QLabel, QFrame, QVBoxLayout, QHBoxLayout, 
    QSizePolicy, QWidget, QSpacerItem
)
from PySide6.QtCore import Qt, Signal

from ui.common.styles import (
    PRIMARY_COLOR, SECONDARY_COLOR, SECONDARY_BUTTON_STYLE, PRIMARY_BUTTON_STYLE,
    get_title_font, get_body_font, MARGIN_MEDIUM, SPACING_MEDIUM
)

class HeaderWithBackButton(QWidget):
    """
    A header widget with a title and back button.
    
    This widget is used at the top of pages to provide a consistent navigation.
    Updated with McCain branding elements.
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
        
        # Title with McCain styling - yellow period at the end
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(get_title_font(size=20))
        
        # Add yellow period/full stop
        yellow_dot = QLabel(".")
        yellow_dot.setStyleSheet(f"color: {PRIMARY_COLOR}; font-size: 20pt; font-weight: bold;")
        yellow_dot.setFont(get_title_font(size=20))
        
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(yellow_dot, alignment=Qt.AlignBottom)
        title_layout.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_container)
        
        # Add a spacer to balance the layout
        layout.addItem(QSpacerItem(150, 0))


class FeatureButton(QPushButton):
    """
    A custom button for feature selection on the home page.
    
    Features a title, description, and consistent styling.
    Updated with McCain branding elements.
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
        
        # Title label with yellow period/full stop
        title_layout = QHBoxLayout()
        
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(get_title_font(size=14))
        title_label.setWordWrap(True)
        
        # Add yellow period/full stop
        yellow_dot = QLabel(".")
        yellow_dot.setStyleSheet(f"color: {PRIMARY_COLOR}; font-size: 14pt; font-weight: bold;")
        yellow_dot.setFont(get_title_font(size=14))
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(yellow_dot, alignment=Qt.AlignBottom)
        title_layout.setAlignment(Qt.AlignCenter)
        
        # Description label
        desc_label = QLabel(self.description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(get_body_font())
        desc_label.setWordWrap(True)
        
        layout.addLayout(title_layout)
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

class GaugeWidget(QWidget):
    """A pressure gauge style widget for visualizing ratings or values."""
    
    def __init__(self, parent=None, min_value=0, max_value=100, critical_threshold=70, warning_threshold=30):
        """
        Initialize the gauge widget.
        
        Args:
            parent: Parent widget
            min_value: Minimum value on gauge
            max_value: Maximum value on gauge
            critical_threshold: Threshold for critical/high values (red zone)
            warning_threshold: Threshold for warning/medium values (yellow zone)
        """
        super().__init__(parent)
        
        # Set default values
        self.min_value = min_value
        self.max_value = max_value
        self.critical_threshold = critical_threshold
        self.warning_threshold = warning_threshold
        self.current_value = min_value
        self.label_text = ""
        
        # Colors
        self.background_color = QColor(240, 240, 240)
        self.border_color = QColor(120, 120, 120)
        self.text_color = QColor(30, 30, 30)
        self.needle_color = QColor(180, 0, 0)
        
        # Color zones
        self.low_color = QColor("#77DD77")
        self.medium_color = QColor("#FFF275")
        self.high_color = QColor("#FF6961")
        
        # Set minimum size
        self.setMinimumSize(200, 120)
        
        # Initialize UI
        self.initUI()
    
    def initUI(self):
        """Initialize the UI components."""
        # Layout for the gauge
        layout = QVBoxLayout(self)
        
        # Label for displaying value and text
        self.value_label = QLabel("0")
        self.value_label.setFont(get_body_font(size=12, bold=True))
        self.value_label.setAlignment(Qt.AlignCenter)
        
        # Description label
        self.description_label = QLabel("No data")
        self.description_label.setFont(get_body_font(size=10))
        self.description_label.setAlignment(Qt.AlignCenter)
        
        # Add some spacing for the gauge drawing area
        layout.addStretch(2)
        layout.addWidget(self.value_label)
        layout.addWidget(self.description_label)
        
        # Set layout margins
        layout.setContentsMargins(10, 10, 10, 10)
    
    def set_value(self, value, label_text=""):
        """
        Set the value and optional text label for the gauge.
        
        Args:
            value: Value to display on the gauge
            label_text: Text to display below the gauge
        """
        # Ensure value is within range
        self.current_value = max(self.min_value, min(self.max_value, value))
        self.label_text = label_text
        
        # Update labels
        self.value_label.setText(f"{self.current_value:.1f}")
        self.description_label.setText(label_text)
        
        # Determine color based on thresholds
        if self.current_value >= self.critical_threshold:
            color = self.high_color.name()
        elif self.current_value >= self.warning_threshold:
            color = self.medium_color.name()
        else:
            color = self.low_color.name()
        
        # Apply color to the value label for immediate visual feedback
        self.value_label.setStyleSheet(f"color: {color};")
        
        # Update the widget
        self.update()
    
    def paintEvent(self, event):
        """Paint the gauge widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate the gauge dimensions
        rect = self.rect()
        gauge_height = rect.height() - self.value_label.height() - self.description_label.height() - 20
        gauge_rect = QRect(rect.left() + 10, rect.top() + 10, rect.width() - 20, gauge_height)
        
        # Draw the gauge background
        self.draw_gauge_background(painter, gauge_rect)
        
        # Draw the needle
        self.draw_needle(painter, gauge_rect)
    
    def draw_gauge_background(self, painter, rect):
        """Draw the gauge background with colored zones."""
        # Set up the painter
        painter.setPen(QPen(self.border_color, 2))
        
        # Calculate the gauge metrics
        center_x = rect.center().x()
        center_y = rect.bottom()
        radius = min(rect.width() / 2, rect.height())
        
        # Calculate the angles (in degrees) for the thresholds
        start_angle = 180  # Start at the left side (180 degrees)
        end_angle = 0      # End at the right side (0 degrees)
        angle_range = start_angle - end_angle
        
        # Draw the outer arc
        painter.drawArc(
            center_x - radius, 
            center_y - radius, 
            radius * 2, 
            radius * 2, 
            start_angle * 16, 
            -angle_range * 16
        )
        
        # Calculate the threshold angles
        warning_angle = start_angle - (angle_range * (self.warning_threshold - self.min_value) / 
                                     (self.max_value - self.min_value))
        critical_angle = start_angle - (angle_range * (self.critical_threshold - self.min_value) / 
                                      (self.max_value - self.min_value))
        
        # Draw the colored arcs
        # Low zone (green)
        painter.setPen(QPen(self.low_color, 8))
        painter.drawArc(
            center_x - radius + 4, 
            center_y - radius + 4, 
            (radius - 4) * 2, 
            (radius - 4) * 2, 
            start_angle * 16, 
            -(start_angle - warning_angle) * 16
        )
        
        # Medium zone (yellow)
        painter.setPen(QPen(self.medium_color, 8))
        painter.drawArc(
            center_x - radius + 4, 
            center_y - radius + 4, 
            (radius - 4) * 2, 
            (radius - 4) * 2, 
            warning_angle * 16, 
            -(warning_angle - critical_angle) * 16
        )
        
        # High zone (red)
        painter.setPen(QPen(self.high_color, 8))
        painter.drawArc(
            center_x - radius + 4, 
            center_y - radius + 4, 
            (radius - 4) * 2, 
            (radius - 4) * 2, 
            critical_angle * 16, 
            -(critical_angle - end_angle) * 16
        )
        
        # Draw tick marks
        self.draw_tick_marks(painter, center_x, center_y, radius)
    
    def draw_tick_marks(self, painter, center_x, center_y, radius):
        """Draw tick marks around the gauge."""
        painter.setPen(QPen(self.text_color, 1))
        
        # Calculate angles and positions for tick marks
        outer_radius = radius - 2
        inner_radius = radius - 10
        text_radius = radius - 25
        
        # Draw the tick marks and values
        for i in range(self.min_value, self.max_value + 1, 10):
            # Calculate angle for this tick mark
            angle_deg = 180 - (i - self.min_value) * 180 / (self.max_value - self.min_value)
            angle_rad = math.radians(angle_deg)
            
            # Calculate positions
            outer_x = center_x + outer_radius * math.cos(angle_rad)
            outer_y = center_y - outer_radius * math.sin(angle_rad)
            inner_x = center_x + inner_radius * math.cos(angle_rad)
            inner_y = center_y - inner_radius * math.sin(angle_rad)
            
            # Draw the tick mark
            painter.drawLine(QPointF(outer_x, outer_y), QPointF(inner_x, inner_y))
            
            # Draw the value text for major ticks
            if i % 20 == 0 or i == self.min_value or i == self.max_value:
                text_x = center_x + text_radius * math.cos(angle_rad)
                text_y = center_y - text_radius * math.sin(angle_rad)
                
                # Create a bounding rect for the text
                font = painter.font()
                font.setPointSize(8)
                painter.setFont(font)
                
                # Calculate text rect
                text_rect = QRectF(text_x - 15, text_y - 8, 30, 16)
                
                # Center the text at the calculated position
                painter.drawText(text_rect, Qt.AlignCenter, str(i))
    
    def draw_needle(self, painter, rect):
        """Draw the gauge needle pointing to the current value."""
        # Calculate the needle metrics
        center_x = rect.center().x()
        center_y = rect.bottom()
        radius = min(rect.width() / 2, rect.height()) - 15
        
        # Calculate the angle for the current value
        angle_deg = 180 - (self.current_value - self.min_value) * 180 / (self.max_value - self.min_value)
        angle_rad = math.radians(angle_deg)
        
        # Calculate the needle endpoint
        needle_x = center_x + radius * math.cos(angle_rad)
        needle_y = center_y - radius * math.sin(angle_rad)
        
        # Draw the needle
        painter.setPen(QPen(self.needle_color, 2))
        painter.drawLine(QPointF(center_x, center_y), QPointF(needle_x, needle_y))
        
        # Draw the center knob
        painter.setPen(QPen(self.border_color, 1))
        painter.setBrush(QBrush(self.needle_color))
        painter.drawEllipse(QPointF(center_x, center_y), 5, 5)