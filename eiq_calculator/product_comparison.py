"""
Product Comparison Calculator for the LORENZO POZZI Pesticide App.

This module provides the ProductComparisonCalculator widget for comparing EIQ
values of multiple pesticide products with improved UOM management and Model/View architecture.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, 
                              QLabel, QTableView, QHeaderView, QDoubleSpinBox)
from common.styles import get_subtitle_font, PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
from common.widgets import ContentFrame
from data.product_repository import ProductRepository
from eiq_calculator.eiq_conversions import APPLICATION_RATE_CONVERSION
from eiq_calculator.eiq_models import ProductComparisonCalculatorModel, ComparisonResultsModel
from data.product_repository import ProductRepository


class ProductComparisonCalculator(QWidget):
    """
    Widget for comparing EIQ values of multiple pesticide products with real-time updates.
    Uses Qt's Model/View architecture for better separation of concerns.
    """
    
    def __init__(self, parent=None):
        """Initialize the product comparison calculator widget."""
        super().__init__(parent)
        self.parent = parent
        
        # Create models
        self.comparison_model = ProductComparisonCalculatorModel(self)
        self.results_model = ComparisonResultsModel(self)
        
        # Connect signals
        self.comparison_model.calculation_required = self.refresh_all_calculations
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Products selection section
        selection_frame = ContentFrame()
        selection_layout = QVBoxLayout()
        
        selection_title = QLabel("Select Products to Compare")
        selection_title.setFont(get_subtitle_font())
        selection_layout.addWidget(selection_title)
        
        # Comparison selection table
        self.comparison_selection_table = QTableView()
        self.comparison_selection_table.setModel(self.comparison_model)
        self.comparison_selection_table.setAlternatingRowColors(True)
        self.comparison_selection_table.setSelectionBehavior(QTableView.SelectRows)
        
        # Set up table properties
        header = self.comparison_selection_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Product Type
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Product Name
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Active Ingredients
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Application Rate
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Unit
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Applications
        
        # Set up cell editors for the table
        self.setup_cell_editors()
        
        # Add initial empty row in model
        self.comparison_model.addEmptyRow()
        
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
        results_title.setFont(get_subtitle_font())
        results_layout.addWidget(results_title)
        
        # Results table
        self.comparison_results_table = QTableView()
        self.comparison_results_table.setModel(self.results_model)
        self.comparison_results_table.setAlternatingRowColors(True)
        
        # Set up table properties
        header = self.comparison_results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        results_layout.addWidget(self.comparison_results_table)
        
        results_frame.layout.addLayout(results_layout)
        main_layout.addWidget(results_frame)
    
    def setup_cell_editors(self):
        """Set up cell editors for the comparison table."""
        # We'll use the selection_changed signal to handle product selection
        self.comparison_selection_table.selectionModel().selectionChanged.connect(
            self.handle_selection_changed)
    
    def handle_selection_changed(self, selected, deselected):
        """Handle selection changes in the table."""
        # We'll implement product selection via a separate dialog or combobox
        # This is just a placeholder for future implementation
        pass
    
    def add_product_row(self):
        """Add a new row to the comparison table."""
        row = self.comparison_model.addEmptyRow()
        
        # Create and set up a product selector for this row
        self.create_product_selector(row)
    
    def create_product_selector(self, row):
        """Create a product selector for the given row."""
        # Product Type combo box
        type_combo = QComboBox()
        type_combo.addItem("Select type...")
        
        # Load product types
        repo = ProductRepository.get_instance()
        products = repo.get_filtered_products()
        product_types = sorted(list(set(p.product_type for p in products if p.product_type)))
        
        type_combo.addItems(product_types)
        type_combo.currentIndexChanged.connect(lambda idx, r=row: self.update_product_combo(r))
        self.comparison_selection_table.setIndexWidget(
            self.comparison_model.index(row, 0), type_combo)
        
        # Product Name combo box
        product_combo = QComboBox()
        product_combo.addItem("Select product...")
        product_combo.currentIndexChanged.connect(lambda idx, r=row: self.update_product_info(r))
        self.comparison_selection_table.setIndexWidget(
            self.comparison_model.index(row, 1), product_combo)
        
        # Application rate spinner
        rate_spin = QDoubleSpinBox()
        rate_spin.setRange(0.0, 9999.99)
        rate_spin.setValue(0.0)
        rate_spin.setDecimals(2)
        rate_spin.valueChanged.connect(lambda value, r=row: self.update_rate(r, value))
        self.comparison_selection_table.setIndexWidget(
            self.comparison_model.index(row, 3), rate_spin)
        
        # Unit combo box
        unit_combo = QComboBox()
        unit_combo.addItems(sorted(APPLICATION_RATE_CONVERSION.keys()))
        unit_combo.currentIndexChanged.connect(
            lambda idx, r=row: self.update_unit(r, unit_combo.currentText()))
        self.comparison_selection_table.setIndexWidget(
            self.comparison_model.index(row, 4), unit_combo)
        
        # Applications spinner
        apps_spin = QDoubleSpinBox()
        apps_spin.setRange(1, 10)
        apps_spin.setValue(1)
        apps_spin.setDecimals(0)
        apps_spin.valueChanged.connect(
            lambda value, r=row: self.update_applications(r, int(value)))
        self.comparison_selection_table.setIndexWidget(
            self.comparison_model.index(row, 5), apps_spin)
    
    def update_product_combo(self, row):
        """Update the product combo box based on the selected product type."""
        # Get the type combo
        type_combo = self.comparison_selection_table.indexWidget(
            self.comparison_model.index(row, 0))
        
        # Get the product combo
        product_combo = self.comparison_selection_table.indexWidget(
            self.comparison_model.index(row, 1))
        
        if not type_combo or not product_combo:
            return
        
        product_type = type_combo.currentText()
        if product_type == "Select type...":
            # Clear the product combo
            product_combo.clear()
            product_combo.addItem("Select product...")
            return
        
        # Get products filtered by type
        repo = ProductRepository.get_instance()
        products = repo.get_filtered_products()
        filtered_products = [p for p in products if p.product_type == product_type]
        
        # Update product combo
        product_combo.clear()
        product_combo.addItem("Select product...")
        product_combo.addItems([p.product_name for p in filtered_products])
    
    def update_product_info(self, row):
        """Update product information when a product is selected."""
        product_combo = self.comparison_selection_table.indexWidget(
            self.comparison_model.index(row, 1))
        
        if not product_combo or product_combo.currentIndex() == 0:
            # Clear the row data in the model
            self.comparison_model.updateProduct(row, None)
            
            # Remove any results for this row
            self.results_model.removeResult(row)
            return
        
        product_name = product_combo.currentText()
        
        try:
            # Find the product in the repository
            repo = ProductRepository.get_instance()
            products = repo.get_filtered_products()
            product = None
            
            for p in products:
                if p.product_name == product_name:
                    product = p
                    break
            
            if not product:
                raise ValueError(f"Product '{product_name}' not found")
            
            # Update the model with the product data
            self.comparison_model.updateProduct(row, product)
            
            # Update the rate spinner with the product's rate
            rate_spin = self.comparison_selection_table.indexWidget(
                self.comparison_model.index(row, 3))
            
            if rate_spin:
                if product.label_maximum_rate is not None:
                    rate_spin.setValue(product.label_maximum_rate)
                elif product.label_minimum_rate is not None:
                    rate_spin.setValue(product.label_minimum_rate)
            
            # Update the unit combo with the product's UOM
            unit_combo = self.comparison_selection_table.indexWidget(
                self.comparison_model.index(row, 4))
            
            if unit_combo and product.rate_uom:
                index = unit_combo.findText(product.rate_uom)
                if index >= 0:
                    unit_combo.setCurrentIndex(index)
            
            # Calculate Field EIQ for this row
            self.calculate_single_row(row)
            
        except Exception as e:
            print(f"Error loading product info for '{product_name}': {e}")
            # Clear row data in the model
            self.comparison_model.updateProduct(row, None)
            
            # Remove any results for this row
            self.results_model.removeResult(row)
    
    def update_rate(self, row, value):
        """Update the application rate in the model."""
        self.comparison_model.updateRate(row, value)
        self.calculate_single_row(row)
    
    def update_unit(self, row, unit):
        """Update the unit in the model."""
        self.comparison_model.updateUnit(row, unit)
        self.calculate_single_row(row)
    
    def update_applications(self, row, applications):
        """Update the number of applications in the model."""
        self.comparison_model.updateApplications(row, applications)
        self.calculate_single_row(row)
    
    def remove_selected_row(self):
        """Remove the selected row from the table."""
        selected_rows = self.comparison_selection_table.selectionModel().selectedRows()
        
        if not selected_rows:
            return
        
        # Sort in reverse order to avoid index issues when removing
        rows = sorted([index.row() for index in selected_rows], reverse=True)
        
        for row in rows:
            # Remove from results model first
            self.results_model.removeResult(row)
            
            # Then remove from comparison model
            self.comparison_model.removeRow(row)
        
        # Ensure there's always at least one row
        if self.comparison_model.rowCount() == 0:
            self.add_product_row()
    
    def refresh_product_data(self):
        """Refresh product data based on the filtered products."""
        # Clear existing data
        self.comparison_model.setProducts([])
        self.results_model.clearResults()
        
        # Reset the table
        self.comparison_selection_table.setModel(self.comparison_model)
        
        # Add a new empty row
        self.add_product_row()
    
    def calculate_single_row(self, row):
        """
        Calculate EIQ for a single row and update the results.
        This enables real-time updates for each product individually.
        """
        # Get product data from the model
        product_data = self.comparison_model.getProductData(row)
        if not product_data or not product_data.get("product"):
            # Remove result if it exists
            self.results_model.removeResult(row)
            return
            
        # Calculate Field EIQ using the model's method
        field_eiq = self.comparison_model.calculateFieldEIQ(row)
        
        # Update the results model
        self.results_model.updateResult(
            product_data["product"], field_eiq, row)
    
    def refresh_all_calculations(self):
        """Calculate and display EIQ comparison results for all rows."""
        # Iterate through all products in the model
        for row in range(self.comparison_model.rowCount()):
            self.calculate_single_row(row)