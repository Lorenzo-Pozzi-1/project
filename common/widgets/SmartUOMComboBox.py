"""
Smart UOM ComboBox for the LORENZO POZZI Pesticide App.

This module provides a custom QComboBox with integrated custom UOM composition capability.
"""

from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QWidget, QPushButton, QDialog, QVBoxLayout, 
    QFormLayout, QDialogButtonBox, QLabel, QToolTip, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from data.UOM_repository import UOMRepository
from common.styles import get_medium_font

class CustomUOMDialog(QDialog):
    """Dialog for composing custom UOM from numerator and denominator."""
    
    def __init__(self, parent=None, allow_simple_units=True):
        super().__init__(parent)
        self.allow_simple_units = allow_simple_units
        self.setWindowTitle("Custom Unit of Measure")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Compose a custom unit of measure:")
        instructions.setFont(get_medium_font(bold=True))
        layout.addWidget(instructions)
        
        # Add simple unit option if allowed
        if self.allow_simple_units:
            simple_instructions = QLabel("For simple units (length, weight, volume), leave denominator empty:")
            simple_instructions.setFont(get_medium_font())
            layout.addWidget(simple_instructions)
        
        # Form layout for numerator and denominator
        form_layout = QFormLayout()
        
        # Get base units from repository
        repo = UOMRepository.get_instance()
        
        # Separate by category for better organization
        weight_units = [u for u, unit in repo._base_units.items() if unit.category == 'weight']
        volume_units = [u for u, unit in repo._base_units.items() if unit.category == 'volume'] 
        area_units = [u for u, unit in repo._base_units.items() if unit.category == 'area']
        length_units = [u for u, unit in repo._base_units.items() if unit.category == 'length']
        
        # Numerator dropdown
        self.numerator_combo = QComboBox()
        self.numerator_combo.addItem("-- Select Amount Unit --")
        self.numerator_combo.addItems(["--- Weight ---"] + weight_units)
        self.numerator_combo.addItems(["--- Volume ---"] + volume_units)
        if self.allow_simple_units:
            self.numerator_combo.addItems(["--- Length ---"] + length_units)
            self.numerator_combo.addItems(["--- Area ---"] + area_units)
        self.numerator_combo.setFont(get_medium_font())
        form_layout.addRow("Amount (Numerator):", self.numerator_combo)
        
        # Slash label
        slash_label = QLabel("/")
        slash_label.setAlignment(Qt.AlignCenter)
        slash_label.setFont(QFont("Arial", 16, QFont.Bold))
        form_layout.addRow("", slash_label)
        
        # Denominator dropdown
        self.denominator_combo = QComboBox()
        self.denominator_combo.addItem("-- Select Per Unit --")
        if self.allow_simple_units:
            self.denominator_combo.addItem("(None - for simple units)")
        self.denominator_combo.addItems(["--- Area ---"] + area_units)
        self.denominator_combo.addItems(["--- Length ---"] + length_units)
        self.denominator_combo.addItems(["--- Weight ---"] + weight_units)  # For concentrations
        self.denominator_combo.addItems(["--- Volume ---"] + volume_units)  # For concentrations
        self.denominator_combo.setFont(get_medium_font())
        form_layout.addRow("Per (Denominator):", self.denominator_combo)
        
        layout.addLayout(form_layout)
        
        # Preview
        self.preview_label = QLabel("Preview: ")
        self.preview_label.setFont(get_medium_font(bold=True))
        layout.addWidget(self.preview_label)
        
        # Connect signals for live preview
        self.numerator_combo.currentTextChanged.connect(self.update_preview)
        self.denominator_combo.currentTextChanged.connect(self.update_preview)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initially disable OK button
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(False)
    
    def update_preview(self):
        """Update the preview and enable/disable OK button."""
        num = self.numerator_combo.currentText()
        den = self.denominator_combo.currentText()
        
        # Skip header items and placeholders
        if num.startswith("--") or num.startswith("---"):
            self.preview_label.setText("Preview: ")
            self.ok_button.setEnabled(False)
            return
        
        # Handle simple units (no denominator)
        if den == "(None - for simple units)" or den.startswith("--"):
            if num and not num.startswith("---"):
                self.preview_label.setText(f"Preview: {num}")
                self.ok_button.setEnabled(True)
            else:
                self.preview_label.setText("Preview: ")
                self.ok_button.setEnabled(False)
            return
        
        # Handle compound units
        if den.startswith("---"):
            self.preview_label.setText("Preview: ")
            self.ok_button.setEnabled(False)
            return
        
        if num and den:
            custom_uom = f"{num}/{den}"
            self.preview_label.setText(f"Preview: {custom_uom}")
            self.ok_button.setEnabled(True)
        else:
            self.preview_label.setText("Preview: ")
            self.ok_button.setEnabled(False)
    
    def get_custom_uom(self):
        """Get the composed custom UOM string."""
        num = self.numerator_combo.currentText()
        den = self.denominator_combo.currentText()
        
        if not num or num.startswith("--") or num.startswith("---"):
            return None
        
        # Simple unit case
        if den == "(None - for simple units)" or den.startswith("--"):
            return num
        
        # Compound unit case
        if den.startswith("---"):
            return None
            
        return f"{num}/{den}"


class SmartUOMComboBox(QWidget):
    """
    Smart UOM ComboBox with integrated custom UOM composition.
    
    This widget combines a standard combobox with common UOMs and a pencil button
    that opens a dialog for custom UOM composition.
    """
    
    currentTextChanged = Signal(str)  # Emitted when UOM selection changes
    
    def __init__(self, parent=None, uom_type="application_rate"):
        """
        Initialize the smart UOM combobox.
        
        Args:
            parent: Parent widget
            uom_type: Type of UOM ("application_rate", "concentration", etc.)
        """
        super().__init__(parent)
        self.uom_type = uom_type
        self.setup_ui()
        self.populate_common_uoms()
    
    def setup_ui(self):
        """Set up the widget UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Main combobox
        self.combobox = QComboBox()
        self.combobox.setFont(get_medium_font())
        self.combobox.currentTextChanged.connect(self.on_selection_changed)
        layout.addWidget(self.combobox)
        
        # Custom UOM button (pencil emoji)
        self.custom_button = QPushButton("✏️")
        self.custom_button.setFixedSize(24, 24)
        self.custom_button.setToolTip("Create custom unit of measure")
        self.custom_button.clicked.connect(self.open_custom_dialog)
        QApplication.setStartDragTime(0)  # Reduce tooltip delay to minimum
        layout.addWidget(self.custom_button)
    
    def populate_common_uoms(self):
        """Populate the combobox with common UOMs based on frequency data."""
        
        # Common UOMs ordered by frequency (from your data)
        if self.uom_type == "application_rate":
            common_uoms = [
                "fl oz/acre",    # 614
                "pt/acre",       # 252  
                "lb/acre",       # 249
                "l/ha",          # 144
                "oz/acre",       # 106
                "ml/ha",         # 104
                "qt/acre",       # 89
                "g/ha",          # 76
                "fl oz/cwt",     # 50
                "gal/acre",      # 46
                "kg/ha",         # 28
                "ml/100kg",      # 16
                "ml/100m",       # 9
                "lb/cwt",        # 7
                "fl oz/1000ft",  # 4
                "ml/acre",       # 3
                "oz/cwt",        # 3
                "g/cwt",         # 2
            ]
        elif self.uom_type == "concentration":
            common_uoms = [
                "lb/gal",        # 1027
                "%",             # 517
                "g/l",           # 262
            ]
        else:
            # Default set
            common_uoms = ["kg/ha", "l/ha", "lb/acre", "fl oz/acre"]
        
        # Add placeholder and common UOMs
        self.combobox.addItem("-- Select unit --")
        self.combobox.addItems(common_uoms)
    
    def on_selection_changed(self, text):
        """Handle selection changes in the combobox."""
        if not text.startswith("--"):
            self.currentTextChanged.emit(text)
    
    def open_custom_dialog(self):
        """Open the custom UOM composition dialog."""
        dialog = CustomUOMDialog(self)
        if dialog.exec() == QDialog.Accepted:
            custom_uom = dialog.get_custom_uom()
            if custom_uom:
                # Add to combobox if not already present
                if self.combobox.findText(custom_uom) == -1:
                    self.combobox.addItem(custom_uom)
                
                # Select the custom UOM
                self.combobox.setCurrentText(custom_uom)
    
    def currentText(self):
        """Get the currently selected UOM text."""
        text = self.combobox.currentText()
        return text if not text.startswith("--") else ""
    
    def setCurrentText(self, text):
        """Set the current UOM text."""
        index = self.combobox.findText(text)
        if index >= 0:
            self.combobox.setCurrentIndex(index)
        else:
            # Add custom UOM if not found
            self.combobox.addItem(text)
            self.combobox.setCurrentText(text)
    
    def addItem(self, text):
        """Add an item to the combobox."""
        self.combobox.addItem(text)
    
    def addItems(self, texts):
        """Add multiple items to the combobox."""
        self.combobox.addItems(texts)

    def populate_common_uoms(self):
        """Populate the combobox with common UOMs based on frequency data."""
        
        # Clear existing items
        self.combobox.clear()
        
        if self.uom_type == "length":
            # Simple length units for row spacing
            common_uoms = ["inch", "cm", "m", "ft"]
            
        elif self.uom_type == "seeding_rate":
            # Seeding rate units (weight/area)
            common_uoms = ["kg/ha", "kg/acre", "lbs/ha", "lbs/acre"]
            
        elif self.uom_type == "application_rate":
            # Application rate UOMs ordered by frequency
            common_uoms = [
                "fl oz/acre",    # 614
                "pt/acre",       # 252  
                "lb/acre",       # 249
                "l/ha",          # 144
                "oz/acre",       # 106
                "ml/ha",         # 104
                "qt/acre",       # 89
                "g/ha",          # 76
                "fl oz/cwt",     # 50
                "gal/acre",      # 46
                "kg/ha",         # 28
                "ml/100kg",      # 16
                "ml/100m",       # 9
                "lb/cwt",        # 7
                "fl oz/1000ft",  # 4
                "ml/acre",       # 3
                "oz/cwt",        # 3
                "g/cwt",         # 2
            ]
        elif self.uom_type == "concentration":
            # Concentration units
            common_uoms = [
                "lb/gal",        # 1027
                "%",             # 517
                "g/l",           # 262
            ]
        else:
            # Default set
            common_uoms = ["kg/ha", "l/ha", "lb/acre", "fl oz/acre"]
        
        # Add placeholder and common UOMs
        self.combobox.addItem("-- Select unit --")
        self.combobox.addItems(common_uoms)