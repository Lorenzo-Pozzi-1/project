"""
Products comparison tab for the Lorenzo Pozzi Pesticide App

This module defines the ProductsComparisonTab class which handles the product
comparison functionality.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt

from common.styles import get_body_font


class ProductsComparisonTab(QWidget):
    """
    Products comparison tab for comparing selected products.
    
    This tab displays a table comparing the properties of selected products
    side by side.
    """
    def __init__(self, parent=None):
        """Initialize the products comparison tab."""
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Message for when no products are selected
        self.no_selection_label = QLabel("Select products from the list tab and click 'Compare Selected Products'")
        self.no_selection_label.setAlignment(Qt.AlignCenter)
        self.no_selection_label.setFont(get_body_font(size=12))
        main_layout.addWidget(self.no_selection_label)
        
        # Comparison table (initially hidden)
        self.comparison_table = QTableWidget()
        self.comparison_table.setVisible(False)
        main_layout.addWidget(self.comparison_table)
    
    def update_comparison_view(self, selected_products):
        """Update the comparison view with the selected products."""
        if not selected_products:
            # If no products selected, show message
            self.no_selection_label.setText("No products selected for comparison. Please select at least one product.")
            self.no_selection_label.setVisible(True)
            self.comparison_table.setVisible(False)
            return
        
        # Hide the "no selection" message
        self.no_selection_label.setVisible(False)
        
        # Show and configure the comparison table
        self.comparison_table.setVisible(True)
        
        # Get the first product to determine available columns
        if not selected_products:
            return
        
        first_product = selected_products[0].to_dict()
        all_columns = list(first_product.keys())
        
        # Filter out columns we don't want to compare
        columns_to_hide = [
            "region", "number of ai", "ai1 eiq", "ai1concentration", "uom",
            "ai2", "ai2 eiq", "ai2 group", "ai2concentration", "uom.1",
            "ai3", "ai3 eiq", "ai3 group", "ai3concentration", "uom.2",
            "ai4", "ai4 eiq", "ai4 group", "ai4concentration", "uom.3",
        ]
        
        # Filter the column keys to only include visible columns
        visible_columns = []
        for key in all_columns:
            if not any(hide_key.lower() == key.lower() for hide_key in columns_to_hide):
                visible_columns.append(key)
        
        # Set up comparison table
        self.comparison_table.setRowCount(len(visible_columns))
        self.comparison_table.setColumnCount(len(selected_products) + 1)
        
        # Set headers
        headers = ["Property"]
        for product in selected_products:
            product_dict = product.to_dict()
            product_name_key = "product name"  # Default key for product name
            # If product name column isn't available, use first column that contains "name"
            if product_name_key not in product_dict:
                for key in product_dict.keys():
                    if "name" in key.lower():
                        product_name_key = key
                        break
            headers.append(product_dict.get(product_name_key, "Unknown Product"))
        
        self.comparison_table.setHorizontalHeaderLabels(headers)
        
        # Set row labels (first column)
        for row, property_name in enumerate(visible_columns):
            self.comparison_table.setItem(row, 0, QTableWidgetItem(property_name))
        
        # Populate product data
        for col, product in enumerate(selected_products, 1):
            # Convert product object to dictionary
            product_dict = product.to_dict()
            
            # Fill in properties
            for row, property_name in enumerate(visible_columns):
                value = product_dict.get(property_name, "")
                self.comparison_table.setItem(row, col, QTableWidgetItem(str(value) if value is not None else ""))
        
        # Resize columns to fit content
        self.comparison_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for col in range(1, self.comparison_table.columnCount()):
            self.comparison_table.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)
    
    def clear_comparison(self):
        """Clear the comparison table and show the no selection message."""
        self.no_selection_label.setText("Select products from the list tab and click 'Compare Selected Products'")
        self.no_selection_label.setVisible(True)
        self.comparison_table.setVisible(False)