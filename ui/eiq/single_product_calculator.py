"""
Single Product EIQ Calculator for the LORENZO POZZI Pesticide App.

This module provides the SingleProductCalculator widget for calculating EIQ
of a single pesticide product with search and suggestions functionality.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, 
    QFormLayout, QDoubleSpinBox, QLineEdit, QListWidget, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QColor, QPalette

from ui.common.styles import (
    get_title_font, get_subtitle_font, get_body_font, PRIMARY_BUTTON_STYLE, 
    SECONDARY_BUTTON_STYLE, EIQ_LOW_COLOR, EIQ_MEDIUM_COLOR, EIQ_HIGH_COLOR
)
from ui.common.widgets import ContentFrame, GaugeWidget

# Import EIQ utilities
from ui.eiq.eiq_utils import (
    get_products_from_csv, get_product_info, 
    calculate_field_eiq, get_impact_category
)
from data.products_data import load_products


class ProductSearchField(QWidget):
    """A custom search field with suggestions displayed underneath."""
    
    # Signal emitted when a product is selected
    product_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_items = []  # All available products
        self.filtered_items = []  # Filtered products based on search
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Search field
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Type to search products...")
        self.search_field.setFont(get_body_font())
        self.search_field.textChanged.connect(self.update_suggestions)
        layout.addWidget(self.search_field)
        
        # Suggestions container
        self.suggestions_container = QFrame()
        self.suggestions_container.setFrameStyle(QFrame.StyledPanel)
        self.suggestions_container.setStyleSheet("""
            QFrame {
                border: 1px solid #CCCCCC;
                border-top: none;
                background-color: white;
            }
        """)
        
        # Scroll area for suggestions to handle large lists
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Suggestions list
        self.suggestions_list = QListWidget()
        self.suggestions_list.setFrameStyle(QFrame.NoFrame)
        self.suggestions_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.suggestions_list.setStyleSheet("""
            QListWidget {
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #F5F5F5;
            }
            QListWidget::item:selected {
                background-color: #E0E0E0;
            }
        """)
        self.suggestions_list.itemClicked.connect(self.select_suggestion)
        scroll_area.setWidget(self.suggestions_list)
        
        # Add scroll area to suggestions container
        suggestions_layout = QVBoxLayout(self.suggestions_container)
        suggestions_layout.setContentsMargins(0, 0, 0, 0)
        suggestions_layout.addWidget(scroll_area)
        
        # Add suggestions container to main layout
        layout.addWidget(self.suggestions_container)
        
        # Initially hide suggestions
        self.suggestions_container.setVisible(False)
    
    def update_suggestions(self, text):
        """Update suggestions based on input text."""
        # Clear selection when search text changes
        self.suggestions_list.clearSelection()
        
        if not text:
            # Hide suggestions when search field is empty
            self.suggestions_container.setVisible(False)
            return
        
        # Filter items based on search text
        self.filtered_items = [
            item for item in self.all_items 
            if text.lower() in item.lower()
        ]
        
        # Update suggestions list
        self.suggestions_list.clear()
        self.suggestions_list.addItems(self.filtered_items)
        
        # Show suggestions if there are any matches
        has_suggestions = len(self.filtered_items) > 0
        self.suggestions_container.setVisible(has_suggestions)
        
        # Set fixed height based on number of items
        if has_suggestions:
            item_height = self.suggestions_list.sizeHintForRow(0)
            num_visible_items = min(8, len(self.filtered_items))
            list_height = item_height * num_visible_items + 4
            self.suggestions_list.setFixedHeight(list_height)
    
    def select_suggestion(self, item):
        """Handle selection of a suggestion."""
        selected_text = item.text()
        self.search_field.setText(selected_text)
        self.suggestions_container.setVisible(False)
        self.product_selected.emit(selected_text)
    
    def set_items(self, items):
        """Set the full list of available items."""
        self.all_items = items
        self.update_suggestions(self.search_field.text())
    
    def clear(self):
        """Clear the search field and hide suggestions."""
        self.search_field.clear()
        self.suggestions_container.setVisible(False)


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
        self.ai1_eiq_label = None
        self.ai_percent_spin = None
        self.rate_spin = None
        self.rate_unit_combo = None
        self.applications_spin = None
        self.field_eiq_result = None
        self.impact_gauge = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Product selection area
        product_frame = ContentFrame()
        product_layout = QFormLayout()
        
        # Region selection
        self.region_combo = QComboBox()
        self.region_combo.setFont(get_body_font())
        
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
        
        # AI1 EIQ - Use consistent naming
        self.ai1_eiq_label = QLabel("--")
        self.ai1_eiq_label.setFont(get_body_font())
        product_layout.addRow("AI1 EIQ:", self.ai1_eiq_label)
        
        # Active ingredient percentage - Updated for consistency with CSV column change
        self.ai_percent_spin = QDoubleSpinBox()
        self.ai_percent_spin.setRange(0.1, 100.0)
        self.ai_percent_spin.setValue(0.0)
        self.ai_percent_spin.setSuffix("%")
        self.ai_percent_spin.valueChanged.connect(self.calculate_single_eiq)
        product_layout.addRow("Active Ingredient %:", self.ai_percent_spin)
        
        # Application rate
        rate_layout = QHBoxLayout()
        
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0.01, 100.0)
        self.rate_spin.setValue(0.0)
        self.rate_spin.valueChanged.connect(self.calculate_single_eiq)
        
        # Unit of measure selection for application rate
        self.rate_unit_combo = QComboBox()
        self.rate_unit_combo.addItems([
            "kg/ha", "g/ha", "L/ha", "mL/ha", 
            "lbs/acre", "oz/acre", "fl oz/acre", "gal/acre", 
            "pints/acre", "quarts/acre"
        ])
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
        
        # Results area
        results_frame = ContentFrame()
        results_layout = QVBoxLayout()
        
        results_title = QLabel("EIQ Results")
        results_title.setFont(get_subtitle_font(size=16))
        results_layout.addWidget(results_title)
        
        # Field EIQ result
        field_eiq_layout = QHBoxLayout()
        field_eiq_label = QLabel("Field EIQ:")
        field_eiq_label.setFont(get_body_font(size=14, bold=True))
        
        self.field_eiq_result = QLabel("--")
        self.field_eiq_result.setFont(get_body_font(size=16, bold=True))
        
        field_eiq_layout.addWidget(field_eiq_label)
        field_eiq_layout.addWidget(self.field_eiq_result)
        field_eiq_layout.addStretch(1)
        
        results_layout.addLayout(field_eiq_layout)
        
        # Impact rating gauge
        self.impact_gauge = GaugeWidget(
            min_value=0,
            max_value=100,
            critical_threshold=50,  # Adjust based on your EIQ thresholds
            warning_threshold=20    # Adjust based on your EIQ thresholds
        )
        results_layout.addWidget(self.impact_gauge)
        
        results_frame.layout.addLayout(results_layout)
        layout.addWidget(results_frame)
        
        # Save and Export buttons
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Save Calculation")
        save_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        save_button.clicked.connect(self.save_calculation)
        
        export_button = QPushButton("Export Results")
        export_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        export_button.clicked.connect(self.export_results)
        
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
                self.ai1_eiq_label.setText("--")
                self.ai_percent_spin.setValue(0.0)
                self.rate_spin.setValue(0.0)
                self.impact_gauge.set_value(0, "Select a product")
            else:
                # Handle case where no products are loaded
                self.product_search.setEnabled(False)
                print("No products found in CSV file")
        
        except Exception as e:
            print(f"Error updating product list: {e}")
            self.product_search.setEnabled(False)
    
    def update_product_info(self, product_name):
        """Update product information when a product is selected."""
        if not all([self.ai1_eiq_label, self.ai_percent_spin, self.rate_spin, self.rate_unit_combo]):
            return
            
        if not product_name:
            # Clear fields if no product is selected
            self.ai1_eiq_label.setText("--")
            self.ai_percent_spin.setValue(0.0)
            self.rate_spin.setValue(0.0)
            self.impact_gauge.set_value(0, "No product selected")
            return
            
        try:
            # Get product info from CSV data
            product_info = get_product_info(product_name)
            
            # Update fields with product data
            self.ai1_eiq_label.setText(str(product_info["ai1_eiq"]))
            self.ai_percent_spin.setValue(product_info["ai_percent"])
            self.rate_spin.setValue(product_info["default_rate"])
            
            # Try to set rate unit if available in product data
            unit = product_info.get("default_unit", "")
            if unit:
                index = self.rate_unit_combo.findText(unit)
                if index >= 0:
                    self.rate_unit_combo.setCurrentIndex(index)
            
            # Calculate EIQ with new values
            self.calculate_single_eiq()
        except Exception as e:
            print(f"Error loading product info for '{product_name}': {e}")
            # Clear fields on error
            self.ai1_eiq_label.setText("--")
            self.ai_percent_spin.setValue(0.0)
            self.rate_spin.setValue(0.0)
            self.impact_gauge.set_value(0, "Error loading product")
    
    def calculate_single_eiq(self):
        """Calculate the Field EIQ for a single product."""
        if not all([self.ai1_eiq_label, self.field_eiq_result, self.impact_gauge]):
            return
            
        # Check if a product is selected and has valid EIQ value
        if self.ai1_eiq_label.text() == "--":
            return
        
        try:
            # Get values
            ai1_eiq = float(self.ai1_eiq_label.text())
            ai_percent = self.ai_percent_spin.value()
            rate = self.rate_spin.value()
            applications = self.applications_spin.value()
            unit = self.rate_unit_combo.currentText()
            
            # Calculate Field EIQ
            field_eiq = calculate_field_eiq(ai1_eiq, ai_percent, rate, unit, applications)
            
            # Update result display
            self.field_eiq_result.setText(f"{field_eiq:.2f}")
            
            # Update impact rating gauge
            rating, _ = get_impact_category(field_eiq)
            self.impact_gauge.set_value(field_eiq, rating)
            
        except (ValueError, ZeroDivisionError, AttributeError) as e:
            print(f"Error calculating EIQ: {e}")
            self.field_eiq_result.setText("Error")
            self.impact_gauge.set_value(0, "Error in calculation")
    
    def save_calculation(self):
        """Save the current calculation to history."""
        print("Save calculation")
        # In a real application, this would save the calculation to a database
    
    def export_results(self):
        """Export calculation results to a file."""
        print("Export results")
        # In a real application, this would export to CSV or PDF