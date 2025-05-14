"""Application Row Widget for the LORENZO POZZI Pesticide App with drag support."""

from contextlib import contextmanager
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QComboBox, QDoubleSpinBox, QLabel, QSizePolicy, QFrame, QApplication, QMessageBox
from data.product_repository import ProductRepository
from data.ai_repository import AIRepository
from common.styles import APPLICATION_ROW_STYLE
from math_module.eiq_calculations import calculate_product_field_eiq
from math_module.eiq_conversions import APPLICATION_RATE_CONVERSION


class ApplicationRowWidget(QFrame):
    """Widget representing a single pesticide application row with drag & drop."""
    
    data_changed = Signal(object)  # Emitted when any data in the row changes
    drag_started = Signal(object)  # Emitted when a drag starts
    drag_ended = Signal(object)    # Emitted when a drag ends
    delete_requested = Signal(object)  # Emitted when delete is confirmed
    ROW_HEIGHT = 40
    
    def __init__(self, parent=None, field_area=10.0, field_area_uom="ha", index=0):
        """
        Initialize the application row widget.
        
        Args:
            parent: Parent widget
            field_area: Default field area to use
            field_area_uom: Unit of measure for field area
            index: Row index in the container
        """
        super().__init__(parent)
        self.field_area = field_area
        self.field_area_uom = field_area_uom
        self.product_types = []
        self.index = index  # Store the row index
        self.drag_start_position = None
        self.is_dragging = False
        
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
        
        # Enable drag support
        self.setAcceptDrops(True)
        
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
        layout.setContentsMargins(2, 1, 2, 1)
        layout.setSpacing(5)

        # Add drag handle
        drag_handle = QLabel("≡")
        drag_handle.setAlignment(Qt.AlignCenter)
        drag_handle.setFixedWidth(16) 
        drag_handle.setStyleSheet("color: #666; font-size: 16px;")
        drag_handle.setCursor(Qt.OpenHandCursor)
        layout.addWidget(drag_handle)
        
        # Add application number label
        self.app_number_label = QLabel(str(self.index + 1))  # +1 for human-readable numbering
        self.app_number_label.setAlignment(Qt.AlignCenter)
        self.app_number_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.app_number_label)

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
        self.uom_combo = self._create_combo_box(items=sorted(APPLICATION_RATE_CONVERSION.keys()))
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
        
        # Add delete button at the end
        delete_button = QLabel("✕")
        delete_button.setFixedSize(24, 24)
        delete_button.setCursor(Qt.PointingHandCursor)
        delete_button.setToolTip("Remove application")
        delete_button.clicked.connect(self.confirm_delete)
        layout.addWidget(delete_button)
        
        # Update stretch factors for the new delete button
        stretches = [0, 1, 2, 1, 3, 1, 1, 1, 2, 2, 1, 0]  # Added 0 for non-stretching delete button
        for i, stretch in enumerate(stretches):
            layout.setStretch(i, stretch)
    
    def update_app_number(self, number):
        """Update the displayed application number."""
        self.app_number_label.setText(str(number))

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

    def mousePressEvent(self, event):
        """Handle mouse press events to initiate drag."""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for drag operations."""
        if not (event.buttons() & Qt.LeftButton):
            return
            
        # Only start drag after moving a certain distance
        if ((event.pos() - self.drag_start_position).manhattanLength() 
                < QApplication.startDragDistance()):
            return
            
        # Create drag object
        drag = QDrag(self)
        mimedata = QMimeData()
        
        # Store the row index in the mime data
        mimedata.setData("application/x-applicationrow-index", str(self.index).encode())
        drag.setMimeData(mimedata)
        
        # Apply visual effect for being dragged
        original_style = self.styleSheet()
        self.setStyleSheet(original_style + """
            background-color: #f0f9ff;
            border-left: 3px solid #3b82f6;
            border-right: 3px solid #3b82f6;
        """)
        self.setGraphicsEffect(None)  # Remove any existing effects
        
        # Emit signal that drag has started
        self.is_dragging = True
        self.drag_started.emit(self)
        
        # Execute drag operation
        result = drag.exec_(Qt.MoveAction)
        
        # Reset style after drag
        self.setStyleSheet(original_style)
        self.is_dragging = False
        self.drag_ended.emit(self)
    
    def set_drag_appearance(self, is_dragging):
        """Update visual appearance during drag."""
        original_style = APPLICATION_ROW_STYLE
        if is_dragging:
            self.setStyleSheet(original_style + """
                background-color: #f0f9ff;
                border-left: 3px solid #3b82f6;
                border-right: 3px solid #3b82f6;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            """)
            self.raise_()  # Bring to front
        else:
            self.setStyleSheet(original_style)
    
    def set_index(self, index):
        """Update the row index."""
        self.index = index

    def confirm_delete(self):
        """Show confirmation dialog for deleting the application."""
        product_name = self.product_combo.currentText()
        if product_name == "Select a product...":
            product_name = "this application"
        
        # Create message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Removal")
        msg_box.setText(f"Are you sure you want to remove this application: {product_name}?")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)  # Default to No for safety
        
        # Style the message box to match your app's aesthetics
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton[text="Yes"] {
                background-color: #EF4444;
                color: white;
            }
            QPushButton[text="No"] {
                background-color: #E5E7EB;
                color: #1F2937;
            }
        """)
        
        # Show the dialog and process the result
        result = msg_box.exec_()
        
        if result == QMessageBox.Yes:
            # Signal parent to remove this row
            self.delete_requested.emit(self)