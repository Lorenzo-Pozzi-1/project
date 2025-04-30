"""
Single Product EIQ Calculator for the LORENZO POZZI Pesticide App.

This module provides the SingleProductCalculator widget for calculating EIQ
of a single pesticide product with search and suggestions functionality.
It supports displaying multiple active ingredients (up to 4) with improved UOM handling.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, 
    QFormLayout, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush

from common.styles import PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE, get_body_font
from common.widgets import ContentFrame
from eiq_calculator.eiq_ui_components import get_products_from_csv, get_product_info, ProductSearchField, EiqResultDisplay
from eiq_calculator.eiq_calculations import calculate_product_field_eiq
from eiq_calculator.eiq_conversions import convert_concentration_to_percent, convert_concentration_to_decimal, APPLICATION_RATE_CONVERSION


class SingleProductCalculator(QWidget):
    """Widget for calculating EIQ for a single pesticide product."""
    
    def __init__(self, parent=None):
        """Initialize the single product calculator widget."""
        super().__init__(parent)
        self.parent = parent
        
        # Store the full list of products
        self.all_products = []
        
        # Initialize UI elements to avoid AttributeError
        self.product_type_combo = None
        self.product_search = None
        self.ai_table = None  # Changed to table for multiple AIs
        self.rate_spin = None
        self.rate_unit_combo = None
        self.applications_spin = None
        self.eiq_results_display = None
        
        # Currently selected product data
        self.current_product = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout with stretching to ensure proper alignment when window is resized
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Product selection area
        product_frame = ContentFrame()
        product_layout = QFormLayout()
        product_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Load products data
        self.all_products = get_products_from_csv()
        
        # Product type selection
        self.product_type_combo = QComboBox()
        self.product_type_combo.setFont(get_body_font())
        
        # Load product types from products data
        product_types = []
        if self.all_products:
            product_types = sorted(list(set(p.product_type for p in self.all_products if p.product_type)))
        
        self.product_type_combo.addItem("All Types")
        self.product_type_combo.addItems(product_types)
        self.product_type_combo.currentIndexChanged.connect(self.update_product_list)
        product_layout.addRow("Product Type:", self.product_type_combo)
        
        # Product selection with search
        self.product_search = ProductSearchField()
        self.product_search.product_selected.connect(self.update_product_info)
        product_layout.addRow("Product:", self.product_search)

        # Create Active Ingredients table
        self.ai_table = QTableWidget()
        self.ai_table.setRowCount(0)  # Start empty
        self.ai_table.setColumnCount(3)
        self.ai_table.setHorizontalHeaderLabels(["Active Ingredient", "EIQ", "Concentration %"])
        
        # Make all columns equal width by setting them all to Stretch
        header = self.ai_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Set a reasonable fixed height for the table
        self.ai_table.setMinimumHeight(120)
        self.ai_table.setMaximumHeight(150)
        self.ai_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Use a direct form layout row instead of a container
        product_layout.addRow("Active Ingredients:", self.ai_table)
        
        # Application rate
        rate_layout = QHBoxLayout()
        
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0.0, 9999.99)
        self.rate_spin.setValue(0.0)
        self.rate_spin.setDecimals(2)
        self.rate_spin.valueChanged.connect(self.calculate_single_eiq)
        
        # Unit of measure selection for application rate
        self.rate_unit_combo = QComboBox()
        # Populate with sorted options from the APPLICATION_RATE_CONVERSION dictionary
        self.rate_unit_combo.addItems(sorted(APPLICATION_RATE_CONVERSION.keys()))
        self.rate_unit_combo.setFont(get_body_font())
        self.rate_unit_combo.currentIndexChanged.connect(self.calculate_single_eiq)
        
        rate_layout.addWidget(self.rate_spin)
        rate_layout.addWidget(self.rate_unit_combo)
        
        product_layout.addRow("Application Rate:", rate_layout)
        
        # Number of applications
        self.applications_spin = QDoubleSpinBox()
        self.applications_spin.setRange(1, 10)
        self.applications_spin.setValue(1)
        self.applications_spin.setDecimals(0)
        self.applications_spin.valueChanged.connect(self.calculate_single_eiq)
        product_layout.addRow("Number of Applications:", self.applications_spin)
        
        product_frame.layout.addLayout(product_layout)
        layout.addWidget(product_frame)
        
        # Results area using the EiqResultDisplay component
        results_frame = ContentFrame()
        self.eiq_results_display = EiqResultDisplay()
        results_frame.layout.addWidget(self.eiq_results_display)
        layout.addWidget(results_frame)
        
        # Save and Export buttons
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Save Calculation")
        save_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        
        export_button = QPushButton("Export Results")
        export_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(export_button)
        buttons_layout.addStretch(1)
        
        layout.addLayout(buttons_layout)
        
        # Update product list
        self.update_product_list()
    
    def update_product_list(self):
        """Update the product list based on selected product type."""
        if not self.product_search:
            return
        
        try:
            if self.all_products:
                # Filter by product type if selected
                filtered_products = self.all_products
                product_type = self.product_type_combo.currentText()
                
                if product_type != "All Types":
                    filtered_products = [p for p in self.all_products if p.product_type == product_type]
                
                # Get product display names
                product_names = [p.display_name for p in filtered_products]
                
                # Update search field with filtered products
                self.product_search.set_items(product_names)
                
                # Clear current selection
                self.product_search.clear()
                
                # Reset fields
                self.clear_ai_table()
                self.rate_spin.setValue(0.0)
                self.eiq_results_display.update_result(0.0)
            else:
                # Handle case where no products are loaded
                self.product_search.setEnabled(False)
                print("No products found in CSV file")
        
        except Exception as e:
            print(f"Error updating product list: {e}")
            self.product_search.setEnabled(False)
    
    def clear_ai_table(self):
        """Clear the active ingredients table."""
        self.ai_table.setRowCount(0)

    def update_product_info(self, product_name):
        """Update product information when a product is selected."""
        if not product_name:
            # Clear fields if no product is selected
            self.clear_ai_table()
            self.rate_spin.setValue(0.0)
            self.eiq_results_display.update_result(0.0)
            return
            
        try:
            # Find the actual product object by name (removing any suffix in parentheses)
            name_without_suffix = product_name.split(" (")[0]
            for product in self.all_products:
                if product.product_name == name_without_suffix:
                    self.current_product = product
                    break
            
            if not self.current_product:
                raise ValueError(f"Product '{name_without_suffix}' not found")
            
            # Clear active ingredients table
            self.clear_ai_table()
            
            # Add rows for each active ingredient that has data
            ai_data = []
            
            # Check AI1 data
            if self.current_product.ai1:
                concentration = self.current_product.ai1_concentration
                uom = self.current_product.ai1_concentration_uom
                percent_value = convert_concentration_to_percent(concentration, uom)
                
                ai_data.append({
                    "name": self.current_product.ai1,
                    "eiq": self.current_product.ai1_eiq if self.current_product.ai1_eiq is not None else "--",
                    "percent": percent_value if percent_value is not None else "--"
                })
            
            # Check AI2 data
            if self.current_product.ai2:
                concentration = self.current_product.ai2_concentration
                uom = self.current_product.ai2_concentration_uom
                percent_value = convert_concentration_to_percent(concentration, uom)
                
                ai_data.append({
                    "name": self.current_product.ai2,
                    "eiq": self.current_product.ai2_eiq if self.current_product.ai2_eiq is not None else "--",
                    "percent": percent_value if percent_value is not None else "--"
                })
            
            # Check AI3 data
            if self.current_product.ai3:
                concentration = self.current_product.ai3_concentration
                uom = self.current_product.ai3_concentration_uom
                percent_value = convert_concentration_to_percent(concentration, uom)
                
                ai_data.append({
                    "name": self.current_product.ai3,
                    "eiq": self.current_product.ai3_eiq if self.current_product.ai3_eiq is not None else "--",
                    "percent": percent_value if percent_value is not None else "--"
                })
            
            # Check AI4 data
            if self.current_product.ai4:
                concentration = self.current_product.ai4_concentration
                uom = self.current_product.ai4_concentration_uom
                percent_value = convert_concentration_to_percent(concentration, uom)
                
                ai_data.append({
                    "name": self.current_product.ai4,
                    "eiq": self.current_product.ai4_eiq if self.current_product.ai4_eiq is not None else "--",
                    "percent": percent_value if percent_value is not None else "--"
                })
            
            # Add rows to table
            self.ai_table.setRowCount(len(ai_data))
            
            for i, ai in enumerate(ai_data):
                # Name
                name_item = QTableWidgetItem(ai["name"])
                name_item.setTextAlignment(Qt.AlignCenter)
                self.ai_table.setItem(i, 0, name_item)
                
                # EIQ
                eiq_item = QTableWidgetItem(str(ai["eiq"]))
                eiq_item.setTextAlignment(Qt.AlignCenter)
                self.ai_table.setItem(i, 1, eiq_item)
                
                # Percent
                percent_item = QTableWidgetItem(f"{ai['percent']}%" if ai["percent"] != "--" else "--")
                percent_item.setTextAlignment(Qt.AlignCenter)
                self.ai_table.setItem(i, 2, percent_item)
            
            # Update application rate with max rate from product data
            if self.current_product.label_maximum_rate is not None:
                self.rate_spin.setValue(self.current_product.label_maximum_rate)
            elif self.current_product.label_minimum_rate is not None:
                self.rate_spin.setValue(self.current_product.label_minimum_rate)
            else:
                self.rate_spin.setValue(0.0)
            
            # Set rate unit to match product's UOM
            rate_unit = self.current_product.rate_uom
            if rate_unit and rate_unit in APPLICATION_RATE_CONVERSION:
                index = self.rate_unit_combo.findText(rate_unit)
                if index >= 0:
                    self.rate_unit_combo.setCurrentIndex(index)
            
            # Calculate EIQ with new values
            self.calculate_single_eiq()
            
        except Exception as e:
            print(f"Error loading product info for '{product_name}': {e}")
            # Clear fields on error
            self.clear_ai_table()
            self.rate_spin.setValue(0.0)
            self.eiq_results_display.update_result(0.0)
    
    def calculate_single_eiq(self):
        """Calculate the Field EIQ for a single product."""
        if not self.current_product or self.ai_table.rowCount() == 0:
            self.eiq_results_display.update_result(0.0)
            return
            
        try:
            # Collect all active ingredients data from the table
            active_ingredients = []
            
            for row in range(self.ai_table.rowCount()):
                # Get AI data from table
                name_item = self.ai_table.item(row, 0)
                eiq_item = self.ai_table.item(row, 1)
                percent_item = self.ai_table.item(row, 2)
                
                if not eiq_item or not percent_item or eiq_item.text() == "--" or percent_item.text() == "--":
                    continue
                
                # Extract percent value without '%' sign if present
                percent_text = percent_item.text()
                if "%" in percent_text:
                    percent_value = float(percent_text.replace("%", "").strip())
                else:
                    percent_value = float(percent_text)
                
                active_ingredients.append({
                    'name': name_item.text() if name_item else "",
                    'eiq': float(eiq_item.text()),
                    'percent': percent_value
                })
            
            # Get application parameters
            rate = self.rate_spin.value()
            applications = int(self.applications_spin.value())
            unit = self.rate_unit_combo.currentText()
            
            # Calculate total Field EIQ using the improved function
            total_field_eiq = calculate_product_field_eiq(
                active_ingredients, rate, unit, applications)
            
            # Update result display with the new EIQ value
            self.eiq_results_display.update_result(total_field_eiq)
            
        except (ValueError, ZeroDivisionError, AttributeError) as e:
            print(f"Error calculating EIQ: {e}")
            self.eiq_results_display.update_result(0.0)