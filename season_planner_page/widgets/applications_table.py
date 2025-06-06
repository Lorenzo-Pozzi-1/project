"""
Applications Table Widget for the Season Planner.

Rewritten version with proper Qt lifecycle management and deterministic delegate timing.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView, QAbstractItemView, QMessageBox
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
    """
    Main applications table widget with Excel-like editing capabilities.
    
    Uses proper Qt lifecycle management to avoid delegate initialization race conditions.
    Delegates are created during construction but only assigned after the widget is shown
    and geometry is properly established.
    """
    
    # Signals
    applications_changed = Signal()  # Emitted when applications data changes
    eiq_changed = Signal(float)  # Emitted when total EIQ changes
    
    def __init__(self, parent=None):
        """Initialize the applications table widget."""
        super().__init__(parent)
        
        # Create the model first
        self.model = ApplicationTableModel()
        self.model.eiq_changed.connect(self.eiq_changed)
        self.model.dataChanged.connect(lambda: self.applications_changed.emit())
        self.model.rowsInserted.connect(lambda: self.applications_changed.emit())
        self.model.rowsRemoved.connect(lambda: self.applications_changed.emit())
        
        # Create delegates immediately but don't assign them yet
        self._create_delegates()
        
        # Set up UI
        self.setup_ui()
        
        # Track delegate assignment state
        self._delegates_assigned = False
    
    def _create_delegates(self):
        """
        Create all delegate instances with proper parent relationships.
          Delegates are created here but not assigned to columns until showEvent().
        This ensures they have proper parent-child relationships while avoiding
        Qt initialization timing issues.
        """
        self.delegates: Dict[str, Any] = {
            'reorder': ReorderDelegate(self),
            'date': DateDelegate(self),
            'rate': RateDelegate(self), 
            'area': AreaDelegate(self),
            'product_type': ProductTypeDelegate(self),
            'method': MethodDelegate(self),
            'product_name': ProductNameDelegate(self),
            'rate_uom': UOMDelegate(self, uom_type="application_rate")
        }
        
        # Connect reorder delegate signals
        self.delegates['reorder'].move_up.connect(self._on_move_up)
        self.delegates['reorder'].move_down.connect(self._on_move_down)
        
        # Store delegate references to prevent garbage collection
        # This is critical - without these references, delegates can be destroyed
        for delegate in self.delegates.values():
            delegate.setParent(self)
    
    def setup_ui(self):
        """Set up the UI components without delegate assignment."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Create table view
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        
        # Configure table view
        self._configure_table_view()
        
        layout.addWidget(self.table_view)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.add_button = create_button(
            text="Add Application", 
            style="white", 
            callback=self.add_application
        )
        button_layout.addWidget(self.add_button)
        
        self.remove_button = create_button(
            text="Remove Selected", 
            style="white", 
            callback=self.remove_selected_application
        )
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def _configure_table_view(self):
        """Configure the table view appearance and behavior."""
        # Set style
        self.table_view.setStyleSheet(GENERIC_TABLE_STYLE + """
            QTableView::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        
        # Configure selection
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Configure headers
        horizontal_header = self.table_view.horizontalHeader()
        horizontal_header.setSectionResizeMode(QHeaderView.Interactive)
        horizontal_header.setStretchLastSection(False)
        
        vertical_header = self.table_view.verticalHeader()
        vertical_header.setVisible(False)  # Hide row numbers (we have App # column)
        
        # Configure editing
        self.table_view.setEditTriggers(
            QAbstractItemView.DoubleClicked | 
            QAbstractItemView.EditKeyPressed |
            QAbstractItemView.AnyKeyPressed
        )
        
        # Set alternating row colors
        self.table_view.setAlternatingRowColors(True)
          # Set the table contents to use the medium font
        self.table_view.setFont(get_medium_font()) 

        # Set initial column widths
        self._set_initial_column_widths()
    
    def _set_initial_column_widths(self):
        """Set column width policies."""
        header = self.table_view.horizontalHeader()
        
        # Set reorder column to fixed width (just needs space for up/down buttons)
        if self.model.columnCount() > self.model.COL_REORDER:
            header.setSectionResizeMode(self.model.COL_REORDER, QHeaderView.Fixed)
            header.resizeSection(self.model.COL_REORDER, 80)  # Fixed width for buttons
        
        # Set all other columns to stretch equally
        for col in range(self.model.columnCount()):
            if col != self.model.COL_REORDER:
                header.setSectionResizeMode(col, QHeaderView.Stretch)
            
        # Make product name column stretch more to accommodate longer names
        if self.model.columnCount() > self.model.COL_PRODUCT_NAME:
            header.setSectionResizeMode(self.model.COL_PRODUCT_NAME, QHeaderView.Stretch)
    
    def showEvent(self, event: QShowEvent):
        """
        Handle widget show event - assign delegates when geometry is ready.
        
        This is the critical timing fix. Qt guarantees that when showEvent() fires:
        - Widget geometry is valid and established
        - Event loop is properly initialized
        - Parent-child relationships are stable
        - All UI components are ready for delegate assignment
        """
        super().showEvent(event)
        
        # Only assign delegates once, on first show
        if not self._delegates_assigned:
            self._assign_delegates_to_columns()
            self._delegates_assigned = True
    
    def _assign_delegates_to_columns(self):
        """
        Assign pre-created delegates to their respective table columns.
        
        This method is called from showEvent() when we're guaranteed that:
        - Table geometry is valid
        - Model is properly attached
        - Event handling is ready
        """
        try:    
            # Define column-to-delegate mapping
            column_assignments = {
                self.model.COL_REORDER: self.delegates['reorder'],
                self.model.COL_DATE: self.delegates['date'],
                self.model.COL_RATE: self.delegates['rate'],
                self.model.COL_AREA: self.delegates['area'],
                self.model.COL_PRODUCT_TYPE: self.delegates['product_type'],
                self.model.COL_METHOD: self.delegates['method'],
                self.model.COL_PRODUCT_NAME: self.delegates['product_name'],
                self.model.COL_RATE_UOM: self.delegates['rate_uom']
            }
            
            # Assign each delegate to its column
            for column_index, delegate in column_assignments.items():
                if column_index < self.model.columnCount():
                    self.table_view.setItemDelegateForColumn(column_index, delegate)
                else:
                    print(f"Warning: Column index {column_index} exceeds model column count")
            
            print(f"Successfully assigned {len(column_assignments)} delegates to table columns")
            
        except Exception as e:
            print(f"Error assigning delegates to columns: {e}")
            traceback.print_exc()
            # Don't re-raise - we want the table to remain functional even if delegates fail
    
    def _validate_delegate_assignment(self) -> bool:
        """
        Validate that delegates are properly assigned and functional.
        
        Returns:
            bool: True if all expected delegates are assigned, False otherwise
        """
        expected_columns = [
            self.model.COL_REORDER,
            self.model.COL_DATE,
            self.model.COL_RATE,
            self.model.COL_AREA,
            self.model.COL_PRODUCT_TYPE,
            self.model.COL_METHOD,
            self.model.COL_PRODUCT_NAME,
            self.model.COL_RATE_UOM
        ]
        
        for col in expected_columns:
            delegate = self.table_view.itemDelegateForColumn(col)
            if delegate is None or delegate == self.table_view.itemDelegate():
                print(f"Warning: Column {col} does not have a custom delegate assigned")
                return False
        
        return True
    
    def _on_move_up(self, row: int):
        """Handle move up signal from reorder delegate."""
        if self.model.move_application_up(row):
            # Update selection to follow the moved row
            new_index = self.model.index(row - 1, self.model.COL_REORDER)
            self.table_view.selectionModel().setCurrentIndex(new_index, self.table_view.selectionModel().SelectionFlag.ClearAndSelect | self.table_view.selectionModel().SelectionFlag.Rows)
            self.applications_changed.emit()
    
    def _on_move_down(self, row: int):
        """Handle move down signal from reorder delegate."""
        if self.model.move_application_down(row):
            # Update selection to follow the moved row
            new_index = self.model.index(row + 1, self.model.COL_REORDER)
            self.table_view.selectionModel().setCurrentIndex(new_index, self.table_view.selectionModel().SelectionFlag.ClearAndSelect | self.table_view.selectionModel().SelectionFlag.Rows)
            self.applications_changed.emit()
    
    # --- Public Interface Methods ---
    
    def add_application(self):
        """Add a new application row."""
        row = self.model.add_application()
        
        # Just scroll to show the new row, but don't select it
        if row >= 0:
            new_index = self.model.index(row, self.model.COL_DATE)
            self.table_view.scrollTo(new_index, QAbstractItemView.EnsureVisible)
            # Don't select - let user explicitly choose what to select
        
        return row
    
    def remove_selected_application(self):
        """Remove the currently selected application with confirmation."""
        # Get the current selection
        selection_model = self.table_view.selectionModel()
        
        # Check if we have any applications at all
        if self.model.rowCount() == 0:
            QMessageBox.information(
                self,
                "No Applications",
                "There are no applications to remove.",
                QMessageBox.Ok
            )
            return
        
        # More robust selection detection
        selected_rows = selection_model.selectedRows()
        current_index = selection_model.currentIndex()
        
        # Check for explicit row selection (user clicked on a row)
        has_explicit_selection = (
            len(selected_rows) > 0 and 
            any(self.table_view.selectionModel().isRowSelected(idx.row()) for idx in selected_rows)
        )
        
        if not has_explicit_selection:
            # No explicit selection - show warning dialog
            QMessageBox.warning(
                self,
                "No Application Selected",
                "Please select an application to remove by clicking on a row.\n\n"
                "Tip: Click on any cell in the row you want to remove.",
                QMessageBox.Ok
            )
            return
        
        # Get the explicitly selected row
        if not selected_rows:
            # Fallback check - should not happen given the above logic
            QMessageBox.warning(
                self,
                "Selection Error", 
                "Unable to determine which row is selected. Please try again.",
                QMessageBox.Ok
            )
            return
        
        # Get the row number from the first selected index
        current_row = selected_rows[0].row()
        
        # Validate row number against BOTH model and view
        if current_row < 0 or current_row >= self.model.rowCount():
            QMessageBox.warning(
                self,
                "Invalid Selection",
                f"The selected row ({current_row}) is not valid. Please select a visible application.",
                QMessageBox.Ok
            )
            return
        
        # Confirm removal
        # Get product name or use "Empty row" if not available
        product_name = self.model.data(self.model.index(current_row, self.model.COL_PRODUCT_NAME))
        display_name = product_name if product_name else "Empty row"
        
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove this application?\n\nApp # {current_row+1}: {display_name}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove the application
            success = self.model.remove_application(current_row)
            if not success:
                QMessageBox.warning(
                    self,
                    "Removal Failed",
                    "Failed to remove the selected application.",
                    QMessageBox.Ok
                )
    
    def get_applications(self) -> List[Application]:
        """Get all current applications."""
        return self.model.get_applications()
    
    def set_applications(self, applications: List[Application]):
        """
        Set the applications list.
        
        Args:
            applications: List of Application objects to display
        """
        try:
            # Ensure we have Application objects
            app_objects = []
            for i, app in enumerate(applications):
                if hasattr(app, 'product_name'):
                    # It's already an Application object
                    app_objects.append(app)
                else:
                    # Convert dict to Application if needed
                    from data import Application
                    app_obj = Application.from_dict(app)
                    app_objects.append(app_obj)
            
            # Set applications in model
            self.model.set_applications(app_objects)
            
            # Force view refresh
            self.table_view.reset()
            
        except Exception as e:
            print(f"ERROR in set_applications(): {e}")
            traceback.print_exc()
    
    def clear_applications(self):
        """Clear all applications from the table."""
        self.model.set_applications([])
    
    def set_field_area(self, area: float, uom: str):
        """
        Set default field area for new applications.
        
        Args:
            area: Field area value
            uom: Field area unit of measure
        """
        self.model.set_field_area(area, uom)
    
    def get_total_field_eiq(self) -> float:
        """Calculate and return total Field EIQ for all applications."""
        return self.model.get_total_field_eiq()
    
    def refresh_product_data(self):
        """
        Refresh product data when filtered products change in the main application.
        
        This method is called when the main window's product filters change,
        requiring delegates to refresh their product lists and the model to
        recalculate EIQ values.
        """
        try:
            # Refresh product data in the ProductNameDelegate
            product_name_delegate = self.delegates.get('product_name')
            if product_name_delegate and hasattr(product_name_delegate, 'refresh_products'):
                product_name_delegate.refresh_products()
            
            # Refresh product data in the ProductTypeDelegate
            product_type_delegate = self.delegates.get('product_type')
            if product_type_delegate and hasattr(product_type_delegate, 'refresh_product_types'):
                product_type_delegate.refresh_product_types()
            
            # Force recalculation of all EIQ values since product availability may have changed
            self.model._recalculate_all_eiq()
            
            # Emit data changed for all cells to refresh display
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
        """
        Check if delegates have been properly assigned and are ready for use.
        
        Returns:
            bool: True if delegates are assigned and functional
        """
        return self._delegates_assigned and self._validate_delegate_assignment()
    def get_delegate_info(self) -> Dict[str, str]:
        """
        Get information about assigned delegates for debugging.
        
        Returns:
            Dict mapping column names to delegate class names
        """
        if not self._delegates_assigned:
            return {"status": "Delegates not yet assigned"}
        
        delegate_info = {}
        column_names = [
            ("reorder", self.model.COL_REORDER),
            ("date", self.model.COL_DATE),
            ("rate", self.model.COL_RATE),
            ("area", self.model.COL_AREA),
            ("product_type", self.model.COL_PRODUCT_TYPE),
            ("method", self.model.COL_METHOD),
            ("product_name", self.model.COL_PRODUCT_NAME),
            ("rate_uom", self.model.COL_RATE_UOM)
        ]
        
        for name, col_index in column_names:
            delegate = self.table_view.itemDelegateForColumn(col_index)
            if delegate:
                delegate_info[name] = delegate.__class__.__name__
            else:
                delegate_info[name] = "No delegate assigned"
        
        return delegate_info