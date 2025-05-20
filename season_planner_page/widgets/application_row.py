"""Application Row Widget for the LORENZO POZZI Pesticide App with drag support."""

from contextlib import contextmanager
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QLabel, QSizePolicy, QFrame, QApplication, QMessageBox, QPushButton, QDoubleSpinBox, QComboBox
from data import ProductRepository, AIRepository
from common import DRAGGING_ROW_STYLE, FRAME_STYLE, REMOVE_BUTTON_STYLE, BODY_FONT_SIZE, ProductSelectionWidget, ApplicationParamsWidget
from math_module import calculate_product_field_eiq


class ApplicationRowWidget(QFrame):
    """Widget representing a single pesticide application row with drag & drop."""
    
    # Signals
    data_changed = Signal(object)  
    drag_started = Signal(object)  
    drag_ended = Signal(object)    
    delete_requested = Signal(object)  
    
    ROW_HEIGHT = 100
    
    def __init__(self, parent=None, field_area=10.0, field_area_uom="acre", index=0):
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
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setStyleSheet(FRAME_STYLE)
        self.setFixedHeight(self.ROW_HEIGHT)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setAcceptDrops(True)
        
        self.setup_ui()
        self.refresh_products()
    
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
        layout.addWidget(self.drag_handle)
        layout.setStretch(0, 0)
        
        # Application number
        self.app_number_label = QLabel(str(self.index + 1))
        self.app_number_label.setAlignment(Qt.AlignCenter)
        self.app_number_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.app_number_label)
        layout.setStretch(1, 1)
        
        # Date field
        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("Enter date or description")
        self.date_edit.textChanged.connect(self.on_data_changed)
        layout.addWidget(self.date_edit)
        layout.setStretch(2, 1)
        
        # Product selection widget
        style_config = {'font_size': BODY_FONT_SIZE, 'bold': False}
        self.product_selection = ProductSelectionWidget(
            orientation='horizontal', 
            style_config=style_config,
            show_labels=False,
        )
        self.product_selection.product_selected.connect(self.on_product_selected)
        layout.addWidget(self.product_selection)
        layout.setStretch(3, 2)  # Give more space to product selection
        
        # Application parameters widget (replaces rate_spin and uom_combo)
        self.app_params = ApplicationParamsWidget(
            orientation='horizontal',
            style_config=style_config,
            show_labels=False,
            show_applications=False
        )
        self.app_params.params_changed.connect(self.on_params_changed)
        layout.addWidget(self.app_params)
        layout.setStretch(4, 2)  # Give more space to application parameters
        
        # Area treated
        area_layout = QHBoxLayout()
        area_layout.setContentsMargins(0, 0, 0, 0)
        area_layout.setSpacing(2)
        
        self.area_spin = QDoubleSpinBox()
        self.area_spin.setRange(0.0, 9999.99)
        self.area_spin.setDecimals(1)
        self.area_spin.setValue(self.field_area)
        self.area_spin.valueChanged.connect(self.on_data_changed)
        area_layout.addWidget(self.area_spin)
        
        area_frame = QFrame()
        area_frame.setLayout(area_layout)
        layout.addWidget(area_frame)
        layout.setStretch(5, 1)
        
        # Application method
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Broadcast", "Band", "Foliar spray", "Soil incorporation",
            "Seed treatment", "Spot treatment", "Chemigation"
        ])
        self.method_combo.currentIndexChanged.connect(self.on_data_changed)
        layout.addWidget(self.method_combo)
        layout.setStretch(6, 1)
        
        # AI Groups (read-only)
        self.ai_groups_label = QLabel("")
        self.ai_groups_label.setAlignment(Qt.AlignCenter)
        self.ai_groups_label.setWordWrap(True)
        layout.addWidget(self.ai_groups_label)
        layout.setStretch(7, 1)
        
        # Field EIQ (read-only)
        self.field_eiq_label = QLabel("")
        self.field_eiq_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.field_eiq_label)
        layout.setStretch(8, 1)
        
        # Delete button
        delete_button = QPushButton("✕")
        delete_button.setFixedSize(24, 24)
        delete_button.setCursor(Qt.PointingHandCursor)
        delete_button.setToolTip("Remove application")
        delete_button.setStyleSheet(REMOVE_BUTTON_STYLE)
        delete_button.clicked.connect(self.confirm_delete)
        layout.addWidget(delete_button)
        layout.setStretch(9, 0)
    
    def update_app_number(self, number):
        """Update the displayed application number."""
        self.app_number_label.setText(str(number))

    def refresh_products(self):
        """Refresh product data in the product selection widget."""
        self.product_selection.refresh_data()
    
    def on_product_selected(self, product_name):
        """Handle product selection from the product selection widget."""
        product = None if not product_name else self.products_repo.get_product_by_name(product_name)
        
        if not product:
            self.ai_groups_label.setText("")
            self.field_eiq_label.setText("")
            self.on_data_changed()
            return
        
        # Update application parameters
        rate = product.label_maximum_rate if product.label_maximum_rate is not None else \
               product.label_minimum_rate if product.label_minimum_rate is not None else 0.0
        unit = product.rate_uom or ""
        
        # Set parameters in the application params widget
        self.app_params.set_params(rate=rate, unit=unit, applications=1)
        
        # Update AI Groups
        self.ai_groups_label.setText(", ".join(filter(None, product.get_ai_groups())))
        
        # Calculate and update Field EIQ
        self.calculate_field_eiq()
        self.on_data_changed()
    
    def on_params_changed(self):
        """Handle changes to application parameters."""
        self.calculate_field_eiq()
        self.on_data_changed()
    
    def calculate_field_eiq(self):
        """Calculate and update the Field EIQ for this application."""
        product_name = self.product_selection.get_selected_product()
        if not product_name:
            self.field_eiq_label.setText("")
            return
            
        product = self.products_repo.get_product_by_name(product_name)
        if not product:
            self.field_eiq_label.setText("")
            return
            
        try:
            # Get application parameters
            params = self.app_params.get_params()
            field_eiq = calculate_product_field_eiq(
                product.get_ai_data(),
                params["rate"],
                params["unit"],
                applications=1  # Always use 1 for a single application row
            )
            self.field_eiq_label.setText(f"{field_eiq:.2f}")
        except Exception as e:
            print(f"Error calculating Field EIQ: {e}")
            self.field_eiq_label.setText("Error")
    
    def on_data_changed(self):
        """Handle changes to any data in the row and update calculations."""
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
        product_name = self.product_selection.get_selected_product()
        if not product_name:
            return None
        
        # Get product type
        product = self.products_repo.get_product_by_name(product_name)
        product_type = product.product_type if product else ""
        
        # Get application parameters
        params = self.app_params.get_params()
        
        return {
            "application_date": self.date_edit.text(),
            "product_type": product_type,
            "product_name": product_name,
            "rate": params["rate"],
            "rate_uom": params["unit"],
            "area": self.area_spin.value(),
            "application_method": self.method_combo.currentText(),
            "ai_groups": self.ai_groups_label.text().split(", ") if self.ai_groups_label.text() else [],
            "field_eiq": self.get_field_eiq()
        }
    
    def set_application_data(self, data):
        """Set the application data from a dictionary."""
        with self.blocked_signals():
            # Set date
            if "application_date" in data:
                self.date_edit.setText(data["application_date"])
            
            # Set product (will also update product type internally)
            if "product_name" in data:
                self.product_selection.set_selected_product(data["product_name"])
            
            # Set application parameters
            rate = data.get("rate")
            unit = data.get("rate_uom")
            self.app_params.set_params(rate=rate, unit=unit, applications=1)
            
            # Set area
            if "area" in data:
                self.area_spin.setValue(data["area"])
            
            # Set application method
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
        self.setStyleSheet(DRAGGING_ROW_STYLE)
        
        # Signal drag started
        self.is_dragging = True
        self.drag_started.emit(self)
        
        # Execute drag operation
        drag.exec_(Qt.MoveAction)
        
        # Reset appearance and signal drag ended
        self.setStyleSheet(FRAME_STYLE)
        self.is_dragging = False
        self.drag_ended.emit(self)
    
    def confirm_delete(self):
        """Show confirmation dialog for deleting the application."""
        product_name = self.product_selection.get_selected_product() or ""
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Removal")
        msg_box.setText(f"Are you sure you want to remove this application?\n<div align='center'><b>{product_name}</b></div>")
        msg_box.setTextFormat(Qt.RichText)  # Set format to interpret HTML tags
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            self.delete_requested.emit(self)