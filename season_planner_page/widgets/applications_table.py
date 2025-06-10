"""Applications Table Widget for the Season Planner."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView, 
    QAbstractItemView, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QShowEvent
from typing import List, Dict, Any
import traceback

from common import create_button, GENERIC_TABLE_STYLE, get_medium_font
from data import Application
from ..models.application_table_model import ApplicationTableModel
from ..delegates.date_delegate import DateDelegate
from ..delegates.numeric_delegate import RateDelegate, AreaDelegate
from ..delegates.method_delegate import MethodDelegate
from ..delegates.product_name_delegate import ProductNameDelegate
from ..delegates.uom_delegate import UOMDelegate
from ..delegates.product_type_delegate import ProductTypeDelegate
from ..delegates.reorder_delegate import ReorderDelegate


class ApplicationsTableWidget(QWidget):
    """Main applications table widget with Excel-like editing capabilities."""
    
    # Signals
    applications_changed = Signal()
    eiq_changed = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize model
        self.model = ApplicationTableModel()
        self._connect_model_signals()
        
        # Initialize delegates
        self.delegates = {}
        self._delegates_assigned = False
        self._create_delegates()
        
        # Setup UI
        self._setup_ui()
    
    def _connect_model_signals(self):
        """Connect model signals to local handlers."""
        self.model.eiq_changed.connect(self.eiq_changed)
        self.model.dataChanged.connect(self.applications_changed)
        self.model.rowsInserted.connect(self.applications_changed)
        self.model.rowsRemoved.connect(self.applications_changed)
    
    def _create_delegates(self):
        """Create all delegate instances."""
        self.delegates = {
            'reorder': ReorderDelegate(self),
            'date': DateDelegate(self),
            'rate': RateDelegate(self),
            'area': AreaDelegate(self),
            'product_type': ProductTypeDelegate(self),
            'method': MethodDelegate(self),
            'product_name': ProductNameDelegate(self),
            'rate_uom': UOMDelegate(self, uom_type="application_rate")
        }
        
        # Connect reorder signals
        self.delegates['reorder'].move_up.connect(self._move_up)
        self.delegates['reorder'].move_down.connect(self._move_down)
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Create and configure table
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self._configure_table()
        layout.addWidget(self.table_view)
        
        # Add control buttons
        layout.addLayout(self._create_button_layout())
    
    def _configure_table(self):
        """Configure table appearance and behavior."""
        # Styling
        self.table_view.setStyleSheet(GENERIC_TABLE_STYLE + """
            QTableView::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        self.table_view.setFont(get_medium_font())
        self.table_view.setAlternatingRowColors(True)
        
        # Selection behavior
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Edit triggers
        self.table_view.setEditTriggers(
            QAbstractItemView.DoubleClicked | 
            QAbstractItemView.EditKeyPressed |
            QAbstractItemView.AnyKeyPressed
        )
        
        # Headers
        self._configure_headers()
    
    def _configure_headers(self):
        """Configure table headers."""
        h_header = self.table_view.horizontalHeader()
        h_header.setSectionResizeMode(QHeaderView.Interactive)
        h_header.setStretchLastSection(False)
        
        # Hide vertical header (row numbers handled by App # column)
        self.table_view.verticalHeader().setVisible(False)
        
        # Set column widths
        self._set_column_widths()
    
    def _set_column_widths(self):
        """Set initial column width policies."""
        header = self.table_view.horizontalHeader()
        
        # Fixed width for reorder buttons
        if self.model.columnCount() > self.model.COL_REORDER:
            header.setSectionResizeMode(self.model.COL_REORDER, QHeaderView.Fixed)
            header.resizeSection(self.model.COL_REORDER, 80)
        
        # Stretch other columns
        for col in range(self.model.columnCount()):
            if col != self.model.COL_REORDER:
                header.setSectionResizeMode(col, QHeaderView.Stretch)
    
    def _create_button_layout(self) -> QHBoxLayout:
        """Create the button layout."""
        layout = QHBoxLayout()
        
        self.add_button = create_button(
            text="Add Application",
            style="white",
            callback=self.add_application
        )
        layout.addWidget(self.add_button)
        
        self.remove_button = create_button(
            text="Remove Selected",
            style="white",
            callback=self.remove_selected_application
        )
        layout.addWidget(self.remove_button)
        
        layout.addStretch()
        return layout
    
    def showEvent(self, event: QShowEvent):
        """Assign delegates when widget is first shown."""
        super().showEvent(event)
        
        if not self._delegates_assigned:
            self._assign_delegates()
            self._delegates_assigned = True
    
    def _assign_delegates(self):
        """Assign delegates to table columns."""
        try:
            assignments = {
                self.model.COL_REORDER: self.delegates['reorder'],
                self.model.COL_DATE: self.delegates['date'],
                self.model.COL_RATE: self.delegates['rate'],
                self.model.COL_AREA: self.delegates['area'],
                self.model.COL_PRODUCT_TYPE: self.delegates['product_type'],
                self.model.COL_METHOD: self.delegates['method'],
                self.model.COL_PRODUCT_NAME: self.delegates['product_name'],
                self.model.COL_RATE_UOM: self.delegates['rate_uom']
            }
            
            for col_index, delegate in assignments.items():
                if col_index < self.model.columnCount():
                    self.table_view.setItemDelegateForColumn(col_index, delegate)
            
        except Exception as e:
            print(f"Error assigning delegates: {e}")
            traceback.print_exc()
    
    def _move_up(self, row: int):
        """Handle move up action."""
        if self.model.move_application_up(row):
            self._select_row(row - 1)
            self.applications_changed.emit()
    
    def _move_down(self, row: int):
        """Handle move down action."""
        if self.model.move_application_down(row):
            self._select_row(row + 1)
            self.applications_changed.emit()
    
    def _select_row(self, row: int):
        """Select a specific row."""
        if 0 <= row < self.model.rowCount():
            index = self.model.index(row, 0)
            selection_flags = (
                self.table_view.selectionModel().SelectionFlag.ClearAndSelect |
                self.table_view.selectionModel().SelectionFlag.Rows
            )
            self.table_view.selectionModel().setCurrentIndex(index, selection_flags)
    
    def _get_selected_row(self) -> int:
        """Get the currently selected row index, or -1 if none selected."""
        selected_rows = self.table_view.selectionModel().selectedRows()
        return selected_rows[0].row() if selected_rows else -1
    
    def _show_message(self, title: str, message: str, msg_type="information"):
        """Show a message box."""
        msg_box = getattr(QMessageBox, msg_type, QMessageBox.information)
        msg_box(self, title, message, QMessageBox.Ok)
    
    def _confirm_action(self, title: str, message: str) -> bool:
        """Show a confirmation dialog."""
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    # Public Interface
    
    def add_application(self) -> int:
        """Add a new application row."""
        # Get the selected row to determine insertion position
        selected_row = self._get_selected_row()
        
        # Insert after selected row, or at the end if no selection
        if selected_row >= 0:
            insert_position = selected_row + 1
        else:
            insert_position = -1  # Will be set to end by model
        
        row = self.model.add_application(insert_position)
        if row >= 0:
            # Scroll to new row but don't select it
            new_index = self.model.index(row, self.model.COL_DATE)
            self.table_view.scrollTo(new_index, QAbstractItemView.EnsureVisible)
        return row
    
    def remove_selected_application(self):
        """Remove the currently selected application with confirmation."""
        if self.model.rowCount() == 0:
            self._show_message("No Applications", "There are no applications to remove.")
            return
        
        selected_row = self._get_selected_row()
        if selected_row == -1:
            self._show_message(
                "No Application Selected",
                "Please select an application to remove by clicking on a row.",
                "warning"
            )
            return
        
        # Get display name for confirmation
        product_name = self.model.data(
            self.model.index(selected_row, self.model.COL_PRODUCT_NAME)
        )
        display_name = product_name or "Empty row"
        
        # Confirm removal
        if self._confirm_action(
            "Confirm Removal",
            f"Are you sure you want to remove this application?\n\n"
            f"App # {selected_row + 1}: {display_name}"
        ):
            if not self.model.remove_application(selected_row):
                self._show_message("Removal Failed", "Failed to remove the selected application.", "warning")
    
    def get_applications(self) -> List[Application]:
        """Get all current applications."""
        return self.model.get_applications()
    
    def set_applications(self, applications: List[Application]):
        """Set the applications list."""
        try:
            # Ensure we have Application objects
            app_objects = []
            for app in applications:
                if hasattr(app, 'product_name'):
                    app_objects.append(app)
                else:
                    app_objects.append(Application.from_dict(app))
            
            self.model.set_applications(app_objects)
            self.table_view.reset()
            
        except Exception as e:
            print(f"Error in set_applications(): {e}")
            traceback.print_exc()
    
    def clear_applications(self):
        """Clear all applications from the table."""
        self.model.set_applications([])
    
    def set_field_area(self, area: float, uom: str):
        """Set default field area for new applications."""
        self.model.set_field_area(area, uom)
    
    def get_total_field_eiq(self) -> float:
        """Calculate and return total Field EIQ for all applications."""
        return self.model.get_total_field_eiq()
    
    def refresh_product_data(self):
        """Refresh product data when filtered products change."""
        try:
            # Refresh delegates
            delegates_to_refresh = [
                ('product_name', 'refresh_products'),
                ('product_type', 'refresh_product_types')
            ]
            
            for delegate_name, method_name in delegates_to_refresh:
                delegate = self.delegates.get(delegate_name)
                if delegate and hasattr(delegate, method_name):
                    getattr(delegate, method_name)()
            
            # Recalculate EIQ and refresh display
            self.model._recalculate_all_eiq()
            
            if self.model.rowCount() > 0:
                top_left = self.model.index(0, 0)
                bottom_right = self.model.index(
                    self.model.rowCount() - 1,
                    self.model.columnCount() - 1
                )
                self.model.dataChanged.emit(top_left, bottom_right)
                
        except Exception as e:
            print(f"Error refreshing product data: {e}")
            traceback.print_exc()
    
    def is_delegates_ready(self) -> bool:
        """Check if delegates have been properly assigned."""
        return self._delegates_assigned
    
    def get_delegate_info(self) -> Dict[str, str]:
        """Get information about assigned delegates for debugging."""
        if not self._delegates_assigned:
            return {"status": "Delegates not yet assigned"}
        
        info = {}
        columns = [
            ("reorder", self.model.COL_REORDER),
            ("date", self.model.COL_DATE),
            ("rate", self.model.COL_RATE),
            ("area", self.model.COL_AREA),
            ("product_type", self.model.COL_PRODUCT_TYPE),
            ("method", self.model.COL_METHOD),
            ("product_name", self.model.COL_PRODUCT_NAME),
            ("rate_uom", self.model.COL_RATE_UOM)
        ]
        
        for name, col_index in columns:
            delegate = self.table_view.itemDelegateForColumn(col_index)
            info[name] = delegate.__class__.__name__ if delegate else "No delegate assigned"
        
        return info