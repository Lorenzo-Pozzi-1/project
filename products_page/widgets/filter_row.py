"""
Filter row component for the LORENZO POZZI Pesticide App.

This module defines the FilterRow widget which provides a reusable 
filter control for table filtering.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Signal
from common import REMOVE_BUTTON_STYLE, FRAME_STYLE
from common.widgets.widgets import create_button

class FilterRow(QWidget):
    """
    A filter row widget containing field selection and filter input.
    
    This widget provides a single filter criteria consisting of a field
    dropdown and a text input for the filter value.
    """
    
    filter_changed = Signal()  # Signal emitted when the filter changes
    remove_requested = Signal(object)  # Signal emitted when remove button is clicked
    
    def __init__(self, fields, field_to_column_map, parent=None):
        """
        Initialize a filter row with the given field options.
        
        Args:
            fields: List of field names to display in dropdown
            field_to_column_map: Dictionary mapping field names to actual column indices
            parent: Parent widget
        """
        super().__init__(parent)
        self.fields = fields
        self.field_to_column_map = field_to_column_map
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components with simplified structure."""
        # Single horizontal layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.setStyleSheet(FRAME_STYLE)
        
        # Field selection dropdown
        self.field_combo = QComboBox()
        self.field_combo.addItem("Select field...")
        self.field_combo.addItems(self.fields)
        self.field_combo.setMinimumWidth(150)
        self.field_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(self.field_combo)
        
        # Contains label
        contains_label = QLabel("contains:")
        layout.addWidget(contains_label)
        
        # Filter value input
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Type to filter...")
        self.value_input.textChanged.connect(self.on_filter_changed)
        layout.addWidget(self.value_input)
        
        # Remove button
        self.remove_button = create_button(style='remove', callback=self.request_remove)
        self.remove_button.setFixedSize(24, 24)
        self.remove_button.setToolTip("Remove this filter")
        layout.addWidget(self.remove_button)
    
    def on_filter_changed(self):
        """Handle changes to the filter criteria."""
        self.filter_changed.emit()
    
    def request_remove(self):
        """Request removal of this filter row."""
        self.remove_requested.emit(self)
    
    def get_filter_criteria(self):
        """
        Get the current filter criteria as a tuple.
        
        Returns:
            tuple: (column_index, filter_text) or None if no valid field selected
        """
        field_index = self.field_combo.currentIndex()
        selected_field = self.field_combo.currentText()
        filter_text = self.value_input.text().strip().lower()
        
        # Ignore if "Select field..." is chosen (index 0)
        if field_index > 0:
            # Look up the actual column index from the field name
            column_index = self.field_to_column_map.get(selected_field)
            if column_index is not None:
                return (column_index, filter_text)
        
        return None