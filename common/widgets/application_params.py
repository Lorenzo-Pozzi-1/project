"""
Application parameters widgets for the LORENZO POZZI Pesticide App.

This module provides widgets for entering application rate, units, and other parameters.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QFormLayout, QLabel, QMessageBox
from PySide6.QtCore import Signal, Property
from common.styles import get_medium_font, get_small_font
from common.utils import get_config
from common.widgets.header_frame_buttons import ContentFrame
from common.widgets.UOM_selector import SmartUOMSelector
from common.widgets.tracer import calculation_tracer
from data.repository_UOM import UOMRepository, CompositeUOM


class ApplicationRateWidget(QWidget):
    """Widget for entering application rate with unit selection and automatic conversion."""
    
    value_changed = Signal()
    
    def __init__(self, parent=None, style_config=None):
        """Initialize the application rate widget."""
        super().__init__(parent)
        self._style_config = style_config or {}
        self._previous_uom = SmartUOMSelector.BASE_UOM_TEXT  # Start with base state
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        font = get_small_font()
        
        # Rate spinbox
        self._rate_spin = QDoubleSpinBox()
        self._rate_spin.setRange(0.0, 999999.99)
        self._rate_spin.setValue(0.0)
        self._rate_spin.setDecimals(2)
        self._rate_spin.setFont(font)
        self._rate_spin.valueChanged.connect(self.value_changed)
        layout.addWidget(self._rate_spin)
        
        # Unit combo box
        self._unit_combo = SmartUOMSelector(uom_type="application_rate")
        self._unit_combo.currentTextChanged.connect(self._on_uom_changed)
        layout.addWidget(self._unit_combo)
    
    def _on_uom_changed(self, new_uom):
        """Handle UOM change and convert the rate value accordingly."""
        # Skip conversion if transitioning from/to base state
        if (self._previous_uom == SmartUOMSelector.BASE_UOM_TEXT or 
            new_uom == SmartUOMSelector.BASE_UOM_TEXT or
            not new_uom or not self._previous_uom):
            # Just update previous UOM and emit signal
            self._previous_uom = new_uom
            self.value_changed.emit()
            return
        
        if new_uom == self._previous_uom:
            # No actual change
            return
        
        # Get current rate value
        current_rate = self._rate_spin.value()
        
        # Convert the rate from previous UOM to new UOM
        converted_rate = self._convert_rate(current_rate, self._previous_uom, new_uom)
        
        if converted_rate is not None:
            # Conversion successful - update rate and previous UOM
            self._rate_spin.blockSignals(True)
            self._rate_spin.setValue(converted_rate)
            self._rate_spin.blockSignals(False)
            
            calculation_tracer.log(f"Auto-converted rate: {current_rate} {self._previous_uom} → {converted_rate:.2f} {new_uom}")
            
            # Update previous UOM only after successful conversion
            self._previous_uom = new_uom
        else:
            # Conversion failed - revert UOM back to previous value
            self._unit_combo.blockSignals(True)
            self._unit_combo.setCurrentText(self._previous_uom)
            self._unit_combo.blockSignals(False)
            
            # Don't update _previous_uom since we're keeping the old one
            return  # Exit early to avoid emitting value_changed
        
        # Emit change signal only if conversion was successful
        self.value_changed.emit()
    
    def _convert_rate(self, value, from_uom, to_uom):
        """
        Convert rate value between UOMs.
        
        Args:
            value (float): Rate value to convert
            from_uom (str): Source UOM
            to_uom (str): Target UOM
            
        Returns:
            float or None: Converted value or None if conversion failed
        """
        if not from_uom or not to_uom:
            return None
        
        try:
            # Get UOM repository
            uom_repo = UOMRepository.get_instance()
            
            # Create composite UOM objects
            from_composite = CompositeUOM(from_uom)
            to_composite = CompositeUOM(to_uom)
            
            # Get user preferences for complex conversions
            user_preferences = get_config("user_preferences", {})
            
            # Perform conversion
            converted_value = uom_repo.convert_composite_uom(
                value, from_composite, to_composite, user_preferences
            )
            
            return converted_value
            
        except Exception as e:
            # Show warning dialog for incompatible conversions
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Unit Conversion Error!")
            msg_box.setText(
                f"Cannot convert from '{from_uom}' to '{to_uom}'"
            )
            msg_box.setDetailedText(str(e))
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            
            calculation_tracer.log(f"Rate conversion failed: {from_uom} → {to_uom}: {e}")
            # Return None to signal conversion failure - original value will be kept
            return None
    
    # Property-based API for rate
    def _get_rate(self):
        return self._rate_spin.value()
    
    def _set_rate(self, rate):
        self._rate_spin.setValue(rate)
    
    rate = Property(float, _get_rate, _set_rate)
    
    # Property-based API for unit
    def _get_unit(self):
        current_text = self._unit_combo.currentText()
        # Return None if in base state to maintain backward compatibility
        return None if current_text == SmartUOMSelector.BASE_UOM_TEXT else current_text
    
    def _set_unit(self, unit):
        # Set unit using two-step process to avoid validation
        if unit is None or unit == "":
            # Reset to base state
            self._unit_combo.resetToBase()
            self._previous_uom = SmartUOMSelector.BASE_UOM_TEXT
        else:
            # Two-step change: base -> target to avoid validation
            self._unit_combo.resetToBase()  # Step 1: to base (no signal)
            self._previous_uom = SmartUOMSelector.BASE_UOM_TEXT
            self._unit_combo.setCurrentText(unit)  # Step 2: base -> target
            self._previous_uom = unit
    
    unit = Property(str, _get_unit, _set_unit)


class ApplicationParamsWidget(QWidget):
    """Widget for entering all application parameters."""
    
    params_changed = Signal()
    
    def __init__(self, parent=None, orientation='vertical', style_config=None, 
                 show_labels=True, show_applications=True):
        """Initialize the application parameters widget with flexible layout."""
        super().__init__(parent)
        self._orientation = orientation
        self._style_config = style_config or {}
        self._show_labels = show_labels
        self._show_applications = show_applications
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        # Create main layout based on orientation
        layout = QHBoxLayout(self) if self._orientation == 'horizontal' else QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Get font styling
        font_size = self._style_config.get('font_size', 14)  # Using direct value instead of constant
        bold = self._style_config.get('bold', False)
        font = get_medium_font(size=font_size, bold=bold)
        
        # Create content frame
        content_frame = ContentFrame()
        
        # Application rate widget
        self._rate_widget = ApplicationRateWidget(style_config=self._style_config)
        self._rate_widget.value_changed.connect(self.params_changed)
        self._rate_widget._rate_spin.setFont(font)
        self._rate_widget._unit_combo.button.setFont(font)
        
        # Create layout based on orientation and label preferences
        if self._show_labels:
            form_layout = QFormLayout()
            form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
            
            # Rate label
            rate_label = QLabel("Application Rate:")
            rate_label.setFont(font)
            form_layout.addRow(rate_label, self._rate_widget)
            
            # Number of applications (if needed)
            if self._show_applications:
                self._applications_spin = QDoubleSpinBox()
                self._applications_spin.setRange(1, 10)
                self._applications_spin.setValue(1)
                self._applications_spin.setDecimals(0)
                self._applications_spin.setFont(font)
                self._applications_spin.valueChanged.connect(self.params_changed)
                
                apps_label = QLabel("Number of Applications:")
                apps_label.setFont(font)
                form_layout.addRow(apps_label, self._applications_spin)
            
            content_frame.layout.addLayout(form_layout)
        else:
            # Simple layout without labels
            simple_layout = QHBoxLayout() if self._orientation == 'horizontal' else QVBoxLayout()
            simple_layout.setSpacing(5 if self._orientation == 'vertical' else 10)
            
            simple_layout.addWidget(self._rate_widget)
            
            if self._show_applications:
                self._applications_spin = QDoubleSpinBox()
                self._applications_spin.setRange(1, 10)
                self._applications_spin.setValue(1)
                self._applications_spin.setDecimals(0)
                self._applications_spin.setFont(font)
                self._applications_spin.valueChanged.connect(self.params_changed)
                simple_layout.addWidget(self._applications_spin)
                
            content_frame.layout.addLayout(simple_layout)
        
        layout.addWidget(content_frame)
    
    def get_params(self):
        """Get all application parameters."""
        params = {
            "rate": self._rate_widget.rate,
            "unit": self._rate_widget.unit,
            "applications": int(self._applications_spin.value()) if self._show_applications else 1
        }
        return params
    
    def set_params(self, rate=None, unit=None, applications=None):
        """Set application parameters."""
        with self._block_signals():
            if rate is not None:
                self._rate_widget.rate = rate
            
            if unit is not None:
                self._rate_widget.unit = unit
            
            if applications is not None and self._show_applications:
                self._applications_spin.setValue(applications)
    
    def _block_signals(self):
        """Context manager to temporarily block widget signals."""
        class SignalBlocker:
            def __init__(self, widget):
                self.widget = widget
            
            def __enter__(self):
                self.widget.blockSignals(True)
                return self
            
            def __exit__(self, *args):
                self.widget.blockSignals(False)
                self.widget.params_changed.emit()
        
        return SignalBlocker(self)