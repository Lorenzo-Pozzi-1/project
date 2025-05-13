"""
EIQ UI Components for the LORENZO POZZI Pesticide App.

This module provides UI components for EIQ calculations and display.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QFrame, QScrollArea, QTableWidgetItem
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush
from common.styles import get_subtitle_font, get_body_font, EIQ_LOW_COLOR, EIQ_MEDIUM_COLOR, EIQ_HIGH_COLOR
from common.widgets import ScoreBar
from math_module.eiq_calculations import format_eiq_result, get_impact_category

LOW_THRESHOLD = 33.3
HIGH_THRESHOLD = 66.6

def get_eiq_color(eiq_value, low_threshold=LOW_THRESHOLD, high_threshold=HIGH_THRESHOLD):
    """Get color for EIQ value based on thresholds."""
    if eiq_value < low_threshold:
        return EIQ_LOW_COLOR
    elif eiq_value < high_threshold:
        return EIQ_MEDIUM_COLOR
    else:
        return EIQ_HIGH_COLOR

class ProductSearchField(QWidget):
    """A custom search field with suggestions displayed underneath."""
    
    # Signal emitted when a product is selected
    product_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_items = []  # All available products
        self.filtered_items = []  # Filtered products based on search
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Search field
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Type to search products...")
        self.search_field.setFont(get_body_font())
        self.search_field.textChanged.connect(self.update_suggestions)
        
        # Add focus events to show/hide suggestions
        self.search_field.focusInEvent = self.on_focus_in
        self.search_field.focusOutEvent = self.on_focus_out
        
        layout.addWidget(self.search_field)
        
        # Suggestions container
        self.suggestions_container = QFrame()
        self.suggestions_container.setFrameStyle(QFrame.StyledPanel)
        self.suggestions_container.setStyleSheet("""
            QFrame {
                border: 1px solid #CCCCCC;
                border-top: none;
                background-color: white;
            }
        """)
        
        # Scroll area for suggestions to handle large lists
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Suggestions list
        self.suggestions_list = QListWidget()
        self.suggestions_list.setFrameStyle(QFrame.NoFrame)
        self.suggestions_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.suggestions_list.setStyleSheet("""
            QListWidget {
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #F5F5F5;
            }
            QListWidget::item:selected {
                background-color: #E0E0E0;
            }
        """)
        self.suggestions_list.itemClicked.connect(self.select_suggestion)
        scroll_area.setWidget(self.suggestions_list)
        
        # Add scroll area to suggestions container
        suggestions_layout = QVBoxLayout(self.suggestions_container)
        suggestions_layout.setContentsMargins(0, 0, 0, 0)
        suggestions_layout.addWidget(scroll_area)
        
        # Add suggestions container to main layout
        layout.addWidget(self.suggestions_container)
        
        # Initially hide suggestions
        self.suggestions_container.setVisible(False)
    
    def on_focus_in(self, event):
        self.handle_focus(event, is_focused=True)

    def on_focus_out(self, event):
        self.handle_focus(event, is_focused=False)

    def handle_focus(self, event, is_focused):
        """Handle focus in/out events."""
        if is_focused:
            QLineEdit.focusInEvent(self.search_field, event)
            if not self.search_field.text():
                self.filtered_items = self.all_items.copy()
                self.update_suggestions(self.search_field.text())
        else:
            QLineEdit.focusOutEvent(self.search_field, event)
            self.suggestions_container.setVisible(False)
    
    def update_suggestions(self, text):
        """Update suggestions based on input text."""
        # Clear selection when search text changes
        self.suggestions_list.clearSelection()
        
        if not text:
            # Show all items when text is cleared
            self.filtered_items = self.all_items.copy()
        else:
            # Filter items based on search text
            self.filtered_items = [
                item for item in self.all_items 
                if text.lower() in item.lower()
            ]
        
        # Update suggestions list
        self.suggestions_list.clear()
        self.suggestions_list.addItems(self.filtered_items)
        
        # Show suggestions if there are any matches
        self.update_suggestions_visibility()
    
    def update_suggestions_visibility(self):
        """Show or hide the suggestions container based on available items."""
        has_suggestions = len(self.filtered_items) > 0
        self.suggestions_container.setVisible(has_suggestions)
        if has_suggestions:
            item_height = self.suggestions_list.sizeHintForRow(0)
            num_visible_items = min(8, len(self.filtered_items))
            self.suggestions_list.setFixedHeight(item_height * num_visible_items + 4)
    
    def select_suggestion(self, item):
        """Handle selection of a suggestion."""
        selected_text = item.text()
        self.search_field.setText(selected_text)
        self.suggestions_container.setVisible(False)
        self.product_selected.emit(selected_text)
    
    def set_items(self, items):
        """Set the full list of available items."""
        self.all_items = items
        self.update_suggestions(self.search_field.text())
    
    def clear(self):
        """Clear the search field and hide suggestions."""
        self.search_field.clear()
        self.suggestions_container.setVisible(False)

class EiqResultDisplay(QWidget):
    """A widget for displaying EIQ results with score bar and rating."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignCenter)
        
        # Results title
        results_title = QLabel("EIQ Results")
        results_title.setFont(get_subtitle_font())
        layout.addWidget(results_title)
        
        # Field EIQ result layout
        field_eiq_layout = QHBoxLayout()
        field_eiq_label = QLabel("Field EIQ:")
        field_eiq_label.setFont(get_subtitle_font(bold=True))

        # Labels for both ha and acre values
        self.field_eiq_result_ha = QLabel("-- /ha")
        self.field_eiq_result_ha.setFont(get_subtitle_font(bold=True))
        
        field_eiq_layout.addWidget(field_eiq_label)
        field_eiq_layout.addWidget(self.field_eiq_result_ha)
        field_eiq_layout.addStretch(1)
        
        layout.addLayout(field_eiq_layout)
        
        # Create score bar with default thresholds and labels
        self.score_bar = ScoreBar(
            thresholds=[LOW_THRESHOLD, HIGH_THRESHOLD],
            labels=["Low", "Medium", "High", "EXTREME"],
            title_text="Field EIQ score:"
        )
        layout.addWidget(self.score_bar)
    
    def update_result(self, field_eiq):
        """Update the EIQ result display with the calculated value."""
        self.set_field_eiq_text(field_eiq)
        
        # Update score bar
        rating, _ = get_impact_category(field_eiq)
        self.score_bar.set_value(field_eiq, rating)

    def set_field_eiq_text(self, field_eiq):
        """Set the field EIQ text"""
        if field_eiq <= 0:
            self.field_eiq_result_ha.setText("-- /ha")
            self.score_bar.set_value(0, "No calculation")
            return
        
        ha_text = format_eiq_result(field_eiq)
        self.field_eiq_result_ha.setText(ha_text)

class ColorCodedEiqItem(QTableWidgetItem):
    """A table item specifically for EIQ values with automatic color coding."""
    
    def __init__(self, eiq_value, low_threshold=LOW_THRESHOLD, high_threshold=HIGH_THRESHOLD):
        """
        Initialize with EIQ value and thresholds.
        
        Args:
            eiq_value (float): The EIQ value to display
            low_threshold (float): Values below this are considered "low impact"
            high_threshold (float): Values above this are considered "high impact"
        """
        if isinstance(eiq_value, (int, float)):
            display_value = f"{eiq_value:.1f}"
        else:
            display_value = str(eiq_value)
            
        super().__init__(display_value)
        
        self.setTextAlignment(Qt.AlignCenter)
        
        # Apply color coding based on thresholds
        try:
            value_float = float(eiq_value)
            self.setBackground(QBrush(get_eiq_color(value_float, low_threshold, high_threshold)))
        except (ValueError, TypeError):
            # If value can't be converted to float, don't apply color
            pass