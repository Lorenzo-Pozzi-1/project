"""
ScoreBar widget for the McCain Pesticides App

This module provides a customizable score bar widget that displays values
on a gradient with configurable thresholds and labels.
"""

from PySide6.QtCore import Qt, QRect, QPointF
from PySide6.QtGui import QColor, QBrush, QPainter, QPen, QLinearGradient
from PySide6.QtWidgets import QWidget, QVBoxLayout
from common.styles import *

class ScoreBar(QWidget):
    """A color gradient bar for displaying scores with customizable thresholds and labels."""
    
    def __init__(self, parent=None, thresholds=None, labels=None, 
                 min_value=0, max_value=100, title_text="Field EIQ score:"):
        """
        Initialize the scorebar widget with customizable thresholds and labels.
        
        Args:
            parent: Parent widget
            thresholds: List of threshold values that separate score categories
                        e.g., [33.3, 66.6] creates three regions: 0-33.3, 33.3-66.6, >66.6
            labels: List of labels for each category, should be len(thresholds) + 1
                    e.g., ["Low", "Medium", "High"] for the regions defined by [33.3, 66.6]
            min_value: Minimum value for the score range
            max_value: Maximum value for the score range
            title_text: Text to display as the title of the score bar
        """
        super().__init__(parent)
        
        # Set default thresholds and labels if not provided
        if thresholds is None:
            thresholds = [33.3, 66.6]
        if labels is None:
            labels = ["Low", "Medium", "High", "EXTREME"]
        
        # Ensure we have one more label than thresholds (n thresholds create n+1 regions)
        if len(labels) < len(thresholds) + 1:
            # Add generic labels if needed
            for i in range(len(labels), len(thresholds) + 1):
                labels.append(f"Level {i+1}")
        
        # Store parameters
        self.thresholds = thresholds
        self.labels = labels
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = 0
        self.label_text = ""
        self.title_text = title_text
        
        # Generate colors for each region
        self.generate_colors()
        
        # Set minimum size
        self.setMinimumSize(200, 140)
        
        # Simple layout with just margins
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        self.setLayout(layout)
    
    def generate_colors(self):
        """Generate gradient colors for regions and text based on number of thresholds."""
        # Create gradient colors for the regions
        self.region_colors = []
        self.BLACKs = []  # Initialize this list first so it always exists
        
        # Default colors for up to 3 regions (4 with extreme)
        default_colors = [
            QColor("#77DD77"),  # Pastel green
            QColor("#FFF275"),  # Pastel yellow
            QColor("#FF6961"),  # Pastel red
            QColor("#FF6961")   # Same as high for extreme
        ]
        
        # Text colors for up to 3 regions (4 with extreme)
        default_BLACKs = [
            QColor("#1E8449"),  # Dark green
            QColor("#B7950B"),  # Dark yellow
            QColor("#B03A2E"),  # Dark red
            QColor("#B03A2E")   # Same as high for extreme
        ]
        
        # Generate colors based on number of regions
        num_regions = len(self.thresholds) + 1
        
        # Use default colors if we have 4 or fewer regions
        if num_regions <= 4:
            self.region_colors = default_colors[:num_regions]
            self.BLACKs = default_BLACKs[:num_regions]
        else:
            # Generate colors along a gradient from green to red
            for i in range(num_regions):
                # Generate a color from green to red based on position
                pos = i / (num_regions - 1)
                r = int(255 * pos)
                g = int(255 * (1 - pos))
                b = 100
                self.region_colors.append(QColor(r, g, b, 180))  # Add some transparency
                
                # Generate darker text colors
                self.BLACKs.append(QColor(r * 0.7, g * 0.7, b * 0.7))
    
    def configure(self, thresholds=None, labels=None, 
                 min_value=None, max_value=None, title_text=None):
        """
        Reconfigure the score bar.
        
        Args:
            thresholds: New list of threshold values
            labels: New list of labels
            min_value: New minimum value
            max_value: New maximum value
            title_text: New title text
        """
        update_colors = False
        
        if thresholds is not None:
            self.thresholds = thresholds
            update_colors = True
            
        if labels is not None:
            self.labels = labels
            # Ensure we have one more label than thresholds
            if len(self.labels) < len(self.thresholds) + 1:
                for i in range(len(self.labels), len(self.thresholds) + 1):
                    self.labels.append(f"Level {i+1}")
        
        if min_value is not None:
            self.min_value = min_value
            
        if max_value is not None:
            self.max_value = max_value
            
        if title_text is not None:
            self.title_text = title_text
            
        if update_colors:
            self.generate_colors()
            
        # Update the display
        self.update()
    
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
        # Handle extreme case
        if self.current_value > self.max_value:
            return self.labels[-1]  # Return the last label for values beyond max
        
        # Find which region the value falls into
        for i, threshold in enumerate(self.thresholds):
            if self.current_value < threshold:
                return self.labels[i]
        
        # If we're past all thresholds but not beyond max_value
        return self.labels[-1]  # Last label

    def get_score_color(self):
        """Get the color that matches the gradient at the current value position."""
        # Cap the value within our range for color calculation
        clamped_value = min(max(self.current_value, self.min_value), self.max_value)
        
        # Calculate relative position (0.0 to 1.0)
        relative_pos = (clamped_value - self.min_value) / (self.max_value - self.min_value)
        
        # Define the same gradient colors used in paintEvent
        low_color = QColor("#77DD77")    # Pastel green
        medium_color = QColor("#FFF275") # Pastel yellow  
        high_color = QColor("#FF6961")   # Pastel red
        
        # Interpolate color based on position
        if relative_pos <= 0.5:
            # Interpolate between low and medium (0.0 to 0.5)
            t = relative_pos * 2  # Scale to 0.0-1.0
            r = int(low_color.red() + t * (medium_color.red() - low_color.red()))
            g = int(low_color.green() + t * (medium_color.green() - low_color.green()))
            b = int(low_color.blue() + t * (medium_color.blue() - low_color.blue()))
        else:
            # Interpolate between medium and high (0.5 to 1.0)
            t = (relative_pos - 0.5) * 2  # Scale to 0.0-1.0
            r = int(medium_color.red() + t * (high_color.red() - medium_color.red()))
            g = int(medium_color.green() + t * (high_color.green() - medium_color.green()))
            b = int(medium_color.blue() + t * (high_color.blue() - medium_color.blue()))
        
        # Return a more saturated but darker version for good readability
        # First increase saturation by boosting the dominant color component
        max_component = max(r, g, b)
        if max_component > 0:
            # Scale up for saturation
            scale_factor = 255 / max_component
            r = min(255, int(r * scale_factor))
            g = min(255, int(g * scale_factor))  
            b = min(255, int(b * scale_factor))
        
        # Then darken for readability while maintaining saturation
        darkness_factor = 0.7  # Adjust this value (0.5-0.8) to control darkness
        r = int(r * darkness_factor)
        g = int(g * darkness_factor)
        b = int(b * darkness_factor)
        
        return QColor(r, g, b)
    
    def paintEvent(self, event):
        """Paint the gradient bar and all other elements."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate dimensions
        rect = self.rect()
        margin = 10
        bar_width = rect.width() - (margin * 2)
        bar_height = 20
        bar_x = rect.x() + margin
        
        # Draw the title
        title_font = get_medium_font(size=14, bold=True)
        painter.setFont(title_font)
        painter.setPen(QPen(QColor("#333333"), 1))
        
        title_rect = QRect(bar_x, margin, bar_width, 25)
        painter.drawText(title_rect, Qt.AlignCenter, self.title_text)
        
        # Position the bar below the title
        bar_y = title_rect.bottom() + 15
        bar_rect = QRect(bar_x, bar_y, bar_width, bar_height)
        
        # Create and draw gradient bar
        gradient = QLinearGradient(bar_rect.topLeft(), bar_rect.topRight())
        
        # Default colors for the smooth gradient
        low_color = QColor("#77DD77")    # Pastel green
        medium_color = QColor("#FFF275") # Pastel yellow
        high_color = QColor("#FF6961")   # Pastel red
        
        # Create smooth gradient transitions regardless of number of thresholds
        gradient.setColorAt(0.0, low_color)
        gradient.setColorAt(0.5, medium_color)
        gradient.setColorAt(1.0, high_color)
        
        painter.fillRect(bar_rect, gradient)
        painter.setPen(QPen(QColor("#CCCCCC"), 1))  # Light gray border
        painter.drawRect(bar_rect)
        
        # Draw ticks and labels
        self._draw_ticks_and_labels(painter, bar_x, bar_y, bar_width, bar_height)
        
        # Draw marker and text if we have a valid value
        if self.current_value > 0:
            self._draw_marker_and_text(painter, bar_x, bar_y, bar_width, bar_height)
    
    def _draw_ticks_and_labels(self, painter, bar_x, bar_y, bar_width, bar_height):
        """Draw tick marks and labels for thresholds."""
        painter.setPen(QPen(QColor(160, 160, 160, 120), 1))
        painter.setFont(get_medium_font(size=8))
        
        # Always draw tick and label at minimum value
        positions = [(0, str(self.min_value))]
        
        # Add ticks and labels for each threshold
        for threshold in self.thresholds:
            relative_pos = (threshold - self.min_value) / (self.max_value - self.min_value)
            positions.append((relative_pos, str(threshold)))
        
        # Always draw tick and label at maximum value
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
        
        # Cap the marker position at the end of the bar
        marker_value = min(max(self.current_value, self.min_value), self.max_value)
        relative_pos = (marker_value - self.min_value) / (self.max_value - self.min_value)
        marker_x = bar_x + relative_pos * bar_width
        
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
        
        # Draw the score level text
        painter.setFont(get_medium_font(size=15, bold=True))
        painter.setPen(QPen(score_color, 1))
        
        text_y = bar_y + bar_height + triangle_height + 5
        text_width = 120
        
        # Keep text within widget bounds
        text_x = max(bar_x, min(marker_x - text_width/2, bar_x + bar_width - text_width))
        
        level_rect = QRect(text_x, text_y, text_width, 20)
        painter.drawText(level_rect, Qt.AlignCenter, score_level)