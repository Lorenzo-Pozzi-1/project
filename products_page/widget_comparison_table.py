"""
Comparison table component for the LORENZO POZZI Pesticide App.

This module defines the ComparisonTable widget which provides a
side-by-side comparison of product properties.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from common import GENERIC_TABLE_STYLE, get_eiq_color, get_medium_font, get_config, calculation_tracer
from common.calculations import eiq_calculator
from common.constants import get_spacing_xlarge


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
        # Define the exact properties to display and their order
        self.display_properties = [
            ("Field EIQ\n1 application, max. rate", "field_eiq"),  # Special calculated field
            ("AI 1", "AI1"),
            ("AI 2", "AI2"),
            ("AI 3", "AI3"),
            ("AI 4", "AI4"),
            ("Formulation", "formulation"),
            ("Application Method", "use"),
            ("Min Rate", "min rate"),
            ("Max Rate", "max rate"),
            ("Rate UOM", "rate UOM"),
            ("REI (hours)", "REI (h)"),
            ("PHI (days)", "PHI (d)"),
            ("min days btwn apps", "min days between applications"),
            ("Type", "type"),
            ("Reg. #", "reg. #"),
            ("Registrant", "registrant")
        ]
    
    def setup_ui(self):
        """Set up the UI components."""
        # Set up visual style
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.verticalHeader().setMinimumHeight(30)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

        
        
        # Style the horizontal header
        self.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.horizontalHeader().setFont(get_medium_font(bold=True))
        self.horizontalHeader().setMinimumHeight(40)
        self.horizontalHeader().setStyleSheet(GENERIC_TABLE_STYLE)

    def set_display_properties(self, properties):
        """
        Set the list of properties to display in the comparison.
        
        Args:
            properties: List of tuples (display_name, property_key)
                       where display_name is shown in the table and 
                       property_key is the key in the product dictionary
        """
        self.display_properties = properties
    
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
        
        # Set up comparison table dimensions
        self.setRowCount(len(self.display_properties))
        self.setColumnCount(len(products) + 1)
        
        # Set column headers
        headers = ["Product"]
        for product in products:
            product_dict = product.to_dict()
            headers.append(str(product_dict.get("name")))
        
        self.setHorizontalHeaderLabels(headers)
        
        # Set row labels and populate data
        for row, (display_name, property_key) in enumerate(self.display_properties):
            # Set the property name in the first column
            self.setItem(row, 0, self.create_table_item(display_name, bold=True))
            
            # Populate data for each product
            for col, product in enumerate(products, 1):
                if property_key == "field_eiq":
                    # Special handling for calculated Field EIQ
                    field_eiq = self.calculate_product_field_eiq(product)
                    eiq_item = self.create_table_item(f"{field_eiq:.2f}" if field_eiq > 0 else "--")
                    if field_eiq > 0:
                        bg_color = get_eiq_color(field_eiq)
                        eiq_item.setBackground(QBrush(bg_color))
                    self.setItem(row, col, eiq_item)
                else:
                    # Regular property from product dictionary
                    product_dict = product.to_dict()
                    value = product_dict.get(property_key, "")
                    # Check for missing or empty values
                    if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
                        display_value = "--"
                    else:
                        display_value = str(value)
                    self.setItem(row, col, self.create_table_item(display_value))
        
        # Resize columns
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for col in range(1, self.columnCount()):
            self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)
        
        # Force row heights to resize to content after populating data
        self.setRowHeight(0,2*get_spacing_xlarge()) 
        # self.resizeRowsToContents()
    
    def calculate_product_field_eiq(self, product):
        """Calculate the Field EIQ for a product using its maximum application rate."""
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
            
            # Get user preferences for UOM conversions
            user_preferences = get_config("user_preferences", {})
            
            # Calculate Field EIQ
            calculation_tracer.log(f"\n\n====================================================================")
            calculation_tracer.log(f"{product.product_name}")
            calculation_tracer.log(f"====================================================================")
            field_eiq = eiq_calculator.calculate_product_field_eiq(
                active_ingredients=ai_data,
                application_rate=rate,
                application_rate_uom=product.rate_uom,
                applications=1,
                user_preferences=user_preferences
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
        font = get_medium_font(bold=bold)
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
        self.no_selection_label.setFont(get_medium_font())
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