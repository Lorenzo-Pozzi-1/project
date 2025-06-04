"""
Applications Table Widget for Season Planner V2.

Final production version with sequential delegate assignment to avoid Qt conflicts.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton, QHeaderView, QAbstractItemView
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from typing import List

from common import create_button, GENERIC_TABLE_STYLE
from data import Application
from ..models.application_table_model import ApplicationTableModel
from ..delegates.date_delegate import DateDelegate
from ..delegates.numeric_delegate import RateDelegate, AreaDelegate
from ..delegates.method_delegate import MethodDelegate
from ..delegates.product_delegate import ProductDelegate
from ..delegates.uom_delegate import UOMDelegate


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
        self.setup_shortcuts()
        
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
        self.table_view.setSortingEnabled(False)  # Disable to maintain order
        
        # Configure editing
        self.table_view.setEditTriggers(
            QAbstractItemView.DoubleClicked | 
            QAbstractItemView.EditKeyPressed |
            QAbstractItemView.AnyKeyPressed
        )
        
        # Set alternating row colors
        self.table_view.setAlternatingRowColors(True)
        
        # Set initial column widths
        self._set_initial_column_widths()
    
    def _set_initial_column_widths(self):
        """Set initial column widths for better appearance."""
        header = self.table_view.horizontalHeader()
        
        # Column widths (in pixels)
        column_widths = {
            self.model.COL_APP_NUM: 60,    # App #
            self.model.COL_DATE: 100,      # Date
            self.model.COL_PRODUCT: 200,   # Product (widest)
            self.model.COL_RATE: 80,       # Rate
            self.model.COL_RATE_UOM: 100,  # Rate UOM
            self.model.COL_AREA: 80,       # Area
            self.model.COL_METHOD: 120,    # Method
            self.model.COL_AI_GROUPS: 150, # AI Groups
            self.model.COL_FIELD_EIQ: 80   # Field EIQ
        }
        
        for col, width in column_widths.items():
            header.resizeSection(col, width)
        
        # Make product column stretch to fill available space
        header.setSectionResizeMode(self.model.COL_PRODUCT, QHeaderView.Stretch)
    
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
            method_delegate = MethodDelegate(self)
            self.table_view.setItemDelegateForColumn(self.model.COL_METHOD, method_delegate)
            
            product_delegate = ProductDelegate(self)
            self.table_view.setItemDelegateForColumn(self.model.COL_PRODUCT, product_delegate)
            
            uom_delegate = UOMDelegate(self, uom_type="application_rate")
            self.table_view.setItemDelegateForColumn(self.model.COL_RATE_UOM, uom_delegate)
            
        except Exception as e:
            print(f"Error in _setup_complex_delegates(): {e}")
    
    def setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # F2 to edit current cell
        edit_shortcut = QShortcut(QKeySequence(Qt.Key_F2), self.table_view)
        edit_shortcut.activated.connect(self._edit_current_cell)
        
        # Delete key to remove selected row
        delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self.table_view)
        delete_shortcut.activated.connect(self.remove_selected_application)
        
        # Insert key to add new row
        insert_shortcut = QShortcut(QKeySequence(Qt.Key_Insert), self.table_view)
        insert_shortcut.activated.connect(self.add_application)
    
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
        current_row = self.table_view.currentIndex().row()
        if current_row >= 0:
            self.model.remove_application(current_row)
    
    def get_applications(self) -> List[Application]:
        """Get all applications."""
        return self.model.get_applications()
    
    def set_applications(self, applications: List[Application]):
        """Set the applications list."""
        self.model.set_applications(applications)
    
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