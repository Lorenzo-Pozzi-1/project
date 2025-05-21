# config_dialog.py with updated seeding rate setting
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QHBoxLayout,
                             QComboBox, QDoubleSpinBox, QCheckBox, QFormLayout, QDialogButtonBox, QGroupBox)
from PySide6.QtCore import Qt
from common import get_config, save_config, get_medium_font, get_subtitle_font

class ConfigDialog(QDialog):
    """Configuration dialog for setting default application values."""
    
    def __init__(self, parent=None):
        """Initialize the configuration dialog."""
        super().__init__(parent)
        self.setWindowTitle("Application Settings")
        self.setMinimumWidth(450)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Default Application Settings")
        title_label.setFont(get_subtitle_font())
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Region group
        region_group = QGroupBox("Region Settings")
        region_layout = QFormLayout(region_group)
        
        # Country selection
        self.country_combo = QComboBox()
        self.country_combo.setFont(get_medium_font())
        self.country_combo.addItems(["Canada", "United States"])
        self.country_combo.currentIndexChanged.connect(self.update_regions)
        region_layout.addRow("Default Country:", self.country_combo)
        
        # Region selection
        self.region_combo = QComboBox()
        self.region_combo.setFont(get_medium_font())
        region_layout.addRow("Default Region:", self.region_combo)
        
        main_layout.addWidget(region_group)
        
        # Field parameters group
        field_group = QGroupBox("Field Parameters")
        field_layout = QFormLayout(field_group)
        
        # Row Spacing with unit selection
        row_spacing_layout = QHBoxLayout()

        self.row_spacing_spin = QDoubleSpinBox()
        self.row_spacing_spin.setRange(0, 100)
        self.row_spacing_spin.setValue(34.0)
        self.row_spacing_spin.setDecimals(1)
        row_spacing_layout.addWidget(self.row_spacing_spin)

        self.row_spacing_unit = QComboBox()
        self.row_spacing_unit.addItems(["inches", "cm"])
        row_spacing_layout.addWidget(self.row_spacing_unit)

        field_layout.addRow("Default Row Spacing:", row_spacing_layout)
        
        # Seeding Rate with unit selection (updated)
        seeding_rate_layout = QHBoxLayout()
        
        self.seeding_rate_spin = QDoubleSpinBox()
        self.seeding_rate_spin.setRange(0, 10000)
        self.seeding_rate_spin.setValue(2000)
        self.seeding_rate_spin.setDecimals(0)
        seeding_rate_layout.addWidget(self.seeding_rate_spin)
        
        self.seeding_rate_unit = QComboBox()
        self.seeding_rate_unit.addItems(["kg/ha", "kg/acre", "pound/ha", "pounds/acre"])
        seeding_rate_layout.addWidget(self.seeding_rate_unit)
        
        field_layout.addRow("Default Seeding Rate:", seeding_rate_layout)
        
        main_layout.addWidget(field_group)
        
        # "Don't ask again" checkbox
        self.dont_ask_check = QCheckBox("Don't show this dialog on startup")
        self.dont_ask_check.setFont(get_medium_font())
        main_layout.addWidget(self.dont_ask_check)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)        
        main_layout.addWidget(button_box)
        
        # Populate regions based on initial country
        self.update_regions()
    
    def update_regions(self):
        """Update regions dropdown based on selected country."""
        self.region_combo.clear()
        country = self.country_combo.currentText()
        
        # Add default option
        self.region_combo.addItem("None of these")
        
        # Add country-specific regions
        if country == "United States":
            self.region_combo.addItems(["Washington", "Idaho", "Wisconsin", "Maine"])
        elif country == "Canada":
            self.region_combo.addItems([
                "New Brunswick", "Prince Edward Island", "Alberta", 
                "Manitoba", "Quebec", "Saskatchewan"
            ])
    
    def load_settings(self):
        """Load existing settings from config."""
        config = get_config("user_settings", {})
        
        # Load country
        country = config.get("default_country", "Canada")
        index = self.country_combo.findText(country)
        if index >= 0:
            self.country_combo.setCurrentIndex(index)
        
        # Load region (after country is set to ensure regions are populated)
        region = config.get("default_region", "None of these")
        index = self.region_combo.findText(region)
        if index >= 0:
            self.region_combo.setCurrentIndex(index)
        
        # Load row spacing with unit
        row_spacing = config.get("default_row_spacing", 34.0)
        row_spacing_unit = config.get("default_row_spacing_unit", "inches")
        index = self.row_spacing_unit.findText(row_spacing_unit)
        self.row_spacing_unit.setCurrentIndex(index)
        self.row_spacing_spin.setValue(row_spacing)
        
        # Load seeding rate with unit (updated)
        seeding_rate = config.get("default_seeding_rate", 2000)
        seeding_rate_unit = config.get("default_seeding_rate_unit", "kg/ha")
        index = self.seeding_rate_unit.findText(seeding_rate_unit)
        if index >= 0:
            self.seeding_rate_unit.setCurrentIndex(index)
        self.seeding_rate_spin.setValue(seeding_rate)
        
        # Load other settings
        self.dont_ask_check.setChecked(config.get("dont_show_config_dialog", False))
    
    def save_settings(self):
        """Save settings to config."""
        config = get_config("user_settings", {})
        
        # Update configuration values
        config["default_country"] = self.country_combo.currentText()
        config["default_region"] = self.region_combo.currentText()
        config["default_row_spacing"] = self.row_spacing_spin.value()
        config["default_row_spacing_unit"] = self.row_spacing_unit.currentText()
        config["default_seeding_rate"] = self.seeding_rate_spin.value()
        config["default_seeding_rate_unit"] = self.seeding_rate_unit.currentText()
        config["dont_show_config_dialog"] = self.dont_ask_check.isChecked()
        
        # Save to global config
        updated_config = get_config(None, {})
        updated_config["user_settings"] = config
        save_config(updated_config)
    
    def accept(self):
        """Handle OK button click by saving settings."""
        self.save_settings()
        super().accept()