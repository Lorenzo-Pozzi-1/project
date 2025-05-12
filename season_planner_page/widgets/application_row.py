"""
Application Row Widget for the LORENZO POZZI Pesticide App.

This module defines a custom widget representing a single application row
in the season planner. Updated to get EIQ values from active ingredients repository.
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLineEdit, QComboBox, 
                             QDoubleSpinBox, QLabel, QSizePolicy, QFrame)
from PySide6.QtCore import Qt, Signal, QSize, QEvent
from PySide6.QtGui import QWheelEvent
from data.product_repository import ProductRepository
from data.ai_repository import AIRepository
from math_module.eiq_conversions import convert_concentration_to_decimal, convert_concentration_to_percent
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
        self.product_type_combo = QComboBox()
        self.product_type_combo.addItem("Select type...")
        self.product_type_combo.currentIndexChanged.connect(self.on_product_type_changed)
        layout.addWidget(self.product_type_combo)
        
        # Product selection
        self.product_combo = QComboBox()
        self.product_combo.addItem("Select a product...")
        self.product_combo.currentIndexChanged.connect(self.on_product_changed)
        layout.addWidget(self.product_combo)
        
        # Application rate - using our custom spin box that ignores wheel events unless focused
        self.rate_spin = NoScrollSpinBox()
        self.rate_spin.setRange(0.0, 9999.99)
        self.rate_spin.setDecimals(2)
        self.rate_spin.setValue(0.0)
        self.rate_spin.valueChanged.connect(self.on_data_changed)
        layout.addWidget(self.rate_spin)
        
        # Rate UOM
        self.uom_combo = QComboBox()
        common_uoms = ["kg/ha", "l/ha", "g/ha", "ml/ha", "lbs/acre", "fl oz/acre", "oz/acre"]
        self.uom_combo.addItems(common_uoms)
        self.uom_combo.currentIndexChanged.connect(self.on_data_changed)
        layout.addWidget(self.uom_combo)
        
        # Area treated - using our custom spin box that ignores wheel events unless focused
        self.area_spin = NoScrollSpinBox()
        self.area_spin.setRange(0.0, 9999.99)
        self.area_spin.setDecimals(1)
        self.area_spin.setValue(self.field_area)  # Default to field area
        self.area_spin.valueChanged.connect(self.on_data_changed)
        layout.addWidget(self.area_spin)
        
        # Application method
        self.method_combo = QComboBox()
        method_options = ["Broadcast", "Band", "Foliar spray", "Soil incorporation",
                       "Seed treatment", "Spot treatment", "Chemigation"]
        self.method_combo.addItems(method_options)
        self.method_combo.currentIndexChanged.connect(self.on_data_changed)
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
        products = products_repo.get_filtered_products()
        product = None
        
        for p in products:
            if p.product_name == product_name:
                product = p
                break
        
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
            products_repo = ProductRepository.get_instance()
            products = products_repo.get_filtered_products()
            product = None
            
            for p in products:
                if p.product_name == product_name:
                    product = p
                    break
            
            if not product:
                self.field_eiq_label.setText("")
                return
            
            # Prepare active ingredients data for calculation
            active_ingredients = []
            
            # AI1
            if product.ai1:
                # Get EIQ from repository
                eiq = self.ai_repo.get_ai_eiq(product.ai1)
                if eiq is not None and product.ai1_concentration is not None:
                    # Convert concentration to decimal (0-1) using appropriate conversion function
                    ai_decimal = convert_concentration_to_decimal(
                        product.ai1_concentration, 
                        product.ai1_concentration_uom
                    )
                    
                    if ai_decimal is not None:
                        # Convert decimal to percent for the calculate_field_eiq function
                        ai_percent = ai_decimal * 100
                        
                        active_ingredients.append({
                            'name': product.ai1,
                            'eiq': eiq,
                            'percent': ai_percent
                        })
            
            # AI2
            if product.ai2:
                # Get EIQ from repository
                eiq = self.ai_repo.get_ai_eiq(product.ai2)
                if eiq is not None and product.ai2_concentration is not None:
                    # Convert concentration to decimal (0-1)
                    ai_decimal = convert_concentration_to_decimal(
                        product.ai2_concentration, 
                        product.ai2_concentration_uom
                    )
                    
                    if ai_decimal is not None:
                        # Convert decimal to percent
                        ai_percent = ai_decimal * 100
                        
                        active_ingredients.append({
                            'name': product.ai2,
                            'eiq': eiq,
                            'percent': ai_percent
                        })
            
            # AI3
            if product.ai3:
                # Get EIQ from repository
                eiq = self.ai_repo.get_ai_eiq(product.ai3)
                if eiq is not None and product.ai3_concentration is not None:
                    # Convert concentration to decimal (0-1)
                    ai_decimal = convert_concentration_to_decimal(
                        product.ai3_concentration, 
                        product.ai3_concentration_uom
                    )
                    
                    if ai_decimal is not None:
                        # Convert decimal to percent
                        ai_percent = ai_decimal * 100
                        
                        active_ingredients.append({
                            'name': product.ai3,
                            'eiq': eiq,
                            'percent': ai_percent
                        })
            
            # AI4
            if product.ai4:
                # Get EIQ from repository
                eiq = self.ai_repo.get_ai_eiq(product.ai4)
                if eiq is not None and product.ai4_concentration is not None:
                    # Convert concentration to decimal (0-1)
                    ai_decimal = convert_concentration_to_decimal(
                        product.ai4_concentration, 
                        product.ai4_concentration_uom
                    )
                    
                    if ai_decimal is not None:
                        # Convert decimal to percent
                        ai_percent = ai_decimal * 100
                        
                        active_ingredients.append({
                            'name': product.ai4,
                            'eiq': eiq,
                            'percent': ai_percent
                        })
            
            # Calculate Field EIQ using the function from math_module that expects
            # active ingredients with eiq, percent, and name
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
        
        if "application_date" in data:
            self.date_edit.setText(data["application_date"])
        
        if "product_type" in data:
            index = self.product_type_combo.findText(data["product_type"])
            if index >= 0:
                self.product_type_combo.setCurrentIndex(index)
                
                # Need to update product list after setting type
                self.on_product_type_changed()
        
        if "product_name" in data:
            index = self.product_combo.findText(data["product_name"])
            if index >= 0:
                self.product_combo.setCurrentIndex(index)
        
        if "rate" in data:
            self.rate_spin.setValue(data["rate"])
        
        if "rate_uom" in data:
            index = self.uom_combo.findText(data["rate_uom"])
            if index >= 0:
                self.uom_combo.setCurrentIndex(index)
        
        if "area" in data:
            self.area_spin.setValue(data["area"])
        
        if "application_method" in data:
            index = self.method_combo.findText(data["application_method"])
            if index >= 0:
                self.method_combo.setCurrentIndex(index)
        
        # Unblock signals
        self.blockSignals(False)
        
        # Recalculate field EIQ
        self.calculate_field_eiq()
        
        # Emit data changed signal
        self.data_changed.emit(self)