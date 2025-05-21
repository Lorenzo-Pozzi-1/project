"""
Filter row components for the LORENZO POZZI Pesticide App.

This module defines the FilterRow widget which provides a reusable 
filter control for table filtering, and the FilterRowContainer which
manages multiple filter rows.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QLineEdit, QScrollArea, QFrame
from PySide6.QtCore import Signal, Qt
from common import FRAME_STYLE, get_medium_font, get_subtitle_font, create_button


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
        """Set up the UI components."""
        # Single horizontal layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Field selection dropdown
        self.field_combo = QComboBox()
        self.field_combo.addItem("Select field...")
        self.field_combo.setFont(get_medium_font())
        self.field_combo.addItems(self.fields)
        self.field_combo.setMinimumWidth(150)
        self.field_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(self.field_combo)
        
        # Contains label
        contains_label = QLabel("contains:")
        contains_label.setFont(get_medium_font())
        layout.addWidget(contains_label)
        
        # Filter value input
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Type to filter...")
        self.value_input.setFont(get_medium_font())
        self.value_input.textChanged.connect(self.on_filter_changed)
        layout.addWidget(self.value_input)
        
        # Remove button
        self.remove_button = create_button(style='remove', callback=self.request_remove)
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


class FilterRowContainer(QWidget):
    """
    A container widget that manages multiple FilterRow instances.
    
    This widget provides a scrollable area for filter rows, an add button,
    and handles the coordination between multiple filter rows.
    """
    
    filters_changed = Signal()  # Signal emitted when any filter changes
    
    def __init__(self, parent=None):
        """Initialize the filter row container."""
        super().__init__(parent)
        self.filter_rows = []
        self.visible_columns = []
        self.field_to_column_map = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # Filter title
        selection_title = QLabel("Filter Products")
        selection_title.setFont(get_subtitle_font())
        main_layout.addWidget(selection_title)
        
        # Filter rows area
        self.filter_rows_container = QWidget()
        self.filter_rows_container.setStyleSheet("background-color: white;")
        self.filter_rows_layout = QHBoxLayout(self.filter_rows_container)
        self.filter_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_rows_layout.setAlignment(Qt.AlignLeft)
        
        # Scrollable area for filter rows
        filter_scroll = QScrollArea()
        filter_scroll.setStyleSheet("QScrollArea { background-color: white; border: none; }")
        filter_scroll.setWidgetResizable(True)
        filter_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        filter_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        filter_scroll.setFrameShape(QFrame.NoFrame)
        filter_scroll.setWidget(self.filter_rows_container)
        filter_scroll.setMaximumHeight(60)
        main_layout.addWidget(filter_scroll)
        
        # Add filter button
        add_filter_button = create_button(text="Add Another Filter", style='white', callback=self.add_filter_row)
        main_layout.addWidget(add_filter_button, alignment=Qt.AlignLeft)
    
    def set_filter_data(self, visible_columns, field_to_column_map):
        """
        Set the filter data for populating filter rows.
        
        Args:
            visible_columns: List of column names visible in the table
            field_to_column_map: Map of column names to table column indices
        """
        self.visible_columns = visible_columns
        self.field_to_column_map = field_to_column_map
        
        # Add initial filter row if none exist
        if not self.filter_rows and self.visible_columns:
            self.add_filter_row()
    
    def add_filter_row(self):
        """Add a new filter row."""
        if not self.visible_columns:
            return
            
        filter_row = FilterRow(self.visible_columns, self.field_to_column_map, self)
        filter_row.filter_changed.connect(self.on_filter_changed)
        filter_row.remove_requested.connect(self.remove_filter_row)
        
        self.filter_rows_layout.addWidget(filter_row)
        self.filter_rows.append(filter_row)
        
        # Show/hide remove buttons based on number of rows
        for row in self.filter_rows:
            row.remove_button.setVisible(len(self.filter_rows) > 1)
    
    def remove_filter_row(self, filter_row):
        """Remove a filter row."""
        if filter_row in self.filter_rows:
            self.filter_rows_layout.removeWidget(filter_row)
            self.filter_rows.remove(filter_row)
            filter_row.deleteLater()
            
            # Update remove button visibility
            for row in self.filter_rows:
                row.remove_button.setVisible(len(self.filter_rows) > 1)
            
            self.on_filter_changed()
    
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
        for filter_row in self.filter_rows:
            criteria = filter_row.get_filter_criteria()
            if criteria and criteria[1]:  # Only if column and non-empty text
                filters.append(criteria)
        return filters
    
    def reset_filters(self):
        """Reset all filter rows."""
        # Clear existing filter rows
        while self.filter_rows:
            row = self.filter_rows.pop()
            self.filter_rows_layout.removeWidget(row)
            row.deleteLater()
        
        # Add a single empty filter row if columns exist
        if self.visible_columns:
            self.add_filter_row()