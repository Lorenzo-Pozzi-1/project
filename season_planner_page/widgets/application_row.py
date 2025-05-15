"""Application Row Widget for the LORENZO POZZI Pesticide App with drag support."""

from contextlib import contextmanager
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QComboBox, QDoubleSpinBox, QLabel, QSizePolicy, QFrame, QApplication, QMessageBox, QPushButton
from data.product_repository import ProductRepository
from data.ai_repository import AIRepository
from common.styles import APPLICATION_ROW_STYLE
from math_module.eiq_calculations import calculate_product_field_eiq
from math_module.eiq_conversions import APPLICATION_RATE_CONVERSION


class ApplicationRowWidget(QFrame):
    """Widget representing a single pesticide application row with drag & drop."""
    
    # Signals
    data_changed = Signal(object)  
    drag_started = Signal(object)  
    drag_ended = Signal(object)    
    delete_requested = Signal(object)  
    
    ROW_HEIGHT = 40
    
    def __init__(self, parent=None, field_area=10.0, field_area_uom="ha", index=0):
        """Initialize the application row widget."""
        super().__init__(parent)
        self.field_area = field_area
        self.field_area_uom = field_area_uom
        self.index = index
        self.drag_start_position = None
        self.is_dragging = False
        
        # Store repository instances
        self.products_repo = ProductRepository.get_instance()
        self.ai_repo = AIRepository.get_instance()
        
        # Set frame properties
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setStyleSheet(APPLICATION_ROW_STYLE)
        self.setFixedHeight(self.ROW_HEIGHT)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
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
    
    def setup_ui(self):
        """Set up the UI components for the application row."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 1, 2, 1)
        layout.setSpacing(5)

        # Drag handle
        self.drag_handle = QLabel("≡")
        self.drag_handle.setAlignment(Qt.AlignCenter)
        self.drag_handle.setFixedWidth(16)
        self.drag_handle.setCursor(Qt.OpenHandCursor)
        
        # Application number
        self.app_number_label = QLabel(str(self.index + 1))
        self.app_number_label.setAlignment(Qt.AlignCenter)
        self.app_number_label.setStyleSheet("font-weight: bold;")
        
        # Date field
        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("Enter date or description")
        self.date_edit.textChanged.connect(self.on_data_changed)
        
        # Product Type selection
        self.product_type_combo = QComboBox()
        self.product_type_combo.addItem("Select type...")
        self.product_type_combo.currentIndexChanged.connect(self.on_product_type_changed)
        
        # Product selection
        self.product_combo = QComboBox()
        self.product_combo.addItem("Select a product...")
        self.product_combo.currentIndexChanged.connect(self.on_product_changed)
        
        # Application rate
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0.0, 9999.99)
        self.rate_spin.setDecimals(2)
        self.rate_spin.setValue(0.0)
        self.rate_spin.valueChanged.connect(self.on_data_changed)
        
        # Rate UOM
        self.uom_combo = QComboBox()
        self.uom_combo.addItems(sorted(APPLICATION_RATE_CONVERSION.keys()))
        self.uom_combo.currentIndexChanged.connect(self.on_data_changed)
        
        # Area treated
        self.area_spin = QDoubleSpinBox()
        self.area_spin.setRange(0.0, 9999.99)
        self.area_spin.setDecimals(1)
        self.area_spin.setValue(self.field_area)
        self.area_spin.valueChanged.connect(self.on_data_changed)
        
        # Application method
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Broadcast", "Band", "Foliar spray", "Soil incorporation",
            "Seed treatment", "Spot treatment", "Chemigation"
        ])
        self.method_combo.currentIndexChanged.connect(self.on_data_changed)
        
        # AI Groups (read-only)
        self.ai_groups_label = QLabel("")
        self.ai_groups_label.setAlignment(Qt.AlignCenter)
        self.ai_groups_label.setWordWrap(True)
        
        # Field EIQ (read-only)
        self.field_eiq_label = QLabel("")
        self.field_eiq_label.setAlignment(Qt.AlignCenter)
        
        # Delete button
        delete_button = QPushButton("✕")
        delete_button.setFixedSize(24, 24)
        delete_button.setCursor(Qt.PointingHandCursor)
        delete_button.setToolTip("Remove application")
        delete_button.setStyleSheet("color: #EF4026; font-weight: bold;")
        delete_button.clicked.connect(self.confirm_delete)
        
        # Add widgets to layout
        widgets = [
            self.drag_handle, self.app_number_label, self.date_edit, 
            self.product_type_combo, self.product_combo, self.rate_spin, 
            self.uom_combo, self.area_spin, self.method_combo, 
            self.ai_groups_label, self.field_eiq_label, delete_button
        ]
        
        for widget in widgets:
            layout.addWidget(widget)
        
        # Set stretch factors
        stretches = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]
        for i, stretch in enumerate(stretches):
            layout.setStretch(i, stretch)
    
    def update_app_number(self, number):
        """Update the displayed application number."""
        self.app_number_label.setText(str(number))

    def load_product_types(self):
        """Load product types from repository and populate the combo box."""
        products = self.products_repo.get_filtered_products()
        product_types = sorted(list(set(p.product_type for p in products if p.product_type)))
        
        self.product_type_combo.clear()
        self.product_type_combo.addItem("Select type...")
        self.product_type_combo.addItems(product_types)
    
    def on_product_type_changed(self):
        """Handle product type selection changes and update product list."""
        self.product_combo.clear()
        self.product_combo.addItem("Select a product...")
        
        if self.product_type_combo.currentIndex() == 0:
            self.ai_groups_label.setText("")
            self.field_eiq_label.setText("")
            self.on_data_changed()
            return
        
        selected_type = self.product_type_combo.currentText()
        products = [p for p in self.products_repo.get_filtered_products() 
                   if p.product_type == selected_type]
        
        for product in products:
            self.product_combo.addItem(product.product_name)
            
        self.ai_groups_label.setText("")
        self.field_eiq_label.setText("")
        self.on_data_changed()
    
    def on_product_changed(self):
        """Handle product selection changes and update related fields."""
        product = None if self.product_combo.currentIndex() == 0 else \
                 self.products_repo.get_product_by_name(self.product_combo.currentText())
        
        if not product:
            self.ai_groups_label.setText("")
            self.field_eiq_label.setText("")
            self.on_data_changed()
            return
        
        # Update UOM
        if product.rate_uom:
            index = self.uom_combo.findText(product.rate_uom)
            if index >= 0:
                self.uom_combo.setCurrentIndex(index)
        
        # Update AI Groups
        self.ai_groups_label.setText(", ".join(filter(None, product.get_ai_groups())))
        
        # Update application rate
        if product.label_maximum_rate is not None:
            self.rate_spin.setValue(product.label_maximum_rate)
        elif product.label_minimum_rate is not None:
            self.rate_spin.setValue(product.label_minimum_rate)
        
        self.calculate_field_eiq()
        self.on_data_changed()
    
    def calculate_field_eiq(self):
        """Calculate and update the Field EIQ for this application."""
        product = None if self.product_combo.currentIndex() == 0 else \
                 self.products_repo.get_product_by_name(self.product_combo.currentText())
        
        if not product:
            self.field_eiq_label.setText("")
            return
            
        try:
            field_eiq = calculate_product_field_eiq(
                product.get_ai_data(),
                self.rate_spin.value(),
                self.uom_combo.currentText(),
                applications=1
            )
            self.field_eiq_label.setText(f"{field_eiq:.2f}")
        except Exception as e:
            print(f"Error calculating Field EIQ: {e}")
            self.field_eiq_label.setText("Error")
    
    def on_data_changed(self):
        """Handle changes to any data in the row and update calculations."""
        if self.sender() in (self.rate_spin, self.uom_combo):
            self.calculate_field_eiq()
        self.data_changed.emit(self)
    
    def get_field_eiq(self):
        """Get the calculated Field EIQ value or 0.0 if not available."""
        try:
            return float(self.field_eiq_label.text()) if self.field_eiq_label.text() else 0.0
        except ValueError:
            return 0.0
    
    def set_field_area(self, area, uom):
        """Set the default field area and update spinner."""
        self.field_area = area
        self.field_area_uom = uom
        self.area_spin.setValue(area)
    
    def get_application_data(self):
        """Get the application data as a dictionary or None if no product selected."""
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
        with self.blocked_signals():
            # Set date first (unrelated to product selection)
            if "application_date" in data:
                self.date_edit.setText(data["application_date"])
            
            # Handle product type first
            product_type = data.get("product_type")
            product_name = data.get("product_name")
            
            # Step 1: Set the product type if available
            if product_type:
                index = self.product_type_combo.findText(product_type)
                if index >= 0:
                    self.product_type_combo.setCurrentIndex(index)
                    # Manually call this to update product list without emitting signals
                    self.on_product_type_changed()
                else:
                    print(f"Warning: Product type '{product_type}' not found in dropdown")
            
            # Step 2: Now set the product name after product list is populated
            if product_name:
                index = self.product_combo.findText(product_name)
                if index >= 0:
                    self.product_combo.setCurrentIndex(index)
                else:
                    print(f"Warning: Product name '{product_name}' not found in dropdown for type '{product_type}'")
            
            # Set the remaining fields
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
        
        # Now let the signals propagate normally
        self.calculate_field_eiq()
        self.data_changed.emit(self)
    
    def set_index(self, index):
        """Update the row index."""
        self.index = index
    
    def mousePressEvent(self, event):
        """Handle mouse press events to initiate drag."""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for drag operations."""
        if not (event.buttons() & Qt.LeftButton):
            return
            
        if ((event.pos() - self.drag_start_position).manhattanLength() 
                < QApplication.startDragDistance()):
            return
        
        # Start drag operation
        drag = QDrag(self)
        mimedata = QMimeData()
        mimedata.setData("application/x-applicationrow-index", str(self.index).encode())
        drag.setMimeData(mimedata)
        
        # Set drag appearance
        self.setStyleSheet(APPLICATION_ROW_STYLE)
        
        # Signal drag started
        self.is_dragging = True
        self.drag_started.emit(self)
        
        # Execute drag operation
        drag.exec_(Qt.MoveAction)
        
        # Reset appearance and signal drag ended
        self.setStyleSheet(APPLICATION_ROW_STYLE)
        self.is_dragging = False
        self.drag_ended.emit(self)
    
    def confirm_delete(self):
        """Show confirmation dialog for deleting the application."""
        product_name = "" if self.product_combo.currentText() == "Select a product..." else self.product_combo.currentText()
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Removal")
        msg_box.setText(f"Are you sure you want to remove this application?\n<div align='center'><b>{product_name}</b></div>")
        msg_box.setTextFormat(Qt.RichText)  # Set format to interpret HTML tags
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            self.delete_requested.emit(self)