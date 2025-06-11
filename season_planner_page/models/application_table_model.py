"""
Application Table Model for the Season Planner.

Clean Qt model interface with validation and EIQ calculation delegated to separate services.
"""

from dataclasses import dataclass
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal
from PySide6.QtGui import QColor
from typing import List, Any, Optional
from data import Application, ProductRepository
from common import get_config
from .application_validator import ApplicationValidator, ValidationState
from .application_eiq_calculator import ApplicationEIQCalculator


@dataclass
class ColumnDefinition:
    """Definition for a table column."""
    index: int
    name: str
    editable: bool


class ApplicationTableModel(QAbstractTableModel):
    """
    table model for managing pesticide applications.
    
    Focuses on Qt interface while delegating validation and calculations
    to dedicated service classes.
    """
    
    # Signals
    eiq_changed = Signal(float)
    validation_changed = Signal()
    
    # Column definitions
    _COLUMN_DEFS = [
        ColumnDefinition(0, "Reorder", True),
        ColumnDefinition(1, "App #", False),
        ColumnDefinition(2, "Date", True),
        ColumnDefinition(3, "Product Type", True),
        ColumnDefinition(4, "Product Name", True),
        ColumnDefinition(5, "Rate", True),
        ColumnDefinition(6, "Rate UOM", True),
        ColumnDefinition(7, "Area", True),
        ColumnDefinition(8, "Method", True),
        ColumnDefinition(9, "AI Groups", False),
        ColumnDefinition(10, "Field EIQ", False),
        ColumnDefinition(11, "Status", False),
    ]
    
    COLUMNS = [col.name for col in _COLUMN_DEFS]
    EDITABLE_COLUMNS = {col.index for col in _COLUMN_DEFS if col.editable}
    _COLUMN_INDEX_MAP = {col.name: col.index for col in _COLUMN_DEFS}

    @classmethod
    def _col_index(cls, name: str) -> int:
        """Helper method to find column indexes by name."""
        if name not in cls._COLUMN_INDEX_MAP:
            raise ValueError(f"Column '{name}' not found")
        return cls._COLUMN_INDEX_MAP[name]
    
    def __init__(self, parent=None):
        """Initialize the application table model."""
        super().__init__(parent)
        
        # Data storage
        self._applications: List[Application] = []
        self._validation_cache: dict[int, Any] = {}
        self._field_area = 10.0
        self._field_area_uom = "acre"
        
        # Service classes
        self._validator = ApplicationValidator()
        self._eiq_calculator = ApplicationEIQCalculator(get_config("user_preferences", {}))
        
        # Repository references
        self._products_repo = ProductRepository.get_instance()

    # --- QAbstractTableModel Interface ---
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of applications."""
        if parent.isValid():
            return 0
        return len(self._applications)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns."""
        if parent.isValid():
            return 0
        return len(self.COLUMNS)
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        """Return header data for the table."""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal and 0 <= section < len(self.COLUMNS):
                return self.COLUMNS[section]
            elif orientation == Qt.Vertical:
                return str(section + 1)
        return None
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return data for the given index and role."""
        if not index.isValid() or index.row() >= len(self._applications):
            return None
        
        try:
            app = self._applications[index.row()]
            col = index.column()
            
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return self._get_cell_data(app, col, index.row())
            elif role == Qt.BackgroundRole:
                return self._get_cell_background(app, col, index.row())
            elif role == Qt.ToolTipRole:
                return self._get_cell_tooltip(app, col, index.row())
        
        except Exception as e:
            print(f"Error in data() method: {e}")
            return None
        
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        """Set data for the given index."""
        if not index.isValid() or index.row() >= len(self._applications):
            return False
        
        if role != Qt.EditRole or index.column() not in self.EDITABLE_COLUMNS:
            return False
        
        try:
            app = self._applications[index.row()]
            row = index.row()
            col = index.column()
            
            # Set the data
            if self._set_cell_data(app, col, value):
                # Clear validation cache for this row
                if self._affects_validation(col):
                    self._validation_cache.pop(row, None)
                
                # Update dependent fields
                self._update_dependent_fields(app, col, row)
                
                # Emit signals
                self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.BackgroundRole, Qt.ToolTipRole])
                self._emit_signals()
                
                return True
                
        except Exception as e:
            print(f"Error in setData(): {e}")
            return False
        
        return False
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Return flags for the given index."""
        if not index.isValid():
            return Qt.NoItemFlags
        
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        
        if index.column() in self.EDITABLE_COLUMNS:
            flags |= Qt.ItemIsEditable
        
        return flags
    
    def insertRows(self, position: int, rows: int, parent: QModelIndex = QModelIndex()) -> bool:
        """Insert new application rows."""
        if parent.isValid():
            return False
            
        if position < 0 or position > len(self._applications):
            position = len(self._applications)
        
        try:            
            self.beginInsertRows(parent, position, position + rows - 1)
            
            for i in range(rows):
                app = Application(
                    area=self._field_area,
                    application_method=""
                )
                self._applications.insert(position + i, app)
            
            self.endInsertRows()
            self._clear_validation_cache()
            self._recalculate_all_eiq()
            self._emit_signals()
            return True
            
        except Exception as e:
            print(f"Error in insertRows(): {e}")
            return False
    
    def removeRows(self, position: int, rows: int, parent: QModelIndex = QModelIndex()) -> bool:
        """Remove application rows."""
        if parent.isValid() or position < 0 or position >= len(self._applications):
            return False
        
        rows = min(rows, len(self._applications) - position)
        if rows <= 0:
            return False
        
        try:
            self.beginRemoveRows(parent, position, position + rows - 1)
            
            for _ in range(rows):
                if position < len(self._applications):
                    self._applications.pop(position)
            
            self.endRemoveRows()
            self._clear_validation_cache()
            self._recalculate_all_eiq()
            self._emit_signals()
            return True
            
        except Exception as e:
            print(f"Error in removeRows(): {e}")
            return False

    # --- Public Interface ---
    
    def get_applications(self) -> List[Application]:
        """Get all applications."""
        return self._applications.copy()
    
    def set_applications(self, applications: List[Application]):
        """Set the applications list."""
        try:
            self.beginResetModel()
            
            self._applications = []
            for app in applications:
                if hasattr(app, 'product_name'):
                    self._applications.append(app)
                else:
                    self._applications.append(Application.from_dict(app))
            
            self.endResetModel()
            self._clear_validation_cache()
            self._recalculate_all_eiq()
            self._emit_signals()
            
        except Exception as e:
            print(f"Error in set_applications(): {e}")
            self.endResetModel()

    def add_application(self, position: int = -1) -> int:
        """Add a new application and return its row index."""
        if position < 0 or position > len(self._applications):
            position = len(self._applications)
        
        if self.insertRows(position, 1):
            return position
        return -1
    
    def remove_application(self, row: int) -> bool:
        """Remove application at the given row."""
        return self.removeRows(row, 1)
    
    def set_field_area(self, area: float, uom: str):
        """Set default field area for new applications."""
        self._field_area = area
        self._field_area_uom = uom
    
    def get_total_field_eiq(self) -> float:
        """Calculate total Field EIQ for all valid applications."""
        return self._eiq_calculator.get_total_eiq(self._applications)
    
    def get_validation_summary(self) -> dict:
        """Get a summary of validation states across all applications."""
        return self._validator.get_validation_summary(self._applications)
    
    def move_application_up(self, row: int) -> bool:
        """Move an application up by one position."""
        if row <= 0 or row >= len(self._applications):
            return False
        
        try:
            self._applications[row], self._applications[row - 1] = self._applications[row - 1], self._applications[row]
            self._clear_validation_cache()
            
            top_left = self.index(row - 1, 0)
            bottom_right = self.index(row, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
            
            return True
        except Exception as e:
            print(f"Error in move_application_up(): {e}")
            return False
    
    def move_application_down(self, row: int) -> bool:
        """Move an application down by one position."""
        if row < 0 or row >= len(self._applications) - 1:
            return False
        
        try:
            self._applications[row], self._applications[row + 1] = self._applications[row + 1], self._applications[row]
            self._clear_validation_cache()
            
            top_left = self.index(row, 0)
            bottom_right = self.index(row + 1, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
            
            return True
        except Exception as e:
            print(f"Error in move_application_down(): {e}")
            return False

    # --- Private Methods ---
    
    def _affects_validation(self, col: int) -> bool:
        """Check if changing this column affects validation state."""
        validation_affecting_columns = {
            self._col_index("Product Name"),
            self._col_index("Rate"),
            self._col_index("Rate UOM"),
            self._col_index("Area")
        }
        return col in validation_affecting_columns
    
    def _get_cell_data(self, app: Application, col: int, row: int) -> Any:
        """Get data for a specific cell."""
        try:
            if col == self._col_index("Reorder"):
                return ""
            elif col == self._col_index("App #"):
                return row + 1
            elif col == self._col_index("Date"):
                return app.application_date or ""
            elif col == self._col_index("Product Type"):
                return app.product_type or ""
            elif col == self._col_index("Product Name"):
                return app.product_name or ""
            elif col == self._col_index("Rate"):
                return app.rate or 0.0
            elif col == self._col_index("Rate UOM"):
                return app.rate_uom or ""
            elif col == self._col_index("Area"):
                return app.area or 0.0
            elif col == self._col_index("Method"):
                return app.application_method or ""
            elif col == self._col_index("AI Groups"):
                return ", ".join(app.ai_groups) if app.ai_groups else ""
            elif col == self._col_index("Field EIQ"):
                validation = self._get_validation(app, row)
                if validation.can_calculate_eiq and app.field_eiq:
                    return f"{app.field_eiq:.2f}"
                elif validation.state == ValidationState.INVALID_PRODUCT:
                    return "n/a"
                else:
                    return "0.00"
            elif col == self._col_index("Status"):
                validation = self._get_validation(app, row)
                return self._validator.format_validation_status(validation)
            
            return None
        except Exception as e:
            print(f"Error in _get_cell_data(): {e}")
            return ""
    
    def _get_cell_background(self, app: Application, col: int, row: int) -> Optional[QColor]:
        """Get background color for a cell based on validation state."""
        validation = self._get_validation(app, row)
        
        if validation.state == ValidationState.INVALID_PRODUCT:
            return QColor("#ffebee")  # Light red
        elif validation.state == ValidationState.INVALID_DATA:
            return QColor("#fff3e0")  # Light orange
        elif validation.state == ValidationState.INCOMPLETE:
            return QColor("#f3e5f5")  # Light purple
        elif validation.state == ValidationState.VALID_ESTIMATED:
            return QColor("#fff9c4")  # Light yellow for estimated EIQ
        
        return None
    
    def _get_cell_tooltip(self, app: Application, col: int, row: int) -> str:
        """Get tooltip for a cell with detailed validation information."""
        validation = self._get_validation(app, row)
        
        # Special handling for estimated EIQ applications
        if validation.state == ValidationState.VALID_ESTIMATED:
            return ("This application uses estimated EIQ because the product lacks "
                   "active ingredient data. EIQ is calculated as the average of other "
                   "valid applications in this scenario.")
        
        # Show primary message for most columns
        if validation.issues:
            primary_message = validation.primary_message
            
            # For status column, show all issues
            if col == self._col_index("Status") and len(validation.issues) > 1:
                all_messages = [issue.message for issue in validation.issues]
                return "\n".join(all_messages)
            
            return primary_message
        
        # Special tooltips for specific columns when valid
        if col == self._col_index("Field EIQ"):
            if validation.can_calculate_eiq:
                return "EIQ calculated from product database"
            elif validation.state == ValidationState.VALID:
                return "Valid application but EIQ calculation requires additional product data"
            else:
                return "Cannot calculate EIQ due to validation issues"
        
        return "Application is valid"
    
    def _set_cell_data(self, app: Application, col: int, value: Any) -> bool:
        """Set data for a specific cell with validation."""
        try:
            if col == self._col_index("Date"):
                app.application_date = str(value) if value else ""
            elif col == self._col_index("Product Type"):
                app.product_type = str(value) if value else ""
            elif col == self._col_index("Product Name"):
                app.product_name = str(value) if value else ""
            elif col == self._col_index("Rate"):
                app.rate = float(value) if value else 0.0
            elif col == self._col_index("Rate UOM"):
                app.rate_uom = str(value) if value else ""
            elif col == self._col_index("Area"):
                app.area = float(value) if value else 0.0
            elif col == self._col_index("Method"):
                app.application_method = str(value) if value else ""
            else:
                return False
            
            return True
            
        except (ValueError, TypeError) as e:
            print(f"Invalid value in _set_cell_data: {e}")
            return False

    def _update_dependent_fields(self, app: Application, changed_col: int, row: int):
        """Update fields that depend on the changed column."""
        try:
            if changed_col == self._col_index("Product Name"):
                # Auto-set product type if not set and product is found
                if app.product_name and not app.product_type:
                    product = self._find_product(app.product_name)
                    if product:
                        app.product_type = product.product_type
                
                self._update_ai_groups(app, row)
                
                # Clear validation cache and recalculate all EIQs
                self._validation_cache.clear()
                self._recalculate_all_eiq()
                
                # Emit changes for the entire table since averages may have changed
                if self.rowCount() > 0:
                    top_left = self.index(0, 0)
                    bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
                    self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole, Qt.BackgroundRole, Qt.ToolTipRole])
            
            elif changed_col in {self._col_index("Rate"), self._col_index("Rate UOM")}:
                # Rate or UOM changed - recalculate all EIQs to update averages
                self._validation_cache.clear()
                self._recalculate_all_eiq()
                
                # Emit change for the entire table since averages may have changed
                if self.rowCount() > 0:
                    top_left = self.index(0, 0)
                    bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
                    self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole, Qt.BackgroundRole, Qt.ToolTipRole])
        
        except Exception as e:
            print(f"Error in _update_dependent_fields(): {e}")
    
    def _update_ai_groups(self, app: Application, row: int):
        """Update AI groups based on the selected product."""
        try:
            if not app.product_name:
                app.ai_groups = []
                return
            
            product = self._find_product(app.product_name)
            if product:
                ai_groups = product.get_ai_groups()
                app.ai_groups = [group for group in ai_groups if group]
            else:
                app.ai_groups = []
        except Exception as e:
            print(f"Error in _update_ai_groups(): {e}")
            app.ai_groups = []
    
    def _recalculate_all_eiq(self):
        """Recalculate EIQ for all applications."""
        try:
            for app in self._applications:
                self._update_ai_groups(app, 0)  # Row doesn't matter for AI groups
            
            self._eiq_calculator.calculate_all_eiq_values(self._applications)
        except Exception as e:
            print(f"Error in _recalculate_all_eiq(): {e}")
    
    def _get_validation(self, app: Application, row: int):
        """Get validation result with caching."""
        if row not in self._validation_cache:
            self._validation_cache[row] = self._validator.validate_application(app)
        return self._validation_cache[row]
    
    def _clear_validation_cache(self):
        """Clear the validation cache."""
        self._validation_cache.clear()
    
    def _emit_signals(self):
        """Emit change signals."""
        try:
            total_eiq = self.get_total_field_eiq()
            self.eiq_changed.emit(total_eiq)
            self.validation_changed.emit()
        except Exception as e:
            print(f"Error in _emit_signals(): {e}")
    
    def _find_product(self, product_name: str):
        """Find a product by name in the filtered products list."""
        try:
            if not product_name:
                return None
            
            filtered_products = self._products_repo.get_filtered_products()
            for product in filtered_products:
                if product.product_name == product_name:
                    return product
            return None
        except Exception as e:
            print(f"Error in _find_product(): {e}")
            return None
    
    def auto_populate_from_product(self, row: int, product_name: str):
        """Auto-populate application rate and UOM from product label data."""
        try:
            if row >= len(self._applications):
                return
            
            app = self._applications[row]
            product = self._find_product(product_name)
            
            if not product:
                return
            
            # Auto-populate rate if available and current rate is empty/zero
            if (not app.rate or app.rate == 0) and product.label_maximum_rate:
                app.rate = float(product.label_maximum_rate)
            
            # Auto-populate UOM if available and current UOM is empty
            if not app.rate_uom and product.rate_uom:
                app.rate_uom = product.rate_uom
            
            # Clear validation cache and recalculate
            self._validation_cache.pop(row, None)
            self._recalculate_all_eiq()
            
            # Emit changes
            if self.rowCount() > 0:
                top_left = self.index(row, 0)
                bottom_right = self.index(row, self.columnCount() - 1)
                self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole, Qt.BackgroundRole, Qt.ToolTipRole])
            
        except Exception as e:
            print(f"Error in auto_populate_from_product(): {e}")