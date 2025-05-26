"""Application Row Widget for the LORENZO POZZI Pesticide App with drag support."""

from contextlib import contextmanager
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QLabel, QSizePolicy, QFrame, QApplication, QMessageBox, QDoubleSpinBox, QComboBox
from common.constants import get_medium_text_size
from common.utils import get_config
from data import ProductRepository, AIRepository
from common import DRAGGING_ROW_STYLE, FRAME_STYLE, ProductSelectionWidget, ApplicationParamsWidget
from common.calculations import eiq_calculator


class ApplicationRowWidget(QFrame):
    """Widget representing a single pesticide application row with drag & drop."""
    
    # Signals
    data_changed = Signal(object)  
    drag_started = Signal(object)  
    drag_ended = Signal(object)    
    delete_requested = Signal(object)  
    
    ROW_HEIGHT = 40
    
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
        
        # Configure frame
        self._configure_frame()
        self._setup_ui()
        self.refresh_products()
    
    def _configure_frame(self):
        """Configure the frame properties."""
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setStyleSheet(FRAME_STYLE)
        self.setFixedHeight(self.ROW_HEIGHT)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setAcceptDrops(True)
    
    @contextmanager
    def blocked_signals(self):
        """Context manager to temporarily block widget signals."""
        self.blockSignals(True)
        try:
            yield
        finally:
            self.blockSignals(False)
    
    def _setup_ui(self):
        """Set up the UI components for the application row."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 1, 2, 1)
        layout.setSpacing(5)

        # Define widget configurations
        widgets = [
            self._create_drag_handle(),
            self._create_app_number_label(),
            self._create_date_field(),
            self._create_product_selection(),
            self._create_app_params(),
            self._create_area_field(),
            self._create_method_combo(),
            self._create_ai_groups_label(),
            self._create_field_eiq_label(),
            self._create_delete_button()
        ]
        
        # Add widgets with stretch factors
        stretch_factors = [0, 1, 1, 3, 1, 1, 1, 1, 1, 0]
        
        for widget, stretch in zip(widgets, stretch_factors):
            layout.addWidget(widget)
            layout.setStretch(layout.count() - 1, stretch)
    
    def _create_drag_handle(self):
        """Create the drag handle for the row."""
        self.drag_handle = QLabel("≡")
        self.drag_handle.setAlignment(Qt.AlignCenter)
        self.drag_handle.setFixedWidth(16)
        self.drag_handle.setCursor(Qt.OpenHandCursor)
        return self.drag_handle
    
    def _create_app_number_label(self):
        """Create the application number label."""
        self.app_number_label = QLabel(str(self.index + 1))
        self.app_number_label.setAlignment(Qt.AlignCenter)
        self.app_number_label.setStyleSheet("font-weight: bold;")
        return self.app_number_label
    
    def _create_date_field(self):
        """Create the date field."""
        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("Enter date or description")
        self.date_edit.textChanged.connect(self.on_data_changed)
        return self.date_edit
    
    def _create_product_selection(self):
        """Create the product selection widget."""
        style_config = {'font_size': get_medium_text_size(), 'bold': False}
        self.product_selection = ProductSelectionWidget(
            orientation='horizontal', 
            style_config=style_config,
            show_labels=False,
        )
        self.product_selection.product_selected.connect(self.on_product_selected)
        return self.product_selection
    
    def _create_app_params(self):
        """Create the application parameters widget."""
        style_config = {'font_size': get_medium_text_size(), 'bold': False}
        self.app_params = ApplicationParamsWidget(
            orientation='horizontal',
            style_config=style_config,
            show_labels=False,
            show_applications=False
        )
        self.app_params.params_changed.connect(self.on_params_changed)
        return self.app_params
    
    def _create_area_field(self):
        """Create the area field."""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        self.area_spin = QDoubleSpinBox()
        self.area_spin.setRange(0.0, 9999.99)
        self.area_spin.setDecimals(1)
        self.area_spin.setValue(self.field_area)
        self.area_spin.valueChanged.connect(self.on_data_changed)
        layout.addWidget(self.area_spin)
        
        return frame
    
    def _create_method_combo(self):
        """Create the application method combo box."""
        self.method_combo = QComboBox()
        methods = [
            "Broadcast", "Band", "Foliar spray", "Soil incorporation",
            "Seed treatment", "Spot treatment", "Chemigation"
        ]
        self.method_combo.addItems(methods)
        self.method_combo.currentIndexChanged.connect(self.on_data_changed)
        return self.method_combo
    
    def _create_ai_groups_label(self):
        """Create the AI groups label."""
        self.ai_groups_label = QLabel("")
        self.ai_groups_label.setAlignment(Qt.AlignCenter)
        self.ai_groups_label.setWordWrap(True)
        return self.ai_groups_label
    
    def _create_field_eiq_label(self):
        """Create the field EIQ label."""
        self.field_eiq_label = QLabel("")
        self.field_eiq_label.setAlignment(Qt.AlignCenter)
        return self.field_eiq_label
    
    def _create_delete_button(self):
        """Create the delete button."""
        from common import create_button
        delete_button = create_button(text="✕", style='remove', callback=self.confirm_delete)
        delete_button.setFixedSize(24, 24)
        delete_button.setToolTip("Remove application")
        return delete_button
    
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
        rate = (product.label_maximum_rate if product.label_maximum_rate is not None 
                else product.label_minimum_rate if product.label_minimum_rate is not None 
                else 0.0)
        unit = product.rate_uom or ""
        
        # Set parameters in the application params widget
        self.app_params.set_params(rate=rate, unit=unit)
        
        # Update AI Groups
        ai_groups = product.get_ai_groups()
        self.ai_groups_label.setText(", ".join(filter(None, ai_groups)))
        
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
            
            # Get user preferences for UOM conversions
            user_preferences = get_config("user_preferences", {})
            
            # Calculate Field use EIQ
            field_eiq = eiq_calculator.calculate_product_field_eiq(
                active_ingredients=product.get_ai_data(),
                application_rate=params["rate"],
                application_rate_uom=params["unit"],
                applications=1,  # Always use 1 for a single application row
                user_preferences=user_preferences
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
            self.app_params.set_params(rate=rate, unit=unit)
            
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
    
    # Drag and drop functionality
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
        self._start_drag(event)
    
    def _start_drag(self, event):
        """Initialize and execute the drag operation."""
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