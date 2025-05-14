"""
Comparison table component for the LORENZO POZZI Pesticide App.

This module defines the ComparisonTable widget which provides a
side-by-side comparison of product properties.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from common.styles import apply_table_header_style, get_eiq_color
from common.styles import get_body_font
from math_module.eiq_calculations import calculate_product_field_eiq


class ComparisonTable(QTableWidget):
    """
    A table widget for comparing product properties side by side.
    
    This widget displays product properties in a table format with
    properties as rows and products as columns.
    """
    
    def __init__(self, parent=None):
        """Initialize the comparison table."""
        super().__init__(0, 0, parent)
        self.setup_ui()
        self.columns_to_hide = []
        self.set_columns_to_hide([
            "country","region","number of ai","name",
            "[AI1]","[AI2]","[AI3]","[AI4]",
            "[AI1]UOM","[AI2]UOM","[AI3]UOM","[AI4]UOM"
        ])
    
    def setup_ui(self):
        """Set up the UI components."""
        # Set up visual style
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.verticalHeader().setVisible(False)
        
        # Configure horizontal header
        apply_table_header_style(self.horizontalHeader())
        header_font = get_body_font(bold=True)
        self.horizontalHeader().setFont(header_font)
        
        # Configure row heights
        self.verticalHeader().setDefaultSectionSize(40)
    
    def set_columns_to_hide(self, columns):
        """
        Set the list of columns to hide in the comparison.
        
        Args:
            columns: List of column names to hide
        """
        self.columns_to_hide = columns
    
    def update_comparison(self, products):
        """
        Update the comparison table with the provided products.
        
        Args:
            products: List of product objects to compare
        """
        if not products:
            self.setRowCount(0)
            self.setColumnCount(0)
            return
        
        # Get the first product to determine available columns
        first_product = products[0].to_dict()
        all_columns = list(first_product.keys())
        
        # Filter out columns we don't want to compare
        visible_columns = []
        for key in all_columns:
            if not any(hide_key.lower() == key.lower() for hide_key in self.columns_to_hide):
                visible_columns.append(key)
        
        # Set up comparison table
        self.setRowCount(len(visible_columns) + 1)  # +1 for Field EIQ row
        self.setColumnCount(len(products) + 1)
        
        # Set headers
        headers = ["Product"]
        for product in products:
            product_dict = product.to_dict()
            product_name_key = "name"  # Default key for product name
            # If product name column isn't available, use first column that contains "name"
            if product_name_key not in product_dict:
                for key in product_dict.keys():
                    if "name" in key.lower():
                        product_name_key = key
                        break
            headers.append(product_dict.get(product_name_key, "Unknown Product"))
        
        self.setHorizontalHeaderLabels(headers)
        
        # Set row labels (first column)
        for row, property_name in enumerate(visible_columns):
            self.setItem(row, 0, self.create_table_item(property_name, bold=True))
        
        # Add Field EIQ row label
        field_eiq_row = len(visible_columns)
        self.setItem(field_eiq_row, 0, self.create_table_item("Field EIQ\n1 application, max. rate", bold=True))
        self.resizeRowToContents(field_eiq_row)
        
        # Populate product data
        for col, product in enumerate(products, 1):
            # Convert product object to dictionary
            product_dict = product.to_dict()
            
            # Fill in properties
            for row, property_name in enumerate(visible_columns):
                value = product_dict.get(property_name, "")
                self.setItem(row, col, self.create_table_item(str(value) if value is not None else ""))
            
            # Calculate Field EIQ using max rate
            field_eiq = self.calculate_product_field_eiq(product)
            
            # Add Field EIQ value with color coding
            eiq_item = self.create_table_item(f"{field_eiq:.2f}" if field_eiq > 0 else "--")
            if field_eiq > 0:
                bg_color = get_eiq_color(field_eiq)
                eiq_item.setBackground(QBrush(bg_color))
            self.setItem(field_eiq_row, col, eiq_item)
        
        # Resize columns to fit content
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for col in range(1, self.columnCount()):
            self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)
    
    def calculate_product_field_eiq(self, product):
        """
        Calculate the Field EIQ for a product using its maximum application rate.
        
        Args:
            product: The product object
            
        Returns:
            float: Calculated Field EIQ or 0 if calculation fails
        """
        try:
            # Check if product has active ingredients with EIQ data
            ai_data = product.get_ai_data()
            if not ai_data:
                return 0
            
            # Use maximum rate if available, otherwise minimum rate
            rate = product.label_maximum_rate
            if rate is None:
                rate = product.label_minimum_rate
            
            # If no rate available, return 0
            if rate is None or product.rate_uom is None:
                return 0
            
            # Calculate Field EIQ using 1 application
            field_eiq = calculate_product_field_eiq(
                ai_data,
                rate,
                product.rate_uom,
                applications=1
            )
            
            return field_eiq
        except Exception as e:
            print(f"Error calculating Field EIQ: {e}")
            return 0
    
    def create_table_item(self, text, bold=False, background_color=None):
        """
        Create a formatted table item.
        
        Args:
            text: The text to display
            bold: Whether the text should be bold
            background_color: Optional background color
            
        Returns:
            QTableWidgetItem: The formatted table item
        """
        item = QTableWidgetItem(text)
        
        # Set alignment and word wrap
        item.setTextAlignment(Qt.AlignCenter | Qt.TextWordWrap)
        
        # Set font
        font = get_body_font(bold=bold)
        item.setFont(font)
        
        # Set background color if provided
        if background_color:
            item.setBackground(QBrush(QColor(background_color)))
        
        return item
    
    def clear_comparison(self):
        """Clear the comparison table."""
        self.setRowCount(0)
        self.setColumnCount(0)


class ComparisonView(QWidget):
    """
    A container widget for the comparison table with header and message.
    
    This widget provides a complete view for product comparison including
    a header, message when no products are selected, and the comparison table.
    """
    
    def __init__(self, parent=None):
        """Initialize the comparison view."""
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Message for when no products are selected
        self.no_selection_label = QLabel("Select products from the list tab and click 'Compare Selected Products'")
        self.no_selection_label.setAlignment(Qt.AlignCenter)
        self.no_selection_label.setFont(get_body_font())
        layout.addWidget(self.no_selection_label)
        
        # Comparison table (initially hidden)
        self.comparison_table = ComparisonTable()
        self.comparison_table.setVisible(False)
        layout.addWidget(self.comparison_table)
    
    def update_comparison(self, products):
        """
        Update the comparison view with the selected products.
        
        Args:
            products: List of product objects to compare
        """
        if not products:
            # If no products selected, show message
            self.no_selection_label.setText("No products selected for comparison. Please select at least one product.")
            self.no_selection_label.setVisible(True)
            self.comparison_table.setVisible(False)
            return
        
        # Hide the "no selection" message
        self.no_selection_label.setVisible(False)
        
        # Show and update the comparison table
        self.comparison_table.setVisible(True)
        self.comparison_table.update_comparison(products)
    
    def clear(self):
        """Clear the comparison view."""
        self.no_selection_label.setText("Select products from the list tab and click 'Compare Selected Products'")
        self.no_selection_label.setVisible(True)
        self.comparison_table.setVisible(False)
        self.comparison_table.clear_comparison()