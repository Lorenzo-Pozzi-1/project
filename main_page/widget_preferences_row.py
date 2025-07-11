"""
Preferences row widget for the LORENZO POZZI Pesticide App.

This module provides a preferences row widget for the application's home page.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QDoubleSpinBox, QMessageBox
from PySide6.QtCore import Qt, Signal
from common.constants import get_spacing_xlarge
from common.styles import get_medium_font
from common.utils import get_config, save_config
from common.widgets.uom_selector import SmartUOMSelector
from common.widgets.header_frame_buttons import create_button

class PreferencesRow(QWidget):
    """
    Widget displaying a horizontal row of preferences preferences.
    
    This widget contains country/region selection, row spacing, 
    seeding rate, and options to save preferences.
    """
    
    preferences_changed_unsaved = Signal()
    country_changed = Signal(str)
    region_changed = Signal(str)
    preferences_changed = Signal()
    
    def __init__(self, parent=None):
        # Your existing initialization code
        super().__init__(parent)
        self.parent = parent
        self.initializing = True  # Flag to avoid multiple filtering during setup
        self.has_unsaved_changes = False  # Track if there are unsaved changes
        self.setup_ui()
        self.initializing = False  # Setup complete
        
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout - horizontal row for all preferences
        preferences_layout = QHBoxLayout(self)
        preferences_layout.setContentsMargins(0, 0, 0, 0)
        preferences_layout.setAlignment(Qt.AlignCenter)
        
        # Country selection
        country_label = QLabel("Country:")
        country_label.setFont(get_medium_font())
        preferences_layout.addWidget(country_label)
        
        preferences_layout.addSpacing(1)  # 1px spacing between label and control
        
        self.country_combo = QComboBox()
        self.country_combo.setFont(get_medium_font())
        self.country_combo.addItems(["Canada", "United States", "United Kingdom", "Europe"])
        self.country_combo.currentIndexChanged.connect(self.on_country_changed)
        preferences_layout.addWidget(self.country_combo)
        
        preferences_layout.addSpacing(get_spacing_xlarge())
        
        # Region selection
        region_label = QLabel("Region:")
        region_label.setFont(get_medium_font())
        preferences_layout.addWidget(region_label)
        
        preferences_layout.addSpacing(1)  # 1px spacing between label and control
        
        self.region_combo = QComboBox()
        self.region_combo.setFont(get_medium_font())
        self.region_combo.addItem("- Select Region -")
        self.region_combo.currentIndexChanged.connect(self.on_region_changed)
        preferences_layout.addWidget(self.region_combo)
        
        self.update_regions_dropdown()
        
        preferences_layout.addSpacing(get_spacing_xlarge())
        
        # Row Spacing with unit selection
        row_spacing_label = QLabel("Row Spacing:")
        row_spacing_label.setFont(get_medium_font())
        preferences_layout.addWidget(row_spacing_label)
        
        preferences_layout.addSpacing(1)  # 1px spacing between label and control

        self.row_spacing_spin = QDoubleSpinBox()
        self.row_spacing_spin.setRange(0, 100)
        self.row_spacing_spin.setValue(34.0)
        self.row_spacing_spin.setDecimals(1)
        self.row_spacing_spin.setFont(get_medium_font())
        preferences_layout.addWidget(self.row_spacing_spin)
        
        preferences_layout.addSpacing(1)  # 1px spacing between value and UOM

        # SmartUOMSelector for row spacing unit
        self.row_spacing_unit = SmartUOMSelector(uom_type="length")
        preferences_layout.addWidget(self.row_spacing_unit)
        
        preferences_layout.addSpacing(get_spacing_xlarge())
        
        # Seeding Rate with unit selection
        seeding_rate_label = QLabel("Seeding Rate:")
        seeding_rate_label.setFont(get_medium_font())
        preferences_layout.addWidget(seeding_rate_label)
        
        preferences_layout.addSpacing(1)  # 1px spacing between label and control
        
        self.seeding_rate_spin = QDoubleSpinBox()
        self.seeding_rate_spin.setRange(0, 10000)
        self.seeding_rate_spin.setValue(2000)
        self.seeding_rate_spin.setDecimals(0)
        self.seeding_rate_spin.setFont(get_medium_font())
        preferences_layout.addWidget(self.seeding_rate_spin)
        
        preferences_layout.addSpacing(1)  # 1px spacing between value and UOM
        
        # SmartUOMSelector for seeding rate unit
        self.seeding_rate_unit = SmartUOMSelector(uom_type="seeding_rate")
        preferences_layout.addWidget(self.seeding_rate_unit)
        
        preferences_layout.addSpacing(get_spacing_xlarge())
        
        # Save preferences button
        self.save_preferences_button = create_button(text="Save", style="yellow", callback=self.save_preferences)
        preferences_layout.addWidget(self.save_preferences_button)

        # Monitor all controls for changes - Updated signal connections
        self.country_combo.currentTextChanged.connect(self.mark_as_changed)
        self.region_combo.currentTextChanged.connect(self.mark_as_changed)
        self.row_spacing_spin.valueChanged.connect(self.mark_as_changed)
        self.row_spacing_unit.currentTextChanged.connect(self.mark_as_changed)
        self.seeding_rate_spin.valueChanged.connect(self.mark_as_changed)
        self.seeding_rate_unit.currentTextChanged.connect(self.mark_as_changed)

    def get_regions_for_country(self, country):
        """Get region options for a specific country."""
        regions = {
            "United States": ["Washington", "Idaho", "Wisconsin", "Maine"],
            "Canada": ["New Brunswick", "Prince Edward Island", "Alberta", "Manitoba", "Quebec", "Saskatchewan"],
            "United Kingdom": ["United Kingdom"],
            "Europe" : ["France", "Germany", "Netherlands", "Belgium", "Luxemburg"]
        }
        return regions.get(country, [])

    def update_regions_dropdown(self):
        """Update regions dropdown based on selected country."""
        current_region = self.region_combo.currentText()
        country = self.country_combo.currentText()
        
        # Clear and add default option
        self.region_combo.clear()
        self.region_combo.addItem("- Select Region -")
        
        # Add country-specific regions
        self.region_combo.addItems(self.get_regions_for_country(country))
        
        # Try to restore previous selection if available
        index = self.region_combo.findText(current_region)
        self.region_combo.setCurrentIndex(max(0, index))  # Default to "- Select Region -" if not found
    
    def on_country_changed(self, _):
        """Handle country selection change."""
        if self.initializing:
            return  # Skip during initialization
            
        country = self.country_combo.currentText()
        
        # Block signals during dropdown update to prevent cascading events
        self.region_combo.blockSignals(True)
        self.update_regions_dropdown()
        self.region_combo.blockSignals(False)
        
        # Get the new region value
        region = self.region_combo.currentText()
        
        # Mark as changed
        self.mark_as_changed()
        
        # Emit signal for the country change
        self.country_changed.emit(country)
    
    def on_region_changed(self, _):
        """Handle region selection change."""
        if self.initializing:
            return  # Skip during initialization
                
        region = self.region_combo.currentText()
        
        # Mark as changed
        self.mark_as_changed()
        
        # Emit signal with selected region - MainWindow handles filtering
        self.region_changed.emit(region)

    def set_country_region(self, country, region):
        """Set the country and region dropdowns."""
        # Block signals to prevent triggering filter changes during setup
        self.initializing = True
        
        # Set country
        index = self.country_combo.findText(country)
        if index >= 0:
            self.country_combo.setCurrentIndex(index)
        
        # Update regions for selected country
        self.update_regions_dropdown()
        
        # Set region
        index = self.region_combo.findText(region)
        if index >= 0:
            self.region_combo.setCurrentIndex(index)
        
        self.initializing = False
            
    def load_preferences(self):
        """Load existing preferences from config."""
        config = get_config("user_preferences", {})
        
        # Load field parameters
        row_spacing = config.get("default_row_spacing", 34.0)
        row_spacing_unit = config.get("default_row_spacing_unit", "inch")
        
        # Updated to use setCurrentText instead of index-based approach
        self.row_spacing_unit.setCurrentText(row_spacing_unit)
        self.row_spacing_spin.setValue(row_spacing)
        
        # Load seeding rate with unit
        seeding_rate = config.get("default_seeding_rate", 20)
        seeding_rate_unit = config.get("default_seeding_rate_unit", "cwt/acre")
        
        # Updated to use setCurrentText instead of index-based approach
        self.seeding_rate_unit.setCurrentText(seeding_rate_unit)
        self.seeding_rate_spin.setValue(seeding_rate)

        # After loading, reset the unsaved changes flag and update button
        self.has_unsaved_changes = False
        self.update_save_button_state()
    
    def mark_as_changed(self):
        """Mark preferences as changed but not saved."""
        if not self.initializing:
            self.has_unsaved_changes = True
            self.update_save_button_state()
            self.preferences_changed_unsaved.emit()
    
    def update_save_button_state(self):
        """Update the save button appearance based on whether there are unsaved changes."""
        if self.has_unsaved_changes:
            # Unsaved changes - enable button and show "Save"
            self.save_preferences_button.setText("Save")
            self.save_preferences_button.setEnabled(True)
            # Keep the yellow style for unsaved changes
        else:
            # No unsaved changes - disable button and show "Saved"
            self.save_preferences_button.setText("Saved")
            self.save_preferences_button.setEnabled(False)
    
    def save_preferences(self):
        """Save preferences to config."""
        config = get_config("user_preferences", {})
        
        # Update configuration values - currentText() method works the same
        config["default_country"] = self.country_combo.currentText()
        config["default_region"] = self.region_combo.currentText()
        config["default_row_spacing"] = self.row_spacing_spin.value()
        config["default_row_spacing_unit"] = self.row_spacing_unit.currentText()
        config["default_seeding_rate"] = self.seeding_rate_spin.value()
        config["default_seeding_rate_unit"] = self.seeding_rate_unit.currentText()
        
        # Save to global config
        updated_config = get_config(None, {})
        updated_config["user_preferences"] = config
        save_config(updated_config)
        
        # Show confirmation dialog
        self.show_confirmation_dialog()
        
        # Emit signal to notify that preferences have changed
        self.preferences_changed.emit()
        
        # After saving, reset the unsaved changes flag and update button
        self.has_unsaved_changes = False
        self.update_save_button_state()
    
    def show_confirmation_dialog(self):
        """Show a confirmation dialog that preferences have been saved."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Preferences Saved")
        msg_box.setText("Preferences saved successfully.")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Use application style font for the message box
        msg_box.setFont(get_medium_font())
        
        # Show the dialog
        msg_box.exec()