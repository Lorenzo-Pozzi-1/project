"""
Single Product Calculator Tab for the LORENZO POZZI Pesticide App.

This module provides the SingleProductCalculatorTab widget 
for calculating EIQ of a single pesticide product.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QHeaderView, QFormLayout, QTableWidgetItem
from PySide6.QtCore import Qt
from common import GENERIC_TABLE_STYLE, ContentFrame, get_config, calculation_tracer
from common.constants import get_medium_text_size
from data import ProductRepository
from common.widgets.product_selection import ProductSelectionWidget
from common.widgets.application_params import ApplicationParamsWidget
from common.widgets.UOM_selector import SmartUOMSelector
from common.calculations import eiq_calculator
from eiq_calculator_page.widgets_results_display import EiqResultDisplay

class SingleProductCalculatorTab(QWidget):
    """Widget for calculating EIQ for a single pesticide product."""
    
    def __init__(self, parent=None):
        """Initialize the single product calculator tab."""
        super().__init__(parent)
        self.parent = parent
        
        # Currently selected product data
        self.current_product = None
        self.active_ingredients = []
        
        # Initialize product repository
        self.products_repo = ProductRepository.get_instance()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout with proper margins
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Product selection section
        product_frame = ContentFrame()
        product_layout = QVBoxLayout()
        
        # Product selection widget
        self.product_selection = ProductSelectionWidget(orientation='vertical', style_config={'font_size': get_medium_text_size(), 'bold': False})
        self.product_selection.product_selected.connect(self.update_product_info)
        product_layout.addWidget(self.product_selection)
        
        # Create Active Ingredients table
        self.ai_table = QTableWidget()
        self.ai_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ai_table.setStyleSheet(GENERIC_TABLE_STYLE)
        self.ai_table.setRowCount(0)  # Start empty
        self.ai_table.setColumnCount(4)  # 4 columns including UOM
        self.ai_table.setHorizontalHeaderLabels(["Active Ingredient", "EIQ", "Concentration", "UOM"])

        # Configure table columns
        header = self.ai_table.horizontalHeader()
        for i in range(0,header.count()): header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # Set a reasonable height for the table
        self.ai_table.setMinimumHeight(120)
        self.ai_table.setMaximumHeight(150)
        
        # Form layout for better label alignment
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.addRow("Active Ingredients:", self.ai_table)
        product_layout.addLayout(form_layout)
        
        # Create label information table
        self.label_info_table = QTableWidget()
        self.label_info_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.label_info_table.setStyleSheet(GENERIC_TABLE_STYLE)
        self.label_info_table.setRowCount(1)  # One row for the selected product
        self.label_info_table.setColumnCount(7)  # 7 columns for product info
        self.label_info_table.setHorizontalHeaderLabels([
            "Application Method", "Min Rate", "Max Rate", "Rate UOM", 
            "REI (hours)", "PHI (days)", "Min Days Between Apps"
        ])
        self.label_info_table.verticalHeader().setVisible(False)

        # Configure table columns
        header = self.label_info_table.horizontalHeader()
        for i in range(header.count()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        # Set a reasonable height for the table
        self.label_info_table.setFixedHeight(65)
        
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.addRow("Label Information:", self.label_info_table)
        product_layout.addLayout(form_layout)
        
        # Application parameters widget
        self.app_params = ApplicationParamsWidget( orientation='vertical', style_config={'font_size': get_medium_text_size(), 'bold': False})
        self.app_params.params_changed.connect(self.calculate_eiq)
        product_layout.addWidget(self.app_params)
        
        product_frame.layout.addLayout(product_layout)
        layout.addWidget(product_frame)
        
        # Results section
        results_frame = ContentFrame()
        self.eiq_results = EiqResultDisplay()
        results_frame.layout.addWidget(self.eiq_results)
        layout.addWidget(results_frame)
    
    def refresh_product_data(self):
        """Refresh product data based on filtered products."""
        # Clear current product selection
        self.current_product = None
        self.active_ingredients = []
        
        # Refresh product selection widget
        self.product_selection.refresh_data()
        
        # Clear tables
        self.clear_tables()
        
        # Reset application parameters to base state
        self.app_params.set_params(0.0, None, 1)
        
        # Clear EIQ result
        self.eiq_results.update_result(0.0)
    
    def clear_tables(self):
        """Clear the active ingredients and label information tables."""
        self.ai_table.setRowCount(0)
        self.label_info_table.clearContents()
    
    def update_product_info(self, product_name):
        """
        Update product information when a product is selected.
        
        Args:
            product_name (str): The selected product name
        """
        if not product_name:
            # Clear selection if no product name
            self.clear_product_selection()
            return
        
        try:
            # Get product from FILTERED products instead of all products
            filtered_products = self.products_repo.get_filtered_products()
            self.current_product = None
            
            # Find the product in the filtered list
            for product in filtered_products:
                if product.product_name == product_name:
                    self.current_product = product
                    break
            
            if not self.current_product:
                raise ValueError(f"Product '{product_name}' not found in filtered products")
            
            # Get active ingredients data
            self.active_ingredients = self.current_product.get_ai_data()
            
            # Update active ingredients table
            self.ai_table.setRowCount(len(self.active_ingredients))

            for i, ai in enumerate(self.active_ingredients):
                # Name
                name_item = QTableWidgetItem(ai["name"])
                name_item.setTextAlignment(Qt.AlignCenter)
                self.ai_table.setItem(i, 0, name_item)
                
                # EIQ
                eiq_value = ai["eiq"] if ai["eiq"] is not None else "--"
                eiq_item = QTableWidgetItem(str(eiq_value))
                eiq_item.setTextAlignment(Qt.AlignCenter)
                self.ai_table.setItem(i, 1, eiq_item)
                
                # Concentration amount
                concentration_value = ai["concentration"] if ai["concentration"] is not None else "--"
                concentration_item = QTableWidgetItem(str(concentration_value))
                concentration_item.setTextAlignment(Qt.AlignCenter)
                self.ai_table.setItem(i, 2, concentration_item)
                
                # Concentration UOM
                uom_value = ai["uom"] if ai["uom"] is not None else "--"
                uom_item = QTableWidgetItem(str(uom_value))
                uom_item.setTextAlignment(Qt.AlignCenter)
                self.ai_table.setItem(i, 3, uom_item)
            
            # Update label information table
            self.update_label_info()
            
            # Pre-compile application parameters based on product data
            self.update_application_params()
            
            # Calculate EIQ with new values
            self.calculate_eiq()
            
        except Exception as e:
            print(f"Error loading product info for '{product_name}': {e}")
            self.clear_product_selection()
    
    def update_label_info(self):
        """Update the label information table with current product data."""
        if not self.current_product:
            self.label_info_table.clearContents()
            return
        
        # Application Method
        method_item = QTableWidgetItem(self.current_product.application_method or "--")
        method_item.setTextAlignment(Qt.AlignCenter)
        self.label_info_table.setItem(0, 0, method_item)
        
        # Min Rate
        min_rate = "--"
        if self.current_product.label_minimum_rate is not None:
            min_rate = f"{self.current_product.label_minimum_rate:.2f}"
        min_rate_item = QTableWidgetItem(min_rate)
        min_rate_item.setTextAlignment(Qt.AlignCenter)
        self.label_info_table.setItem(0, 1, min_rate_item)
        
        # Max Rate
        max_rate = "--"
        if self.current_product.label_maximum_rate is not None:
            max_rate = f"{self.current_product.label_maximum_rate:.2f}"
        max_rate_item = QTableWidgetItem(max_rate)
        max_rate_item.setTextAlignment(Qt.AlignCenter)
        self.label_info_table.setItem(0, 2, max_rate_item)
        
        # Rate UOM
        uom_item = QTableWidgetItem(self.current_product.rate_uom or "--")
        uom_item.setTextAlignment(Qt.AlignCenter)
        self.label_info_table.setItem(0, 3, uom_item)
        
        # REI (hours)
        rei_item = QTableWidgetItem(str(self.current_product.rei_hours or "--"))
        rei_item.setTextAlignment(Qt.AlignCenter)
        self.label_info_table.setItem(0, 4, rei_item)
        
        # PHI (days)
        phi_item = QTableWidgetItem(str(self.current_product.phi_days or "--"))
        phi_item.setTextAlignment(Qt.AlignCenter)
        self.label_info_table.setItem(0, 5, phi_item)
        
        # Min Days Between Applications
        min_days_item = QTableWidgetItem(str(self.current_product.min_days_between_applications or "--"))
        min_days_item.setTextAlignment(Qt.AlignCenter)
        self.label_info_table.setItem(0, 6, min_days_item)
    
    def update_application_params(self):
        """Update application parameters based on current product data using two-step UOM change."""
        if not self.current_product:  # If no product selected
            self.app_params.set_params(0.0, None, 1)
            return
        
        # Set application rate to max rate if available, otherwise min rate
        rate = 0.0
        if self.current_product.label_maximum_rate is not None:
            rate = self.current_product.label_maximum_rate
        elif self.current_product.label_minimum_rate is not None:
            rate = self.current_product.label_minimum_rate
        
        # Set unit to product's UOM (this will use the two-step process internally)
        unit = self.current_product.rate_uom
        
        # Default to 1 application
        applications = 1

        # Update application parameters widget - the two-step UOM change is handled in set_params
        self.app_params.set_params(rate, unit, applications)
    
    def clear_product_selection(self):
        """Clear the current product selection and related data."""
        # Clear product selection
        self.current_product = None
        self.active_ingredients = []
        
        # Clear tables
        self.clear_tables()
        
        # Reset application parameters to base state
        self.app_params.set_params(0.0, None, 1)
        
        # Clear EIQ result
        self.eiq_results.update_result(0.0)
    
    def calculate_eiq(self):
        """Calculate the Field EIQ for the current product."""
        if not self.current_product or not self.active_ingredients:
            self.eiq_results.update_result(0.0)
            return
        
        try:
            # Get application parameters
            params = self.app_params.get_params()
            
            # Skip calculation if no unit is selected (base state)
            if params["unit"] is None:
                self.eiq_results.update_result(0.0)
                return
            
            # Get user preferences for UOM conversions
            user_preferences = get_config("user_preferences", {})
            
            # Calculate Field EIQ with user preferences
            calculation_tracer.log(f"\n\n====================================================================")
            calculation_tracer.log(f"{self.current_product.product_name}")
            calculation_tracer.log(f"====================================================================")
            field_eiq = eiq_calculator.calculate_product_field_eiq(
                active_ingredients=self.active_ingredients,
                application_rate=params["rate"],
                application_rate_uom=params["unit"],
                applications=params["applications"],
                user_preferences=user_preferences
            )
            
            # Update result display
            self.eiq_results.update_result(field_eiq)
            
        except Exception as e:
            print(f"Error calculating EIQ: {e}")
            self.eiq_results.update_result(0.0)