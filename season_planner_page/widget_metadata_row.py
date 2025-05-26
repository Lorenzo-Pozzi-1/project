"""Season Plan Metadata Widget for the LORENZO POZZI Pesticide App."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QComboBox, QDoubleSpinBox
from PySide6.QtCore import Signal
from datetime import date
from common import ContentFrame, get_medium_font, get_spacing_small


class SeasonPlanMetadataWidget(QWidget):
    """Widget for entering and displaying season plan metadata (crop year, grower, field details, variety)."""
    
    metadata_changed = Signal()  # Signal emitted when any metadata value changes
    
    def __init__(self, parent=None):
        """Initialize the metadata widget."""
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components for the metadata form."""
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create content frame and layout
        metadata_frame = ContentFrame()
        metadata_layout = QHBoxLayout()
        metadata_layout.setSpacing(get_spacing_small())
        
        # --- Crop Year ---
        current_year = date.today().year
        self.crop_year_combo = QComboBox()
        self.crop_year_combo.setFont(get_medium_font())
        years = list(range(current_year - 5, current_year + 6))
        self.crop_year_combo.addItems([f"CY{str(year)[-2:]}" for year in years])
        self.crop_year_combo.setCurrentIndex(5)  # Current year
        self.crop_year_combo.currentIndexChanged.connect(self.on_metadata_changed)
        self._add_field(metadata_layout, "Crop Year", self.crop_year_combo)
        
        # --- Grower Name ---
        self.grower_name_edit = QLineEdit()
        self.grower_name_edit.setPlaceholderText("Enter grower name")
        self.grower_name_edit.textChanged.connect(self.on_metadata_changed)
        self._add_field(metadata_layout, "Grower", self.grower_name_edit, 2)
        
        # --- Field Name ---
        self.field_name_edit = QLineEdit()
        self.field_name_edit.setPlaceholderText("Enter field name")
        self.field_name_edit.textChanged.connect(self.on_metadata_changed)
        self._add_field(metadata_layout, "Field", self.field_name_edit, 2)
        
        # --- Field Area with UOM ---
        area_layout = QHBoxLayout()
        area_layout.setSpacing(2)
        
        self.field_area_spin = QDoubleSpinBox()
        self.field_area_spin.setRange(0, 9999.9)
        self.field_area_spin.setDecimals(1)
        self.field_area_spin.valueChanged.connect(self.on_metadata_changed)
        area_layout.addWidget(self.field_area_spin)
        
        self.field_area_uom_combo = QComboBox()
        self.field_area_uom_combo.setFont(get_medium_font())
        self.field_area_uom_combo.addItems(["acre", "ha"])
        self.field_area_uom_combo.currentIndexChanged.connect(self.on_metadata_changed)
        area_layout.addWidget(self.field_area_uom_combo)
        
        label = QLabel("Area:")
        label.setFont(get_medium_font(bold=True))
        metadata_layout.addWidget(label)
        metadata_layout.addLayout(area_layout)
        metadata_layout.addSpacing(10)
        
        # --- Variety ---
        self.variety_edit = QLineEdit()
        self.variety_edit.setPlaceholderText("Enter potato variety")
        self.variety_edit.textChanged.connect(self.on_metadata_changed)
        self._add_field(metadata_layout, "Variety", self.variety_edit, 2)
        
        metadata_layout.setContentsMargins(0, 0, 10, 0)
        
        metadata_frame.layout.addLayout(metadata_layout)
        main_layout.addWidget(metadata_frame)
    
    def _add_field(self, layout, label_text, widget, stretch=1):
        """Add a field with label to the layout."""
        label = QLabel(f"{label_text}:")
        label.setFont(get_medium_font(bold=True))
        layout.addWidget(label)
        layout.addWidget(widget, stretch)
        layout.addSpacing(10)
    
    def on_metadata_changed(self):
        """Handle changes to any metadata field."""
        self.metadata_changed.emit()
    
    def get_metadata(self):
        """Get the current metadata values as a dictionary."""
        current_year = date.today().year
        selected_index = self.crop_year_combo.currentIndex()
        year = current_year - 5 + selected_index
        
        return {
            "crop_year": year,
            "crop_year_display": self.crop_year_combo.currentText(),
            "grower_name": self.grower_name_edit.text(),
            "field_name": self.field_name_edit.text(),
            "field_area": self.field_area_spin.value(),
            "field_area_uom": self.field_area_uom_combo.currentText(),
            "variety": self.variety_edit.text()
        }
    
    def set_metadata(self, metadata):
        """Set the metadata values from a dictionary."""
        self.blockSignals(True)
        try:
            # Set crop year
            if "crop_year" in metadata and metadata["crop_year"] is not None:
                current_year = date.today().year
                year_offset = metadata["crop_year"] - (current_year - 5)
                if 0 <= year_offset < self.crop_year_combo.count():
                    self.crop_year_combo.setCurrentIndex(year_offset)
            
            # Set text fields
            self.grower_name_edit.setText(metadata.get("grower_name", ""))
            self.field_name_edit.setText(metadata.get("field_name", ""))
            self.variety_edit.setText(metadata.get("variety", ""))
            
            # Set numeric/combo fields - ensure we have valid values
            field_area = metadata.get("field_area")
            if field_area is not None:
                self.field_area_spin.setValue(float(field_area))
            else:
                self.field_area_spin.setValue(0)  # Safe default
                
            if "field_area_uom" in metadata and metadata["field_area_uom"]:
                index = self.field_area_uom_combo.findText(metadata["field_area_uom"])
                if index >= 0:
                    self.field_area_uom_combo.setCurrentIndex(index)
        finally:
            self.blockSignals(False)
            self.metadata_changed.emit()
    
    def clear(self):
        """Clear all metadata fields."""
        default_metadata = {
            "crop_year": "",
            "grower_name": "",
            "field_name": "",
            "field_area": "0",
            "field_area_uom": "acre",
            "variety": ""
        }
        self.set_metadata(default_metadata)