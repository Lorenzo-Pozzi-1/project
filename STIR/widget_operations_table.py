"""
STIR Table Widget

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
from .repository_machine import MachineRepository
from .delegates.machine_delegate import MachineSelectionDelegate
from .delegates.group_delegate import GroupSelectionDelegate
from .delegates.numeric_delegate import NumericDelegate


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
        self.machine_repo = MachineRepository.get_instance()
        self.row_to_operation_map = {}  # Maps table row to operation index
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
        
        # Edit triggers - allow editing for group and machine columns
        self.table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        
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
        
        # Connect cell changed signal
        self.table.cellChanged.connect(self._on_cell_changed)
        
        # Headers
        self._configure_headers()
    
    def _on_cell_changed(self, row: int, column: int):
        """Handle cell value changes."""
        if column == 0:  # Group column
            # Find the operation index from the displayed table row
            operation_index = self._get_operation_index_from_row(row)
            if operation_index >= 0 and operation_index < len(self.operations):
                operation = self.operations[operation_index]
                new_group_text = self.table.item(row, column).text()
                
                # Clean up the group text (remove indentation spaces)
                new_group = new_group_text.strip()
                
                # Update operation group
                operation.operation_group = new_group
                
                # Refresh the table display to regroup operations
                self.table.cellChanged.disconnect(self._on_cell_changed)
                self._populate_table()
                self.table.cellChanged.connect(self._on_cell_changed)
                self._emit_signals()
                
        elif column == 1:  # Machine column
            # Find the operation index from the displayed table row
            operation_index = self._get_operation_index_from_row(row)
            if operation_index >= 0 and operation_index < len(self.operations):
                operation = self.operations[operation_index]
                new_machine_name = self.table.item(row, column).text()
                
                # Update operation with new machine
                if new_machine_name:
                    machine = self.machine_repo.get_machine_by_name(new_machine_name)
                    if machine:
                        # Update operation with machine parameters
                        operation.machine_name = machine.name
                        operation.depth = machine.depth
                        operation.depth_uom = machine.depth_uom
                        operation.speed = machine.speed
                        operation.speed_uom = machine.speed_uom
                        operation.surface_area_disturbed = machine.surface_area_disturbed
                        operation.tillage_type_factor = machine.tillage_type_factor
                        
                        # Recalculate STIR value
                        operation.calculate_stir()
                        
                        # Refresh the table display (disconnect signal to prevent recursion)
                        self.table.cellChanged.disconnect(self._on_cell_changed)
                        self._populate_table()
                        self.table.cellChanged.connect(self._on_cell_changed)
                        self._emit_signals()
                else:
                    # Clear machine data if empty selection
                    operation.machine_name = ""
                    operation.depth = 0.0
                    operation.speed = 0.0
                    operation.surface_area_disturbed = 100.0
                    operation.tillage_type_factor = 0.7
                    operation.calculate_stir()
                    
                    # Refresh the table display (disconnect signal to prevent recursion)
                    self.table.cellChanged.disconnect(self._on_cell_changed)
                    self._populate_table()
                    self.table.cellChanged.connect(self._on_cell_changed)
                    self._emit_signals()
        
        elif column in [2, 3, 4, 5]:  # Numeric columns: Depth, Speed, Area, Passes
            # Find the operation index from the displayed table row
            operation_index = self._get_operation_index_from_row(row)
            if operation_index >= 0 and operation_index < len(self.operations):
                operation = self.operations[operation_index]
                new_value_text = self.table.item(row, column).text()
                
                try:
                    if column == 2:  # Depth
                        # Parse depth value (remove units)
                        value_str = new_value_text.replace("cm", "").strip()
                        operation.depth = float(value_str) if value_str else 0.0
                        
                    elif column == 3:  # Speed
                        # Parse speed value (remove units)
                        value_str = new_value_text.replace("km/h", "").strip()
                        operation.speed = float(value_str) if value_str else 0.0
                        
                    elif column == 4:  # Area Disturbed
                        # Parse percentage value
                        value_str = new_value_text.replace("%", "").strip()
                        operation.surface_area_disturbed = float(value_str) if value_str else 100.0
                        
                    elif column == 5:  # Number of Passes
                        # Parse integer value
                        operation.number_of_passes = int(new_value_text) if new_value_text else 1
                    
                    # Recalculate STIR value
                    operation.calculate_stir()
                    
                    # Refresh the table display (disconnect signal to prevent recursion)
                    self.table.cellChanged.disconnect(self._on_cell_changed)
                    self._populate_table()
                    self.table.cellChanged.connect(self._on_cell_changed)
                    self._emit_signals()
                    
                except (ValueError, TypeError) as e:
                    print(f"Warning: Invalid numeric value '{new_value_text}' for column {column}: {e}")
                    # Refresh table to revert to original value
                    self.table.cellChanged.disconnect(self._on_cell_changed)
                    self._populate_table()
                    self.table.cellChanged.connect(self._on_cell_changed)
    
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
            callback=lambda: self.add_operation()  # Use lambda to ignore the boolean signal
        )
        layout.addWidget(self.add_button)
        
        # Remove selected button
        self.remove_button = create_button(
            text="Remove Selected",
            style="white",
            callback=lambda: self.remove_selected_operation()  # Use lambda to ignore the boolean signal
        )
        layout.addWidget(self.remove_button)
        
        layout.addStretch()
        return layout
    
    def set_operations(self, operations: List[Operation]):
        """Set the operations to display in the table."""
        self.operations = operations or []
        
        # Disconnect cell changed signal to prevent unwanted triggers during repopulation
        self.table.cellChanged.disconnect(self._on_cell_changed)
        self._populate_table()
        self.table.cellChanged.connect(self._on_cell_changed)
        
        self._emit_signals()
    
    def get_operations(self) -> List[Operation]:
        """Get the current list of operations."""
        return self.operations.copy()
    
    def add_operation(self, operation: Optional[Operation] = None):
        """Add a new operation to the table after the currently selected operation."""
        if operation is None:
            # Create a new empty operation
            operation = Operation()
        
        # Ensure we're adding an Operation object
        if not isinstance(operation, Operation):
            # Log warning and create new operation instead
            print(f"Warning: Expected Operation object, got {type(operation)}. Creating new operation.")
            operation = Operation()
        
        # Determine where to insert the new operation
        current_row = self.table.currentRow()
        if current_row >= 0:
            # Get the operation index for the selected row
            selected_operation_index = self._get_operation_index_from_row(current_row)
            if selected_operation_index >= 0 and selected_operation_index < len(self.operations):
                # Get the group of the selected operation to use as default for new operation
                selected_operation = self.operations[selected_operation_index]
                operation.operation_group = selected_operation.operation_group or "pre-plant"
                
                # Insert after the selected operation
                insert_index = selected_operation_index + 1
            else:
                # If we can't find the selected operation, append at the end
                insert_index = len(self.operations)
        else:
            # No selection, append at the end
            insert_index = len(self.operations)
        
        # Insert the operation at the determined position
        self.operations.insert(insert_index, operation)
        
        # Disconnect cell changed signal to prevent unwanted triggers during repopulation
        self.table.cellChanged.disconnect(self._on_cell_changed)
        self._populate_table()
        self.table.cellChanged.connect(self._on_cell_changed)
        
        self._emit_signals()
        
        # Find and select the newly added operation in the table
        self._select_operation_by_index(insert_index)
    
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
        """Calculate the total STIR value for all operations (rounded up to next integer)."""
        import math
        total = sum(op.stir_value for op in self.operations if op.stir_value is not None)
        return math.ceil(total)
    
    def _populate_table(self):
        """Populate the table with operations grouped by operation_group."""
        # Block signals during population to prevent unwanted cell change events
        self.table.blockSignals(True)
        
        # Clear existing spans first
        self.table.clearSpans()
        
        # Group operations by operation_group
        grouped_operations = self._group_operations_by_group()
        
        # Calculate total rows needed (operations + group headers)
        total_rows = len(self.operations) + len(grouped_operations)
        self.table.setRowCount(total_rows)
        
        current_row = 0
        # Track which table row corresponds to which operation
        self.row_to_operation_map = {}
        
        # Sort groups in chronological order: pre-plant, in-season, harvest
        group_order = ["pre-plant", "in-season", "harvest"]
        sorted_groups = []
        
        # Add groups in chronological order if they exist
        for group in group_order:
            if group in grouped_operations:
                sorted_groups.append(group)
        
        # Add any other groups that might exist (shouldn't happen normally)
        for group in grouped_operations.keys():
            if group not in sorted_groups:
                sorted_groups.append(group)
        
        for group_name in sorted_groups:
            operations_in_group = grouped_operations[group_name]
            
            # Add group header row
            self._add_group_header(current_row, group_name, len(operations_in_group))
            current_row += 1
            
            # Add operations in this group
            group_total_stir = 0
            for operation in operations_in_group:
                # Find the actual index of this operation in self.operations
                operation_index = self.operations.index(operation)
                self.row_to_operation_map[current_row] = operation_index
                
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
        
        # Re-enable signals
        self.table.blockSignals(False)
    
    def _group_operations_by_group(self) -> Dict[str, List[Operation]]:
        """Group operations by their operation_group."""
        grouped = defaultdict(list)
        
        for operation in self.operations:
            # Validate that operation is an Operation object
            if not hasattr(operation, 'operation_group'):
                print(f"Warning: Invalid operation object found: {type(operation)}. Skipping.")
                continue
            
            # Get the clean group name (handle None and default to "pre-plant")
            group_name = operation.operation_group or "pre-plant"
            # Clean up any extra text that might have been added
            if " (" in group_name:
                group_name = group_name.split(" (")[0]
            
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
        # Group (editable, indented for visual hierarchy)
        # Clean the group name to remove any count text that might have been added
        clean_group_name = operation.operation_group or 'pre-plant'
        if " (" in clean_group_name:
            clean_group_name = clean_group_name.split(" (")[0]
        
        group_item = QTableWidgetItem(f"  {clean_group_name}")
        group_item.setFlags(group_item.flags() | Qt.ItemIsEditable)
        self.table.setItem(row, 0, group_item)
        
        # Machine (editable)
        machine_item = QTableWidgetItem(operation.machine_name or "")
        machine_item.setFlags(machine_item.flags() | Qt.ItemIsEditable)
        self.table.setItem(row, 1, machine_item)
        
        # Depth (editable with numeric delegate)
        depth_text = f"{operation.depth or 0:.1f}" if operation.depth is not None else "0.0"
        depth_item = QTableWidgetItem(depth_text)
        depth_item.setFlags(depth_item.flags() | Qt.ItemIsEditable)  # Make editable
        depth_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 2, depth_item)
        
        # Speed (editable with numeric delegate)
        speed_text = f"{operation.speed or 0:.1f}" if operation.speed is not None else "0.0"
        speed_item = QTableWidgetItem(speed_text)
        speed_item.setFlags(speed_item.flags() | Qt.ItemIsEditable)  # Make editable
        speed_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 3, speed_item)
        
        # Area Disturbed (editable with numeric delegate)
        area_text = f"{operation.surface_area_disturbed or 0:.0f}%" if operation.surface_area_disturbed is not None else "0%"
        area_item = QTableWidgetItem(area_text)
        area_item.setFlags(area_item.flags() | Qt.ItemIsEditable)  # Make editable
        area_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 4, area_item)
        
        # Number of Passes (editable with numeric delegate)
        passes_text = f"{operation.number_of_passes or 1}" if operation.number_of_passes is not None else "1"
        passes_item = QTableWidgetItem(passes_text)
        passes_item.setFlags(passes_item.flags() | Qt.ItemIsEditable)  # Make editable
        passes_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 5, passes_item)
        
        # STIR Value (read-only, calculated - rounded up to next integer)
        import math
        stir_value = operation.stir_value or 0
        stir_rounded = math.ceil(stir_value)
        stir_text = f"{stir_rounded}"
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
        import math
        # Round up the group total to next integer
        group_total_rounded = math.ceil(group_total)
        total_item = QTableWidgetItem(f"{group_total_rounded}")
        total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
        total_item.setTextAlignment(Qt.AlignCenter)
        
        # Make it bold
        font = get_medium_font(bold=True)
        total_item.setFont(font)
        
        self.table.setItem(header_row, 7, total_item)
    
    def _get_operation_index_from_row(self, display_row: int) -> int:
        """Get the operation index from the displayed table row."""
        # Use the row to operation mapping if available
        if hasattr(self, 'row_to_operation_map') and display_row in self.row_to_operation_map:
            return self.row_to_operation_map[display_row]
        
        # Fallback method: count only operation rows (skip group headers)
        operation_index = 0
        
        for row in range(display_row):
            # Check if this is a group header by looking at span
            if self.table.columnSpan(row, 0) > 1:
                # This is a group header, skip
                continue
            else:
                # This is an operation row
                operation_index += 1
        
        return operation_index
    
    def _select_operation_by_index(self, operation_index: int):
        """Select the table row corresponding to the given operation index."""
        if not hasattr(self, 'row_to_operation_map'):
            return
        
        # Find the table row that corresponds to this operation index
        for table_row, mapped_operation_index in self.row_to_operation_map.items():
            if mapped_operation_index == operation_index:
                self.table.selectRow(table_row)
                return
        
        # If not found, try to select the last row
        if self.table.rowCount() > 0:
            self.table.selectRow(self.table.rowCount() - 1)
    
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