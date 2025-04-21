"""
Products list tab for the Lorenzo Pozzi Pesticide App

This module defines the ProductsListTab class which handles the product listing
and filtering functionality.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QCheckBox, QMenu
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush, QCursor

from ui.common.styles import get_body_font, PRIMARY_BUTTON_STYLE
from data.products_data import load_products


class ProductsListTab(QWidget):
    """
    Products list tab for displaying and filtering the products.
    
    This tab displays a table of products with filtering capabilities for
    each column.
    """
    def __init__(self, parent=None):
        """Initialize the products list tab."""
        super().__init__(parent)
        self.parent = parent
        self.column_keys = []  # Store CSV column keys
        self.region_column_index = -1  # Will store index of the region column
        self.active_filters = {}
        self.original_header_texts = {}  # Store original header texts
        self.all_products = []  # Store all loaded products
        self.setup_ui()
        self.load_product_data()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create table for products (columns will be set dynamically when loading data)
        self.products_table = QTableWidget()
        self.products_table.setAlternatingRowColors(True)
        self.products_table.verticalHeader().setVisible(False)  # Hide row numbers
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Connect header click for filtering
        self.products_table.horizontalHeader().sectionClicked.connect(self.header_clicked)
        
        main_layout.addWidget(self.products_table)
        
        # "Compare Selected" button
        compare_button = QPushButton("View Fact Sheet / Compare Selected Products")
        compare_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        compare_button.clicked.connect(self.parent.compare_selected_products)
        compare_button.setMinimumWidth(300)
        compare_button.setFont(get_body_font(size=11))
        
        main_layout.addWidget(compare_button, alignment=Qt.AlignRight)
    
    def load_product_data(self):
        """Load product data from the database using the load_products function."""
        self.products_table.setRowCount(0)
        products = load_products()
        
        if not products:
            return

        # Filter products by selected region
        filtered_products = []
        selected_region = self.parent.parent.selected_country if self.parent and self.parent.parent and hasattr(self.parent.parent, 'selected_country') else None
        
        if selected_region:
            # Only include products for the selected region
            filtered_products = [p for p in products if p.region == selected_region]
        else:
            # If no region selected, show all products
            filtered_products = products
            
        self.all_products = filtered_products  # Store filtered list of Product objects
        
        # Get the first product to determine column structure
        if filtered_products:
            first_product = filtered_products[0].to_dict()
            
            # Get all keys from the product dictionary
            self.column_keys = list(first_product.keys())
            
            # Set column count to all fields plus one for checkbox
            self.products_table.setColumnCount(len(self.column_keys) + 1)
            
            # Set column headers
            headers = ["Select"] + self.column_keys
            self.products_table.setHorizontalHeaderLabels(headers)
            
            # Store original header texts
            self.original_header_texts = {}
            for i, header_text in enumerate(headers):
                self.original_header_texts[i] = header_text
            
            # Set column resize modes
            self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Checkbox column
            for i in range(1, len(headers)):
                self.products_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            
            # Columns to hide (case-insensitive matching to handle potential variations)
            # Updated to handle the new concentration columns format
            columns_to_hide = [
                "region", "number of ai", "ai1 eiq", "ai1_concentration_%", "uom",
                "ai2", "ai2 eiq", "ai2 group", "ai2_concentration_%", "uom.1",
                "ai3", "ai3 eiq", "ai3 group", "ai3_concentration_%", "uom.2",
                "ai4", "ai4 eiq", "ai4 group", "ai4_concentration_%", "uom.3",
            ]
            
            # Hide specified columns
            for col, key in enumerate(self.column_keys, start=1):
                # Check if the key matches any of the hide keys in a case-insensitive manner
                if any(hide_key.lower() == key.lower() for hide_key in columns_to_hide):
                    self.products_table.setColumnHidden(col, True)

        # Set row count for filtered products
        self.products_table.setRowCount(len(filtered_products))
        
        # Populate the table with product data
        for row, product in enumerate(filtered_products):
            product_dict = product.to_dict()

            # Add checkbox for product selection
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, r=row: self.product_selected(r, state))
            checkbox_cell = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_cell)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.products_table.setCellWidget(row, 0, checkbox_cell)

            # Add all product fields
            for col, key in enumerate(self.column_keys, start=1):
                value = product_dict.get(key, "")
                self.products_table.setItem(row, col, QTableWidgetItem(str(value) if value is not None else ""))
        
        # Apply header styling after loading data
        self.update_header_styling()
    
    def header_clicked(self, column_index):
        """Handle click on table header for filtering."""
        # Skip the first column (checkbox column)
        if column_index == 0:
            return
        
        # Get unique values for this column
        unique_values = set()
        for row in range(self.products_table.rowCount()):
            # Only consider visible rows to respect currently applied filters
            if not self.products_table.isRowHidden(row):
                item = self.products_table.item(row, column_index)
                if item and item.text().strip():  # Only add non-empty values
                    unique_values.add(item.text())
        
        # Create a context menu with filter options
        menu = QMenu(self)
        header_text = self.products_table.horizontalHeaderItem(column_index).text()
        
        # Add "All" option
        all_action = menu.addAction("All")
        all_action.setCheckable(True)
        
        # Check if this column is currently filtered
        if column_index not in self.active_filters:
            all_action.setChecked(True)
        
        menu.addSeparator()
        
        # Add each unique value as an option
        value_actions = {}
        for value in sorted(unique_values):
            action = menu.addAction(value)
            action.setCheckable(True)
            
            # Check the action if it's in the active filter for this column
            if column_index in self.active_filters and value in self.active_filters[column_index]:
                action.setChecked(True)
            
            value_actions[action] = value
        
        # Add a "Clear Filter" option if filter is active
        if column_index in self.active_filters:
            menu.addSeparator()
            clear_action = menu.addAction("Clear Filter")
        else:
            clear_action = None
        
        # Show the menu at cursor position
        action = menu.exec(QCursor.pos())
        
        if action:
            if action == all_action:
                # Remove this column from filters
                if column_index in self.active_filters:
                    del self.active_filters[column_index]
            elif clear_action and action == clear_action:
                # Remove this column from filters
                if column_index in self.active_filters:
                    del self.active_filters[column_index]
            else:
                # Apply filter for the selected value
                value = value_actions.get(action)
                if value:
                    # Initialize filter set for this column if not exists
                    if column_index not in self.active_filters:
                        self.active_filters[column_index] = set()
                    
                    # Toggle the value in the filter set
                    if value in self.active_filters[column_index]:
                        self.active_filters[column_index].remove(value)
                        # If no values left, remove the column filter
                        if not self.active_filters[column_index]:
                            del self.active_filters[column_index]
                    else:
                        self.active_filters[column_index].add(value)
        
        # Apply all active filters
        self.apply_filters()
        
        # Update header styling to indicate active filters
        self.update_header_styling()
    
    def apply_filters(self):
        """Apply all active filters to the products table."""
        # Show all rows initially
        for row in range(self.products_table.rowCount()):
            self.products_table.showRow(row)
        
        # No filters active, return early
        if not self.active_filters:
            return
        
        # Check each row against all active filters
        for row in range(self.products_table.rowCount()):
            show_row = True
            
            # Check each active filter
            for column, allowed_values in self.active_filters.items():
                item = self.products_table.item(row, column)
                if item and item.text() not in allowed_values:
                    show_row = False
                    break
            
            # Show or hide the row based on filter results
            if show_row:
                self.products_table.showRow(row)
            else:
                self.products_table.hideRow(row)
    
    def update_header_styling(self):
        """Update header styling to indicate which columns have active filters."""
        for column in range(self.products_table.columnCount()):
            header_item = self.products_table.horizontalHeaderItem(column)
            if header_item and column in self.original_header_texts:
                if column in self.active_filters:
                    # Format to indicate active filter (green and bold)
                    header_item.setForeground(QBrush(QColor("#007C3E")))  # Green for active filters
                    header_item.setFont(get_body_font(size=10, bold=True))
                    
                    # Add a filter indicator to the header text
                    header_item.setText(f"{self.original_header_texts[column]} ↓")
                else:
                    # Reset to default
                    header_item.setForeground(QBrush(QColor("#000000")))
                    header_item.setFont(get_body_font(size=10, bold=False))
                    
                    # Restore the original header text without any indicators
                    header_item.setText(self.original_header_texts[column])
    
    def product_selected(self, row, state):
        """Handle product selection for comparison."""
        product = self.all_products[row]
        if state:
            if product not in self.parent.selected_products:
                self.parent.selected_products.append(product)
        else:
            if product in self.parent.selected_products:
                self.parent.selected_products.remove(product)