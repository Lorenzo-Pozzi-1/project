"""
Applications Table Widget for the Season Planner.

This version works with the simplified model and provides better user feedback
and actions for handling validation issues.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView, 
    QAbstractItemView, QMessageBox, QLabel, QPushButton, QFrame,
    QToolButton, QMenu
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QShowEvent, QIcon
from typing import List, Dict, Any
import traceback

from common import create_button, GENERIC_TABLE_STYLE, get_medium_font, get_small_font
from data import Application
from ..models.application_table_model import ApplicationTableModel, ValidationState
from ..delegates.date_delegate import DateDelegate
from ..delegates.numeric_delegate import RateDelegate, AreaDelegate
from ..delegates.method_delegate import MethodDelegate
from ..delegates.product_name_delegate import ProductNameDelegate
from ..delegates.uom_delegate import UOMDelegate
from ..delegates.product_type_delegate import ProductTypeDelegate
from ..delegates.reorder_delegate import ReorderDelegate


class ValidationSummaryWidget(QWidget):
    """Widget showing validation summary and action buttons."""
    
    fix_issues_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the validation summary UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Status frame
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Box)
        status_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f8f9fa;
                padding: 2px;
            }
        """)
        
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(8, 4, 8, 4)
        
        # Validation summary label
        self.summary_label = QLabel("All applications valid")
        self.summary_label.setFont(get_small_font())
        status_layout.addWidget(self.summary_label)
        
        status_layout.addStretch()
        
        # Fix issues button
        self.fix_button = QPushButton("Fix Issues")
        self.fix_button.setVisible(False)
        self.fix_button.clicked.connect(self.fix_issues_requested)
        self.fix_button.setStyleSheet("""
            QPushButton {
                background-color: #ff6b35;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e55a2b;
            }
        """)
        status_layout.addWidget(self.fix_button)
        
        layout.addWidget(status_frame)
    
    def update_validation_summary(self, summary: dict):
        """Update the validation summary display."""
        valid_count = summary.get(ValidationState.VALID, 0)
        invalid_product_count = summary.get(ValidationState.INVALID_PRODUCT, 0)
        invalid_data_count = summary.get(ValidationState.INVALID_DATA, 0)
        incomplete_count = summary.get(ValidationState.INCOMPLETE, 0)
        
        total_issues = invalid_product_count + invalid_data_count + incomplete_count
        total_apps = sum(summary.values())
        
        if total_issues == 0:
            self.summary_label.setText(f"✓ All {total_apps} applications valid")
            self.summary_label.setStyleSheet("color: #28a745;")
            self.fix_button.setVisible(False)
        else:
            issues_text = []
            if invalid_product_count > 0:
                issues_text.append(f"{invalid_product_count} invalid products")
            if invalid_data_count > 0:
                issues_text.append(f"{invalid_data_count} data errors")
            if incomplete_count > 0:
                issues_text.append(f"{incomplete_count} incomplete")
            
            self.summary_label.setText(f"⚠ {total_issues} issues: " + ", ".join(issues_text))
            self.summary_label.setStyleSheet("color: #dc3545;")
            self.fix_button.setVisible(True)


class ApplicationsTableWidget(QWidget):
    """applications table widget with validation feedback and fix actions."""
    
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
        
        # Timer for validation updates
        self._validation_timer = QTimer()
        self._validation_timer.setSingleShot(True)
        self._validation_timer.timeout.connect(self._update_validation_display)
    
    def _connect_model_signals(self):
        """Connect model signals to local handlers."""
        self.model.eiq_changed.connect(self.eiq_changed)
        self.model.dataChanged.connect(self.applications_changed)
        self.model.rowsInserted.connect(self.applications_changed)
        self.model.rowsRemoved.connect(self.applications_changed)
        self.model.validation_changed.connect(self._schedule_validation_update)
    
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
        
        # Validation summary widget
        self.validation_widget = ValidationSummaryWidget()
        self.validation_widget.fix_issues_requested.connect(self._fix_issues)
        layout.addWidget(self.validation_widget)
        
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
        
        # Fixed width columns
        fixed_columns = {
            "Reorder": 80,
            "App #": 60,
            "Rate": 80,
            "Area": 80,
            "Field EIQ": 90,
            "Status": 120
        }
        
        for col in range(self.model.columnCount()):
            col_name = self.model.COLUMNS[col]
            
            if col_name in fixed_columns:
                header.setSectionResizeMode(col, QHeaderView.Fixed)
                header.resizeSection(col, fixed_columns[col_name])
            else:
                header.setSectionResizeMode(col, QHeaderView.Stretch)
    
    def _create_button_layout(self) -> QHBoxLayout:
        """Create the button layout."""
        layout = QHBoxLayout()
        
        # Add application button
        self.add_button = create_button(
            text="Add Application",
            style="white",
            callback=self.add_application
        )
        layout.addWidget(self.add_button)
        
        # Remove selected button
        self.remove_button = create_button(
            text="Remove Selected",
            style="white",
            callback=self.remove_selected_application
        )
        layout.addWidget(self.remove_button)
        
        # Quick actions menu
        self.actions_button = QToolButton()
        self.actions_button.setText("Quick Actions")
        self.actions_button.setPopupMode(QToolButton.InstantPopup)
        
        actions_menu = QMenu(self.actions_button)
        actions_menu.addAction("Fix Selected Product", self._fix_selected_product)
        actions_menu.addAction("Clear Invalid Applications", self._clear_invalid_applications)
        actions_menu.addSeparator()
        actions_menu.addAction("Recalculate All EIQ", self._recalculate_all_eiq)
        
        self.actions_button.setMenu(actions_menu)
        layout.addWidget(self.actions_button)
        
        layout.addStretch()
        return layout
    
    def showEvent(self, event: QShowEvent):
        """Assign delegates when widget is first shown."""
        super().showEvent(event)
        
        if not self._delegates_assigned:
            self._assign_delegates()
            self._delegates_assigned = True
            self._update_validation_display()
    
    def _assign_delegates(self):
        """Assign delegates to table columns."""
        try:
            assignments = {
                self.model._col_index("Reorder"): self.delegates['reorder'],
                self.model._col_index("Date"): self.delegates['date'],
                self.model._col_index("Rate"): self.delegates['rate'],
                self.model._col_index("Area"): self.delegates['area'],
                self.model._col_index("Product Type"): self.delegates['product_type'],
                self.model._col_index("Method"): self.delegates['method'],
                self.model._col_index("Product Name"): self.delegates['product_name'],
                self.model._col_index("Rate UOM"): self.delegates['rate_uom']
            }
            
            for col_index, delegate in assignments.items():
                if col_index < self.model.columnCount():
                    self.table_view.setItemDelegateForColumn(col_index, delegate)
            
        except Exception as e:
            print(f"Error assigning delegates: {e}")
            traceback.print_exc()
    
    def _schedule_validation_update(self):
        """Schedule a validation display update."""
        self._validation_timer.start(100)  # 100ms delay to batch updates
    
    def _update_validation_display(self):
        """Update the validation summary display."""
        try:
            summary = self.model.get_validation_summary()
            self.validation_widget.update_validation_summary(summary)
        except Exception as e:
            print(f"Error updating validation display: {e}")
    
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
    
    # Action handlers
    
    def _fix_issues(self):
        """Attempt to fix validation issues automatically."""
        fixed_count = 0
        applications = self.model.get_applications()
        
        for row in range(len(applications)):
            if self.model.fix_product_at_row(row):
                fixed_count += 1
        
        if fixed_count > 0:
            self._show_message(
                "Issues Fixed",
                f"Fixed {fixed_count} product issues automatically."
            )
        else:
            self._show_message(
                "No Auto-fixes Available",
                "No issues could be fixed automatically. You may need to manually correct products.",
                "information"
            )
    
    def _fix_selected_product(self):
        """Fix the product issue in the selected row."""
        selected_row = self._get_selected_row()
        if selected_row == -1:
            self._show_message(
                "No Selection",
                "Please select an application to fix.",
                "warning"
            )
            return
        
        if self.model.fix_product_at_row(selected_row):
            self._show_message(
                "Product Fixed",
                "Product issue fixed successfully."
            )
        else:
            self._show_message(
                "Cannot Fix",
                "Could not automatically fix this product issue.",
                "warning"
            )
    
    def _clear_invalid_applications(self):
        """Remove all applications with validation issues."""
        summary = self.model.get_validation_summary()
        invalid_count = (
            summary.get(ValidationState.INVALID_PRODUCT, 0) +
            summary.get(ValidationState.INVALID_DATA, 0)
        )
        
        if invalid_count == 0:
            self._show_message(
                "No Invalid Applications",
                "There are no invalid applications to remove."
            )
            return
        
        if not self._confirm_action(
            "Remove Invalid Applications",
            f"This will remove {invalid_count} applications with validation errors.\n\n"
            f"Are you sure you want to continue?"
        ):
            return
        
        # Remove invalid applications (iterate backwards to maintain indices)
        applications = self.model.get_applications()
        for row in range(len(applications) - 1, -1, -1):
            app = applications[row]
            # Check if this application has validation issues
            validation = self.model._validate_application(app, row)
            if validation.state in [ValidationState.INVALID_PRODUCT, ValidationState.INVALID_DATA]:
                self.model.remove_application(row)
        
        self._show_message(
            "Invalid Applications Removed",
            f"Removed {invalid_count} invalid applications."
        )
    
    def _recalculate_all_eiq(self):
        """Recalculate EIQ for all applications."""
        self.model._recalculate_all_eiq()
        self.model._clear_validation_cache()
        
        # Emit full table update
        if self.model.rowCount() > 0:
            top_left = self.model.index(0, 0)
            bottom_right = self.model.index(
                self.model.rowCount() - 1,
                self.model.columnCount() - 1
            )
            self.model.dataChanged.emit(top_left, bottom_right)
        
        self._show_message(
            "EIQ Recalculated",
            "EIQ values have been recalculated for all applications."
        )
    
    # Public Interface
    
    def add_application(self) -> int:
        """Add a new application row."""
        selected_row = self._get_selected_row()
        
        if selected_row >= 0:
            insert_position = selected_row + 1
        else:
            insert_position = -1
        
        row = self.model.add_application(insert_position)
        if row >= 0:
            new_index = self.model.index(row, self.model._col_index("Date"))
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
        
        product_name = self.model.data(
            self.model.index(selected_row, self.model._col_index("Product Name"))
        )
        display_name = product_name or "Empty row"
        
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
            self.model._clear_validation_cache()
            
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