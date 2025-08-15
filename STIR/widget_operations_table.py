"""
STIR Operations Table Widget

A table widget for displaying and managing STIR operations grouped by operation_group.
Shows operations with their parameters and calculated STIR values.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QLabel, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import List, Dict, Optional
from collections import defaultdict

from common.styles import GENERIC_TABLE_STYLE, get_medium_font, get_subtitle_font
from common.widgets.header_frame_buttons import ContentFrame, create_button
from .model_operation import Operation


class STIROperationsTableWidget(QWidget):
    """
    Table widget for displaying STIR operations grouped by operation_group.
    
    Displays operations with columns: Group, Machine, Depth, Speed, Area Disturbed, 
    N of Passes, STIR, and Total.
    """
    
    # Signals
    operations_changed = Signal()
    stir_changed = Signal(float)
    
    def __init__(self, parent=None):
        """Initialize the STIR operations table widget."""
        super().__init__(parent)
        self.operations = []  # List of Operation objects
        self.header_labels = [
            "Group", "Machine", "Depth", "Speed", 
            "Area Disturbed", "N of Passes", "STIR", "Total"
        ]
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Create and configure table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(self.header_labels)
        
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
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Edit triggers - make most columns read-only for display
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Headers
        self._configure_headers()
    
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
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
    
    def _create_button_layout(self) -> QHBoxLayout:
        """Create the button layout for operations management."""
        layout = QHBoxLayout()
        
        # Add operation button
        self.add_button = create_button(
            text="Add Operation",
            style="white",
            callback=self.add_operation
        )
        layout.addWidget(self.add_button)
        
        # Remove selected button
        self.remove_button = create_button(
            text="Remove Selected",
            style="white",
            callback=self.remove_selected_operation
        )
        layout.addWidget(self.remove_button)
        
        layout.addStretch()
        return layout
    
    def set_operations(self, operations: List[Operation]):
        """Set the operations to display in the table."""
        self.operations = operations or []
        self._populate_table()
        self._emit_signals()
    
    def get_operations(self) -> List[Operation]:
        """Get the current list of operations."""
        return self.operations.copy()
    
    def add_operation(self, operation: Optional[Operation] = None):
        """Add a new operation to the table."""
        if operation is None:
            # Create a new empty operation
            from .model_operation import Operation  # Ensure Operation is imported
            operation = Operation()
        
        # Ensure we're adding an Operation object
        if not isinstance(operation, Operation):
            # Log warning and create new operation instead
            print(f"Warning: Expected Operation object, got {type(operation)}. Creating new operation.")
            from .model_operation import Operation
            operation = Operation()
        
        self.operations.append(operation)
        self._populate_table()
        self._emit_signals()
        
        # Select the new operation
        if self.table.rowCount() > 0:
            self.table.selectRow(self.table.rowCount() - 1)
    
    def remove_selected_operation(self):
        """Remove the currently selected operation."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(
                self, "No Selection", 
                "Please select an operation to remove."
            )
            return
        
        # Find the operation index from the displayed table
        operation_index = self._get_operation_index_from_row(current_row)
        if operation_index >= 0:
            # Confirm deletion
            result = QMessageBox.question(
                self, "Confirm Deletion",
                "Are you sure you want to remove this operation?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if result == QMessageBox.Yes:
                self.operations.pop(operation_index)
                self._populate_table()
                self._emit_signals()
    
    def get_total_stir(self) -> float:
        """Calculate the total STIR value for all operations."""
        return sum(op.stir_value for op in self.operations if op.stir_value is not None)
    
    def _populate_table(self):
        """Populate the table with operations grouped by operation_group."""
        # Group operations by operation_group
        grouped_operations = self._group_operations_by_group()
        
        # Calculate total rows needed (operations + group headers)
        total_rows = len(self.operations) + len(grouped_operations)
        self.table.setRowCount(total_rows)
        
        current_row = 0
        
        # Sort groups for consistent display
        sorted_groups = sorted(grouped_operations.keys())
        
        for group_name in sorted_groups:
            operations_in_group = grouped_operations[group_name]
            
            # Add group header row
            self._add_group_header(current_row, group_name, len(operations_in_group))
            current_row += 1
            
            # Add operations in this group
            group_total_stir = 0
            for operation in operations_in_group:
                self._add_operation_row(current_row, operation)
                group_total_stir += operation.stir_value or 0
                current_row += 1
            
            # Update the group header with total
            self._update_group_total(current_row - len(operations_in_group) - 1, group_total_stir)
        
        # If no operations, show empty state
        if not self.operations:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("No operations")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsEditable)
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, empty_item)
            
            # Span across all columns
            self.table.setSpan(0, 0, 1, 8)
        
        # Resize rows to content
        self.table.resizeRowsToContents()
    
    def _group_operations_by_group(self) -> Dict[str, List[Operation]]:
        """Group operations by their operation_group."""
        grouped = defaultdict(list)
        
        for operation in self.operations:
            # Validate that operation is an Operation object
            if not hasattr(operation, 'operation_group'):
                print(f"Warning: Invalid operation object found: {type(operation)}. Skipping.")
                continue
            
            group_name = operation.operation_group or "Ungrouped"
            grouped[group_name].append(operation)
        
        return dict(grouped)
    
    def _add_group_header(self, row: int, group_name: str, count: int):
        """Add a group header row."""
        # Group name with count
        header_text = f"{group_name} ({count} operation{'s' if count != 1 else ''})"
        header_item = QTableWidgetItem(header_text)
        
        # Make it bold and non-editable
        font = get_medium_font(bold=True)
        header_item.setFont(font)
        header_item.setFlags(header_item.flags() & ~Qt.ItemIsEditable)
        header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.table.setItem(row, 0, header_item)
        
        # Add empty items to other columns (required before merging)
        for col in range(1, 7):  # Columns 1-6
            empty_item = QTableWidgetItem("")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, col, empty_item)
        
        # Total column will be updated separately
        total_item = QTableWidgetItem("")
        total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
        total_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 7, total_item)
        
        # Merge the cells for group name across columns 0-6
        self.table.setSpan(row, 0, 1, 7)
    
    def _add_operation_row(self, row: int, operation: Operation):
        """Add a regular operation row."""
        # Group (indented for visual hierarchy)
        group_item = QTableWidgetItem(f"  {operation.machine_name or 'Unknown Machine'}")
        group_item.setFlags(group_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 0, group_item)
        
        # Machine (already in group column, so this could be operation type or leave empty)
        machine_item = QTableWidgetItem(operation.operation_type or "")
        machine_item.setFlags(machine_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 1, machine_item)
        
        # Depth
        depth_text = f"{operation.depth or 0:.1f}" if operation.depth is not None else "0.0"
        depth_item = QTableWidgetItem(depth_text)
        depth_item.setFlags(depth_item.flags() & ~Qt.ItemIsEditable)
        depth_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 2, depth_item)
        
        # Speed
        speed_text = f"{operation.speed or 0:.1f}" if operation.speed is not None else "0.0"
        speed_item = QTableWidgetItem(speed_text)
        speed_item.setFlags(speed_item.flags() & ~Qt.ItemIsEditable)
        speed_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 3, speed_item)
        
        # Area Disturbed
        area_text = f"{operation.area_disturbed or 0:.0f}%" if operation.area_disturbed is not None else "0%"
        area_item = QTableWidgetItem(area_text)
        area_item.setFlags(area_item.flags() & ~Qt.ItemIsEditable)
        area_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 4, area_item)
        
        # Number of Passes
        passes_text = f"{operation.number_of_passes or 1}" if operation.number_of_passes is not None else "1"
        passes_item = QTableWidgetItem(passes_text)
        passes_item.setFlags(passes_item.flags() & ~Qt.ItemIsEditable)
        passes_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 5, passes_item)
        
        # STIR Value
        stir_text = f"{operation.stir_value or 0:.1f}" if operation.stir_value is not None else "0.0"
        stir_item = QTableWidgetItem(stir_text)
        stir_item.setFlags(stir_item.flags() & ~Qt.ItemIsEditable)
        stir_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 6, stir_item)
        
        # Total (empty for individual operations, only shown in group headers)
        total_item = QTableWidgetItem("")
        total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 7, total_item)
    
    def _update_group_total(self, header_row: int, group_total: float):
        """Update the group header's total column."""
        total_item = QTableWidgetItem(f"{group_total:.1f}")
        total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
        total_item.setTextAlignment(Qt.AlignCenter)
        
        # Make it bold
        font = get_medium_font(bold=True)
        total_item.setFont(font)
        
        self.table.setItem(header_row, 7, total_item)
    
    def _get_operation_index_from_row(self, display_row: int) -> int:
        """Get the operation index from the displayed table row."""
        # This is complex because of group headers
        # For now, we'll use a simple approach - this could be enhanced
        operation_index = 0
        
        for row in range(display_row + 1):
            item = self.table.item(row, 0)
            if item and not item.text().startswith("  "):
                # This is a group header, skip
                continue
            else:
                # This is an operation row
                if row == display_row:
                    return operation_index
                operation_index += 1
        
        return -1
    
    def _emit_signals(self):
        """Emit change signals."""
        total_stir = self.get_total_stir()
        self.operations_changed.emit()
        self.stir_changed.emit(total_stir)
    
    def clear_operations(self):
        """Clear all operations from the table."""
        self.operations.clear()
        self._populate_table()
        self._emit_signals()