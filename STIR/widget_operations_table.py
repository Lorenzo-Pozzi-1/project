"""
STIR Table Widget

A table widget for displaying and managing STIR operations grouped by operation_group.
Shows operations with their parameters and calculated STIR values using Model/View architecture.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from typing import List, Optional

from common.styles import GENERIC_TABLE_STYLE, get_medium_font
from common.widgets.header_frame_buttons import create_button
from .model_operation import Operation
from .models.operations_table_model import STIROperationsTableModel
from .delegates.machine_delegate import MachineSelectionDelegate
from .delegates.group_delegate import GroupSelectionDelegate
from .delegates.numeric_delegate import NumericDelegate


class STIROperationsTableWidget(QWidget):
    """
    Table widget for displaying STIR operations grouped by operation_group using Model/View architecture.
    
    Displays operations with columns: Group, Machine, Depth, Speed, Area Disturbed, 
    N of Passes, STIR, and Total.
    """
    
    # Signals
    operations_changed = Signal()
    stir_changed = Signal(float)
    
    def __init__(self, parent=None):
        """Initialize the STIR operations table widget."""
        super().__init__(parent)
        
        # Create model and view
        self.model = STIROperationsTableModel(self)
        
        # Connect model signals
        self.model.operations_changed.connect(self.operations_changed)
        self.model.stir_changed.connect(self.stir_changed)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Create and configure table view
        self.table = QTableView()
        self.table.setModel(self.model)
        
        self._configure_table()
        layout.addWidget(self.table)
        
        # Add control buttons
        layout.addLayout(self._create_button_layout())
    
    def _configure_table(self):
        """Configure table appearance and behavior."""
        # Styling
        self.table.setStyleSheet(GENERIC_TABLE_STYLE)
        self.table.setFont(get_medium_font())
        self.table.setAlternatingRowColors(True)
        
        # Selection behavior
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        
        # Edit triggers
        self.table.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)
        
        # Set up delegates
        self.group_delegate = GroupSelectionDelegate(self)
        self.machine_delegate = MachineSelectionDelegate(self)
        self.numeric_delegate = NumericDelegate(self)
        
        self.table.setItemDelegateForColumn(0, self.group_delegate)  # Group column
        self.table.setItemDelegateForColumn(1, self.machine_delegate)  # Machine column
        self.table.setItemDelegateForColumn(2, self.numeric_delegate)  # Depth column
        self.table.setItemDelegateForColumn(3, self.numeric_delegate)  # Speed column
        self.table.setItemDelegateForColumn(4, self.numeric_delegate)  # Area Disturbed column
        self.table.setItemDelegateForColumn(5, self.numeric_delegate)  # Number of Passes column
        
        # Headers
        self._configure_headers()
        
        # Connect to model reset to update spans
        self.model.modelReset.connect(self._update_spans)
    
    def _configure_headers(self):
        """Configure table headers."""
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(False)
        
        # Hide vertical header (row numbers)
        self.table.verticalHeader().setVisible(False)
        
        # Set column widths
        self._set_column_widths()
    
    def _set_column_widths(self):
        """Set initial column width policies."""
        header = self.table.horizontalHeader()
        
        # Set all columns to stretch equally
        for col in range(self.model.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
    
    def _update_spans(self):
        """Update cell spans for group headers after model changes."""
        # Clear existing spans
        self.table.clearSpans()
        
        # Set spans for header rows
        for row in range(self.model.rowCount()):
            if self.model.is_header_row(row):
                start_col, span_count = self.model.get_header_span(row)
                self.table.setSpan(row, start_col, 1, span_count)
    
    def _create_button_layout(self) -> QHBoxLayout:
        """Create the button layout for operations management."""
        layout = QHBoxLayout()
        
        # Add operation button
        self.add_button = create_button(
            text="Add Operation",
            style="white",
            callback=lambda: self.add_operation()
        )
        layout.addWidget(self.add_button)
        
        # Remove selected button
        self.remove_button = create_button(
            text="Remove Selected",
            style="white",
            callback=lambda: self.remove_selected_operation()
        )
        layout.addWidget(self.remove_button)
        
        layout.addStretch()
        return layout
    
    def set_operations(self, operations: List[Operation]):
        """Set the operations to display in the table."""
        self.model.set_operations(operations)
    
    def get_operations(self) -> List[Operation]:
        """Get the current list of operations."""
        return self.model.get_operations()
    
    def add_operation(self, operation: Optional[Operation] = None):
        """Add a new operation to the table after the currently selected operation."""
        # Determine where to insert the new operation
        current_index = self.table.currentIndex()
        after_index = -1
        
        if current_index.isValid():
            operation_index = self.model.get_operation_index_from_display_row(current_index.row())
            if operation_index >= 0:
                after_index = operation_index
        
        # Add the operation through the model
        new_operation_index = self.model.add_operation(operation, after_index)
        
        # Select the newly added operation
        self._select_operation_by_index(new_operation_index)
    
    def remove_selected_operation(self):
        """Remove the currently selected operation."""
        current_index = self.table.currentIndex()
        if not current_index.isValid():
            QMessageBox.information(
                self, "No Selection", 
                "Please select an operation to remove."
            )
            return
        
        # Find the operation index from the selected row
        operation_index = self.model.get_operation_index_from_display_row(current_index.row())
        if operation_index < 0:
            QMessageBox.information(
                self, "Invalid Selection", 
                "Please select an operation row to remove."
            )
            return
        
        # Confirm deletion
        result = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to remove this operation?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            self.model.remove_operation(operation_index)
    
    def get_total_stir(self) -> float:
        """Calculate the total STIR value for all operations (rounded up to next integer)."""
        return self.model.get_total_stir()
    
    def clear_operations(self):
        """Clear all operations from the table."""
        self.model.clear_operations()
    
    def _select_operation_by_index(self, operation_index: int):
        """Select the table row corresponding to the given operation index."""
        display_row = self.model.get_display_row_from_operation_index(operation_index)
        if display_row >= 0:
            self.table.selectRow(display_row)
