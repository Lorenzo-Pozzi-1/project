"""
ScoreBar widget for the McCain Pesticides App

This module provides a customizable score bar widget that displays values
on a gradient with preset configurations.
"""

from PySide6.QtCore import Qt, QRect, QPointF
from PySide6.QtGui import QColor, QBrush, QPainter, QPen, QLinearGradient
from PySide6.QtWidgets import QWidget, QVBoxLayout
from common.constants import (
    EIQ_LOW_THRESHOLD, EIQ_MEDIUM_THRESHOLD, EIQ_HIGH_THRESHOLD,
    ADVANCED, ONBOARDING, ENGAGED, LEADING, GREEN, YELLOW_PRESSED,
    get_medium_text_size, get_large_text_size,
    get_margin_small, get_spacing_medium
)
from common.styles import get_medium_font

class ScoreBar(QWidget):
    """A color gradient bar for displaying scores with preset color schemes."""
    
    def __init__(self, parent=None, preset="calculator"):
        """
        Initialize the scorebar widget with a preset configuration.
        
        Args:
            parent: Parent widget
            preset: "calculator" or "regen_ag" for different configurations
        """
        super().__init__(parent)
        
        self.preset = preset
        self.current_value = 0
        self.label_text = ""
        
        # Configure everything based on preset
        self._setup_preset_configuration()
        
        # Set minimum size
        self.setMinimumSize(200, 140)
        
        # Use responsive layout with constants
        layout = QVBoxLayout(self)
        margin = get_margin_small()
        layout.setContentsMargins(margin, margin//2, margin, margin//2)
        self.setLayout(layout)
    
    def _setup_preset_configuration(self):
        """Set up all configuration based on the selected preset."""
        if self.preset == "calculator":
            self.title_text = "Field EIQ score:"
            self.thresholds = [EIQ_LOW_THRESHOLD, EIQ_MEDIUM_THRESHOLD, EIQ_HIGH_THRESHOLD]
            self.labels = ["Low", "Medium", "High", "Very High"]
            self.min_value = 0
            self.max_value = EIQ_HIGH_THRESHOLD
            
            # Simple 3-color scheme: green -> yellow -> red
            self.gradient_colors = [
                QColor(34, 197, 94),   # Brilliant green
                QColor(255, 235, 59),  # Bright yellow
                QColor(239, 68, 68)    # Bright red
            ]
            self.region_colors = [
                QColor(GREEN),   # Green region
                QColor(YELLOW_PRESSED),  # Yellow region
                QColor(255, 152, 0),   # Orange region
                QColor(239, 68, 68)    # Red region
            ]
            
        elif self.preset == "regen_ag":
            self.title_text = "RegenAg framework class:"
            self.thresholds = [LEADING, ADVANCED, ENGAGED, ONBOARDING]
            self.labels = ["Leading", "Advanced", "Engaged", "Onboarding", "Out of range"]
            self.min_value = 0
            self.max_value = 2500
            
            # Simple 3-color scheme: green -> yellow -> red
            self.gradient_colors = [
                QColor(34, 197, 94),   # Bright green
                QColor(255, 235, 59),  # Bright yellow
                QColor(239, 68, 68)    # Bright red
            ]
            self.region_colors = [
                QColor(GREEN),   # Leading (green)
                QColor(102, 204, 102), # Advanced (medium green)
                QColor(153, 221, 68),  # Engaged (light green)
                QColor(YELLOW_PRESSED),  # Onboarding (yellow)
                QColor(239, 68, 68)    # Out of range (red)
            ]
            
        else:
            raise ValueError(f"Unknown preset: {self.preset}")
    
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
        """Get the score level based on the current value."""
        if self.current_value > self.max_value:
            return self.labels[-1]
        
        for i, threshold in enumerate(self.thresholds):
            if self.current_value < threshold:
                return self.labels[i]
        
        return self.labels[-1]

    def get_score_color(self):
        """Get the color that matches the current value position."""
        # Cap the value within our range
        clamped_value = min(max(self.current_value, self.min_value), self.max_value)
        
        # Find which region we're in
        region_index = 0
        for i, threshold in enumerate(self.thresholds):
            if clamped_value >= threshold:
                region_index = i + 1
            else:
                break
        
        # Return the corresponding region color
        return self.region_colors[min(region_index, len(self.region_colors) - 1)]
    
    def paintEvent(self, event):
        """Paint the gradient bar and all other elements."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate dimensions using responsive constants
        rect = self.rect()
        margin = get_margin_small()
        bar_width = rect.width() - (margin * 2)
        bar_height = 20
        bar_x = rect.x() + margin
        
        # Draw the title using responsive font
        title_font = get_medium_font(size=get_medium_text_size(), bold=True)
        painter.setFont(title_font)
        painter.setPen(QPen(QColor("#333333"), 1))
        
        title_rect = QRect(bar_x, margin, bar_width, 25)
        painter.drawText(title_rect, Qt.AlignCenter, self.title_text)
        
        # Position the bar below the title
        bar_y = title_rect.bottom() + get_spacing_medium()
        bar_rect = QRect(bar_x, bar_y, bar_width, bar_height)
        
        # Create gradient based on preset
        gradient = QLinearGradient(bar_rect.topLeft(), bar_rect.topRight())
        
        if self.preset == "calculator":
            gradient.setColorAt(0, self.gradient_colors[0])    # Green
            gradient.setColorAt(0.35, self.gradient_colors[1]) # Yellow
            gradient.setColorAt(1, self.gradient_colors[2])    # Red
            
        elif self.preset == "regen_ag":
            gradient.setColorAt(0, self.gradient_colors[0])    # Green
            gradient.setColorAt(0.6, self.gradient_colors[1])  # Yellow
            gradient.setColorAt(1, self.gradient_colors[2])    # Red
        
        painter.fillRect(bar_rect, gradient)
        painter.setPen(QPen(QColor("#CCCCCC"), 1))
        painter.drawRect(bar_rect)
        
        # Draw ticks and labels
        self._draw_ticks_and_labels(painter, bar_x, bar_y, bar_width, bar_height)
        
        # Draw marker and text if we have a valid value
        if self.current_value > 0:
            self._draw_marker_and_text(painter, bar_x, bar_y, bar_width, bar_height)

    def _draw_ticks_and_labels(self, painter, bar_x, bar_y, bar_width, bar_height):
        """Draw tick marks and labels for thresholds."""
        painter.setPen(QPen(QColor(160, 160, 160, 200), 1))
        painter.setFont(get_medium_font(size=8))
        
        # Collect all positions
        positions = [(0, str(self.min_value))]
        
        for threshold in self.thresholds:
            relative_pos = (threshold - self.min_value) / (self.max_value - self.min_value)
            positions.append((relative_pos, str(threshold)))
        
        positions.append((1.0, str(self.max_value)))
        
        # Draw all ticks and labels
        for relative_pos, label in positions:
            x_pos = bar_x + relative_pos * bar_width
            painter.drawLine(x_pos, bar_y + bar_height, x_pos, bar_y + bar_height + 3)
            painter.drawText(QRect(x_pos - 15, bar_y + bar_height + 4, 30, 12), Qt.AlignCenter, label)
    
    def _draw_marker_and_text(self, painter, bar_x, bar_y, bar_width, bar_height):
        """Draw the position marker and score level text."""
        score_level = self.get_score_level()
        score_color = self.get_score_color()
        
        # Cap the marker position
        marker_value = min(max(self.current_value, self.min_value), self.max_value)
        relative_pos = (marker_value - self.min_value) / (self.max_value - self.min_value)
        marker_x = bar_x + relative_pos * bar_width
        
        # Draw triangle marker
        triangle_width = 10
        triangle_height = 8
        
        points = [
            QPointF(marker_x, bar_y + bar_height),
            QPointF(marker_x - triangle_width/2, bar_y + bar_height + triangle_height),
            QPointF(marker_x + triangle_width/2, bar_y + bar_height + triangle_height)
        ]
        
        painter.setBrush(QBrush(QColor("#333333")))
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.drawPolygon(points)
        
        # Draw score level text using responsive font
        painter.setFont(get_medium_font(size=get_large_text_size(), bold=True))
        painter.setPen(QPen(score_color, 1))
        
        text_y = bar_y + bar_height + triangle_height + get_spacing_medium()
        text_width = 120
        
        text_x = max(bar_x, min(marker_x - text_width/2, bar_x + bar_width - text_width))
        
        level_rect = QRect(text_x, text_y, text_width, 20)
        painter.drawText(level_rect, Qt.AlignCenter, score_level)