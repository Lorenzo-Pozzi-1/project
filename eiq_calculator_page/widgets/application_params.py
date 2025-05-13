"""
Application parameters widgets for the LORENZO POZZI Pesticide App.

This module provides widgets for entering application rate, units, and other parameters.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QComboBox, QLabel, QFormLayout
from PySide6.QtCore import Qt, Signal
from common.styles import get_body_font
from math_module.eiq_conversions import APPLICATION_RATE_CONVERSION


class ApplicationRateWidget(QWidget):
    """
    Widget for entering application rate with unit selection.
    
    This widget combines a numeric spin box for the rate and a combo box 
    for the unit of measurement.
    """
    
    # Signal emitted when rate or unit changes
    value_changed = Signal()
    
    def __init__(self, parent=None):
        """Initialize the application rate widget."""
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Horizontal layout for rate and unit
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Rate spinbox
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0.0, 9999.99)
        self.rate_spin.setValue(0.0)
        self.rate_spin.setDecimals(2)
        self.rate_spin.valueChanged.connect(self.on_value_changed)
        layout.addWidget(self.rate_spin)
        
        # Unit combo box
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(sorted(APPLICATION_RATE_CONVERSION.keys()))
        self.unit_combo.setFont(get_body_font())
        self.unit_combo.currentIndexChanged.connect(self.on_value_changed)
        layout.addWidget(self.unit_combo)
    
    def on_value_changed(self):
        """Handle rate or unit changes."""
        self.value_changed.emit()
    
    def get_rate(self):
        """
        Get the current application rate.
        
        Returns:
            float: The application rate value
        """
        return self.rate_spin.value()
    
    def get_unit(self):
        """
        Get the current unit of measurement.
        
        Returns:
            str: The unit of measurement
        """
        return self.unit_combo.currentText()
    
    def set_rate(self, rate):
        """
        Set the application rate.
        
        Args:
            rate (float): The application rate value
        """
        self.rate_spin.setValue(rate)
    
    def set_unit(self, unit):
        """
        Set the unit of measurement.
        
        Args:
            unit (str): The unit of measurement
        """
        index = self.unit_combo.findText(unit)
        if index >= 0:
            self.unit_combo.setCurrentIndex(index)


class ApplicationParamsWidget(QWidget):
    """
    Widget for entering all application parameters.
    
    This widget provides inputs for application rate, units, and number of applications.
    """
    
    # Signal emitted when any parameter changes
    params_changed = Signal()
    
    def __init__(self, parent=None):
        """Initialize the application parameters widget."""
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Form layout for inputs
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Application rate widget
        self.rate_widget = ApplicationRateWidget()
        self.rate_widget.value_changed.connect(self.on_params_changed)
        form_layout.addRow("Application Rate:", self.rate_widget)
        
        # Number of applications
        self.applications_spin = QDoubleSpinBox()
        self.applications_spin.setRange(1, 10)
        self.applications_spin.setValue(1)
        self.applications_spin.setDecimals(0)
        self.applications_spin.valueChanged.connect(self.on_params_changed)
        form_layout.addRow("Number of Applications:", self.applications_spin)
        
        layout.addLayout(form_layout)
    
    def on_params_changed(self):
        """Handle parameter changes."""
        self.params_changed.emit()
    
    def get_params(self):
        """
        Get all application parameters.
        
        Returns:
            dict: Dictionary with rate, unit, and applications
        """
        return {
            "rate": self.rate_widget.get_rate(),
            "unit": self.rate_widget.get_unit(),
            "applications": int(self.applications_spin.value())
        }
    
    def set_params(self, rate=None, unit=None, applications=None):
        """
        Set application parameters.
        
        Args:
            rate (float, optional): Application rate
            unit (str, optional): Unit of measurement
            applications (int, optional): Number of applications
        """
        # Only update provided parameters
        if rate is not None:
            self.rate_widget.set_rate(rate)
        
        if unit is not None:
            self.rate_widget.set_unit(unit)
        
        if applications is not None:
            self.applications_spin.setValue(applications)