"""
Product Comparison Calculator for the LORENZO POZZI Pesticide App.

This module provides the ProductComparisonCalculator widget for comparing EIQ
values of multiple pesticide products with improved UOM management.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QDoubleSpinBox,
    QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush

from common.styles import get_subtitle_font, PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
from common.widgets import ContentFrame
from eiq_calculator.eiq_ui_components import get_products_from_csv, ColorCodedEiqItem
from eiq_calculator.eiq_calculations import calculate_product_field_eiq, format_eiq_result
from eiq_calculator.eiq_conversions import convert_concentration_to_percent, convert_concentration_to_decimal, APPLICATION_RATE_CONVERSION


class ProductComparisonCalculator(QWidget):
    """Widget for comparing EIQ values of multiple pesticide products with real-time updates."""
    
    def __init__(self, parent=None):
        """Initialize the product comparison calculator widget."""
        super().__init__(parent)
        self.parent = parent
        self.products_data = []  # List to track product data
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Products selection section
        selection_frame = ContentFrame()
        selection_layout = QVBoxLayout()
        
        selection_title = QLabel("Select Products to Compare")
        selection_title.setFont(get_subtitle_font(size=16))
        selection_layout.addWidget(selection_title)
        
        # Comparison selection table
        self.comparison_selection_table = QTableWidget(0, 6)
        self.comparison_selection_table.setHorizontalHeaderLabels([
            "Product Type", "Product Name", "Active Ingredients", "Application Rate", 
            "Unit", "Applications"
        ])
        
        # Set up table properties
        header = self.comparison_selection_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        # Add initial empty rows
        self.add_product_row()
        
        selection_layout.addWidget(self.comparison_selection_table)
        
        # Add another product button and remove selected button
        buttons_layout = QHBoxLayout()
        
        add_product_button = QPushButton("Add Another Product")
        add_product_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        add_product_button.clicked.connect(self.add_product_row)
        buttons_layout.addWidget(add_product_button)
        
        remove_button = QPushButton("Remove Selected")
        remove_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        remove_button.clicked.connect(self.remove_selected_row)
        buttons_layout.addWidget(remove_button)
        
        buttons_layout.addStretch(1)
        
        selection_layout.addLayout(buttons_layout)
        
        selection_frame.layout.addLayout(selection_layout)
        main_layout.addWidget(selection_frame)
        
        # Comparison results section
        results_frame = ContentFrame()
        results_layout = QVBoxLayout()
        
        results_title = QLabel("EIQ Comparison Results")
        results_title.setFont(get_subtitle_font(size=16))
        results_layout.addWidget(results_title)
        
        # Results table
        self.comparison_results_table = QTableWidget(0, 3)
        self.comparison_results_table.setHorizontalHeaderLabels([
            "Product", "Field EIQ / acre", "Field EIQ / ha"
        ])
        
        # Set up table properties - all columns equal width
        self.comparison_results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        results_layout.addWidget(self.comparison_results_table)
        
        results_frame.layout.addLayout(results_layout)
        main_layout.addWidget(results_frame)
        
        # Export button
        export_button = QPushButton("Export Comparison")
        export_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        export_button.clicked.connect(self.export_comparison)
        main_layout.addWidget(export_button, alignment=Qt.AlignRight)
    
    def add_product_row(self):
        """Add a new row to the comparison selection table."""
        row = self.comparison_selection_table.rowCount()
        self.comparison_selection_table.insertRow(row)
        
        # Product Type combo box
        type_combo = QComboBox()
        type_combo.addItem("Select type...")
        
        # Load product types
        products = get_products_from_csv()
        product_types = []
        if products:
            product_types = sorted(list(set(p.product_type for p in products if p.product_type)))
        
        type_combo.addItems(product_types)
        type_combo.currentIndexChanged.connect(lambda idx, r=row: self.update_product_combo(r))
        self.comparison_selection_table.setCellWidget(row, 0, type_combo)
        
        # Product Name combo box
        product_combo = QComboBox()
        product_combo.addItem("Select product...")
        product_combo.currentIndexChanged.connect(lambda idx, r=row: self.update_product_info(r))
        self.comparison_selection_table.setCellWidget(row, 1, product_combo)
        
        # Active ingredient (read-only)
        ai_item = QTableWidgetItem("")
        ai_item.setFlags(ai_item.flags() & ~Qt.ItemIsEditable)
        self.comparison_selection_table.setItem(row, 2, ai_item)
        
        # Application rate spinner
        rate_spin = QDoubleSpinBox()
        rate_spin.setRange(0.0, 9999.99)
        rate_spin.setValue(0.0)
        rate_spin.setDecimals(2)
        # Connect to real-time calculation
        rate_spin.valueChanged.connect(lambda value, r=row: self.calculate_single_row(r))
        self.comparison_selection_table.setCellWidget(row, 3, rate_spin)
        
        # Unit combo box
        unit_combo = QComboBox()
        # Use the units from APPLICATION_RATE_CONVERSION
        unit_combo.addItems(sorted(APPLICATION_RATE_CONVERSION.keys()))
        # Connect to real-time calculation
        unit_combo.currentIndexChanged.connect(lambda idx, r=row: self.calculate_single_row(r))
        self.comparison_selection_table.setCellWidget(row, 4, unit_combo)
        
        # Applications spinner
        apps_spin = QDoubleSpinBox()
        apps_spin.setRange(1, 10)
        apps_spin.setValue(1)
        apps_spin.setDecimals(0)
        # Connect to real-time calculation
        apps_spin.valueChanged.connect(lambda value, r=row: self.calculate_single_row(r))
        self.comparison_selection_table.setCellWidget(row, 5, apps_spin)
        
        # Add a new entry to track this row's data
        self.products_data.append({
            "product": None,
            "active_ingredients": []
        })
    
    def remove_selected_row(self):
        """Remove the selected row from the table."""
        selected_rows = self.comparison_selection_table.selectionModel().selectedRows()
        
        if not selected_rows:
            return
        
        # Sort in reverse order to avoid index issues when removing
        rows = sorted([index.row() for index in selected_rows], reverse=True)
        
        for row in rows:
            self.comparison_selection_table.removeRow(row)
            
            # Also remove from the data tracking list
            if 0 <= row < len(self.products_data):
                self.products_data.pop(row)
        
        # Ensure there's always at least one row
        if self.comparison_selection_table.rowCount() == 0:
            self.add_product_row()
            
        # Update results after removing rows
        self.refresh_all_calculations()
    
    def update_product_combo(self, row):
        """Update the product combo box based on the selected product type."""
        type_combo = self.comparison_selection_table.cellWidget(row, 0)
        product_combo = self.comparison_selection_table.cellWidget(row, 1)
        
        if not type_combo or not product_combo:
            return
        
        product_type = type_combo.currentText()
        if product_type == "Select type...":
            # Clear the product combo
            product_combo.clear()
            product_combo.addItem("Select product...")
            return
        
        # Get products filtered by type
        products = get_products_from_csv()
        filtered_products = [p for p in products if p.product_type == product_type]
        
        # Update product combo
        product_combo.clear()
        product_combo.addItem("Select product...")
        product_combo.addItems([p.product_name for p in filtered_products])
    
    def update_product_info(self, row):
        """Update product information when a product is selected."""
        product_combo = self.comparison_selection_table.cellWidget(row, 1)
        
        if not product_combo or product_combo.currentIndex() == 0:
            # Clear the row data
            self.comparison_selection_table.item(row, 2).setText("")
            
            if 0 <= row < len(self.products_data):
                self.products_data[row]["product"] = None
                self.products_data[row]["active_ingredients"] = []
                
            # Clear any previous results for this row
            self.calculate_single_row(row)
            return
        
        product_name = product_combo.currentText()
        
        try:
            # Find the product in the database
            products = get_products_from_csv()
            product = None
            for p in products:
                if p.product_name == product_name:
                    product = p
                    break
            
            if not product:
                raise ValueError(f"Product '{product_name}' not found")
            
            # Store the product data
            if 0 <= row < len(self.products_data):
                self.products_data[row]["product"] = product
                
                # Get active ingredients
                ai_data = []
                
                # Check AI1 data
                if product.ai1:
                    concentration = product.ai1_concentration
                    uom = product.ai1_concentration_uom
                    percent_value = convert_concentration_to_percent(concentration, uom)
                    
                    ai_data.append({
                        "name": product.ai1,
                        "eiq": product.ai1_eiq if product.ai1_eiq is not None else "--",
                        "percent": percent_value if percent_value is not None else "--"
                    })
                
                # Check AI2 data
                if product.ai2:
                    concentration = product.ai2_concentration
                    uom = product.ai2_concentration_uom
                    percent_value = convert_concentration_to_percent(concentration, uom)
                    
                    ai_data.append({
                        "name": product.ai2,
                        "eiq": product.ai2_eiq if product.ai2_eiq is not None else "--",
                        "percent": percent_value if percent_value is not None else "--"
                    })
                
                # Check AI3 data
                if product.ai3:
                    concentration = product.ai3_concentration
                    uom = product.ai3_concentration_uom
                    percent_value = convert_concentration_to_percent(concentration, uom)
                    
                    ai_data.append({
                        "name": product.ai3,
                        "eiq": product.ai3_eiq if product.ai3_eiq is not None else "--",
                        "percent": percent_value if percent_value is not None else "--"
                    })
                
                # Check AI4 data
                if product.ai4:
                    concentration = product.ai4_concentration
                    uom = product.ai4_concentration_uom
                    percent_value = convert_concentration_to_percent(concentration, uom)
                    
                    ai_data.append({
                        "name": product.ai4,
                        "eiq": product.ai4_eiq if product.ai4_eiq is not None else "--",
                        "percent": percent_value if percent_value is not None else "--"
                    })
                
                self.products_data[row]["active_ingredients"] = ai_data
                
                # Display first active ingredient in the table or "None" if no AI
                ai_display = ", ".join(product.active_ingredients) if product.active_ingredients else "None"
                self.comparison_selection_table.item(row, 2).setText(ai_display)
                
                # Update application rate with max rate from product data
                rate_spin = self.comparison_selection_table.cellWidget(row, 3)
                if rate_spin:
                    if product.label_maximum_rate is not None:
                        rate_spin.setValue(product.label_maximum_rate)
                    elif product.label_minimum_rate is not None:
                        rate_spin.setValue(product.label_minimum_rate)
                    else:
                        rate_spin.setValue(0.0)
                
                # Set rate unit to match product's UOM
                unit_combo = self.comparison_selection_table.cellWidget(row, 4)
                if unit_combo and product.rate_uom:
                    index = unit_combo.findText(product.rate_uom)
                    if index >= 0:
                        unit_combo.setCurrentIndex(index)
                        
                # The rate or unit setting will trigger calculate_single_row
                # But we call it explicitly just in case
                self.calculate_single_row(row)
            
        except Exception as e:
            print(f"Error loading product info for '{product_name}': {e}")
            # Clear fields on error
            if 0 <= row < len(self.products_data):
                self.products_data[row]["product"] = None
                self.products_data[row]["active_ingredients"] = []
                
            # Clear any previous results for this row
            self.calculate_single_row(row)
    
    def calculate_single_row(self, row):
        """
        Calculate EIQ for a single row and update the results table.
        This enables real-time updates for each product individually.
        Uses improved UOM handling for consistent calculations.
        """
        # Only process if the row exists in our data structure
        if not (0 <= row < len(self.products_data)):
            return
            
        # Get the product data for this row
        product_data = self.products_data[row]
        product = product_data.get("product")
        active_ingredients = product_data.get("active_ingredients", [])
        
        # Skip calculation if no valid product or active ingredients
        if not product or not active_ingredients:
            # Remove this product from results table if it exists
            self.update_results_for_row(row, None, None)
            return
            
        try:
            # Get application parameters
            rate_spin = self.comparison_selection_table.cellWidget(row, 3)
            unit_combo = self.comparison_selection_table.cellWidget(row, 4) 
            apps_spin = self.comparison_selection_table.cellWidget(row, 5)
            
            rate = rate_spin.value() if rate_spin else 0.0
            unit = unit_combo.currentText() if unit_combo else "lbs/acre"
            applications = int(apps_spin.value()) if apps_spin else 1
            
            # Calculate total Field EIQ using the improved function with proper UOM handling
            # This now uses our enhanced standardize_eiq_calculation under the hood
            total_field_eiq = calculate_product_field_eiq(
                active_ingredients, rate, unit, applications)
            
            # For the comparison table, we prefer to show per-ha values as the primary metric
            # But also calculate per-acre for display
            field_eiq_per_acre = total_field_eiq / 2.47  # Convert ha to acre
            
            # Update the results table for this row
            self.update_results_for_row(row, field_eiq_per_acre, total_field_eiq)
            
        except (ValueError, ZeroDivisionError, AttributeError) as e:
            print(f"Error calculating EIQ for row {row}: {e}")
            # Clear results for this row
            self.update_results_for_row(row, None, None)
    
    def update_results_for_row(self, selection_row, field_eiq_acre, field_eiq_ha):
        """
        Update the results table for a specific row.
        """
        if not 0 <= selection_row < len(self.products_data) or not self.products_data[selection_row]["product"]:
            # Find and remove any existing results for this row
            for r in range(self.comparison_results_table.rowCount()):
                if r < self.comparison_results_table.rowCount():
                    product_item = self.comparison_results_table.item(r, 0)
                    if product_item and product_item.data(Qt.UserRole) == selection_row:
                        self.comparison_results_table.removeRow(r)
                        break
            return
            
        product_name = self.products_data[selection_row]["product"].product_name
        
        # Check if we already have a row for this product in the results table
        found_row = -1
        for r in range(self.comparison_results_table.rowCount()):
            product_item = self.comparison_results_table.item(r, 0)
            if product_item and product_item.data(Qt.UserRole) == selection_row:
                found_row = r
                break
                
        if field_eiq_acre is None or field_eiq_acre <= 0:
            # If invalid EIQ and we found a row, remove it
            if found_row >= 0:
                self.comparison_results_table.removeRow(found_row)
            return
            
        # If we didn't find a row, add a new one
        if found_row == -1:
            found_row = self.comparison_results_table.rowCount()
            self.comparison_results_table.insertRow(found_row)
            
        # Product name with reference to source row
        product_item = QTableWidgetItem(product_name)
        product_item.setData(Qt.UserRole, selection_row)  # Store reference to selection table row
        self.comparison_results_table.setItem(found_row, 0, product_item)
        
        # Field EIQ / acre with color coding
        eiq_acre_item = ColorCodedEiqItem(
            field_eiq_acre, 
            low_threshold=20, 
            high_threshold=40
        )
        self.comparison_results_table.setItem(found_row, 1, eiq_acre_item)
        
        # Field EIQ / ha with color coding
        eiq_ha_item = ColorCodedEiqItem(
            field_eiq_ha, 
            low_threshold=50, 
            high_threshold=100
        )
        self.comparison_results_table.setItem(found_row, 2, eiq_ha_item)
    
    def refresh_all_calculations(self):
        """Calculate and display EIQ comparison results for all rows."""
        # Clear the results table
        self.comparison_results_table.setRowCount(0)
        
        # Iterate through all products in the selection table
        for row in range(self.comparison_selection_table.rowCount()):
            self.calculate_single_row(row)
    
    def export_comparison(self):
        """Export comparison results to a file."""
        print("Export comparison results")
        # In a real application, this would export to CSV or PDF