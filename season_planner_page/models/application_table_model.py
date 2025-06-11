"""
Fixed Application Table Model for the Season Planner.

This version fixes the validation state machine to ensure all states are reachable
and implements proper hierarchical validation with support for multiple issues.
"""

from dataclasses import dataclass
from enum import Enum
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal
from PySide6.QtGui import QColor
from typing import List, Any, Optional
from data import Application, ProductRepository
from common import eiq_calculator, get_config

class ValidationState(Enum):
    """Clear validation states for applications."""
    VALID = "valid"
    VALID_ESTIMATED = "valid_estimated"  # Valid but using estimated EIQ
    INVALID_PRODUCT = "invalid_product"
    INVALID_DATA = "invalid_data"
    INCOMPLETE = "incomplete"

@dataclass
class ValidationIssue:
    """Individual validation issue."""
    field: str
    message: str
    severity: str  # 'error', 'warning', 'info'

@dataclass
class ValidationResult:
    """Result of application validation with support for multiple issues."""
    state: ValidationState
    issues: List[ValidationIssue]
    can_calculate_eiq: bool = False
    
    @property
    def message(self) -> str:
        """Get combined message from all issues."""
        if not self.issues:
            return "Application is valid"
        return "; ".join(issue.message for issue in self.issues)
    
    @property
    def primary_message(self) -> str:
        """Get the most important message."""
        if not self.issues:
            return "Application is valid"
        return self.issues[0].message

@dataclass
class ColumnDefinition:
    """Definition for a table column."""
    index: int
    name: str
    editable: bool

class ApplicationTableModel(QAbstractTableModel):
    """
    Fixed table model for managing pesticide applications.
    
    Key improvements:
    - Fixed validation state machine with proper hierarchy
    - Support for multiple simultaneous validation issues
    - Clear validation states that are all reachable
    - Better error handling and user feedback
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
        self._validation_cache: dict[int, ValidationResult] = {}
        self._field_area = 10.0
        self._field_area_uom = "acre"
        
        # Repository references
        self._products_repo = ProductRepository.get_instance()
        self._user_preferences = get_config("user_preferences", {})

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
                # Clear validation cache for this row only when it might affect validation
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
        try:
            total_eiq = 0.0
            for app in self._applications:
                if app.field_eiq and app.field_eiq > 0:
                    total_eiq += app.field_eiq
            return total_eiq
        except Exception as e:
            print(f"Error in get_total_field_eiq(): {e}")
            return 0.0
    
    def get_validation_summary(self) -> dict:
        """Get a summary of validation states across all applications."""
        summary = {
            ValidationState.VALID: 0,
            ValidationState.VALID_ESTIMATED: 0,
            ValidationState.INVALID_PRODUCT: 0,
            ValidationState.INVALID_DATA: 0,
            ValidationState.INCOMPLETE: 0
        }
        
        for i, app in enumerate(self._applications):
            validation = self._validate_application(app, i)
            summary[validation.state] += 1
        
        return summary
    
    def move_application_up(self, row: int) -> bool:
        """Move an application up by one position."""
        if row <= 0 or row >= len(self._applications):
            return False
        
        try:
            self._applications[row], self._applications[row - 1] = self._applications[row - 1], self._applications[row]
            
            # Clear validation cache for affected rows
            self._validation_cache.pop(row, None)
            self._validation_cache.pop(row - 1, None)
            
            # Emit data changed
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
            
            # Clear validation cache for affected rows
            self._validation_cache.pop(row, None)
            self._validation_cache.pop(row + 1, None)
            
            # Emit data changed
            top_left = self.index(row, 0)
            bottom_right = self.index(row + 1, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
            
            return True
        except Exception as e:
            print(f"Error in move_application_down(): {e}")
            return False
    
    def fix_product_at_row(self, row: int) -> bool:
        """Attempt to fix product issues at the specified row."""
        if row < 0 or row >= len(self._applications):
            return False
        
        app = self._applications[row]
        
        # Try to find a similar product if the current one doesn't exist
        if app.product_name:
            similar_product = self._find_similar_product(app.product_name)
            if similar_product:
                app.product_name = similar_product.product_name
                app.product_type = similar_product.product_type
                
                # Clear cache and recalculate
                self._validation_cache.pop(row, None)
                self._update_ai_groups(app, row)
                self._calculate_field_eiq(app, row)
                
                # Emit changes
                self._emit_row_changed(row)
                self._emit_signals()
                return True
        
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
                validation = self._validate_application(app, row)
                if validation.can_calculate_eiq and app.field_eiq:
                    return f"{app.field_eiq:.2f}"
                elif validation.state == ValidationState.INVALID_PRODUCT:
                    return "n/a"
                else:
                    return "0.00"
            elif col == self._col_index("Status"):
                validation = self._validate_application(app, row)
                return self._format_validation_status(validation)
            
            return None
        except Exception as e:
            print(f"Error in _get_cell_data(): {e}")
            return ""
    
    def _get_cell_background(self, app: Application, col: int, row: int) -> Optional[QColor]:
        """Get background color for a cell based on validation state."""
        validation = self._validate_application(app, row)
        
        # Color code based on validation state
        if validation.state == ValidationState.INVALID_PRODUCT:
            return QColor("#ffebee")  # Light red
        elif validation.state == ValidationState.INVALID_DATA:
            return QColor("#fff3e0")  # Light orange
        elif validation.state == ValidationState.INCOMPLETE:
            return QColor("#f3e5f5")  # Light purple
        elif validation.state == ValidationState.VALID_ESTIMATED:
            return QColor("#fff9c4")  # Light yellow for estimated EIQ
        
        # Special case for EIQ column - show when calculation is missing
        if col == self._col_index("Field EIQ"):
            if validation.state == ValidationState.VALID and not validation.can_calculate_eiq:
                return QColor("#e8f5e8")  # Light green (valid but no EIQ)
        
        return None
    
    def _get_cell_tooltip(self, app: Application, col: int, row: int) -> str:
        """Get tooltip for a cell with detailed validation information."""
        validation = self._validate_application(app, row)
        
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
    
    def _validate_application(self, app: Application, row: int) -> ValidationResult:
        """Validate an application and return detailed result."""
        # Check cache first
        if row in self._validation_cache:
            return self._validation_cache[row]
        
        # Perform validation
        result = self._perform_validation(app)
        
        # Cache result
        self._validation_cache[row] = result
        
        return result
    
    def _perform_validation(self, app: Application) -> ValidationResult:
        """
        Perform comprehensive validation with proper state hierarchy.
        
        Validation order:
        1. Check for missing required fields (INCOMPLETE)
        2. Validate data ranges and formats (INVALID_DATA)  
        3. Check product existence (INVALID_PRODUCT)
        4. Confirm EIQ calculation capability (VALID)
        """
        issues = []
        
        # 1. INCOMPLETE STATE: Check for missing required fields
        missing_fields = []
        if not app.product_name or not app.product_name.strip():
            missing_fields.append("product name")
        if not app.rate or app.rate <= 0:
            missing_fields.append("application rate")
        if not app.rate_uom or not app.rate_uom.strip():
            missing_fields.append("rate unit")
        
        if missing_fields:
            issues.append(ValidationIssue(
                field="required_fields",
                message=f"Missing required fields: {', '.join(missing_fields)}",
                severity="error"
            ))
            return ValidationResult(
                ValidationState.INCOMPLETE,
                issues,
                False
            )
        
        # 2. INVALID_DATA STATE: Validate data ranges and formats
        if app.rate is not None and app.rate < 0:
            issues.append(ValidationIssue(
                field="rate",
                message="Application rate cannot be negative",
                severity="error"
            ))
        
        if app.area is not None and app.area < 0:
            issues.append(ValidationIssue(
                field="area",
                message="Application area cannot be negative", 
                severity="error"
            ))
        
        # Check for unreasonably high values that might be data entry errors
        if app.rate is not None and app.rate > 10000:
            issues.append(ValidationIssue(
                field="rate",
                message="Application rate seems unusually high - please verify",
                severity="warning"
            ))
        
        if issues:
            return ValidationResult(
                ValidationState.INVALID_DATA,
                issues,
                False
            )
        
        # 3. INVALID_PRODUCT STATE: Check product existence
        product = self._find_product(app.product_name)
        if not product:
            issues.append(ValidationIssue(
                field="product_name",
                message=f"Product '{app.product_name}' not found in database",
                severity="error"
            ))
            return ValidationResult(
                ValidationState.INVALID_PRODUCT,
                issues,
                False
            )
        
        # 4. VALID STATE: All validations passed
        # Check if we can calculate EIQ
        can_calculate_eiq = (
            app.product_name and app.product_name.strip() and
            app.rate and app.rate > 0 and
            app.rate_uom and app.rate_uom.strip() and
            product is not None
        )
        
        # Check if product has AI data for EIQ calculation
        has_ai_data = False
        if product:
            ai_data = product.get_ai_data()
            has_ai_data = bool(ai_data)
        
        if can_calculate_eiq and has_ai_data:
            issues.append(ValidationIssue(
                field="status",
                message="Application is valid and EIQ can be calculated",
                severity="info"
            ))
            return ValidationResult(
                ValidationState.VALID,
                issues,
                True
            )
        elif can_calculate_eiq and not has_ai_data:
            # Valid but will use estimated EIQ
            issues.append(ValidationIssue(
                field="eiq",
                message="Application is valid but uses estimated EIQ (product lacks AI data)",
                severity="info"
            ))
            return ValidationResult(
                ValidationState.VALID_ESTIMATED,
                issues,
                True  # Can calculate EIQ (using estimation)
            )
        else:
            issues.append(ValidationIssue(
                field="eiq",
                message="Application is valid but EIQ calculation requires additional data",
                severity="warning"
            ))
            return ValidationResult(
                ValidationState.VALID,
                issues,
                False
            )
    
    def _format_validation_status(self, validation: ValidationResult) -> str:
        """Format validation status for display with issue count."""
        status_map = {
            ValidationState.VALID: "✓ Valid",
            ValidationState.VALID_ESTIMATED: "✓ Valid (Est.)",
            ValidationState.INVALID_PRODUCT: "✗ Invalid Product", 
            ValidationState.INVALID_DATA: "⚠ Invalid Data",
            ValidationState.INCOMPLETE: "◯ Incomplete"
        }
        
        base_status = status_map.get(validation.state, "Unknown")
        
        # Add issue count for non-valid states
        if validation.state not in [ValidationState.VALID, ValidationState.VALID_ESTIMATED] and len(validation.issues) > 1:
            base_status += f" ({len(validation.issues)} issues)"
        
        return base_status
    
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
                self._calculate_field_eiq(app, row)
                
                # Emit changes for dependent columns
                self._emit_row_changed(row)
                
            elif changed_col in {self._col_index("Rate"), self._col_index("Rate UOM")}:
                self._calculate_field_eiq(app, row)
                
                # Emit change for EIQ column
                eiq_index = self.index(row, self._col_index("Field EIQ"))
                status_index = self.index(row, self._col_index("Status"))
                self.dataChanged.emit(eiq_index, status_index, [Qt.DisplayRole, Qt.BackgroundRole, Qt.ToolTipRole])
                
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
    
    def _calculate_field_eiq(self, app: Application, row: int):
        """Calculate Field EIQ for a single application."""
        try:
            # Reset EIQ
            app.field_eiq = 0.0
            
            # Check if we have all required data
            if not app.product_name or not app.rate or not app.rate_uom:
                return
            
            product = self._find_product(app.product_name)
            if not product:
                return
            
            ai_data = product.get_ai_data()
            if ai_data:
                # Calculate EIQ from product data
                field_eiq = eiq_calculator.calculate_product_field_eiq(
                    active_ingredients=ai_data,
                    application_rate=app.rate,
                    application_rate_uom=app.rate_uom,
                    applications=1,
                    user_preferences=self._user_preferences
                )
                app.field_eiq = field_eiq
            else:
                # Product lacks AI data - use average EIQ of other applications
                avg_eiq = self._calculate_average_eiq_for_estimation()
                app.field_eiq = avg_eiq
            
        except Exception as e:
            print(f"Error in _calculate_field_eiq(): {e}")
            app.field_eiq = 0.0
    
    def _calculate_average_eiq_for_estimation(self) -> float:
        """Calculate average EIQ from applications that have valid EIQ calculations."""
        try:
            valid_eiq_values = []
            
            for app in self._applications:
                if not app.product_name or not app.rate or not app.rate_uom:
                    continue
                
                product = self._find_product(app.product_name)
                if not product:
                    continue
                
                ai_data = product.get_ai_data()
                if ai_data:  # Only include applications with real AI data
                    try:
                        eiq = eiq_calculator.calculate_product_field_eiq(
                            active_ingredients=ai_data,
                            application_rate=app.rate,
                            application_rate_uom=app.rate_uom,
                            applications=1,
                            user_preferences=self._user_preferences
                        )
                        if eiq > 0:
                            valid_eiq_values.append(eiq)
                    except Exception:
                        continue
            
            if valid_eiq_values:
                return sum(valid_eiq_values) / len(valid_eiq_values)
            else:
                # No valid EIQ values available, return a default
                return 50.0  # Conservative default EIQ value
                
        except Exception as e:
            print(f"Error calculating average EIQ: {e}")
            return 50.0
    
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
    
    def _find_similar_product(self, product_name: str):
        """Find a similar product using fuzzy matching."""
        try:
            if not product_name:
                return None
            
            product_lower = product_name.lower()
            filtered_products = self._products_repo.get_filtered_products()
            
            # First try: exact substring match
            for product in filtered_products:
                db_lower = product.product_name.lower()
                if product_lower in db_lower or db_lower in product_lower:
                    return product
            
            # Second try: word overlap
            product_words = set(product_lower.split())
            best_match = None
            best_score = 0
            
            for product in filtered_products:
                db_words = set(product.product_name.lower().split())
                overlap = len(product_words.intersection(db_words))
                
                if overlap > best_score and overlap >= 2:
                    best_score = overlap
                    best_match = product
            
            return best_match
            
        except Exception as e:
            print(f"Error in _find_similar_product(): {e}")
            return None
    
    def _recalculate_all_eiq(self):
        """Recalculate EIQ for all applications."""
        try:
            for row, app in enumerate(self._applications):
                self._update_ai_groups(app, row)
                self._calculate_field_eiq(app, row)
        except Exception as e:
            print(f"Error in _recalculate_all_eiq(): {e}")
    
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
    
    def _emit_row_changed(self, row: int):
        """Emit dataChanged for an entire row."""
        try:
            left_index = self.index(row, 0)
            right_index = self.index(row, self.columnCount() - 1)
            self.dataChanged.emit(left_index, right_index, [Qt.DisplayRole, Qt.BackgroundRole, Qt.ToolTipRole])
        except Exception as e:
            print(f"Error in _emit_row_changed(): {e}")
    
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
            self._calculate_field_eiq(app, row)
            
            # Emit changes
            self._emit_row_changed(row)
            
        except Exception as e:
            print(f"Error in auto_populate_from_product(): {e}")