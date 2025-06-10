"""
Application Table Model for the Season Planner.

QAbstractTableModel that manages pesticide application data with automatic
EIQ calculations and validation.
"""

from dataclasses import dataclass
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal
from PySide6.QtGui import QColor
from typing import List, Any
from data import Application, ProductRepository
from common import eiq_calculator, get_config

@dataclass
class ColumnDefinition:
    """Definition for a table column."""
    index: int
    name: str
    editable: bool

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
    ]
    
    COLUMNS = [col.name for col in _COLUMN_DEFS]
    EDITABLE_COLUMNS = {col.index for col in _COLUMN_DEFS if col.editable}
    _COLUMN_INDEX_MAP = {col.name: col.index for col in _COLUMN_DEFS}

    @classmethod
    def _col_index(cls, name: str) -> int:
        """Helper methods to find column indexes by name."""
        if name not in cls._COLUMN_INDEX_MAP:
            raise ValueError(f"Column '{name}' not found")
        return cls._COLUMN_INDEX_MAP[name]
    
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
        if parent.isValid():
            return 0  # No children for table items
        return len(self._applications)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns."""
        if parent.isValid():
            return 0  # No children for table items
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
        if not index.isValid() or index.row() >= len(self._applications) or index.column() >= len(self.COLUMNS):
            return None
        
        try:
            app = self._applications[index.row()]
            col = index.column()
            
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return self._get_cell_data(app, col)
            
            elif role == Qt.BackgroundRole:
                # Yellow background for estimated EIQ values
                if col == self._col_index("Field EIQ") and self._should_use_estimated_eiq(app):
                    return QColor(255, 255, 0, 100)  # Light yellow background
                
                # Existing validation error background
                if (index.row(), col) in self._validation_errors:
                    return QColor("#fff3cd")  # Light yellow for validation errors
            
            elif role == Qt.ToolTipRole:
                # Special tooltip for estimated EIQ
                if col == self._col_index("Field EIQ") and self._should_use_estimated_eiq(app):
                    avg_eiq = self._calculate_average_eiq()
                    return f"Estimated EIQ (average of other applications): {avg_eiq:.2f}"
                
                # Show validation error as tooltip
                error = self._validation_errors.get((index.row(), col))
                if error:
                    return error
        
        except Exception as e:
            print(f"Error in data() method: {e}")
            return None
        
        return None
    
    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        """Set data for the given index."""
        if not index.isValid() or index.row() >= len(self._applications) or index.column() >= len(self.COLUMNS):
            return False
        
        if role != Qt.EditRole:
            return False
        
        try:
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
                
        except Exception as e:
            print(f"Error in setData() method: {e}")
            return False
        
        return False
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Return flags for the given index."""
        if not index.isValid() or index.row() >= len(self._applications) or index.column() >= len(self.COLUMNS):
            return Qt.NoItemFlags
        
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        
        # Make certain columns editable
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
                        
            # Emit EIQ changed signal
            try:
                self._emit_eiq_changed()
            except Exception as e:
                print(f"Error in _emit_eiq_changed: {e}")
            
            return True
            
        except Exception as e:
            print(f"ERROR in insertRows(): {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def removeRows(self, position: int, rows: int, parent: QModelIndex = QModelIndex()) -> bool:
        """Remove application rows."""
        if parent.isValid():
            return False
        
        # Validate position and rows
        if position < 0 or position >= len(self._applications):
            return False
        
        # Ensure we don't remove more rows than exist
        rows = min(rows, len(self._applications) - position)
        if rows <= 0:
            return False
        
        try:
            self.beginRemoveRows(parent, position, position + rows - 1)
            
            for i in range(rows):
                if position < len(self._applications):
                    removed_app = self._applications.pop(position)
                    print(f"Removed application: {removed_app.product_name} at position {position+1}")
            
            self.endRemoveRows()
            self._clear_validation_errors_for_removed_rows(position, rows)
            self._emit_eiq_changed()
            return True
            
        except Exception as e:
            print(f"ERROR in removeRows(): {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # --- Public Interface ---
    
    def get_applications(self) -> List[Application]:
        """Get all applications."""
        return self._applications.copy()
    
    def set_applications(self, applications: List[Application]):
        """Set the applications list."""
        try:
            self.beginResetModel()
            
            # Ensure we have Application objects, not dicts
            self._applications = []
            for i, app in enumerate(applications):
                if hasattr(app, 'product_name'):
                    # It's already an Application object
                    self._applications.append(app)
                    print(f"  Model App {i+1}: {app.product_name} @ {getattr(app, 'rate', 'N/A')} {getattr(app, 'rate_uom', 'N/A')}")
                else:
                    # Convert dict to Application if needed
                    from data import Application
                    app_obj = Application.from_dict(app)
                    self._applications.append(app_obj)
                    print(f"  Model App {i+1} (converted): {app_obj.product_name} @ {app_obj.rate} {app_obj.rate_uom}")
            
            # Clear validation errors
            self._validation_errors.clear()
            
            self.endResetModel()
            
            # Recalculate EIQ for all applications
            self._recalculate_all_eiq()
            self._emit_eiq_changed()
            
        except Exception as e:
            print(f"ERROR in ApplicationTableModel.set_applications(): {e}")
            import traceback
            traceback.print_exc()
            # Ensure we end the reset even if there's an error
            self.endResetModel()
    
    def add_application(self, position: int = -1) -> int:
        """Add a new application and return its row index.
        
        Args:
            position (int): Position to insert at. If -1, insert at end.
        """
        try:
            if position < 0 or position > len(self._applications):
                position = len(self._applications)
            
            success = self.insertRows(position, 1)
            if success:
                return position
            else:
                print("ERROR: insertRows() returned False")
                return -1
        except Exception as e:
            print(f"ERROR in add_application(): {e}")
            import traceback
            traceback.print_exc()
            return -1
    
    def remove_application(self, row: int) -> bool:
        """Remove application at the given row."""
        return self.removeRows(row, 1)
    
    def set_field_area(self, area: float, uom: str):
        """Set default field area for new applications."""
        self._field_area = area
        self._field_area_uom = uom
    
    def get_total_field_eiq(self) -> float:
        """Calculate total Field EIQ for all applications, including estimated values."""
        try:
            total_eiq = 0.0
            for app in self._applications:
                if self._should_use_estimated_eiq(app):
                    # Use estimated EIQ for this application
                    estimated_eiq = self._calculate_average_eiq()
                    total_eiq += estimated_eiq
                else:
                    # Use actual EIQ
                    total_eiq += app.field_eiq or 0.0
            return total_eiq
        except Exception as e:
            print(f"ERROR in get_total_field_eiq(): {e}")
            return 0.0
    
    def get_applications_with_effective_eiq(self) -> List[Application]:
        """
        Get all applications with effective EIQ values (including estimated).
        
        Returns a copy of applications where estimated EIQ values are applied
        to the field_eiq attribute for external use (like comparison tables).
        """
        try:
            applications_copy = []
            avg_eiq = self._calculate_average_eiq()  # Calculate once for efficiency
            
            for app in self._applications:
                # Create a copy of the application
                app_copy = Application(
                    application_date=app.application_date,
                    product_type=app.product_type,
                    product_name=app.product_name,
                    rate=app.rate,
                    rate_uom=app.rate_uom,
                    area=app.area,
                    application_method=app.application_method,
                    ai_groups=app.ai_groups.copy() if app.ai_groups else [],
                    field_eiq=app.field_eiq
                )
                
                # Apply estimated EIQ if needed
                if self._should_use_estimated_eiq(app_copy):
                    app_copy.field_eiq = avg_eiq
                
                applications_copy.append(app_copy)
            
            return applications_copy
        except Exception as e:
            print(f"ERROR in get_applications_with_effective_eiq(): {e}")
            return self._applications.copy()

    def move_application_up(self, row: int) -> bool:
        """Move an application up by one position."""
        if row <= 0 or row >= len(self._applications):
            return False
        
        try:
            # Swap applications
            self._applications[row], self._applications[row - 1] = self._applications[row - 1], self._applications[row]
            
            # Emit data changed for both rows
            top_left = self.index(row - 1, 0)
            bottom_right = self.index(row, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
            
            return True
        except Exception as e:
            print(f"ERROR in move_application_up(): {e}")
            return False
    
    def move_application_down(self, row: int) -> bool:
        """Move an application down by one position."""
        if row < 0 or row >= len(self._applications) - 1:
            return False
        
        try:
            # Swap applications
            self._applications[row], self._applications[row + 1] = self._applications[row + 1], self._applications[row]
            
            # Emit data changed for both rows
            top_left = self.index(row, 0)
            bottom_right = self.index(row + 1, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
            
            return True
        except Exception as e:
            print(f"ERROR in move_application_down(): {e}")
            return False
    
    # --- Private Methods ---
    
    def _get_cell_data(self, app: Application, col: int) -> Any:
        """Get data for a specific cell."""
        try:
            if col == self._col_index("Reorder"):
                return ""
            elif col == self._col_index("App #"):
                return self._applications.index(app) + 1
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
                # Check if this should show estimated EIQ
                if self._should_use_estimated_eiq(app):
                    estimated_eiq = self._calculate_average_eiq()
                    return f"{estimated_eiq:.2f}" if estimated_eiq > 0 else "0.00"
                else:
                    return f"{app.field_eiq:.2f}" if app.field_eiq else "0.00"
            return None
        except Exception as e:
            print(f"ERROR in _get_cell_data(): {e}")
            return ""

    def _should_use_estimated_eiq(self, app: Application) -> bool:
        """
        Check if this application should use estimated EIQ.
        
        Returns True if:
        - Application has rate > 0 (has product and rate data)
        - Field EIQ is 0 (missing AI EIQ data)
        - Product exists in database
        """
        try:
            if not app.rate or app.rate <= 0:
                return False  # No rate, EIQ should stay 0
            
            if app.field_eiq and app.field_eiq > 0:
                return False  # Already has valid EIQ
            
            if not app.product_name:
                return False  # No product selected
            
            # Check if product exists and has AI data but with 0 EIQ values
            product = self._find_product(app.product_name)
            if not product:
                return False  # Product not found
            
            ai_data = product.get_ai_data()
            if not ai_data:
                return False  # No AI data at all
            
            # Check if all AIs have EIQ = 0 (missing EIQ data)
            has_valid_eiq = any(ai.get('eiq', 0) > 0 for ai in ai_data)
            return not has_valid_eiq  # Use estimated if no valid EIQ found
            
        except Exception as e:
            print(f"ERROR in _should_use_estimated_eiq(): {e}")
            return False

    def _calculate_average_eiq(self) -> float:
        """
        Calculate average EIQ from applications with valid EIQ values.
        
        Returns:
            float: Average EIQ value, or 0.0 if no valid values found
        """
        try:
            valid_eiq_values = []
            
            for app in self._applications:
                # Only include applications with valid EIQ (not estimated ones)
                if (app.field_eiq and app.field_eiq > 0 and 
                    not self._should_use_estimated_eiq(app)):
                    valid_eiq_values.append(app.field_eiq)
            
            if valid_eiq_values:
                return sum(valid_eiq_values) / len(valid_eiq_values)
            else:
                return 0.0
                
        except Exception as e:
            print(f"ERROR in _calculate_average_eiq(): {e}")
            return 0.0

    def _set_cell_data(self, app: Application, col: int, value: Any, row: int) -> bool:
        """Set data for a specific cell with validation."""
        self._validation_errors.pop((row, col), None)
        
        try:
            if col == self._col_index("Reorder"):
                return False
            elif col == self._col_index("Date"):
                app.application_date = str(value) if value else ""
            
            elif col == self._col_index("Product Type"):
                old_type = app.product_type
                app.product_type = str(value) if value else ""
                
                if app.product_name and old_type != app.product_type:
                    product = self._find_product(app.product_name)
                    if product and product.product_type != app.product_type:
                        self._validation_errors[(row, self._col_index("Product Name"))] = (
                            f"Product '{app.product_name}' is not of type '{app.product_type}'"
                        )
            
            elif col == self._col_index("Product Name"):
                product_name = str(value) if value else ""
                app.product_name = product_name
                
                if product_name:
                    product = self._find_product(product_name)
                    if product:
                        if app.product_type and app.product_type != product.product_type:
                            self._validation_errors[(row, col)] = (
                                f"Product type mismatch: '{product_name}' is '{product.product_type}', "
                                f"but row type is '{app.product_type}'"
                            )
                        else:
                            if not app.product_type:
                                app.product_type = product.product_type
                    else:
                        if not app.product_type:
                            app.product_type = "Unknown"
                        self._validation_errors[(row, col)] = "Product not found in database"
            
            elif col == self._col_index("Rate"):
                rate = float(value) if value else 0.0
                if rate < 0:
                    self._validation_errors[(row, col)] = "Rate must be positive"
                    return False
                app.rate = rate
            
            elif col == self._col_index("Rate UOM"):
                app.rate_uom = str(value) if value else ""
            
            elif col == self._col_index("Area"):
                area = float(value) if value else 0.0
                if area < 0:
                    self._validation_errors[(row, col)] = "Area must be positive"
                    return False
                app.area = area
            
            elif col == self._col_index("Method"):
                app.application_method = str(value) if value else ""
            
            return True
            
        except (ValueError, TypeError) as e:
            self._validation_errors[(row, col)] = f"Invalid value: {e}"
            return False

    def _update_dependent_fields(self, app: Application, changed_col: int, row: int):
        """Update fields that depend on the changed column."""
        try:
            if changed_col == self._col_index("Product Type"):
                if app.product_name:
                    product = self._find_product(app.product_name)
                    if product and product.product_type != app.product_type:
                        app.product_name = ""
                        app.ai_groups = []
                        app.field_eiq = 0.0
                        
                        name_index = self.index(row, self._col_index("Product Name"))
                        groups_index = self.index(row, self._col_index("AI Groups"))
                        eiq_index = self.index(row, self._col_index("Field EIQ"))
                        
                        self.dataChanged.emit(name_index, name_index, [Qt.DisplayRole])
                        self.dataChanged.emit(groups_index, groups_index, [Qt.DisplayRole])
                        self.dataChanged.emit(eiq_index, eiq_index, [Qt.DisplayRole])
            
            elif changed_col == self._col_index("Product Name"):
                self._update_ai_groups(app, row)
                self._calculate_field_eiq(app, row)
                
                type_index = self.index(row, self._col_index("Product Type"))
                self.dataChanged.emit(type_index, type_index, [Qt.DisplayRole])
            
            elif changed_col in {self._col_index("Rate"), self._col_index("Rate UOM")}:
                self._calculate_field_eiq(app, row)
            
            # Emit dataChanged for potentially affected columns
            affected_cols = []
            if changed_col == self._col_index("Product Name"):
                affected_cols = [self._col_index("AI Groups"), self._col_index("Field EIQ")]
            elif changed_col in {self._col_index("Rate"), self._col_index("Rate UOM")}:
                affected_cols = [self._col_index("Field EIQ")]
            
            for col in affected_cols:
                index = self.index(row, col)
                self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.BackgroundRole, Qt.ToolTipRole])
                
        except Exception as e:
            print(f"ERROR in _update_dependent_fields(): {e}")
    
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
            print(f"ERROR in _update_ai_groups(): {e}")
            app.ai_groups = []
    
    def _calculate_field_eiq(self, app: Application, row: int):
        """Calculate Field EIQ for a single application."""
        try:
            if not app.product_name or not app.rate or not app.rate_uom:
                app.field_eiq = 0.0
                return
            
            product = self._find_product(app.product_name)
            if not product:
                app.field_eiq = 0.0
                self._validation_errors[(row, self._col_index("Field EIQ"))] = "Cannot calculate EIQ: product not found"
                return
            
            ai_data = product.get_ai_data()
            if not ai_data:
                app.field_eiq = 0.0
                self._validation_errors[(row, self._col_index("Field EIQ"))] = "Cannot calculate EIQ: no active ingredient data"
                return
            
            field_eiq = eiq_calculator.calculate_product_field_eiq(
                active_ingredients=ai_data,
                application_rate=app.rate,
                application_rate_uom=app.rate_uom,
                applications=1,
                user_preferences=self._user_preferences
            )
            
            app.field_eiq = field_eiq
            self._validation_errors.pop((row, self._col_index("Field EIQ")), None)
            
        except Exception as e:
            print(f"ERROR in _calculate_field_eiq(): {e}")
            app.field_eiq = 0.0
            self._validation_errors[(row, self._col_index("Field EIQ"))] = f"EIQ calculation error: {e}"
    
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
            print(f"ERROR in _find_product(): {e}")
            return None
    
    def _recalculate_all_eiq(self):
        """Recalculate EIQ for all applications."""
        try:
            for row, app in enumerate(self._applications):
                self._update_ai_groups(app, row)
                self._calculate_field_eiq(app, row)
        except Exception as e:
            print(f"ERROR in _recalculate_all_eiq(): {e}")
    
    def _emit_eiq_changed(self):
        """Emit signal when total EIQ changes."""
        try:
            total_eiq = self.get_total_field_eiq()
            self.eiq_changed.emit(total_eiq)
        except Exception as e:
            print(f"ERROR in _emit_eiq_changed(): {e}")
    
    def _clear_validation_errors_for_removed_rows(self, position: int, rows: int):
        """Clear validation errors for removed rows and adjust indices."""
        try:
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
        except Exception as e:
            print(f"ERROR in _clear_validation_errors_for_removed_rows(): {e}")

    def auto_populate_from_product(self, row: int, product_name: str):
        """Auto-populate application rate and UOM from product label data."""
        try:
            if row >= len(self._applications):
                return
            
            app = self._applications[row]
            product = self._find_product(product_name)
            
            if not product:
                return
            
            if product.label_maximum_rate is not None or product.label_minimum_rate is not None:
                best_rate = (product.label_maximum_rate if product.label_maximum_rate is not None 
                        else product.label_minimum_rate)
                
                if best_rate and best_rate > 0:
                    app.rate = float(best_rate)
                    
                    rate_index = self.index(row, self._col_index("Rate"))
                    self.dataChanged.emit(rate_index, rate_index, [Qt.DisplayRole])
        
            if product.rate_uom:
                app.rate_uom = product.rate_uom
                
                uom_index = self.index(row, self._col_index("Rate UOM"))
                self.dataChanged.emit(uom_index, uom_index, [Qt.DisplayRole])
        
            self._calculate_field_eiq(app, row)
            
            eiq_index = self.index(row, self._col_index("Field EIQ"))
            self.dataChanged.emit(eiq_index, eiq_index, [Qt.DisplayRole])
            
        except Exception as e:
            print(f"ERROR in auto_populate_from_product(): {e}")