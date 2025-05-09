"""
Single Product EIQ Calculator for the LORENZO POZZI Pesticide App.

This module provides the SingleProductCalculator widget for calculating EIQ
of a single pesticide product with search and suggestions functionality.
It supports displaying multiple active ingredients (up to 4) with improved UOM handling
and uses Qt's Model/View architecture.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QFormLayout, 
                              QDoubleSpinBox, QTableView, QHeaderView, QSizePolicy)
from common.styles import get_body_font
from common.widgets import ContentFrame
from data.product_repository import ProductRepository
from eiq_calculator.eiq_ui_components import ProductSearchField, EiqResultDisplay
from eiq_calculator.eiq_calculations import calculate_product_field_eiq
from eiq_calculator.eiq_conversions import APPLICATION_RATE_CONVERSION
from eiq_calculator.eiq_models import ActiveIngredientsModel, LabelInfoModel


class SingleProductCalculator(QWidget):
    """Widget for calculating EIQ for a single pesticide product using Model/View."""
    
    def __init__(self, parent=None):
        """Initialize the single product calculator widget."""
        super().__init__(parent)
        self.parent = parent
        
        # Store the full list of products
        self.all_products = []
        
        # Currently selected product data
        self.current_product = None
        
        # Create models
        self.active_ingredients_model = ActiveIngredientsModel(self)
        self.label_info_model = LabelInfoModel(self)
        
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
        repo = ProductRepository.get_instance()
        self.all_products = repo.get_filtered_products()
        
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

        # Create Active Ingredients table view
        self.ai_table = QTableView()
        self.ai_table.setModel(self.active_ingredients_model)
        self.ai_table.setAlternatingRowColors(True)
        
        # Configure headers
        header = self.ai_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        # Set a reasonable fixed height for the table
        self.ai_table.setMinimumHeight(120)
        self.ai_table.setMaximumHeight(150)
        self.ai_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Use a direct form layout row instead of a container
        product_layout.addRow("Active Ingredients:", self.ai_table)
        
        # Create label information table view
        self.label_info_table = QTableView()
        self.label_info_table.setModel(self.label_info_model)
        self.label_info_table.setAlternatingRowColors(True)
        
        # Configure headers
        header = self.label_info_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        # Set a reasonable fixed height for the table
        self.label_info_table.setMinimumHeight(80)
        self.label_info_table.setMaximumHeight(100)
        self.label_info_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Use a direct form layout row instead of a container
        product_layout.addRow("Label Information:", self.label_info_table)

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
        
        # Update product list
        self.update_product_list()

    def refresh_product_data(self):
        """Refresh product data based on the filtered products."""
        # Reload products with the filtered data
        repo = ProductRepository.get_instance()
        self.all_products = repo.get_filtered_products()
        
        # Update the product list
        self.update_product_list()
        
        # Clear current product selection
        self.product_search.clear()
        self.current_product = None
        self.active_ingredients_model.setProduct(None)
        self.label_info_model.setProduct(None)
        self.rate_spin.setValue(0.0)
        self.eiq_results_display.update_result(0.0)
    
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
                self.current_product = None
                self.active_ingredients_model.setProduct(None)
                self.label_info_model.setProduct(None)
                self.rate_spin.setValue(0.0)
                self.eiq_results_display.update_result(0.0)
            else:
                # Handle case where no products are loaded
                self.product_search.setEnabled(False)
                print("No products found in CSV file")
        
        except Exception as e:
            print(f"Error updating product list: {e}")
            self.product_search.setEnabled(False)
    
    def update_product_info(self, product_name):
        """Update product information when a product is selected."""
        if not product_name:
            # Clear fields if no product is selected
            self.current_product = None
            self.active_ingredients_model.setProduct(None)
            self.label_info_model.setProduct(None)
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
            
            # Update the active ingredients model
            self.active_ingredients_model.setProduct(self.current_product)
            
            # Update the label info model
            self.label_info_model.setProduct(self.current_product)

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
            self.current_product = None
            self.active_ingredients_model.setProduct(None)
            self.label_info_model.setProduct(None)
            self.rate_spin.setValue(0.0)
            self.eiq_results_display.update_result(0.0)
    
    def calculate_single_eiq(self):
        """Calculate the Field EIQ for a single product with improved UOM handling."""
        if not self.current_product or self.active_ingredients_model.rowCount() == 0:
            self.eiq_results_display.update_result(0.0)
            return
            
        try:
            # Get active ingredients data from model
            active_ingredients = self.active_ingredients_model.getActiveIngredients()
            
            # Get application parameters
            rate = self.rate_spin.value()
            applications = int(self.applications_spin.value())
            unit = self.rate_unit_combo.currentText()
            
            # Calculate total Field EIQ using the improved function with proper UOM handling
            total_field_eiq = calculate_product_field_eiq(
                active_ingredients, rate, unit, applications)
            
            # Update result display with the new EIQ value
            self.eiq_results_display.update_result(total_field_eiq)
            
        except (ValueError, ZeroDivisionError, AttributeError) as e:
            print(f"Error calculating EIQ: {e}")
            self.eiq_results_display.update_result(0.0)