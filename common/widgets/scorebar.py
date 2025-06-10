"""
ScoreBar widget for the McCain Pesticides App

This module provides a customizable score bar widget that displays values
on a gradient with preset configurations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
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


@dataclass
class ScenarioData:
    """Data class for scenario information."""
    name: str
    value: float
    color: QColor = field(default_factory=lambda: QColor("#333333"))
    index: Optional[int] = None


@dataclass
class PresetConfig:
    """Configuration data for a preset."""
    title: str
    thresholds: List[float]
    labels: List[str]
    min_value: float
    max_value: float
    gradient_colors: List[QColor]
    region_colors: List[QColor]
    gradient_stops: List[float]


class ScoreBar(QWidget):
    """A color gradient bar for displaying scores with preset color schemes."""
    
    # Class constants
    MINIMUM_SIZE = (200, 140)
    BAR_HEIGHT = 20
    TRIANGLE_WIDTH = 10
    TRIANGLE_HEIGHT = 8
    MIN_LABEL_WIDTH = 80
    
    # Preset configurations
    PRESETS = {
        "calculator": PresetConfig(
            title="Field Use EIQ:",
            thresholds=[EIQ_LOW_THRESHOLD, EIQ_MEDIUM_THRESHOLD, EIQ_HIGH_THRESHOLD],
            labels=["Low", "Medium", "High", "Very High"],
            min_value=0,
            max_value=EIQ_HIGH_THRESHOLD,
            gradient_colors=[QColor(34, 197, 94), QColor(255, 235, 59), QColor(239, 68, 68)],
            region_colors=[QColor(GREEN), QColor(YELLOW_PRESSED), QColor(255, 152, 0), QColor(239, 68, 68)],
            gradient_stops=[0, 0.35, 1]
        ),
        "regen_ag": PresetConfig(
            title="RegenAg framework class:",
            thresholds=[LEADING, ADVANCED, ENGAGED, ONBOARDING],
            labels=["Leading", "Advanced", "Engaged", "Onboarding", "Out of range"],
            min_value=0,
            max_value=2500,
            gradient_colors=[QColor(34, 197, 94), QColor(255, 235, 59), QColor(239, 68, 68)],
            region_colors=[QColor(GREEN), QColor(102, 204, 102), QColor(153, 221, 68), QColor(YELLOW_PRESSED), QColor(239, 68, 68)],
            gradient_stops=[0, 0.6, 1]
        )
    }

    def __init__(self, parent=None, preset="calculator"):
        """
        Initialize the scorebar widget with a preset configuration.
        
        Args:
            parent: Parent widget
            preset: "calculator" or "regen_ag" for different configurations
            
        Raises:
            ValueError: If preset is not recognized
        """
        super().__init__(parent)
        
        if preset not in self.PRESETS:
            raise ValueError(f"Unknown preset: {preset}. Available presets: {list(self.PRESETS.keys())}")
        
        self.config = self.PRESETS[preset]
        self.current_value = 0
        self.label_text = ""
        self.scenarios: List[ScenarioData] = []
        self.multi_scenario_mode = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI layout and sizing."""
        self.setMinimumSize(*self.MINIMUM_SIZE)
        
        layout = QVBoxLayout(self)
        margin = get_margin_small()
        layout.setContentsMargins(margin, margin//2, margin, margin//2)
        self.setLayout(layout)
    
    def set_value(self, value: float, label_text: str = ""):
        """
        Set the value and optional text label for the bar (single-value mode).
        
        Args:
            value: Value to display on the bar
            label_text: Text to display below the bar
        """
        self.current_value = float(value)
        self.label_text = label_text
        self.multi_scenario_mode = False
        self.scenarios.clear()
        self.update()
        
    def set_scenarios(self, scenarios_data: List[Dict]):
        """
        Set multiple scenarios for comparison (multi-scenario mode).
        
        Args:
            scenarios_data: List of dictionaries with keys:
                - 'name': Scenario name (str)
                - 'value': Scenario value (float)
                - 'color': Optional color (QColor), defaults to black
                - 'index': Optional index (int)
        """
        self.scenarios = [
            ScenarioData(
                name=scenario.get('name', 'Unnamed'),
                value=float(scenario.get('value', 0)),
                color=scenario.get('color', QColor("#333333")),
                index=scenario.get('index')
            )
            for scenario in scenarios_data
        ]
        
        self.multi_scenario_mode = True
        self.current_value = 0
        self.label_text = ""
        self.update()
    
    def get_score_level(self, value: Optional[float] = None) -> str:
        """
        Get the score level based on a value.
        
        Args:
            value: Value to evaluate. If None, uses current_value.
            
        Returns:
            Score level string
        """
        if value is None:
            value = self.current_value
            
        if value > self.config.max_value:
            return self.config.labels[-1]
        
        for i, threshold in enumerate(self.config.thresholds):
            if value < threshold:
                return self.config.labels[i]
        
        return self.config.labels[-1]

    def get_score_color(self, value: Optional[float] = None) -> QColor:
        """
        Get the color that matches a value position.
        
        Args:
            value: Value to evaluate. If None, uses current_value.
            
        Returns:
            QColor for the value
        """
        if value is None:
            value = self.current_value
            
        clamped_value = self._clamp_value(value)
        
        # Find which region we're in
        region_index = 0
        for i, threshold in enumerate(self.config.thresholds):
            if clamped_value >= threshold:
                region_index = i + 1
            else:
                break
        
        return self.config.region_colors[min(region_index, len(self.config.region_colors) - 1)]
    
    def _clamp_value(self, value: float) -> float:
        """Clamp a value within the valid range."""
        return min(max(value, self.config.min_value), self.config.max_value)
    
    def _get_relative_position(self, value: float) -> float:
        """Get the relative position (0-1) of a value on the bar."""
        clamped_value = self._clamp_value(value)
        return (clamped_value - self.config.min_value) / (self.config.max_value - self.config.min_value)
    
    def _get_bar_geometry(self) -> Tuple[int, int, int, int]:
        """Get the bar geometry (x, y, width, height)."""
        rect = self.rect()
        margin = get_margin_small()
        bar_width = rect.width() - (margin * 2)
        bar_x = rect.x() + margin
        bar_y = margin + 25 + get_spacing_medium()  # Below title
        return bar_x, bar_y, bar_width, self.BAR_HEIGHT
    
    def paintEvent(self, event):
        """Paint the gradient bar and all other elements."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        bar_x, bar_y, bar_width, bar_height = self._get_bar_geometry()
        
        self._draw_title(painter, bar_x, bar_width)
        self._draw_section_labels(painter, bar_x, bar_y, bar_width, bar_height)
        self._draw_gradient_bar(painter, bar_x, bar_y, bar_width, bar_height)
        self._draw_ticks_and_labels(painter, bar_x, bar_y, bar_width, bar_height)
        
        if self.multi_scenario_mode and self.scenarios:
            self._draw_multiple_markers_and_text(painter, bar_x, bar_y, bar_width, bar_height)
        elif self.current_value > 0:
            self._draw_single_marker_and_text(painter, bar_x, bar_y, bar_width, bar_height)
    
    def _draw_title(self, painter: QPainter, bar_x: int, bar_width: int):
        """Draw the title text."""
        title_font = get_medium_font(size=get_medium_text_size(), bold=True)
        painter.setFont(title_font)
        painter.setPen(QPen(QColor("#333333"), 1))
        
        margin = get_margin_small()
        title_rect = QRect(bar_x, margin, bar_width, 25)
        painter.drawText(title_rect, Qt.AlignCenter, self.config.title)
    
    def _draw_gradient_bar(self, painter: QPainter, bar_x: int, bar_y: int, bar_width: int, bar_height: int):
        """Draw the gradient bar."""
        bar_rect = QRect(bar_x, bar_y, bar_width, bar_height)
        
        gradient = QLinearGradient(bar_rect.topLeft(), bar_rect.topRight())
        for i, (stop, color) in enumerate(zip(self.config.gradient_stops, self.config.gradient_colors)):
            gradient.setColorAt(stop, color)
        
        painter.fillRect(bar_rect, gradient)
        painter.setPen(QPen(QColor("#CCCCCC"), 1))
        painter.drawRect(bar_rect)

    def _draw_ticks_and_labels(self, painter: QPainter, bar_x: int, bar_y: int, bar_width: int, bar_height: int):
        """Draw tick marks and labels for thresholds."""
        painter.setPen(QPen(QColor(160, 160, 160, 200), 1))
        painter.setFont(get_medium_font(size=8))
        
        # Collect all tick positions
        tick_positions = [
            (0, str(int(self.config.min_value))),
            *[(self._get_relative_position(threshold), str(int(threshold))) 
              for threshold in self.config.thresholds],
            (1.0, str(int(self.config.max_value)))
        ]
        
        # Draw ticks and labels
        for relative_pos, label in tick_positions:
            x_pos = bar_x + relative_pos * bar_width
            painter.drawLine(x_pos, bar_y + bar_height, x_pos, bar_y + bar_height + 3)
            painter.drawText(QRect(x_pos - 15, bar_y + bar_height + 4, 30, 18), Qt.AlignCenter, label)
    
    def _draw_section_labels(self, painter: QPainter, bar_x: int, bar_y: int, bar_width: int, bar_height: int):
        """Draw section labels centered above their corresponding regions for regen_ag preset."""
        if self.config.title != "RegenAg framework class:":
            return
        
        painter.setFont(get_medium_font(size=get_medium_text_size(), bold=True))
        painter.setPen(QPen(QColor("#333333"), 1))
        
        # Define section ranges for regen_ag preset
        sections = [
            ("Leading", 0, LEADING),
            ("Advanced", LEADING, ADVANCED),
            ("Engaged", ADVANCED, ENGAGED),
            ("Onboarding", ENGAGED, ONBOARDING)
        ]
        
        label_y = bar_y - get_spacing_medium() - 10  # Position above the bar
        
        for label, start_val, end_val in sections:
            # Calculate relative positions
            start_pos = self._get_relative_position(start_val)
            end_pos = self._get_relative_position(end_val)
            
            # Calculate center position for the label
            center_pos = (start_pos + end_pos) / 2
            label_x = bar_x + center_pos * bar_width
            
            # Draw the label centered
            text_width = 100
            label_rect = QRect(int(label_x - text_width/2), label_y, text_width, 20)
            painter.drawText(label_rect, Qt.AlignCenter, label)
    
    def _draw_single_marker_and_text(self, painter: QPainter, bar_x: int, bar_y: int, bar_width: int, bar_height: int):
        """Draw the position marker and score level text for single value mode."""
        relative_pos = self._get_relative_position(self.current_value)
        marker_x = bar_x + relative_pos * bar_width
        
        self._draw_triangle_marker(painter, marker_x, bar_y + bar_height, QColor("#333333"))
        
        # Draw score level text
        score_level = self.get_score_level()
        score_color = self.get_score_color()
        
        painter.setFont(get_medium_font(size=get_large_text_size(), bold=True))
        painter.setPen(QPen(score_color, 1))
        
        text_y = bar_y + bar_height + self.TRIANGLE_HEIGHT + get_spacing_medium()
        text_width = 120
        text_x = max(bar_x, min(marker_x - text_width/2, bar_x + bar_width - text_width))
        
        level_rect = QRect(int(text_x), text_y, text_width, 24)
        painter.drawText(level_rect, Qt.AlignCenter, score_level)
    
    def _draw_multiple_markers_and_text(self, painter: QPainter, bar_x: int, bar_y: int, bar_width: int, bar_height: int):
        """Draw multiple scenario markers and their labels."""
        # Sort scenarios by value for better label placement
        sorted_scenarios = sorted(self.scenarios, key=lambda s: s.value)
        
        # Draw triangle markers
        marker_positions = []
        for scenario in sorted_scenarios:
            relative_pos = self._get_relative_position(scenario.value)
            marker_x = bar_x + relative_pos * bar_width
            marker_positions.append((marker_x, scenario))
            
            self._draw_triangle_marker(painter, marker_x, bar_y + bar_height, scenario.color)
        
        # Draw scenario labels
        self._draw_scenario_labels(painter, marker_positions, bar_x, bar_y, bar_width, bar_height)
    
    def _draw_triangle_marker(self, painter: QPainter, marker_x: float, marker_y: int, color: QColor):
        """Draw a triangle marker at the specified position."""
        points = [
            QPointF(marker_x, marker_y),
            QPointF(marker_x - self.TRIANGLE_WIDTH/2, marker_y + self.TRIANGLE_HEIGHT),
            QPointF(marker_x + self.TRIANGLE_WIDTH/2, marker_y + self.TRIANGLE_HEIGHT)
        ]
        
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.drawPolygon(points)
    
    def _draw_scenario_labels(self, painter: QPainter, marker_positions: List[Tuple[float, ScenarioData]], 
                            bar_x: int, bar_y: int, bar_width: int, bar_height: int):
        """Draw scenario labels with overlap prevention."""
        if not marker_positions:
            return
        
        painter.setFont(get_medium_font(size=get_medium_text_size(), bold=True))
        painter.setPen(QPen(QColor("#333333"), 1))
        
        text_y = bar_y + bar_height + self.TRIANGLE_HEIGHT + get_spacing_medium()
        label_height = 20  # Increased from 16 to accommodate descenders
        
        # Calculate non-overlapping label positions
        label_positions = self._calculate_label_positions(marker_positions, bar_x, bar_width)
        # Draw all labels
        for label_x, scenario in label_positions:
            # Draw scenario index
            index_text = str(scenario.index) if scenario.index is not None else "?"
            index_rect = QRect(int(label_x), text_y, self.MIN_LABEL_WIDTH, label_height)
            painter.drawText(index_rect, Qt.AlignCenter, index_text)
            
            # Draw collocation (score level) below index
            collocation = self.get_score_level(scenario.value)
            collocation_rect = QRect(int(label_x), text_y + label_height, self.MIN_LABEL_WIDTH, label_height)
            painter.drawText(collocation_rect, Qt.AlignCenter, collocation)
    
    def _calculate_label_positions(self, marker_positions: List[Tuple[float, ScenarioData]], 
                                 bar_x: int, bar_width: int) -> List[Tuple[float, ScenarioData]]:
        """Calculate non-overlapping label positions."""
        label_positions = []
        
        for marker_x, scenario in marker_positions:
            # Start with centered position
            preferred_x = marker_x - self.MIN_LABEL_WIDTH / 2
            label_x = max(bar_x, min(preferred_x, bar_x + bar_width - self.MIN_LABEL_WIDTH))
            
            # Resolve overlaps
            while any(abs(label_x - existing_x) < self.MIN_LABEL_WIDTH 
                     for existing_x, _ in label_positions):
                label_x += self.MIN_LABEL_WIDTH * 0.1
                
                # If we've gone too far right, try going left
                if label_x + self.MIN_LABEL_WIDTH > bar_x + bar_width:
                    label_x = max(bar_x, preferred_x - self.MIN_LABEL_WIDTH * 0.3)
                    break
            
            label_positions.append((label_x, scenario))
        
        return label_positions