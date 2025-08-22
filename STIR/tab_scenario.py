"""STIR Scenario Tab for the STIR Calculator."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Signal

from common.constants import get_margin_large, get_spacing_medium
from common.styles import get_subtitle_font
from common.widgets.header_frame_buttons import ContentFrame
from .widget_operations_table import STIROperationsTableWidget


class STIRScenarioTabPage(QWidget):
    """
    Tab page for displaying and editing a single STIR scenario.
    
    Provides editing capabilities for tillage operations and STIR calculations.
    """
    
    scenario_changed = Signal(object)  # Emitted when scenario data changes
    
    def __init__(self, parent=None, scenario_name="Scenario"):
        """
        Initialize the STIR scenario tab page.
        
        Args:
            parent: Parent widget
            scenario_name: Name of this scenario
        """
        super().__init__(parent)
        self.parent = parent
        self.scenario_name = scenario_name
        self.total_stir_value = 0  # Default value
        self.operations = []  # List to store operations
        
        # Default UOM display settings
        self.display_depth_uom = "inch"
        self.display_speed_uom = "mph"
        
        # Create operations table widget
        self.operations_table = None
        
        self.setup_ui()
        self._connect_signals()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            get_margin_large(), get_margin_large(), 
            get_margin_large(), get_margin_large()
        )
        main_layout.setSpacing(get_spacing_medium())
        
        # Operations section
        operations_frame = ContentFrame()
        operations_layout = QVBoxLayout()
        
        # Operations header
        operations_layout.addWidget(QLabel("STIR Operations", font=get_subtitle_font()))
        
        # Create and add operations table
        self.operations_table = STIROperationsTableWidget()
        operations_layout.addWidget(self.operations_table)
        
        operations_frame.layout.addLayout(operations_layout)
        main_layout.addWidget(operations_frame)
    
    def _connect_signals(self):
        """Connect widget signals."""
        if self.operations_table:
            self.operations_table.operations_changed.connect(self._on_operations_changed)
            self.operations_table.stir_changed.connect(self._on_stir_changed)
    
    def _on_operations_changed(self):
        """Handle operations changes in the table."""
        # Update internal operations list
        self.operations = self.operations_table.get_operations()
        self.scenario_changed.emit(self)
    
    def _on_stir_changed(self, new_total):
        """Handle STIR value changes."""
        self.total_stir_value = new_total
        self.scenario_changed.emit(self)
    
    def get_scenario_name(self):
        """Get the scenario name."""
        return self.scenario_name
    
    def set_scenario_name(self, name):
        """Set the scenario name."""
        old_name = self.scenario_name
        self.scenario_name = name
        if old_name != name:
            self.scenario_changed.emit(self)
    
    def get_total_stir(self):
        """Get the total STIR value."""
        if self.operations_table:
            return self.operations_table.get_total_stir()
        return self.total_stir_value
    
    def calculate_total_stir(self):
        """Calculate total STIR from operations data."""
        if self.operations_table:
            return self.operations_table.get_total_stir()
        return self.total_stir_value
    
    def get_operations_data(self):
        """Get operations data."""
        if self.operations_table:
            return self.operations_table.get_operations()
        return self.operations.copy()
    
    def set_operations_data(self, operations_data):
        """Set operations data."""
        self.operations = operations_data.copy() if operations_data else []
        if self.operations_table:
            self.operations_table.set_operations(self.operations)
        self.scenario_changed.emit(self)
    
    def refresh_data(self):
        """Refresh any dynamic data in the scenario."""
        if self.operations_table:
            # Refresh the table display
            current_operations = self.operations_table.get_operations()
            self.operations_table.set_operations(current_operations)
    
    def has_validation_issues(self):
        """Check if this scenario has any validation issues."""
        # Check if any operations have invalid data
        operations = self.get_operations_data()
        for operation in operations:
            # Basic validation - check if required fields are present
            if not operation.machine_name or operation.stir_value is None:
                return True
        return False
    
    def get_operations_count(self):
        """Get the number of operations in this scenario."""
        if self.operations_table:
            return len(self.operations_table.get_operations())
        return len(self.operations)
    
    def add_operation(self, operation=None):
        """Add a new operation to this scenario."""
        if self.operations_table:
            self.operations_table.add_operation(operation)
    
    def set_display_uom(self, depth_uom, speed_uom):
        """Set the display UOM settings for this scenario."""
        self.display_depth_uom = depth_uom
        self.display_speed_uom = speed_uom
        
        # Update the operations table to refresh display with new UOM
        if self.operations_table:
            self.operations_table.set_display_uom(depth_uom, speed_uom)
    
    def get_display_uom(self):
        """Get current display UOM settings."""
        return {
            'depth_uom': self.display_depth_uom,
            'speed_uom': self.display_speed_uom
        }