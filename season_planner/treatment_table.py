"""
Treatment table widget for the Season Planner.

This module provides a customizable table for editing treatments.
"""

from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView, QApplication,
                             QAbstractItemView, QPushButton, QWidget, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QColor
from common.styles import EIQ_LOW_COLOR, EIQ_MEDIUM_COLOR, EIQ_HIGH_COLOR
from data.product_repository import ProductRepository
from eiq_calculator.eiq_calculations import calculate_product_field_eiq
from season_planner.product_selection_dialog import ProductSelectionDialog

class DragButton(QWidget):
    """Custom widget for the drag handle button."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        # Using text as icon for simplicity (could use an actual icon)
        self.button = QPushButton("≡")
        self.button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                color: #888888;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #444444;
            }
        """)
        layout.addWidget(self.button)


class DeleteButton(QWidget):
    """Custom widget for the delete button."""
    
    clicked = Signal(int)  # Signal to emit the row index
    
    def __init__(self, row_index, parent=None):
        super().__init__(parent)
        self.row_index = row_index
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        self.button = QPushButton("×")
        self.button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                color: #888888;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #FF0000;
            }
        """)
        self.button.clicked.connect(self._button_clicked)
        layout.addWidget(self.button)
    
    def _button_clicked(self):
        """Handle button click by emitting signal with row index."""
        self.clicked.emit(self.row_index)


class TreatmentTable(QTableWidget):
    """
    Custom table widget for editing treatments.
    
    Features:
    - Drag and drop to reorder rows
    - Delete button for each row
    - Automatic EIQ calculation
    """
    
    treatment_changed = Signal()  # Signal when any treatment is modified
    treatment_deleted = Signal(int)  # Signal when a treatment is deleted
    add_treatment_clicked = Signal()  # Signal when add treatment button is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()
        
    def setup_table(self):
        """Set up the table structure and properties."""
        # Define columns
        columns = ["", "Date", "Control Product", "Rate", "Rate UOM", 
                   "Acres", "Application Method", "Active Groups", "Field EIQ", ""]
        
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        
        # Set column properties
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # Drag handle
        self.horizontalHeader().setSectionResizeMode(9, QHeaderView.Fixed)  # Delete button
        self.setColumnWidth(0, 30)  # Narrow column for drag handle
        self.setColumnWidth(9, 30)  # Narrow column for delete button
        
        # Configure selection and editing behavior
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.DoubleClicked | 
                            QAbstractItemView.EditKeyPressed)
        self.cellDoubleClicked.connect(self.cellDoubleClicked)
        self.cellChanged.connect(self.cellChanged)
        
        # Setup style
        self.setAlternatingRowColors(True)
        
    def add_empty_row(self):
        """Add an empty row to the table."""
        row_position = self.rowCount()
        self.insertRow(row_position)
        
        # Add drag handle
        drag_handle = DragButton()
        self.setCellWidget(row_position, 0, drag_handle)
        
        # Add empty cells
        for col in range(1, self.columnCount() - 1):
            self.setItem(row_position, col, QTableWidgetItem(""))
        
        # Add delete button
        delete_button = DeleteButton(row_position)
        delete_button.clicked.connect(self._delete_row)
        self.setCellWidget(row_position, self.columnCount() - 1, delete_button)
        
        return row_position
    
    def add_treatment_row(self):
        """Add a row at the bottom that says '+ add treatment'."""
        row_position = self.rowCount()
        self.insertRow(row_position)
        
        # Create a spanning item across all columns
        self.setSpan(row_position, 0, 1, self.columnCount())
        add_item = QTableWidgetItem("+ add treatment")
        add_item.setTextAlignment(Qt.AlignCenter)
        add_item.setBackground(QColor("#E6F0FF"))  # Light blue background
        self.setItem(row_position, 0, add_item)
        
    def _delete_row(self, row_index):
        """Handle deletion of a row."""
        # Emit signal before deleting the row
        self.treatment_deleted.emit(row_index)
        
        # Remove the row from the table
        self.removeRow(row_index)
        
        # Update delete button indices for all subsequent rows
        for row in range(row_index, self.rowCount()):
            delete_button = self.cellWidget(row, self.columnCount() - 1)
            if isinstance(delete_button, DeleteButton):
                delete_button.row_index = row
    
    def update_field_eiq(self, row, field_eiq):
        """Update the Field EIQ value and color for a row."""
        eiq_item = QTableWidgetItem(str(field_eiq))
        eiq_item.setTextAlignment(Qt.AlignCenter)
        
        # Color code based on EIQ value
        if field_eiq < 33.3:
            eiq_item.setBackground(EIQ_LOW_COLOR)
        elif field_eiq < 66.6:
            eiq_item.setBackground(EIQ_MEDIUM_COLOR)
        else:
            eiq_item.setBackground(EIQ_HIGH_COLOR)
        
        self.setItem(row, 8, eiq_item)
        
    def mousePressEvent(self, event):
        """Handle mouse press events for drag and drop."""
        super().mousePressEvent(event)
        
        # Check if we clicked the add treatment row
        row = self.rowAt(event.position().y())
        if row == self.rowCount() - 1:
            # Check if it's our add treatment row
            item = self.item(row, 0)
            if item and "add treatment" in item.text():
                self.add_treatment_clicked.emit()
                return
            
    def cellDoubleClicked(self, row, column):
        """Handle double-click on a cell."""
        # Skip the add treatment row
        if row == self.rowCount() - 1:
            return
            
        # Handle product selection column
        if column == 2:  # Control Product column
            self._select_product(row)

    def _select_product(self, row):
        """Open product selection dialog and handle selection."""
        dialog = ProductSelectionDialog(self)
        if dialog.exec():
            product = dialog.get_selected_product()
            if product:
                # Set product name in the table
                self.setItem(row, 2, QTableWidgetItem(product.display_name))
                
                # Set default rate and UOM
                if product.label_maximum_rate is not None:
                    self.setItem(row, 3, QTableWidgetItem(str(product.label_maximum_rate)))
                elif product.label_minimum_rate is not None:
                    self.setItem(row, 3, QTableWidgetItem(str(product.label_minimum_rate)))
                    
                if product.rate_uom:
                    self.setItem(row, 4, QTableWidgetItem(product.rate_uom))
                    
                # Set active groups (MoA groups)
                groups = product.get_ai_groups()
                groups_text = ", ".join(filter(None, groups))
                self.setItem(row, 7, QTableWidgetItem(groups_text))
                
                # Calculate and update Field EIQ
                self._update_treatment_eiq(row, product)
                
                # Emit change signal
                self.treatment_changed.emit()

    def _update_treatment_eiq(self, row, product):
        """Calculate and update the Field EIQ for a treatment."""
        try:
            # Get rate and UOM from the table
            rate_item = self.item(row, 3)
            uom_item = self.item(row, 4)
            acres_item = self.item(row, 5)
            
            if not rate_item or not uom_item:
                return
                
            rate = float(rate_item.text()) if rate_item.text() else 0.0
            uom = uom_item.text()
            acres = float(acres_item.text()) if acres_item and acres_item.text() else 0.0
            
            # Prepare active ingredients data for calculation
            active_ingredients = []
            
            # Add AI1 if present
            if product.ai1 and product.ai1_eiq is not None and product.ai1_concentration is not None:
                active_ingredients.append({
                    'name': product.ai1,
                    'eiq': product.ai1_eiq,
                    'percent': product.ai1_concentration
                })
                
            # Add AI2 if present
            if product.ai2 and product.ai2_eiq is not None and product.ai2_concentration is not None:
                active_ingredients.append({
                    'name': product.ai2,
                    'eiq': product.ai2_eiq,
                    'percent': product.ai2_concentration
                })
                
            # Add AI3 if present
            if product.ai3 and product.ai3_eiq is not None and product.ai3_concentration is not None:
                active_ingredients.append({
                    'name': product.ai3,
                    'eiq': product.ai3_eiq,
                    'percent': product.ai3_concentration
                })
                
            # Add AI4 if present
            if product.ai4 and product.ai4_eiq is not None and product.ai4_concentration is not None:
                active_ingredients.append({
                    'name': product.ai4,
                    'eiq': product.ai4_eiq,
                    'percent': product.ai4_concentration
                })
                
            # Calculate Field EIQ
            if active_ingredients and rate > 0:
                field_eiq = calculate_product_field_eiq(active_ingredients, rate, uom)
                
                # Scale by acres if specified
                if acres > 0:
                    field_eiq = field_eiq * acres
                    
                # Update the table
                self.update_field_eiq(row, field_eiq)
                
                # Return the calculated value
                return field_eiq
                
        except (ValueError, TypeError) as e:
            print(f"Error calculating EIQ: {e}")
        
        # Default to 0 if calculation fails
        self.update_field_eiq(row, 0)
        return 0

    def mouseMoveEvent(self, event):
        """Handle mouse move for drag & drop."""
        if not hasattr(self, 'drag_start_position') or not hasattr(self, 'drag_start_row'):
            super().mouseMoveEvent(event)
            return
            
        # Check if we've moved far enough to start a drag
        if ((event.position() - self.drag_start_position).manhattanLength() 
            < QApplication.startDragDistance()):
            super().mouseMoveEvent(event)
            return
        
        # Start drag operation
        row = self.rowAt(event.position().y())
        if row >= 0 and row < self.rowCount() - 1 and row != self.drag_start_row:
            # Simple implementation: just swap rows in the table
            self._swap_rows(self.drag_start_row, row)
            
            # Update drag start row
            self.drag_start_row = row
            
            # Emit change signal
            self.treatment_changed.emit()
        
        super().mouseMoveEvent(event)

    def _swap_rows(self, row1, row2):
        """Swap two rows in the table."""
        if row1 == row2:
            return
            
        # Ensure both rows are valid
        if row1 < 0 or row2 < 0 or row1 >= self.rowCount() - 1 or row2 >= self.rowCount() - 1:
            return
        
        # Remember the current selection
        selected_items = self.selectedItems()
        selected_rows = set(item.row() for item in selected_items)
        
        # Save data from both rows
        row1_data = []
        row2_data = []
        
        for col in range(1, self.columnCount() - 1):  # Skip drag and delete buttons
            item1 = self.item(row1, col)
            item2 = self.item(row2, col)
            
            row1_data.append(item1.text() if item1 else "")
            row2_data.append(item2.text() if item2 else "")
        
        # Swap data
        for col in range(1, self.columnCount() - 1):
            self.setItem(row1, col, QTableWidgetItem(row2_data[col-1]))
            self.setItem(row2, col, QTableWidgetItem(row1_data[col-1]))
        
        # Update delete button indices
        delete_button1 = self.cellWidget(row1, self.columnCount() - 1)
        delete_button2 = self.cellWidget(row2, self.columnCount() - 1)
        
        if isinstance(delete_button1, DeleteButton) and isinstance(delete_button2, DeleteButton):
            delete_button1.row_index, delete_button2.row_index = row2, row1
        
        # Restore selection
        self.clearSelection()
        for row in selected_rows:
            if row == row1:
                self.selectRow(row2)
            elif row == row2:
                self.selectRow(row1)
            else:
                self.selectRow(row)

    def cellChanged(self, row, column):
        """Handle cell content changes."""
        # Skip the add treatment row
        if row == self.rowCount() - 1:
            return
        
        # Handle different columns
        if column == 3:  # Rate column
            self._handle_rate_change(row)
        elif column == 4:  # UOM column
            self._handle_uom_change(row)
        elif column == 5:  # Acres column
            self._handle_acres_change(row)
        
        # Emit signal for general changes
        self.treatment_changed.emit()

    def _handle_rate_change(self, row):
        """Handle changes to the rate column."""
        # Get the product name
        product_item = self.item(row, 2)
        if not product_item or not product_item.text():
            return
        
        # Get the product from the repository
        products_repo = ProductRepository.get_instance()
        products = products_repo.get_filtered_products()
        
        # Find the product by name
        product_name = product_item.text().split(" (")[0]  # Remove any AI suffix
        product = None
        for p in products:
            if p.product_name == product_name:
                product = p
                break
        
        if product:
            # Update the EIQ calculation
            self._update_treatment_eiq(row, product)

    def _handle_uom_change(self, row):
        """Handle changes to the UOM column."""
        # Same as rate change, update EIQ
        self._handle_rate_change(row)

    def _handle_acres_change(self, row):
        """Handle changes to the acres column."""
        # Same as rate change, update EIQ
        self._handle_rate_change(row)