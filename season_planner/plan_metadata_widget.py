"""
Season Plan Metadata Widget for the LORENZO POZZI Pesticide App.

This module defines a widget for entering and displaying metadata for a season plan,
including crop year, grower name, field information, and variety.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QComboBox, QDoubleSpinBox
from PySide6.QtCore import Signal
from datetime import date
from common.widgets import ContentFrame
from common.styles import get_body_font


class SeasonPlanMetadataWidget(QWidget):
    """
    Widget for entering and displaying season plan metadata.
    
    This widget provides form fields for the user to input basic information
    about a season plan, such as crop year, grower, field details, and variety.
    """
    
    # Signal emitted when any metadata value changes
    metadata_changed = Signal()
    
    def __init__(self, parent=None):
        """Initialize the metadata widget."""
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create content frame
        metadata_frame = ContentFrame()
        
        # Use a horizontal layout for all fields on one line
        metadata_layout = QHBoxLayout()
        metadata_layout.setSpacing(15)  # Add some spacing between field groups
        
        # --- Crop Year ---
        cy_label = QLabel("Crop Year:")
        cy_label.setFont(get_body_font(bold=True))
        metadata_layout.addWidget(cy_label)
        
        # Create a combo box with CY format entries
        self.crop_year_combo = QComboBox()
        current_year = date.today().year
        # Add 10 years backward and forward
        for year in range(current_year - 5, current_year + 6):
            # Format as CY followed by last two digits (e.g., CY23 for 2023)
            year_str = f"CY{str(year)[-2:]}"
            self.crop_year_combo.addItem(year_str, year)
        # Set current year as default
        current_index = 5  # 5 years back + current year
        self.crop_year_combo.setCurrentIndex(current_index)
        self.crop_year_combo.currentIndexChanged.connect(self.on_metadata_changed)
        metadata_layout.addWidget(self.crop_year_combo)
        
        # Add some space between field groups
        metadata_layout.addSpacing(10)
        
        # --- Grower Name ---
        grower_label = QLabel("Grower:")
        grower_label.setFont(get_body_font(bold=True))
        metadata_layout.addWidget(grower_label)
        
        self.grower_name_edit = QLineEdit()
        self.grower_name_edit.setPlaceholderText("Enter grower name")
        self.grower_name_edit.textChanged.connect(self.on_metadata_changed)
        metadata_layout.addWidget(self.grower_name_edit, 2)  # Stretch factor of 2
        
        # Add some space between field groups
        metadata_layout.addSpacing(10)
        
        # --- Field Name ---
        field_label = QLabel("Field:")
        field_label.setFont(get_body_font(bold=True))
        metadata_layout.addWidget(field_label)
        
        self.field_name_edit = QLineEdit()
        self.field_name_edit.setPlaceholderText("Enter field name")
        self.field_name_edit.textChanged.connect(self.on_metadata_changed)
        metadata_layout.addWidget(self.field_name_edit, 2)  # Stretch factor of 2
        
        # Add some space between field groups
        metadata_layout.addSpacing(10)
        
        # --- Field Area with UOM ---
        area_label = QLabel("Area:")
        area_label.setFont(get_body_font(bold=True))
        metadata_layout.addWidget(area_label)
        
        self.field_area_spin = QDoubleSpinBox()
        self.field_area_spin.setRange(0.1, 9999.9)
        self.field_area_spin.setDecimals(1)
        self.field_area_spin.setValue(10.0)
        self.field_area_spin.valueChanged.connect(self.on_metadata_changed)
        metadata_layout.addWidget(self.field_area_spin)
        
        self.field_area_uom_combo = QComboBox()
        self.field_area_uom_combo.addItems(["ha", "acre"])
        self.field_area_uom_combo.currentIndexChanged.connect(self.on_metadata_changed)
        metadata_layout.addWidget(self.field_area_uom_combo)
        
        # Add some space between field groups
        metadata_layout.addSpacing(10)
        
        # --- Variety ---
        variety_label = QLabel("Variety:")
        variety_label.setFont(get_body_font(bold=True))
        metadata_layout.addWidget(variety_label)
        
        self.variety_edit = QLineEdit()
        self.variety_edit.setPlaceholderText("Enter potato variety")
        self.variety_edit.textChanged.connect(self.on_metadata_changed)
        metadata_layout.addWidget(self.variety_edit, 2)  # Stretch factor of 2
        
        metadata_frame.layout.addLayout(metadata_layout)
        main_layout.addWidget(metadata_frame)
    
    def on_metadata_changed(self):
        """Handle changes to any metadata field."""
        self.metadata_changed.emit()
    
    def get_metadata(self):
        """
        Get the current metadata values as a dictionary.
        
        Returns:
            dict: Dictionary with metadata values
        """
        # Get the actual year value stored in the combo box
        crop_year = self.crop_year_combo.currentData()
        
        return {
            "crop_year": crop_year,  # This is the numeric year (e.g., 2023)
            "crop_year_display": self.crop_year_combo.currentText(),  # This is the display text (e.g., "CY23")
            "grower_name": self.grower_name_edit.text(),
            "field_name": self.field_name_edit.text(),
            "field_area": self.field_area_spin.value(),
            "field_area_uom": self.field_area_uom_combo.currentText(),
            "variety": self.variety_edit.text()
        }
    
    def set_metadata(self, metadata):
        """
        Set the metadata values in the form.
        
        Args:
            metadata (dict): Dictionary with metadata values
        """
        # Block signals temporarily to prevent multiple metadata_changed signals
        self.blockSignals(True)
        
        if "crop_year" in metadata:
            year = metadata["crop_year"]
            # Find the index with this year as data
            for i in range(self.crop_year_combo.count()):
                if self.crop_year_combo.itemData(i) == year:
                    self.crop_year_combo.setCurrentIndex(i)
                    break
        
        if "grower_name" in metadata:
            self.grower_name_edit.setText(metadata["grower_name"])
        
        if "field_name" in metadata:
            self.field_name_edit.setText(metadata["field_name"])
        
        if "field_area" in metadata:
            self.field_area_spin.setValue(metadata["field_area"])
        
        if "field_area_uom" in metadata:
            index = self.field_area_uom_combo.findText(metadata["field_area_uom"])
            if index >= 0:
                self.field_area_uom_combo.setCurrentIndex(index)
        
        if "variety" in metadata:
            self.variety_edit.setText(metadata["variety"])
        
        # Unblock signals and emit a single change event
        self.blockSignals(False)
        self.metadata_changed.emit()
    
    def clear(self):
        """Clear all metadata fields."""
        self.blockSignals(True)
        
        # Set crop year to current year
        current_year = date.today().year
        for i in range(self.crop_year_combo.count()):
            if self.crop_year_combo.itemData(i) == current_year:
                self.crop_year_combo.setCurrentIndex(i)
                break
                
        self.grower_name_edit.clear()
        self.field_name_edit.clear()
        self.field_area_spin.setValue(10.0)
        self.field_area_uom_combo.setCurrentIndex(0)
        self.variety_edit.clear()
        
        self.blockSignals(False)
        self.metadata_changed.emit()