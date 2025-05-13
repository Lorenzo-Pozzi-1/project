"""Season Plan Metadata Widget for the LORENZO POZZI Pesticide App."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QComboBox, QDoubleSpinBox
from PySide6.QtCore import Signal
from datetime import date
from common.widgets import ContentFrame
from common.styles import get_body_font


class SeasonPlanMetadataWidget(QWidget):
    """Widget for entering and displaying season plan metadata (crop year, grower, field details, variety)."""
    
    metadata_changed = Signal()  # Signal emitted when any metadata value changes
    
    def __init__(self, parent=None):
        """Initialize the metadata widget."""
        super().__init__(parent)
        self.setup_ui()
    
    def _create_field_label(self, text):
        """Create a bold label for a form field."""
        label = QLabel(f"{text}:")
        label.setFont(get_body_font(bold=True))
        return label
    
    def _create_line_edit(self, placeholder):
        """Create a line edit with placeholder text and signal connection."""
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.textChanged.connect(self.on_metadata_changed)
        return edit
    
    def _add_field_section(self, layout, label_text, widget, stretch=1):
        """Add a field section with label and widget to the layout."""
        layout.addWidget(self._create_field_label(label_text))
        layout.addWidget(widget, stretch)
        layout.addSpacing(10)  # Space between field groups
    
    def setup_ui(self):
        """Set up the UI components for the metadata form."""
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create content frame and layout
        metadata_frame = ContentFrame()
        metadata_layout = QHBoxLayout()
        metadata_layout.setSpacing(15)
        
        # --- Crop Year ---
        self.crop_year_combo = QComboBox()
        current_year = date.today().year
        current_index = 5  # Default position (current year) in 11-year range
        
        # Add years in CY format (±5 years from current)
        for i, year in enumerate(range(current_year - 5, current_year + 6)):
            self.crop_year_combo.addItem(f"CY{str(year)[-2:]}", year)
            if year == current_year:
                current_index = i
                
        self.crop_year_combo.setCurrentIndex(current_index)
        self.crop_year_combo.currentIndexChanged.connect(self.on_metadata_changed)
        self._add_field_section(metadata_layout, "Crop Year", self.crop_year_combo)
        
        # --- Grower Name ---
        self.grower_name_edit = self._create_line_edit("Enter grower name")
        self._add_field_section(metadata_layout, "Grower", self.grower_name_edit, 2)
        
        # --- Field Name ---
        self.field_name_edit = self._create_line_edit("Enter field name")
        self._add_field_section(metadata_layout, "Field", self.field_name_edit, 2)
        
        # --- Field Area with UOM ---
        area_layout = QHBoxLayout()
        area_layout.setSpacing(2)
        
        self.field_area_spin = QDoubleSpinBox()
        self.field_area_spin.setRange(0.1, 9999.9)
        self.field_area_spin.setDecimals(1)
        self.field_area_spin.setValue(10.0)
        self.field_area_spin.valueChanged.connect(self.on_metadata_changed)
        area_layout.addWidget(self.field_area_spin)
        
        self.field_area_uom_combo = QComboBox()
        self.field_area_uom_combo.addItems(["acre", "ha"])
        self.field_area_uom_combo.currentIndexChanged.connect(self.on_metadata_changed)
        area_layout.addWidget(self.field_area_uom_combo)
        
        metadata_layout.addWidget(self._create_field_label("Area"))
        metadata_layout.addLayout(area_layout)
        metadata_layout.addSpacing(10)
        
        # --- Variety ---
        self.variety_edit = self._create_line_edit("Enter potato variety")
        self._add_field_section(metadata_layout, "Variety", self.variety_edit, 2)
        
        # Remove the last spacing that was added
        metadata_layout.setContentsMargins(0, 0, 10, 0)
        
        metadata_frame.layout.addLayout(metadata_layout)
        main_layout.addWidget(metadata_frame)
    
    def on_metadata_changed(self):
        """Handle changes to any metadata field."""
        self.metadata_changed.emit()
    
    def get_metadata(self):
        """Get the current metadata values as a dictionary."""
        return {
            "crop_year": self.crop_year_combo.currentData(),
            "crop_year_display": self.crop_year_combo.currentText(),
            "grower_name": self.grower_name_edit.text(),
            "field_name": self.field_name_edit.text(),
            "field_area": self.field_area_spin.value(),
            "field_area_uom": self.field_area_uom_combo.currentText(),
            "variety": self.variety_edit.text()
        }
    
    def set_metadata(self, metadata):
        """Set the metadata values from a dictionary."""
        with self._blocked_signals():
            # Set crop year
            if "crop_year" in metadata:
                year = metadata["crop_year"]
                for i in range(self.crop_year_combo.count()):
                    if self.crop_year_combo.itemData(i) == year:
                        self.crop_year_combo.setCurrentIndex(i)
                        break
            
            # Set text fields
            fields = {
                "grower_name": self.grower_name_edit,
                "field_name": self.field_name_edit,
                "variety": self.variety_edit
            }
            
            for field, widget in fields.items():
                if field in metadata:
                    widget.setText(metadata[field])
            
            # Set numeric/combo fields
            if "field_area" in metadata:
                self.field_area_spin.setValue(metadata["field_area"])
            
            if "field_area_uom" in metadata:
                index = self.field_area_uom_combo.findText(metadata["field_area_uom"])
                if index >= 0:
                    self.field_area_uom_combo.setCurrentIndex(index)
        
        # Signal is emitted after unblock in context manager
    
    def clear(self):
        """Clear all metadata fields."""
        # Create default metadata and apply it
        current_year = date.today().year
        default_metadata = {
            "crop_year": current_year,
            "grower_name": "",
            "field_name": "",
            "field_area": 10.0,
            "field_area_uom": "acre",
            "variety": ""
        }
        self.set_metadata(default_metadata)
    
    def _blocked_signals(self):
        """Context manager to temporarily block widget signals."""
        class SignalBlocker:
            def __init__(self, widget):
                self.widget = widget
            
            def __enter__(self):
                self.widget.blockSignals(True)
                return self.widget
            
            def __exit__(self, *args):
                self.widget.blockSignals(False)
                self.widget.metadata_changed.emit()
        
        return SignalBlocker(self)