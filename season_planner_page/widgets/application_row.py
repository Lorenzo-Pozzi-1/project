"""
Application Row Widget for the LORENZO POZZI Pesticide App.

This module defines a custom widget representing a single application row
in the season planner. Updated to get EIQ values from active ingredients repository.
"""

from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QComboBox, 
                             QDoubleSpinBox, QLabel, QSizePolicy, QFrame)
from PySide6.QtCore import Qt, Signal, QSize
from data.product_repository import ProductRepository
from data.ai_repository import AIRepository
from math_module.eiq_conversions import convert_concentration_to_decimal
from math_module.eiq_calculations import calculate_product_field_eiq

# Create a subclass of QDoubleSpinBox that ignores wheel events unless focused
class NoScrollSpinBox(QDoubleSpinBox):
    def wheelEvent(self, event):
        # Only accept wheel events if the spin box has focus
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            # Pass the wheel event to the parent widget
            if self.parent():
                self.parent().wheelEvent(event)


class ApplicationRowWidget(QFrame):  # Changed from QWidget to QFrame
    """
    Widget representing a single pesticide application.
    
    This widget contains all the fields needed for a single application
    including date, product, rate, area, method, etc.
    """
    
    # Signals
    data_changed = Signal(object)  # Emitted when any data in the row changes
    
    # Fixed row height
    ROW_HEIGHT = 40
    
    def __init__(self, parent=None, field_area=10.0, field_area_uom="ha"):
        """
        Initialize the application row widget.
        
        Args:
            parent: Parent widget
            field_area: Default field area to use
            field_area_uom: Unit of measure for field area
        """
        super().__init__(parent)
        self.field_area = field_area
        self.field_area_uom = field_area_uom
        self.product_types = []  # List of available product types
        
        # Initialize the AI repository for EIQ lookups
        self.ai_repo = AIRepository.get_instance()
        
        # Set frame properties for visible border
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setStyleSheet("""
            ApplicationRowWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f8f8f8;
                margin: 1px;
            }
        """)
        
        # Set fixed height for the row
        self.setFixedHeight(self.ROW_HEIGHT)
        
        # Set a size policy that maintains the fixed height
        size_policy = self.sizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.setSizePolicy(size_policy)
        
        self.setup_ui()
        self.load_product_types()
    
    def _create_spin_box(self, min_val=0.0, max_val=9999.99, decimals=2, initial_val=0.0):
        """Helper method to create spin boxes with standard settings."""
        spin_box = NoScrollSpinBox()
        spin_box.setRange(min_val, max_val)
        spin_box.setDecimals(decimals)
        spin_box.setValue(initial_val)
        spin_box.valueChanged.connect(self.on_data_changed)
        return spin_box
        
    def _create_combo_box(self, items=None, placeholder=None, signal_handler=None):
        """Helper method to create combo boxes with standard settings."""
        combo_box = QComboBox()
        if placeholder:
            combo_box.addItem(placeholder)
        if items:
            combo_box.addItems(items)
        if signal_handler:
            combo_box.currentIndexChanged.connect(signal_handler)
        else:
            combo_box.currentIndexChanged.connect(self.on_data_changed)
        return combo_box
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout - horizontal row
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)  # Smaller margins to fit within the frame
        layout.setSpacing(5)
        
        # Date field (text input)
        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("Enter date or description")
        self.date_edit.textChanged.connect(self.on_data_changed)
        layout.addWidget(self.date_edit)
        
        # Product Type selection
        self.product_type_combo = self._create_combo_box(
            placeholder="Select type...",
            signal_handler=self.on_product_type_changed
        )
        layout.addWidget(self.product_type_combo)
        
        # Product selection
        self.product_combo = self._create_combo_box(
            placeholder="Select a product...",
            signal_handler=self.on_product_changed
        )
        layout.addWidget(self.product_combo)
        
        # Application rate
        self.rate_spin = self._create_spin_box(decimals=2, initial_val=0.0)
        layout.addWidget(self.rate_spin)
        
        # Rate UOM
        common_uoms = ["kg/ha", "l/ha", "g/ha", "ml/ha", "lbs/acre", "fl oz/acre", "oz/acre"]
        self.uom_combo = self._create_combo_box(items=common_uoms)
        layout.addWidget(self.uom_combo)
        
        # Area treated
        self.area_spin = self._create_spin_box(decimals=1, initial_val=self.field_area)
        layout.addWidget(self.area_spin)
        
        # Application method
        method_options = ["Broadcast", "Band", "Foliar spray", "Soil incorporation",
                      "Seed treatment", "Spot treatment", "Chemigation"]
        self.method_combo = self._create_combo_box(items=method_options)
        layout.addWidget(self.method_combo)
        
        # AI Groups (read-only)
        self.ai_groups_label = QLabel("")
        self.ai_groups_label.setAlignment(Qt.AlignCenter)
        self.ai_groups_label.setWordWrap(True)
        layout.addWidget(self.ai_groups_label)
        
        # Field EIQ (read-only)
        self.field_eiq_label = QLabel("")
        self.field_eiq_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.field_eiq_label)
        
        # Set stretch factors to control widget sizing
        layout.setStretch(0, 2)  # Date
        layout.setStretch(1, 1)  # Product Type
        layout.setStretch(2, 3)  # Product
        layout.setStretch(3, 1)  # Rate
        layout.setStretch(4, 1)  # UOM
        layout.setStretch(5, 1)  # Area
        layout.setStretch(6, 2)  # Method
        layout.setStretch(7, 2)  # AI Groups
        layout.setStretch(8, 1)  # Field EIQ
    
    def sizeHint(self):
        """
        Return the recommended size for the widget.
        
        Returns:
            QSize: Recommended size
        """
        # Return a size hint that maintains our fixed height
        width = super().sizeHint().width()
        return QSize(width, self.ROW_HEIGHT)
    
    def minimumSizeHint(self):
        """
        Return the minimum recommended size for the widget.
        
        Returns:
            QSize: Minimum recommended size
        """
        # Return a minimum size hint that maintains our fixed height
        width = super().minimumSizeHint().width()
        return QSize(width, self.ROW_HEIGHT)
    
    def load_product_types(self):
        """Load product types from repository."""
        # Get all products from repository
        products_repo = ProductRepository.get_instance()
        products = products_repo.get_filtered_products()
        
        # Extract unique product types
        self.product_types = sorted(list(set(p.product_type for p in products if p.product_type)))
        
        # Update product type combo box
        self.product_type_combo.clear()
        self.product_type_combo.addItem("Select type...")
        self.product_type_combo.addItems(self.product_types)
    
    def on_product_type_changed(self):
        """Handle product type selection changes."""
        # Get selected type
        type_index = self.product_type_combo.currentIndex()
        
        # Clear product selection
        self.product_combo.clear()
        self.product_combo.addItem("Select a product...")
        
        # If no type selected, return
        if type_index == 0:
            return
        
        selected_type = self.product_type_combo.currentText()
        
        # Load products of the selected type
        products_repo = ProductRepository.get_instance()
        products = products_repo.get_filtered_products()
        
        filtered_products = [p for p in products if p.product_type == selected_type]
        
        # Populate product combo with filtered products
        for product in filtered_products:
            self.product_combo.addItem(product.product_name)
        
        # Reset product-specific fields
        self.ai_groups_label.setText("")
        self.field_eiq_label.setText("")
        
        # Emit data changed
        self.on_data_changed()
    
    def on_product_changed(self):
        """Handle product selection changes."""
        if self.product_combo.currentIndex() == 0:
            # Clear product-related fields if "Select a product..." is chosen
            self.ai_groups_label.setText("")
            self.field_eiq_label.setText("")
            self.on_data_changed()
            return
        
        product_name = self.product_combo.currentText()
        
        # Find product in repository
        products_repo = ProductRepository.get_instance()
        product = self._get_product_by_name(product_name)
        
        if not product:
            return
        
        # Update UOM based on product rate UOM
        if product.rate_uom:
            index = self.uom_combo.findText(product.rate_uom)
            if index >= 0:
                self.uom_combo.setCurrentIndex(index)
        
        # Update AI Groups
        ai_groups = product.get_ai_groups()
        groups_text = ", ".join(filter(None, ai_groups))
        self.ai_groups_label.setText(groups_text)
        
        # Update application rate with max rate or min rate from product
        if product.label_maximum_rate is not None:
            self.rate_spin.setValue(product.label_maximum_rate)
        elif product.label_minimum_rate is not None:
            self.rate_spin.setValue(product.label_minimum_rate)
        
        # Calculate EIQ
        self.calculate_field_eiq()
        
        # Emit data changed signal
        self.on_data_changed()
    
    def _get_product_by_name(self, product_name):
        """Helper method to get product by name from repository."""
        products_repo = ProductRepository.get_instance()
        products = products_repo.get_filtered_products()
        
        for p in products:
            if p.product_name == product_name:
                return p
        return None
    
    def _get_ai_data(self, product, ai_name, ai_concentration, ai_concentration_uom):
        """Helper method to get active ingredient data for EIQ calculation."""
        if not ai_name:
            return None
            
        eiq = self.ai_repo.get_ai_eiq(ai_name)
        if eiq is None or ai_concentration is None:
            return None
            
        ai_decimal = convert_concentration_to_decimal(
            ai_concentration, 
            ai_concentration_uom
        )
        
        if ai_decimal is None:
            return None
            
        return {
            'name': ai_name,
            'eiq': eiq,
            'percent': ai_decimal * 100
        }
    
    def calculate_field_eiq(self):
        """Calculate and update the Field EIQ for this application."""
        try:
            # Check if all necessary data is available
            if self.product_combo.currentIndex() == 0:
                self.field_eiq_label.setText("")
                return
            
            product_name = self.product_combo.currentText()
            application_rate = self.rate_spin.value()
            rate_uom = self.uom_combo.currentText()
            
            # Get product from repository
            product = self._get_product_by_name(product_name)
            
            if not product:
                self.field_eiq_label.setText("")
                return
            
            # Prepare active ingredients data for calculation
            active_ingredients = []
            
            # Process each AI
            for ai_num in range(1, 5):
                ai_name = getattr(product, f'ai{ai_num}', None)
                ai_conc = getattr(product, f'ai{ai_num}_concentration', None)
                ai_conc_uom = getattr(product, f'ai{ai_num}_concentration_uom', None)
                
                ai_data = self._get_ai_data(product, ai_name, ai_conc, ai_conc_uom)
                if ai_data:
                    active_ingredients.append(ai_data)
            
            # Calculate Field EIQ
            field_eiq = calculate_product_field_eiq(
                active_ingredients, application_rate, rate_uom, applications=1
            )
            
            # Update the Field EIQ display
            self.field_eiq_label.setText(f"{field_eiq:.2f}")
            
        except Exception as e:
            print(f"Error calculating Field EIQ: {e}")
            self.field_eiq_label.setText("Error")
    
    def on_data_changed(self):
        """Handle changes to any data in the row."""
        # Recalculate field EIQ when rate or UOM changes
        if self.sender() == self.rate_spin or self.sender() == self.uom_combo:
            self.calculate_field_eiq()
        
        # Emit signal with reference to self
        self.data_changed.emit(self)
    
    def get_field_eiq(self):
        """
        Get the calculated Field EIQ value.
        
        Returns:
            float: Field EIQ value or 0.0 if not available
        """
        try:
            if self.field_eiq_label.text():
                return float(self.field_eiq_label.text())
        except ValueError:
            pass
        
        return 0.0
    
    def set_field_area(self, area, uom):
        """
        Set the default field area.
        
        Args:
            area (float): Area value
            uom (str): Unit of measure
        """
        self.field_area = area
        self.field_area_uom = uom
        
        # Only update the area spin if it's at the previous default value
        if abs(self.area_spin.value() - self.field_area) < 0.01:
            self.area_spin.setValue(area)
    
    def get_application_data(self):
        """
        Get the application data as a dictionary.
        
        Returns:
            dict: Application data or None if no product is selected
        """
        # Skip if no product selected
        if self.product_combo.currentIndex() == 0:
            return None
        
        return {
            "application_date": self.date_edit.text(),
            "product_type": self.product_type_combo.currentText(),
            "product_name": self.product_combo.currentText(),
            "rate": self.rate_spin.value(),
            "rate_uom": self.uom_combo.currentText(),
            "area": self.area_spin.value(),
            "application_method": self.method_combo.currentText(),
            "ai_groups": self.ai_groups_label.text().split(", ") if self.ai_groups_label.text() else [],
            "field_eiq": self.get_field_eiq()
        }
    
    def set_application_data(self, data):
        """
        Set the application data from a dictionary.
        
        Args:
            data (dict): Application data
        """
        # Block signals temporarily to prevent multiple data_changed signals
        self.blockSignals(True)
        
        field_value_pairs = [
            ("application_date", self.date_edit.setText),
            ("product_type", lambda val: self._set_combo_value(self.product_type_combo, val)),
            ("product_name", lambda val: self._set_combo_value(self.product_combo, val)),
            ("rate", self.rate_spin.setValue),
            ("rate_uom", lambda val: self._set_combo_value(self.uom_combo, val)),
            ("area", self.area_spin.setValue),
            ("application_method", lambda val: self._set_combo_value(self.method_combo, val)),
        ]
        
        for field, setter in field_value_pairs:
            if field in data:
                setter(data[field])
                
                # Update product list after setting type
                if field == "product_type":
                    self.on_product_type_changed()
        
        # Unblock signals
        self.blockSignals(False)
        
        # Recalculate field EIQ
        self.calculate_field_eiq()
        
        # Emit data changed signal
        self.data_changed.emit(self)
        
    def _set_combo_value(self, combo, value):
        """Helper method to set combo box value by text."""
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)