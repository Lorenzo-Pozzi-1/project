"""
STIR Operations Table Model

A Qt model for managing STIR operations with grouped display functionality.
Provides a clean Model/View architecture for the operations table.
"""

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal
from PySide6.QtGui import QFont
from typing import List, Any, Optional, Dict
from collections import defaultdict
import math

from ..model_operation import Operation
from ..repository_machine import MachineRepository
from common.styles import get_medium_font


class STIROperationsTableModel(QAbstractTableModel):
    """
    Table model for STIR operations with grouped display.
    
    This model presents operations grouped by operation_group, with group headers
    that span multiple columns. Group headers are virtual rows that don't correspond
    to actual operations.
    """
    
    # Signals
    operations_changed = Signal()
    stir_changed = Signal(float)
    
    # Row types for internal use
    ROW_TYPE_HEADER = "header"
    ROW_TYPE_OPERATION = "operation"
    
    def __init__(self, parent=None):
        """Initialize the STIR operations table model."""
        super().__init__(parent)
        
        # Data storage
        self._operations: List[Operation] = []
        self._row_data: List[Dict] = []  # Maps display rows to data
        self._machine_repo = MachineRepository.get_instance()
        
        # Display UOM settings
        self.display_depth_uom = "inch"
        self.display_speed_uom = "mph"
        
        # Column definitions
        self._columns = [
            "Group", "Machine", "Depth", "Speed", 
            "Area Disturbed", "N of Passes", "STIR"
        ]
    
    # --- QAbstractTableModel Interface ---
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of display rows (operations + group headers)."""
        if parent.isValid():
            return 0
        return len(self._row_data)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns."""
        if parent.isValid():
            return 0
        return len(self._columns)
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        """Return header data for the table."""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal and 0 <= section < len(self._columns):
                header_text = self._columns[section]
                # Add UOM labels to depth and speed columns
                if section == 2:  # Depth column
                    header_text = f"Depth ({self.display_depth_uom})"
                elif section == 3:  # Speed column
                    header_text = f"Speed ({self.display_speed_uom})"
                return header_text
            elif orientation == Qt.Vertical:
                return str(section + 1)
        return None
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return data for the given index and role."""
        if not index.isValid() or index.row() >= len(self._row_data):
            return None
        
        row_info = self._row_data[index.row()]
        row_type = row_info.get("type")
        
        # Only handle operation rows now (no headers)
        if row_type == self.ROW_TYPE_OPERATION:
            return self._get_operation_data(index, role, row_info)
        
        return None
    
    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        """Set data for the given index."""
        if not index.isValid() or index.row() >= len(self._row_data):
            return False
        
        if role != Qt.EditRole:
            return False
        
        row_info = self._row_data[index.row()]
        
        # Only operation rows are editable
        if row_info.get("type") != self.ROW_TYPE_OPERATION:
            return False
        
        operation = row_info.get("operation")
        if not operation:
            return False
        
        column = index.column()
        
        try:
            if column == 0:  # Group
                new_group = str(value).strip()
                if new_group != operation.operation_group:
                    operation.operation_group = new_group
                    self._rebuild_display_data()
                    self._emit_signals()
                    return True
                    
            elif column == 1:  # Machine
                new_machine_name = str(value).strip()
                if new_machine_name != operation.machine_name:
                    if new_machine_name:
                        machine = self._machine_repo.get_machine_by_name(new_machine_name)
                        if machine:
                            # Update operation with machine parameters
                            operation.machine_name = machine.name
                            operation.depth = machine.depth
                            operation.depth_uom = machine.depth_uom
                            operation.speed = machine.speed
                            operation.speed_uom = machine.speed_uom
                            operation.surface_area_disturbed = machine.surface_area_disturbed
                            operation.tillage_type_factor = machine.tillage_type_factor
                            operation.calculate_stir()
                        else:
                            operation.machine_name = new_machine_name
                    else:
                        operation.machine_name = ""
                    
                    self._rebuild_display_data()
                    self._emit_signals()
                    return True
                    
            elif column == 2:  # Depth
                # Convert from display UOM to operation's stored UOM
                display_depth = float(value)
                
                # Convert display value to cm (standard), then to operation's UOM
                if self.display_depth_uom.lower() == 'inch':
                    depth_cm = display_depth * 2.54
                else:
                    depth_cm = display_depth
                
                # Convert cm to operation's stored UOM
                if operation.depth_uom.lower() == 'inch':
                    new_depth = depth_cm / 2.54
                else:
                    new_depth = depth_cm
                
                if abs(new_depth - (operation.depth or 0)) > 0.01:  # Small tolerance for float comparison
                    operation.depth = new_depth
                    operation.calculate_stir()
                    self.dataChanged.emit(index, index, [Qt.DisplayRole])
                    self._emit_signals()
                    return True
                    
            elif column == 3:  # Speed
                # Convert from display UOM to operation's stored UOM
                display_speed = float(value)
                
                # Convert display value to km/h (standard), then to operation's UOM
                if self.display_speed_uom.lower() == 'mph':
                    speed_kmh = display_speed * 1.60934
                else:
                    speed_kmh = display_speed
                
                # Convert km/h to operation's stored UOM
                if operation.speed_uom.lower() == 'mph':
                    new_speed = speed_kmh / 1.60934
                else:
                    new_speed = speed_kmh
                
                if abs(new_speed - (operation.speed or 0)) > 0.01:  # Small tolerance for float comparison
                    operation.speed = new_speed
                    operation.calculate_stir()
                    self.dataChanged.emit(index, index, [Qt.DisplayRole])
                    self._emit_signals()
                    return True
                    
            elif column == 4:  # Area Disturbed
                # Remove % sign if present
                value_str = str(value).replace('%', '').strip()
                new_area = float(value_str)
                if new_area != operation.surface_area_disturbed:
                    operation.surface_area_disturbed = new_area
                    operation.calculate_stir()
                    self.dataChanged.emit(index, index, [Qt.DisplayRole])
                    self._emit_signals()
                    return True
                    
            elif column == 5:  # Number of Passes
                new_passes = int(float(value))
                if new_passes != operation.number_of_passes:
                    operation.number_of_passes = new_passes
                    operation.calculate_stir()
                    self.dataChanged.emit(index, index, [Qt.DisplayRole])
                    self._emit_signals()
                    return True
                    
        except (ValueError, TypeError) as e:
            print(f"Warning: Invalid value '{value}' for column {column}: {e}")
            return False
        
        return False
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Return flags for the given index."""
        if not index.isValid():
            return Qt.NoItemFlags
        
        if index.row() >= len(self._row_data):
            return Qt.NoItemFlags
        
        row_info = self._row_data[index.row()]
        row_type = row_info.get("type")
        
        # Only operation rows exist now
        if row_type == self.ROW_TYPE_OPERATION:
            # Operation rows can be edited for certain columns
            base_flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
            
            # Columns 0-5 are editable, 6 is read-only
            if index.column() <= 5:
                base_flags |= Qt.ItemIsEditable
            
            return base_flags
        
        return Qt.NoItemFlags
    
    # --- Custom Model Interface ---
    
    def set_operations(self, operations: List[Operation]):
        """Set the operations to display in the table."""
        self.beginResetModel()
        self._operations = operations or []
        self._rebuild_display_data()
        self.endResetModel()
        self._emit_signals()
    
    def get_operations(self) -> List[Operation]:
        """Get the current list of operations."""
        return self._operations.copy()
    
    def add_operation(self, operation: Optional[Operation] = None, after_index: int = -1) -> int:
        """Add a new operation. Returns the operation index."""
        if operation is None:
            operation = Operation()
        
        if not isinstance(operation, Operation):
            print(f"Warning: Expected Operation object, got {type(operation)}. Creating new operation.")
            operation = Operation()
        
        # Determine insert position
        if after_index >= 0 and after_index < len(self._operations):
            selected_operation = self._operations[after_index]
            operation.operation_group = selected_operation.operation_group or "pre-plant"
            insert_index = after_index + 1
        else:
            insert_index = len(self._operations)
        
        # Insert the operation
        self._operations.insert(insert_index, operation)
        
        # Rebuild display
        self.beginResetModel()
        self._rebuild_display_data()
        self.endResetModel()
        
        self._emit_signals()
        return insert_index
    
    def remove_operation(self, operation_index: int) -> bool:
        """Remove an operation by its index. Returns True if successful."""
        if 0 <= operation_index < len(self._operations):
            self._operations.pop(operation_index)
            
            self.beginResetModel()
            self._rebuild_display_data()
            self.endResetModel()
            
            self._emit_signals()
            return True
        
        return False
    
    def get_operation_index_from_display_row(self, display_row: int) -> int:
        """Get the operation index from a display row. Returns -1 if not an operation row."""
        if 0 <= display_row < len(self._row_data):
            row_info = self._row_data[display_row]
            if row_info.get("type") == self.ROW_TYPE_OPERATION:
                return row_info.get("operation_index", -1)
        return -1
    
    def get_display_row_from_operation_index(self, operation_index: int) -> int:
        """Get the display row for an operation index. Returns -1 if not found."""
        for row, row_info in enumerate(self._row_data):
            if (row_info.get("type") == self.ROW_TYPE_OPERATION and 
                row_info.get("operation_index") == operation_index):
                return row
        return -1
    
    def get_total_stir(self) -> float:
        """Calculate the total STIR value for all operations (rounded up to next integer)."""
        total = sum(op.stir_value for op in self._operations if op.stir_value is not None)
        return math.ceil(total)
    
    # --- Private Methods ---
    
    def _rebuild_display_data(self):
        """Rebuild the display row data with operations grouped by operation_group."""
        self._row_data.clear()
        
        if not self._operations:
            return
        
        # Group operations by operation_group
        grouped_operations = self._group_operations_by_group()
        
        # Sort groups in chronological order
        group_order = ["pre-plant", "in-season", "harvest"]
        sorted_groups = []
        
        for group in group_order:
            if group in grouped_operations:
                sorted_groups.append(group)
        
        # Add any other groups
        for group in grouped_operations.keys():
            if group not in sorted_groups:
                sorted_groups.append(group)
        
        # Build display rows - operations only, no headers
        for group_name in sorted_groups:
            operations_in_group = grouped_operations[group_name]
            
            # Add operations directly without group header
            for operation in operations_in_group:
                operation_index = self._operations.index(operation)
                operation_info = {
                    "type": self.ROW_TYPE_OPERATION,
                    "operation": operation,
                    "operation_index": operation_index
                }
                self._row_data.append(operation_info)
    
    def _group_operations_by_group(self) -> Dict[str, List[Operation]]:
        """Group operations by their operation_group."""
        grouped = defaultdict(list)
        
        for operation in self._operations:
            if not hasattr(operation, 'operation_group'):
                print(f"Warning: Invalid operation object found: {type(operation)}. Skipping.")
                continue
            
            group_name = operation.operation_group or "pre-plant"
            # Clean up any extra text that might have been added
            if " (" in group_name:
                group_name = group_name.split(" (")[0]
            
            grouped[group_name].append(operation)
        
        return dict(grouped)
    
    def _get_operation_data(self, index: QModelIndex, role: int, row_info: Dict) -> Any:
        """Get data for an operation row."""
        operation = row_info.get("operation")
        if not operation:
            return None
        
        column = index.column()
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if column == 0:  # Group (indented for visual hierarchy)
                clean_group = operation.operation_group or 'pre-plant'
                if " (" in clean_group:
                    clean_group = clean_group.split(" (")[0]
                return f"  {clean_group}" if role == Qt.DisplayRole else clean_group
            
            elif column == 1:  # Machine
                return operation.machine_name or ""
            
            elif column == 2:  # Depth
                # Display depth in the selected UOM
                if operation.depth is not None:
                    display_value = operation.get_depth_in_unit(self.display_depth_uom)
                    return f"{display_value:.1f}"
                else:
                    return "0.0"
            
            elif column == 3:  # Speed
                # Display speed in the selected UOM
                if operation.speed is not None:
                    display_value = operation.get_speed_in_unit(self.display_speed_uom)
                    return f"{display_value:.1f}"
                else:
                    return "0.0"
            
            elif column == 4:  # Area Disturbed
                if role == Qt.EditRole:
                    return f"{operation.surface_area_disturbed or 0:.0f}"
                else:
                    return f"{operation.surface_area_disturbed or 0:.0f}%"
            
            elif column == 5:  # Number of Passes
                return f"{operation.number_of_passes or 1}"
            
            elif column == 6:  # STIR Value
                stir_value = operation.stir_value or 0
                return str(math.ceil(stir_value))
        
        elif role == Qt.TextAlignmentRole:
            if column == 0:  # Group column
                return Qt.AlignLeft | Qt.AlignVCenter
            else:  # All other columns centered
                return Qt.AlignCenter
        
        return None
    
    def _emit_signals(self):
        """Emit change signals."""
        total_stir = self.get_total_stir()
        self.operations_changed.emit()
        self.stir_changed.emit(total_stir)
    
    def set_display_uom(self, depth_uom, speed_uom):
        """Set display UOM settings and refresh headers."""
        self.display_depth_uom = depth_uom
        self.display_speed_uom = speed_uom
        
        # Emit header data changed to update column headers
        self.headerDataChanged.emit(Qt.Horizontal, 2, 3)
        
        # Refresh all data to update display values
        if self._row_data:
            top_left = self.index(0, 2)
            bottom_right = self.index(len(self._row_data) - 1, 3)
            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
    
    def is_group_boundary(self, row: int) -> bool:
        """Check if this row is the first row of a new group (needs divider above)."""
        if row <= 0 or row >= len(self._row_data):
            return False
        
        # Get current and previous row info
        current_row_info = self._row_data[row]
        previous_row_info = self._row_data[row - 1]
        
        # Both must be operation rows
        if (current_row_info.get("type") != self.ROW_TYPE_OPERATION or 
            previous_row_info.get("type") != self.ROW_TYPE_OPERATION):
            return False
        
        # Check if groups are different
        current_operation = current_row_info.get("operation")
        previous_operation = previous_row_info.get("operation")
        
        if not current_operation or not previous_operation:
            return False
        
        current_group = current_operation.operation_group or "pre-plant"
        previous_group = previous_operation.operation_group or "pre-plant"
        
        # Clean up group names
        if " (" in current_group:
            current_group = current_group.split(" (")[0]
        if " (" in previous_group:
            previous_group = previous_group.split(" (")[0]
        
        return current_group != previous_group
