"""
Application parameters widgets for the LORENZO POZZI Pesticide App.

This module provides widgets for entering application rate, units, and other parameters.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QComboBox, QFormLayout, QLabel
from PySide6.QtCore import Signal, Property
from common.styles import get_medium_font, get_small_font
from common.widgets.widgets import ContentFrame
from math_module import APPLICATION_RATE_CONVERSION


class ApplicationRateWidget(QWidget):
    """Widget for entering application rate with unit selection."""
    
    value_changed = Signal()
    
    def __init__(self, parent=None, style_config=None):
        """Initialize the application rate widget."""
        super().__init__(parent)
        self._style_config = style_config or {}
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        font = get_small_font()
        
        # Rate spinbox
        self._rate_spin = QDoubleSpinBox()
        self._rate_spin.setRange(0.0, 9999.99)
        self._rate_spin.setValue(0.0)
        self._rate_spin.setDecimals(2)
        self._rate_spin.setFont(font)
        self._rate_spin.valueChanged.connect(self.value_changed)
        layout.addWidget(self._rate_spin)
        
        # Unit combo box
        self._unit_combo = QComboBox()
        self._unit_combo.addItems(sorted(APPLICATION_RATE_CONVERSION.keys()))
        self._unit_combo.setFont(font)
        self._unit_combo.currentIndexChanged.connect(self.value_changed)
        layout.addWidget(self._unit_combo)
    
    # Property-based API for rate
    def _get_rate(self):
        return self._rate_spin.value()
    
    def _set_rate(self, rate):
        self._rate_spin.setValue(rate)
    
    rate = Property(float, _get_rate, _set_rate)
    
    # Property-based API for unit
    def _get_unit(self):
        return self._unit_combo.currentText()
    
    def _set_unit(self, unit):
        index = self._unit_combo.findText(unit)
        if index >= 0:
            self._unit_combo.setCurrentIndex(index)
    
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
        self._rate_widget._unit_combo.setFont(font)
        
        # Create layout based on orientation and label settings
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