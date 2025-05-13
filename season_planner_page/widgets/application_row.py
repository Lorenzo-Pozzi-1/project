"""Application Row Widget for the LORENZO POZZI Pesticide App."""

from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QComboBox, 
                             QDoubleSpinBox, QLabel, QSizePolicy, QFrame)
from PySide6.QtCore import Qt, Signal
from data.product_repository import ProductRepository
from data.ai_repository import AIRepository
from math_module.eiq_calculations import calculate_product_field_eiq
from contextlib import contextmanager
from common.styles import APPLICATION_ROW_STYLE


class ApplicationRowWidget(QFrame):
    """Widget representing a single pesticide application row."""
    
    data_changed = Signal(object)  # Emitted when any data in the row changes
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
        self.product_types = []
        
        # Store repository instances
        self.products_repo = ProductRepository.get_instance()
        self.ai_repo = AIRepository.get_instance()
        
        # Set frame properties
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setStyleSheet(APPLICATION_ROW_STYLE)
        
        # Set fixed height and size policy
        self.setFixedHeight(self.ROW_HEIGHT)
        size_policy = self.sizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.setSizePolicy(size_policy)
        
        self.setup_ui()
        self.load_product_types()
    
    @contextmanager
    def blocked_signals(self):
        """Context manager to temporarily block widget signals."""
        self.blockSignals(True)
        try:
            yield
        finally:
            self.blockSignals(False)
    
    def _create_spin_box(self, min_val=0.0, max_val=9999.99, decimals=2, initial_val=0.0):
        """Create a QDoubleSpinBox with standard settings."""
        spin_box = QDoubleSpinBox()
        spin_box.setRange(min_val, max_val)
        spin_box.setDecimals(decimals)
        spin_box.setValue(initial_val)
        spin_box.valueChanged.connect(self.on_data_changed)
        return spin_box
        
    def _create_combo_box(self, items=None, placeholder=None, signal_handler=None):
        """Create a QComboBox with standard settings."""
        combo_box = QComboBox()
        if placeholder:
            combo_box.addItem(placeholder)
        if items:
            combo_box.addItems(items)
        combo_box.currentIndexChanged.connect(signal_handler or self.on_data_changed)
        return combo_box
    
    def setup_ui(self):
        """Set up the UI components for the application row."""
        # Main layout - horizontal row
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)
        
        # Date field
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
        
        # Set stretch factors
        stretches = [2, 1, 3, 1, 1, 1, 2, 2, 1]  # Date, Type, Product, Rate, UOM, Area, Method, AIGroups, EIQ
        for i, stretch in enumerate(stretches):
            layout.setStretch(i, stretch)
    
    def _clear_product_fields(self):
        """Clear product-specific fields like AI groups and EIQ."""
        self.ai_groups_label.setText("")
        self.field_eiq_label.setText("")
    
    def _get_current_product(self):
        """Get the currently selected product or None if none selected."""
        return None if self.product_combo.currentIndex() == 0 else self.products_repo.get_product_by_name(self.product_combo.currentText())
    
    def load_product_types(self):
        """Load product types from repository and populate the combo box."""
        # Get unique product types from all products
        products = self.products_repo.get_filtered_products()
        self.product_types = sorted(list(set(p.product_type for p in products if p.product_type)))
        
        # Update product type combo box
        self.product_type_combo.clear()
        self.product_type_combo.addItem("Select type...")
        self.product_type_combo.addItems(self.product_types)
    
    def on_product_type_changed(self):
        """Handle product type selection changes and update product list."""
        # Clear product selection
        self.product_combo.clear()
        self.product_combo.addItem("Select a product...")
        
        # If no type selected, return
        if self.product_type_combo.currentIndex() == 0:
            return
        
        selected_type = self.product_type_combo.currentText()
        
        # Load products of the selected type
        products = self.products_repo.get_filtered_products()
        filtered_products = [p for p in products if p.product_type == selected_type]
        
        # Populate product combo with filtered products
        for product in filtered_products:
            self.product_combo.addItem(product.product_name)
        
        # Reset product-specific fields
        self._clear_product_fields()
        self.on_data_changed()
    
    def on_product_changed(self):
        """Handle product selection changes and update related fields."""
        product = self._get_current_product()
        
        if not product:
            self._clear_product_fields()
            self.on_data_changed()
            return
        
        # Update UOM based on product rate UOM
        if product.rate_uom:
            index = self.uom_combo.findText(product.rate_uom)
            if index >= 0:
                self.uom_combo.setCurrentIndex(index)
        
        # Update AI Groups
        ai_groups = product.get_ai_groups()
        self.ai_groups_label.setText(", ".join(filter(None, ai_groups)))
        
        # Update application rate with max or min rate
        if product.label_maximum_rate is not None:
            self.rate_spin.setValue(product.label_maximum_rate)
        elif product.label_minimum_rate is not None:
            self.rate_spin.setValue(product.label_minimum_rate)
        
        # Calculate EIQ and emit data changed signal
        self.calculate_field_eiq()
        self.on_data_changed()
    
    def calculate_field_eiq(self):
        """Calculate and update the Field EIQ for this application."""
        try:
            product = self._get_current_product()
            
            if not product:
                self.field_eiq_label.setText("")
                return
            
            # Calculate Field EIQ
            field_eiq = calculate_product_field_eiq(
                product.get_ai_data(),
                self.rate_spin.value(),
                self.uom_combo.currentText(),
                applications=1
            )
            
            # Update the Field EIQ display
            self.field_eiq_label.setText(f"{field_eiq:.2f}")
            
        except Exception as e:
            print(f"Error calculating Field EIQ: {e}")
            self.field_eiq_label.setText("Error")
    
    def on_data_changed(self):
        """Handle changes to any data in the row and update calculations."""
        # Recalculate field EIQ when rate or UOM changes
        if self.sender() in (self.rate_spin, self.uom_combo):
            self.calculate_field_eiq()
        
        # Emit signal with reference to self
        self.data_changed.emit(self)
    
    def get_field_eiq(self):
        """Get the calculated Field EIQ value or 0.0 if not available."""
        try:
            if self.field_eiq_label.text():
                return float(self.field_eiq_label.text())
        except ValueError:
            pass
        
        return 0.0
    
    def set_field_area(self, area, uom):
        """Set the default field area and update spinner."""
        self.field_area = area
        self.field_area_uom = uom
        self.area_spin.setValue(area)
    
    def get_application_data(self):
        """Get the application data as a dictionary or None if no product selected."""
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
        """Set the application data from a dictionary."""
        # Use context manager to block signals temporarily
        with self.blocked_signals():
            # Set field values directly
            if "application_date" in data:
                self.date_edit.setText(data["application_date"])
                
            if "product_type" in data:
                self._set_combo_value(self.product_type_combo, data["product_type"])
                self.on_product_type_changed()
                
            if "product_name" in data:
                self._set_combo_value(self.product_combo, data["product_name"])
                
            if "rate" in data:
                self.rate_spin.setValue(data["rate"])
                
            if "rate_uom" in data:
                self._set_combo_value(self.uom_combo, data["rate_uom"])
                
            if "area" in data:
                self.area_spin.setValue(data["area"])
                
            if "application_method" in data:
                self._set_combo_value(self.method_combo, data["application_method"])
        
        # Recalculate field EIQ and emit data changed signal
        self.calculate_field_eiq()
        self.data_changed.emit(self)
        
    def _set_combo_value(self, combo, value):
        """Helper method to set combo box value by text."""
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)