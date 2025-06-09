"""
Filter components for the LORENZO POZZI Pesticide App.

This module defines filter widgets that display as chips for a more modern
and compact filtering interface.
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QComboBox, 
                               QLabel, QLineEdit, QPushButton, QFrame)
from PySide6.QtCore import Signal, Qt
from common import get_medium_font, get_subtitle_font, create_button, FILTER_CHIP_STYLE


class FilterChip(QFrame):
    """
    A chip-style filter widget with field selection and value input.
    
    This widget displays as a rounded chip containing a field dropdown,
    value input, and remove button.
    """
    
    filter_changed = Signal()  # Signal emitted when the filter changes
    remove_requested = Signal(object)  # Signal emitted when remove button is clicked
    
    def __init__(self, fields, field_to_column_map, parent=None):
        """
        Initialize a filter chip with the given field options.
        
        Args:
            fields: List of field names to display in dropdown
            field_to_column_map: Dictionary mapping field names to actual column indices
            parent: Parent widget
        """
        super().__init__(parent)
        self.fields = fields
        self.field_to_column_map = field_to_column_map
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout for the chip
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)
        
        # Field selection dropdown
        self.field_combo = QComboBox()
        self.field_combo.addItem("Select field...")
        self.field_combo.setFont(get_medium_font())
        self.field_combo.addItems(self.fields)
        self.field_combo.setMinimumWidth(120)
        self.field_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(self.field_combo)
        
        # Contains label
        contains_label = QLabel(":")
        contains_label.setFont(get_medium_font())
        layout.addWidget(contains_label)
        
        # Filter value input
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("filter value")
        self.value_input.setFont(get_medium_font())
        self.value_input.setMinimumWidth(100)
        self.value_input.textChanged.connect(self.on_filter_changed)
        layout.addWidget(self.value_input)
        
        # Remove button (small X)
        self.remove_button = QPushButton("×")
        self.remove_button.setFixedSize(20, 20)
        self.remove_button.clicked.connect(self.request_remove)
        self.remove_button.setToolTip("Remove this filter")
        layout.addWidget(self.remove_button)
    
    def setup_style(self):
        """Set up the chip styling."""
        self.setStyleSheet(FILTER_CHIP_STYLE)
    
    def on_filter_changed(self):
        """Handle changes to the filter criteria."""
        self.filter_changed.emit()
    
    def request_remove(self):
        """Request removal of this filter chip."""
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


class FiltersRow(QWidget):
    """
    A container widget that manages multiple FilterChip instances.
    
    This widget displays filter chips in a compact grid layout with
    a maximum of 4 filters.
    """
    
    filters_changed = Signal()  # Signal emitted when any filter changes
    MAX_FILTERS = 4  # Maximum number of filter chips allowed
    
    def __init__(self, parent=None):
        """Initialize the filter container."""
        super().__init__(parent)
        self.filter_chips = []
        self.visible_columns = []
        self.field_to_column_map = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        
        # Header layout for title and add button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Filter title
        selection_title = QLabel("Filter Products")
        selection_title.setFont(get_subtitle_font())
        header_layout.addWidget(selection_title)
        
        # Add filter button
        self.add_filter_button = create_button(
            text="Add Filter", 
            style='white', 
            callback=self.add_filter_chip
        )
        header_layout.addWidget(self.add_filter_button)
        header_layout.addStretch()  # Push items to the left
        
        # Add the header layout to main layout
        main_layout.addLayout(header_layout)
        
        # Chips container - using a flowing layout
        self.chips_container = QWidget()
        self.chips_layout = QHBoxLayout(self.chips_container)
        self.chips_layout.setContentsMargins(0, 0, 0, 0)
        self.chips_layout.setSpacing(8)
        self.chips_layout.setAlignment(Qt.AlignLeft)
        
        # Add chips container to main layout
        main_layout.addWidget(self.chips_container)
        
        # Set a reasonable height for the container
        self.setMaximumHeight(120)
    
    def set_filter_data(self, visible_columns, field_to_column_map):
        """
        Set the filter data for populating filter chips.
        
        Args:
            visible_columns: List of column names visible in the table
            field_to_column_map: Map of column names to table column indices
        """
        self.visible_columns = visible_columns
        self.field_to_column_map = field_to_column_map
        
        # Add initial filter chip if none exist
        if not self.filter_chips and self.visible_columns:
            self.add_filter_chip()
    
    def add_filter_chip(self):
        """Add a new filter chip."""
        if not self.visible_columns or len(self.filter_chips) >= self.MAX_FILTERS:
            return
            
        filter_chip = FilterChip(self.visible_columns, self.field_to_column_map, self)
        filter_chip.filter_changed.connect(self.on_filter_changed)
        filter_chip.remove_requested.connect(self.remove_filter_chip)
        
        self.chips_layout.addWidget(filter_chip)
        self.filter_chips.append(filter_chip)
        
        # Update UI state
        self._update_ui_state()
    
    def remove_filter_chip(self, filter_chip):
        """Remove a filter chip."""
        if filter_chip in self.filter_chips:
            self.chips_layout.removeWidget(filter_chip)
            self.filter_chips.remove(filter_chip)
            filter_chip.deleteLater()
            
            # Update UI state
            self._update_ui_state()
            self.on_filter_changed()
    
    def _update_ui_state(self):
        """Update UI state based on current number of chips."""
        # Show/hide remove buttons based on number of chips
        for chip in self.filter_chips:
            chip.remove_button.setVisible(len(self.filter_chips) > 1)
        
        # Enable/disable add button based on maximum filters
        self.add_filter_button.setEnabled(len(self.filter_chips) < self.MAX_FILTERS)
        
        # Update add button text to show remaining slots
        remaining = self.MAX_FILTERS - len(self.filter_chips)
        if remaining == 0:
            self.add_filter_button.setText("Max filters reached")
        else:
            self.add_filter_button.setText(f"Add Filter")
    
    def on_filter_changed(self):
        """Handle changes to any filter criteria."""
        self.filters_changed.emit()
    
    def get_filter_criteria(self):
        """
        Get all valid filter criteria.
        
        Returns:
            list: List of (column_index, filter_text) tuples
        """
        filters = []
        for filter_chip in self.filter_chips:
            criteria = filter_chip.get_filter_criteria()
            if criteria and criteria[1]:  # Only if column and non-empty text
                filters.append(criteria)
        return filters
    
    def reset_filters(self):
        """Reset all filter chips."""
        # Clear existing filter chips
        while self.filter_chips:
            chip = self.filter_chips.pop()
            self.chips_layout.removeWidget(chip)
            chip.deleteLater()
        
        # Add a single empty filter chip if columns exist
        if self.visible_columns:
            self.add_filter_chip()
        