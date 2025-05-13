"""
Common custom widgets for the LORENZO POZZI Pesticide App

This module provides reusable custom widgets used throughout the application.
"""

from PySide6.QtCore import Qt, Signal, QRect, QPointF
from PySide6.QtGui import QColor, QBrush, QPainter, QPen, QLinearGradient
from PySide6.QtWidgets import QPushButton, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QSizePolicy, QWidget, QTableWidgetItem, QSpacerItem
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


class ColorCodedTableItem(QTableWidgetItem):
    """
    A table item that can be color-coded based on its value.
    
    Useful for field EIQ scores and other numeric values that have thresholds.
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
        
        # Default colors for up to 3 regions (4 with extreme)
        default_colors = [
            QColor("#77DD77"),  # Pastel green
            QColor("#FFF275"),  # Pastel yellow
            QColor("#FF6961"),  # Pastel red
            QColor("#FF6961")   # Same as high for extreme
        ]
        
        # Text colors for up to 3 regions (4 with extreme)
        default_text_colors = [
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
            self.text_colors = default_text_colors[:num_regions]
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
                self.text_colors.append(QColor(r * 0.7, g * 0.7, b * 0.7))
    
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
        """Get the color for the current score level."""
        # Handle extreme case
        if self.current_value > self.max_value:
            return self.text_colors[-1]  # Use the last text color for values beyond max
        
        # Find which region the value falls into - using the same logic as get_score_level()
        for i, threshold in enumerate(self.thresholds):
            if self.current_value < threshold:
                return self.text_colors[i]
        
        # If we're past all thresholds but not beyond max_value
        return self.text_colors[-1]  # Last text color
    
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
        title_font = get_body_font(size=14, bold=True)
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
        painter.setFont(get_body_font(size=8))
        
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
        painter.setFont(get_body_font(size=15, bold=True))
        painter.setPen(QPen(score_color, 1))
        
        text_y = bar_y + bar_height + triangle_height + 5
        text_width = 120
        
        # Keep text within widget bounds
        text_x = max(bar_x, min(marker_x - text_width/2, bar_x + bar_width - text_width))
        
        level_rect = QRect(text_x, text_y, text_width, 20)
        painter.drawText(level_rect, Qt.AlignCenter, score_level)