"""
Application Table Model for Season Planner V2.

QAbstractTableModel that manages pesticide application data with automatic
EIQ calculations and validation.
"""

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal
from PySide6.QtGui import QColor
from typing import List, Any, Optional
from data import Application, ProductRepository
from common import eiq_calculator, get_config


class ApplicationTableModel(QAbstractTableModel):
    """
    Table model for managing pesticide applications.
    
    Provides a clean interface between Application data objects and the table view,
    with automatic EIQ calculations and validation feedback.
    """
    
    # Signals
    eiq_changed = Signal(float)  # Emitted when total EIQ changes
    validation_changed = Signal()  # Emitted when validation state changes
    
    # Column definitions
    COLUMNS = [
        "App #",
        "Date", 
        "Product",
        "Rate",
        "Rate UOM",
        "Area",
        "Method",
        "AI Groups",
        "Field EIQ"
    ]
    
    # Column indices for easy reference
    COL_APP_NUM = 0
    COL_DATE = 1
    COL_PRODUCT = 2
    COL_RATE = 3
    COL_RATE_UOM = 4
    COL_AREA = 5
    COL_METHOD = 6
    COL_AI_GROUPS = 7
    COL_FIELD_EIQ = 8
    
    # Editable columns
    EDITABLE_COLUMNS = {COL_DATE, COL_PRODUCT, COL_RATE, COL_RATE_UOM, COL_AREA, COL_METHOD}
    
    def __init__(self, parent=None):
        """Initialize the application table model."""
        super().__init__(parent)
        
        # Data storage
        self._applications: List[Application] = []
        self._field_area = 10.0
        self._field_area_uom = "acre"
        
        # Validation tracking
        self._validation_errors = {}  # {(row, col): error_message}
        
        # Repository references
        self._products_repo = ProductRepository.get_instance()
        
        # User preferences for calculations
        self._user_preferences = get_config("user_preferences", {})
    
    # --- QAbstractTableModel Interface ---
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of applications."""
        return len(self._applications)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns."""
        return len(self.COLUMNS)
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        """Return header data for the table."""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.COLUMNS[section]
            elif orientation == Qt.Vertical:
                return str(section + 1)
        return None
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return data for the given index and role."""
        if not index.isValid() or index.row() >= len(self._applications):
            return None
        
        app = self._applications[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._get_cell_data(app, col)
        
        elif role == Qt.BackgroundRole:
            # Yellow background for validation errors
            if (index.row(), col) in self._validation_errors:
                return QColor("#fff3cd")  # Light yellow
        
        elif role == Qt.ToolTipRole:
            # Show validation error as tooltip
            error = self._validation_errors.get((index.row(), col))
            if error:
                return error
        
        return None
    
    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        """Set data for the given index."""
        if not index.isValid() or index.row() >= len(self._applications):
            return False
        
        if role != Qt.EditRole:
            return False
        
        app = self._applications[index.row()]
        col = index.column()
        
        # Only allow editing of editable columns
        if col not in self.EDITABLE_COLUMNS:
            return False
        
        # Validate and set the data
        if self._set_cell_data(app, col, value, index.row()):
            # Emit dataChanged signal
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.BackgroundRole, Qt.ToolTipRole])
            
            # Recalculate dependent fields if necessary
            self._update_dependent_fields(app, col, index.row())
            
            return True
        
        return False
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Return flags for the given index."""
        if not index.isValid():
            return Qt.NoItemFlags
        
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        
        # Make certain columns editable
        if index.column() in self.EDITABLE_COLUMNS:
            flags |= Qt.ItemIsEditable
        
        return flags
    
    def insertRows(self, position: int, rows: int, parent: QModelIndex = QModelIndex()) -> bool:
        """Insert new application rows."""
        self.beginInsertRows(parent, position, position + rows - 1)
        
        for i in range(rows):
            app = Application(
                area=self._field_area,
                application_method="Ground"
            )
            self._applications.insert(position + i, app)
        
        self.endInsertRows()
        self._emit_eiq_changed()
        return True
    
    def removeRows(self, position: int, rows: int, parent: QModelIndex = QModelIndex()) -> bool:
        """Remove application rows."""
        if position < 0 or position >= len(self._applications):
            return False
        
        self.beginRemoveRows(parent, position, position + rows - 1)
        
        for i in range(rows):
            if position < len(self._applications):
                self._applications.pop(position)
        
        self.endRemoveRows()
        self._clear_validation_errors_for_removed_rows(position, rows)
        self._emit_eiq_changed()
        return True
    
    # --- Public Interface ---
    
    def get_applications(self) -> List[Application]:
        """Get all applications."""
        return self._applications.copy()
    
    def set_applications(self, applications: List[Application]):
        """Set the applications list."""
        self.beginResetModel()
        self._applications = applications.copy()
        self._validation_errors.clear()
        self.endResetModel()
        self._recalculate_all_eiq()
        self._emit_eiq_changed()
    
    def add_application(self) -> int:
        """Add a new application and return its row index."""
        row = len(self._applications)
        self.insertRows(row, 1)
        return row
    
    def remove_application(self, row: int) -> bool:
        """Remove application at the given row."""
        return self.removeRows(row, 1)
    
    def set_field_area(self, area: float, uom: str):
        """Set default field area for new applications."""
        self._field_area = area
        self._field_area_uom = uom
    
    def get_total_field_eiq(self) -> float:
        """Calculate total Field EIQ for all applications."""
        return sum(app.field_eiq or 0.0 for app in self._applications)
    
    # --- Private Methods ---
    
    def _get_cell_data(self, app: Application, col: int) -> Any:
        """Get data for a specific cell."""
        if col == self.COL_APP_NUM:
            # App number is the row index + 1
            return self._applications.index(app) + 1
        elif col == self.COL_DATE:
            return app.application_date or ""
        elif col == self.COL_PRODUCT:
            return app.product_name or ""
        elif col == self.COL_RATE:
            return app.rate or 0.0
        elif col == self.COL_RATE_UOM:
            return app.rate_uom or ""
        elif col == self.COL_AREA:
            return app.area or 0.0
        elif col == self.COL_METHOD:
            return app.application_method or ""
        elif col == self.COL_AI_GROUPS:
            return ", ".join(app.ai_groups) if app.ai_groups else ""
        elif col == self.COL_FIELD_EIQ:
            return f"{app.field_eiq:.2f}" if app.field_eiq else "0.00"
        return None
    
    def _set_cell_data(self, app: Application, col: int, value: Any, row: int) -> bool:
        """Set data for a specific cell with validation."""
        # Clear any existing validation error for this cell
        self._validation_errors.pop((row, col), None)
        
        try:
            if col == self.COL_DATE:
                app.application_date = str(value) if value else ""
            
            elif col == self.COL_PRODUCT:
                product_name = str(value) if value else ""
                app.product_name = product_name
                
                # Auto-populate product type if product is found
                if product_name:
                    product = self._find_product(product_name)
                    if product:
                        app.product_type = product.product_type
                    else:
                        app.product_type = "Unknown"
                        self._validation_errors[(row, col)] = "Product not found in database"
            
            elif col == self.COL_RATE:
                rate = float(value) if value else 0.0
                if rate < 0:
                    self._validation_errors[(row, col)] = "Rate must be positive"
                    return False
                app.rate = rate
            
            elif col == self.COL_RATE_UOM:
                app.rate_uom = str(value) if value else ""
            
            elif col == self.COL_AREA:
                area = float(value) if value else 0.0
                if area < 0:
                    self._validation_errors[(row, col)] = "Area must be positive"
                    return False
                app.area = area
            
            elif col == self.COL_METHOD:
                app.application_method = str(value) if value else ""
            
            return True
            
        except (ValueError, TypeError) as e:
            self._validation_errors[(row, col)] = f"Invalid value: {e}"
            return False
    
    def _update_dependent_fields(self, app: Application, changed_col: int, row: int):
        """Update fields that depend on the changed column."""
        if changed_col == self.COL_PRODUCT:
            # Product changed - update AI groups and recalculate EIQ
            self._update_ai_groups(app, row)
            self._calculate_field_eiq(app, row)
        
        elif changed_col in {self.COL_RATE, self.COL_RATE_UOM}:
            # Rate parameters changed - recalculate EIQ
            self._calculate_field_eiq(app, row)
        
        # Emit dataChanged for potentially affected columns
        affected_cols = []
        if changed_col == self.COL_PRODUCT:
            affected_cols = [self.COL_AI_GROUPS, self.COL_FIELD_EIQ]
        elif changed_col in {self.COL_RATE, self.COL_RATE_UOM}:
            affected_cols = [self.COL_FIELD_EIQ]
        
        for col in affected_cols:
            index = self.index(row, col)
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.BackgroundRole, Qt.ToolTipRole])
    
    def _update_ai_groups(self, app: Application, row: int):
        """Update AI groups based on the selected product."""
        if not app.product_name:
            app.ai_groups = []
            return
        
        product = self._find_product(app.product_name)
        if product:
            ai_groups = product.get_ai_groups()
            app.ai_groups = [group for group in ai_groups if group]
        else:
            app.ai_groups = []
    
    def _calculate_field_eiq(self, app: Application, row: int):
        """Calculate Field EIQ for a single application."""
        if not app.product_name or not app.rate or not app.rate_uom:
            app.field_eiq = 0.0
            return
        
        product = self._find_product(app.product_name)
        if not product:
            app.field_eiq = 0.0
            self._validation_errors[(row, self.COL_FIELD_EIQ)] = "Cannot calculate EIQ: product not found"
            return
        
        try:
            ai_data = product.get_ai_data()
            if not ai_data:
                app.field_eiq = 0.0
                self._validation_errors[(row, self.COL_FIELD_EIQ)] = "Cannot calculate EIQ: no active ingredient data"
                return
            
            field_eiq = eiq_calculator.calculate_product_field_eiq(
                active_ingredients=ai_data,
                application_rate=app.rate,
                application_rate_uom=app.rate_uom,
                applications=1,
                user_preferences=self._user_preferences
            )
            
            app.field_eiq = field_eiq
            self._validation_errors.pop((row, self.COL_FIELD_EIQ), None)
            
        except Exception as e:
            app.field_eiq = 0.0
            self._validation_errors[(row, self.COL_FIELD_EIQ)] = f"EIQ calculation error: {e}"
    
    def _find_product(self, product_name: str):
        """Find a product by name in the filtered products list."""
        if not product_name:
            return None
        
        filtered_products = self._products_repo.get_filtered_products()
        for product in filtered_products:
            if product.product_name == product_name:
                return product
        return None
    
    def _recalculate_all_eiq(self):
        """Recalculate EIQ for all applications."""
        for row, app in enumerate(self._applications):
            self._update_ai_groups(app, row)
            self._calculate_field_eiq(app, row)
    
    def _emit_eiq_changed(self):
        """Emit signal when total EIQ changes."""
        total_eiq = self.get_total_field_eiq()
        self.eiq_changed.emit(total_eiq)
    
    def _clear_validation_errors_for_removed_rows(self, position: int, rows: int):
        """Clear validation errors for removed rows and adjust indices."""
        # Remove errors for deleted rows
        keys_to_remove = []
        keys_to_update = {}
        
        for (row, col), error in self._validation_errors.items():
            if position <= row < position + rows:
                # Row was deleted
                keys_to_remove.append((row, col))
            elif row >= position + rows:
                # Row index needs to be adjusted
                keys_to_update[(row - rows, col)] = error
                keys_to_remove.append((row, col))
        
        # Apply changes
        for key in keys_to_remove:
            self._validation_errors.pop(key, None)
        
        for key, error in keys_to_update.items():
            self._validation_errors[key] = error