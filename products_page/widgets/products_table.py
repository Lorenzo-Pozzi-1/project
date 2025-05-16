"""
Product table widget for the LORENZO POZZI Pesticide App.

This module defines the ProductTable widget which provides a tabular
view of products with selection, filtering, and sorting capabilities.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Signal

from common.styles import GENERIC_TABLE_STYLE


class ProductTable(QTableWidget):
    """
    A table widget for displaying product information.
    
    This widget provides a tabular view of products with functionality for
    selection, filtering, and sorting.
    """
    
    selection_changed = Signal(list)  # Signal emitted when selection changes
    
    def __init__(self, parent=None):
        """Initialize the product table."""
        super().__init__(parent)
        self.all_products = []
        self.selected_products = []
        self.column_keys = []
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Configure table appearance
        self.setStyleSheet(GENERIC_TABLE_STYLE)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Configure header
        header = self.horizontalHeader()
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self.on_header_clicked)
    
    def set_products(self, products, column_keys=None):
        """
        Set the products to display in the table.
        
        Args:
            products: List of product objects
            column_keys: Optional list of column keys to display
        """
        # Clear existing table
        self.clear()
        self.setRowCount(0)
        
        # Store products
        self.all_products = products
        self.selected_products = []
        
        if not products:
            return
        
        # Determine columns to display
        if column_keys is None:
            # Get columns from first product
            first_product = products[0].to_dict()
            self.column_keys = list(first_product.keys())
        else:
            self.column_keys = column_keys
        
        # Configure table columns
        self._setup_table_columns()
        
        # Set row count
        self.setRowCount(len(products))
        
        # Fill table with data
        self._populate_table(products)
    
    def _setup_table_columns(self):
        """Configure table columns."""
        # Find AI1 column first
        ai1_col = -1
        for i, key in enumerate(self.column_keys):
            if key.lower() == "ai1":
                ai1_col = i
                break
        
        # Basic setup - all columns plus checkbox and groups column
        col_count = len(self.column_keys) + 2  # +1 for checkbox, +1 for groups
        self.setColumnCount(col_count)
        
        # Set header labels
        headers = ["Select"] + self.column_keys
        # Insert Groups header after AI1
        if ai1_col >= 0:
            groups_col = ai1_col + 2  # +1 for checkbox, +1 for position after AI1
            headers.insert(groups_col, "Groups")
        else:
            groups_col = -1
        
        self.setHorizontalHeaderLabels(headers)
        
        # Hide columns and manage visibility
        hide_columns = [
            "country", "region",
            "[ai1]", "[ai1]uom", "ai1 eiq",
            "[ai2]", "[ai2]uom", "ai2 eiq", "ai2",
            "[ai3]", "[ai3]uom", "ai3 eiq", "ai3",
            "[ai4]", "[ai4]uom", "ai4 eiq", "ai4"
        ]
        
        # Setup column properties
        for col, key in enumerate(self.column_keys, start=1):
            # Calculate the actual table column index
            table_col = col
            if groups_col > 0 and col >= groups_col:
                table_col = col + 1  # Adjust for inserted Groups column
            
            # Rename AI column
            if key.lower() == "ai1":
                self.horizontalHeader().model().setHeaderData(table_col, Qt.Horizontal, "AIs")
            
            # Hide specified columns
            elif any(key.lower() == hide_key.lower() for hide_key in hide_columns):
                self.setColumnHidden(table_col, True)
        
        # Set column sizing
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for col in range(1, col_count):
            if not self.isColumnHidden(col):
                self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)
    
    def _populate_table(self, products):
        """Populate table with product data."""
        # Find AI column
        ai1_col = -1
        for i, key in enumerate(self.column_keys):
            if key.lower() == "ai1":
                ai1_col = i
                break
        
        # Calculate groups column position
        groups_col = ai1_col + 2 if ai1_col >= 0 else -1  # +1 for checkbox, +1 for position after AI1
        
        # Fill table rows
        for row, product in enumerate(products):
            product_dict = product.to_dict()
            
            # Add checkbox
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, r=row: self.product_selected(r, state))
            checkbox_cell = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_cell)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.setCellWidget(row, 0, checkbox_cell)
            
            # Fill data cells
            for col, key in enumerate(self.column_keys, start=1):
                # Calculate the actual table column index
                table_col = col
                if groups_col > 0 and col >= groups_col:
                    table_col = col + 1  # Adjust for inserted Groups column
                
                # Handle active ingredients
                if col == ai1_col + 1:  # +1 for checkbox
                    ai_text = ", ".join(product.active_ingredients)
                    self.setItem(row, table_col, QTableWidgetItem(ai_text))
                    
                    # Add MoA groups data
                    if groups_col > 0:
                        ai_groups = product.get_ai_groups()
                        groups_text = ", ".join(filter(None, ai_groups))  # Filter out empty strings
                        self.setItem(row, groups_col, QTableWidgetItem(groups_text))
                else:
                    # Normal column
                    value = product_dict.get(key, "")
                    if value is not None:
                        self.setItem(row, table_col, QTableWidgetItem(str(value)))
                    else:
                        self.setItem(row, table_col, QTableWidgetItem(""))
    
    def product_selected(self, row, state):
        """
        Handle product selection from checkbox.
        
        Args:
            row: Table row index
            state: Qt.CheckState value
        """
        product = self.all_products[row]
        if state:
            if product not in self.selected_products:
                self.selected_products.append(product)
        else:
            if product in self.selected_products:
                self.selected_products.remove(product)
        
        self.selection_changed.emit(self.selected_products)
    
    def get_selected_products(self):
        """
        Get the currently selected products.
        
        Returns:
            list: List of selected product objects
        """
        return self.selected_products
    
    def clear_selection(self):
        """Clear all product selections."""
        self.selected_products = []
        
        # Uncheck all checkboxes
        for row in range(self.rowCount()):
            checkbox_widget = self.cellWidget(row, 0)
            if checkbox_widget:
                layout = checkbox_widget.layout()
                if layout and layout.count() > 0:
                    checkbox = layout.itemAt(0).widget()
                    if isinstance(checkbox, QCheckBox):
                        checkbox.setChecked(False)
        
        self.selection_changed.emit(self.selected_products)
    
    def on_header_clicked(self, column):
        """
        Handle column header click for sorting.
        
        Args:
            column: The clicked column index
        """
        # Skip checkbox column
        if column == 0:
            return
            
        # Sort the table by the selected column
        self.sortByColumn(column, Qt.AscendingOrder)
    
    def apply_filter(self, column, filter_text):
        """
        Apply a text filter to a specific column.
        
        Args:
            column: The column index to filter
            filter_text: The text to filter for
        """
        filter_text = filter_text.lower()
        
        for row in range(self.rowCount()):
            # Get item in the column
            item = self.item(row, column)
            show_row = True
            
            if item:
                # Check if item text contains filter text
                item_text = item.text().lower()
                show_row = filter_text in item_text
            
            # Show or hide the row
            self.setRowHidden(row, not show_row)
    
    def apply_filters(self, filters):
        """
        Apply multiple filters to the table.
        
        Args:
            filters: List of (column_index, filter_text) tuples
        """
        # Show all rows initially
        for row in range(self.rowCount()):
            self.showRow(row)
        
        # Apply each filter in sequence
        for column_index, filter_text in filters:
            if filter_text:  # Only apply if filter text is not empty
                for row in range(self.rowCount()):
                    if not self.isRowHidden(row):  # Only check visible rows
                        item = self.item(row, column_index)
                        cell_text = item.text().lower() if item else ""
                        if filter_text not in cell_text:
                            self.setRowHidden(row, True)