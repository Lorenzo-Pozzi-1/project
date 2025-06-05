"""
Applications Table Widget for Season Planner V2.

Final production version with sequential delegate assignment to avoid Qt conflicts.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView, QAbstractItemView
from PySide6.QtCore import Signal, QTimer
from typing import List

from common import create_button, GENERIC_TABLE_STYLE, get_medium_font
from data import Application
from ..models.application_table_model import ApplicationTableModel
from ..delegates.date_delegate import DateDelegate
from ..delegates.numeric_delegate import RateDelegate, AreaDelegate
from ..delegates.method_delegate import MethodDelegate
from ..delegates.product_name_delegate import ProductNameDelegate
from ..delegates.uom_delegate import UOMDelegate
from ..delegates.product_type_delegate import ProductTypeDelegate


class ApplicationsTableWidget(QWidget):
    """
    Main applications table widget with Excel-like editing capabilities.
    
    Uses sequential delegate assignment to avoid Qt initialization conflicts.
    Combines QTableView with ApplicationTableModel and custom delegates
    to provide a clean, professional table interface.
    """
    
    # Signals
    applications_changed = Signal()  # Emitted when applications data changes
    eiq_changed = Signal(float)  # Emitted when total EIQ changes
    
    def __init__(self, parent=None):
        """Initialize the applications table widget."""
        super().__init__(parent)
        
        # Create the model
        self.model = ApplicationTableModel()
        self.model.eiq_changed.connect(self.eiq_changed)
        self.model.dataChanged.connect(lambda: self.applications_changed.emit())
        self.model.rowsInserted.connect(lambda: self.applications_changed.emit())
        self.model.rowsRemoved.connect(lambda: self.applications_changed.emit())
        
        self.setup_ui()
        
        # IMPORTANT: Set up delegates after widget initialization to avoid Qt conflicts
        QTimer.singleShot(100, self.setup_delegates_sequential)
    
    def setup_ui(self):
        """Set up the UI components."""
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
        self.table_view.setStyleSheet(GENERIC_TABLE_STYLE)
        
        # Configure selection
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Configure headers
        horizontal_header = self.table_view.horizontalHeader()
        horizontal_header.setSectionResizeMode(QHeaderView.Interactive)
        horizontal_header.setStretchLastSection(False)
        
        vertical_header = self.table_view.verticalHeader()
        vertical_header.setVisible(False)  # Hide row numbers (we have App # column)
        
        # Enable sorting
        # self.table_view.setSortingEnabled(False)  # Disable to maintain order
        
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
        """Set all columns to equal width with uniform stretching."""
        header = self.table_view.horizontalHeader()
        
        # Set all columns to stretch equally
        for col in range(self.model.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
            
            # Make product column stretch to fill available space
            header.setSectionResizeMode(self.model.COL_PRODUCT_NAME, QHeaderView.Stretch)
    
    def setup_delegates_sequential(self):
        """
        Set up delegates sequentially to avoid Qt initialization conflicts.
        
        This method assigns delegates one by one with small delays to prevent
        the crashes that occur when multiple delegates are assigned simultaneously.
        """
        try:
            # Phase 1: Simple text-based delegates
            date_delegate = DateDelegate(self)
            self.table_view.setItemDelegateForColumn(self.model.COL_DATE, date_delegate)
            
            # Phase 2: Numeric delegates with small delay
            QTimer.singleShot(25, self._setup_numeric_delegates)
            
        except Exception as e:
            print(f"Error in setup_delegates_sequential(): {e}")
    
    def _setup_numeric_delegates(self):
        """Set up numeric delegates."""
        try:
            rate_delegate = RateDelegate(self)
            self.table_view.setItemDelegateForColumn(self.model.COL_RATE, rate_delegate)
            
            area_delegate = AreaDelegate(self)
            self.table_view.setItemDelegateForColumn(self.model.COL_AREA, area_delegate)
            
            # Phase 3: Complex delegates with delay
            QTimer.singleShot(25, self._setup_complex_delegates)
            
        except Exception as e:
            print(f"Error in _setup_numeric_delegates(): {e}")
    
    def _setup_complex_delegates(self):
        """Set up complex delegates (dialogs, combos)."""
        try:
            # Product type delegate (column 2)
            product_type_delegate = ProductTypeDelegate(self)
            self.table_view.setItemDelegateForColumn(self.model.COL_PRODUCT_TYPE, product_type_delegate)
            
            # Method delegate (column 7)
            method_delegate = MethodDelegate(self)
            self.table_view.setItemDelegateForColumn(self.model.COL_METHOD, method_delegate)
            
            # Product delegate (column 3) - this will auto-populate rate/UOM
            product_name_delegate = ProductNameDelegate(self)
            self.table_view.setItemDelegateForColumn(self.model.COL_PRODUCT_NAME, product_name_delegate)
            
            # UOM delegate (column 5)
            uom_delegate = UOMDelegate(self, uom_type="application_rate")
            self.table_view.setItemDelegateForColumn(self.model.COL_RATE_UOM, uom_delegate)
            
        except Exception as e:
            print(f"Error in _setup_complex_delegates(): {e}")
            import traceback
            traceback.print_exc()
    
    def _edit_current_cell(self):
        """Start editing the current cell."""
        current_index = self.table_view.currentIndex()
        if current_index.isValid():
            self.table_view.edit(current_index)
    
    # --- Public Interface ---
    
    def add_application(self):
        """Add a new application row."""
        row = self.model.add_application()
        
        # Select the new row
        if row >= 0:
            new_index = self.model.index(row, self.model.COL_DATE)
            self.table_view.setCurrentIndex(new_index)
            self.table_view.selectRow(row)
        
        return row
    
    def remove_selected_application(self):
        """Remove the currently selected application."""
        # Get the current selection
        selection_model = self.table_view.selectionModel()
        
        if not selection_model.hasSelection():
            # No selection - show warning dialog
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "No Application Selected",
                "Please select an application to remove.",
                QMessageBox.Ok
            )
            return
        
        # Get the selected row
        selected_indexes = selection_model.selectedRows()
        if not selected_indexes:
            # Fallback check - should not happen but be safe
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "No Application Selected", 
                "Please select an application to remove.",
                QMessageBox.Ok
            )
            return
        
        # Get the row number from the first selected index
        current_row = selected_indexes[0].row()
        
        # Validate row number
        if current_row < 0 or current_row >= self.model.rowCount():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Invalid Selection",
                "The selected application is no longer valid.",
                QMessageBox.Ok
            )
            return
        
        # Optional: Show confirmation dialog for deletion
        from PySide6.QtWidgets import QMessageBox
        
        # Get application info for confirmation
        app_data = self.model.get_applications()[current_row]
        product_name = app_data.product_name or "Unnamed Application"
        
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove this application?\n\n{product_name}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove the application
            self.model.remove_application(current_row)
    
    def get_applications(self) -> List[Application]:
        """Get all applications."""
        return self.model.get_applications()
    
    def set_applications(self, applications: List[Application]):
        """Set the applications list."""
        try:
            # Ensure we have Application objects
            app_objects = []
            for i, app in enumerate(applications):
                if hasattr(app, 'product_name'):
                    # It's already an Application object
                    app_objects.append(app)
                    print(f"  App {i+1}: {app.product_name} @ {getattr(app, 'rate', 'N/A')} {getattr(app, 'rate_uom', 'N/A')}")
                else:
                    # Convert dict to Application
                    from data import Application
                    app_obj = Application.from_dict(app)
                    app_objects.append(app_obj)
                    print(f"  App {i+1} (converted): {app_obj.product_name} @ {app_obj.rate} {app_obj.rate_uom}")
            
            # Set applications in model
            self.model.set_applications(app_objects)
            
            # Force view update
            self.table_view.reset()
            
        except Exception as e:
            print(f"ERROR in set_applications(): {e}")
            import traceback
            traceback.print_exc()
    
    def clear_applications(self):
        """Clear all applications."""
        self.model.set_applications([])
    
    def set_field_area(self, area: float, uom: str):
        """Set default field area for new applications."""
        self.model.set_field_area(area, uom)
    
    def get_total_field_eiq(self) -> float:
        """Get total Field EIQ for all applications."""
        return self.model.get_total_field_eiq()
    
    def refresh_product_data(self):
        """Refresh product data when filtered products change."""
        # Force recalculation of all EIQ values
        self.model._recalculate_all_eiq()
        
        # Emit data changed for all cells to refresh display
        if self.model.rowCount() > 0:
            top_left = self.model.index(0, 0)
            bottom_right = self.model.index(
                self.model.rowCount() - 1, 
                self.model.columnCount() - 1
            )
            self.model.dataChanged.emit(top_left, bottom_right)

    def refresh_product_data(self):
        """Refresh product data when filtered products change."""
        # Refresh product data in the ProductNameDelegate
        product_name_delegate = self.table_view.itemDelegateForColumn(self.model.COL_PRODUCT_NAME)
        if hasattr(product_name_delegate, 'refresh_products'):
            product_name_delegate.refresh_products()
        
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