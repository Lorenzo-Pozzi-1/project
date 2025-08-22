"""
Custom Machine Creation Dialog.

Provides a dialog for creating custom machines with simple tillage factor selection
"""

import csv
import os
import shutil
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QDoubleSpinBox, QPushButton,
                               QDialogButtonBox, QLabel, QMessageBox, QSpinBox,
                               QFileDialog, QSlider, QCheckBox, QComboBox)
from PySide6.QtCore import Qt, Signal
from typing import List, Tuple
from ..model_machine import Machine
from common.utils import resource_path


class CustomMachineDialog(QDialog):
    """Dialog for creating or editing custom machines with simple tillage factor selection."""
    
    machine_created = Signal(Machine)  # Emits the created/edited custom machine
    
    def __init__(self, parent=None, machine_to_edit: Machine = None):
        super().__init__(parent)
        self.machine_to_edit = machine_to_edit
        self.is_editing = machine_to_edit is not None
        self.picture_cleared = False  # Flag to track if picture was intentionally cleared
        
        title = "Edit Custom Machine" if self.is_editing else "Create Custom Machine"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(550, 500)  # Increased size to accommodate new fields
        
        self.setup_ui()
        
        # Pre-populate fields if editing
        if self.is_editing:
            self.populate_edit_fields()
        
    def setup_ui(self):
        """Set up the dialog user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_text = "Edit Custom Machine" if self.is_editing else "Create Custom Machine"
        title_label = QLabel(title_text)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Machine parameters form
        form_layout = QFormLayout()
        
        # Machine name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter custom machine name")
        form_layout.addRow("Machine Name:", self.name_edit)
        
        # Rotates checkbox
        self.rotates_checkbox = QCheckBox("Machine has rotating/powered components")
        form_layout.addRow("Rotates:", self.rotates_checkbox)
        
        # Working depth with unit selection
        depth_layout = QHBoxLayout()
        self.depth_spinbox = QDoubleSpinBox()
        self.depth_spinbox.setRange(0.1, 1000.0)
        self.depth_spinbox.setValue(6.0)  # Default to 6 inches
        self.depth_spinbox.setDecimals(1)
        depth_layout.addWidget(self.depth_spinbox)
        
        self.depth_uom_combo = QComboBox()
        self.depth_uom_combo.addItems(["in", "cm"])
        self.depth_uom_combo.setCurrentText("in")  # Default to inches
        depth_layout.addWidget(self.depth_uom_combo)
        
        form_layout.addRow("Working Depth:", depth_layout)
        
        # Operating speed with unit selection
        speed_layout = QHBoxLayout()
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setRange(0.1, 100.0)
        self.speed_spinbox.setValue(5.0)  # Default to 5 mph
        self.speed_spinbox.setDecimals(1)
        speed_layout.addWidget(self.speed_spinbox)
        
        self.speed_uom_combo = QComboBox()
        self.speed_uom_combo.addItems(["mph", "km/h"])
        self.speed_uom_combo.setCurrentText("mph")  # Default to mph
        speed_layout.addWidget(self.speed_uom_combo)
        
        form_layout.addRow("Operating Speed:", speed_layout)
        
        # Surface area disturbed
        self.surface_area_spinbox = QSpinBox()
        self.surface_area_spinbox.setRange(1, 100)
        self.surface_area_spinbox.setValue(100)
        self.surface_area_spinbox.setSuffix(" %")
        form_layout.addRow("Surface Area Disturbed:", self.surface_area_spinbox)
        
        # Tillage factor slider
        tillage_layout = QHBoxLayout()
        self.tillage_slider = QSlider(Qt.Horizontal)
        self.tillage_slider.setRange(10, 100)  # 0.1 to 1.0 as integers (10 to 100)
        self.tillage_slider.setValue(70)  # Default to 0.7
        self.tillage_slider.setTickPosition(QSlider.TicksBelow)
        self.tillage_slider.setTickInterval(10)
        self.tillage_slider.valueChanged.connect(self.update_tillage_display)
        tillage_layout.addWidget(self.tillage_slider)
        
        self.tillage_value_label = QLabel("0.7")
        self.tillage_value_label.setStyleSheet("font-weight: bold; color: #1976d2; min-width: 30px;")
        tillage_layout.addWidget(self.tillage_value_label)
        
        form_layout.addRow("Tillage Factor:", tillage_layout)
        
        # Picture selection
        picture_layout = QHBoxLayout()
        self.picture_path = ""  # Store the selected picture path
        self.picture_label = QLabel("No picture selected")
        self.picture_label.setStyleSheet("color: #666; font-style: italic;")
        picture_layout.addWidget(self.picture_label)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_picture)
        picture_layout.addWidget(self.browse_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_picture)
        picture_layout.addWidget(self.clear_button)
        
        form_layout.addRow("Picture:", picture_layout)
        
        layout.addLayout(form_layout)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_custom_machine)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def update_tillage_display(self):
        """Update the tillage factor display when slider changes."""
        value = self.tillage_slider.value() / 100.0  # Convert from integer to decimal
        self.tillage_value_label.setText(f"{value:.1f}")
        
    def browse_picture(self):
        """Browse for a picture file."""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Image files (*.png *.jpg *.jpeg *.bmp *.gif)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setWindowTitle("Select Machine Picture")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.picture_path = selected_files[0]
                self.picture_cleared = False  # Reset the cleared flag
                # Show just the filename in the label
                filename = os.path.basename(self.picture_path)
                self.picture_label.setText(f"Selected: {filename}")
                self.picture_label.setStyleSheet("color: #2196f3; font-weight: bold;")
    
    def clear_picture(self):
        """Clear the selected picture."""
        self.picture_path = ""
        self.picture_cleared = True  # Flag to indicate picture was intentionally cleared
        self.picture_label.setText("No picture selected")
        self.picture_label.setStyleSheet("color: #666; font-style: italic;")
    
    def accept_custom_machine(self):
        """Validate inputs and create custom machine."""
        # Validate machine name
        machine_name = self.name_edit.text().strip()
        if not machine_name:
            QMessageBox.warning(self, "Warning", "Please enter a machine name.")
            return
            
        # Get tillage factor from slider
        tillage_factor = self.tillage_slider.value() / 100.0
        
        # Handle picture selection and copying
        picture_name = self.handle_picture_for_machine(machine_name)
        
        # Create custom machine
        custom_machine = Machine(
            name=machine_name,
            depth=self.depth_spinbox.value(),
            depth_uom=self.depth_uom_combo.currentText(),
            speed=self.speed_spinbox.value(),
            speed_uom=self.speed_uom_combo.currentText(),
            surface_area_disturbed=float(self.surface_area_spinbox.value()),
            tillage_type_factor=tillage_factor,
            picture=picture_name,
            rotates=self.rotates_checkbox.isChecked()
        )
        
        # Save to custom machines CSV
        if self.save_custom_machine(custom_machine):
            self.machine_created.emit(custom_machine)
            self.accept()
    
    def handle_picture_for_machine(self, machine_name: str) -> str:
        """Handle picture selection and copying for the machine."""
        # Generate safe filename base
        safe_name = "".join(c for c in machine_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')  # Replace spaces with underscores
        
        # If picture was intentionally cleared
        if self.picture_cleared:
            # Remove existing picture file if editing
            if self.is_editing and self.machine_to_edit.picture:
                old_picture_path = resource_path(f"STIR/images/custom_machines/{self.machine_to_edit.picture}")
                if os.path.exists(old_picture_path):
                    try:
                        os.remove(old_picture_path)
                        print(f"Removed picture file: {self.machine_to_edit.picture}")
                    except Exception as e:
                        print(f"Warning: Could not remove picture file: {e}")
            
            # Return default placeholder filename (no actual file will exist)
            return f"{safe_name}.png"
        
        # If user selected a new picture
        elif self.picture_path:
            try:
                # Get file extension from selected picture
                _, ext = os.path.splitext(self.picture_path)
                if not ext.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
                    QMessageBox.warning(self, "Invalid File", "Please select a valid image file.")
                    return f"{safe_name}.png"  # Default fallback
                
                # Create new filename
                new_filename = f"{safe_name}{ext}"
                
                # Destination path
                dest_path = resource_path(f"STIR/images/custom_machines/{new_filename}")
                
                # Ensure custom machines directory exists
                dest_dir = os.path.dirname(dest_path)
                os.makedirs(dest_dir, exist_ok=True)
                
                # Remove old picture if editing and it exists
                if self.is_editing and self.machine_to_edit.picture:
                    old_picture_path = resource_path(f"STIR/images/custom_machines/{self.machine_to_edit.picture}")
                    if os.path.exists(old_picture_path) and old_picture_path != dest_path:
                        try:
                            os.remove(old_picture_path)
                        except Exception as e:
                            print(f"Warning: Could not remove old picture file: {e}")
                
                # Copy new picture
                shutil.copy2(self.picture_path, dest_path)
                
                return new_filename
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to copy image: {str(e)}")
                return f"{safe_name}.png"  # Default fallback
        
        # No new picture and not cleared - keep existing or use default
        else:
            if self.is_editing and self.machine_to_edit.picture:
                # Keep existing picture
                return self.machine_to_edit.picture
            else:
                # Use default name for new machines
                return f"{safe_name}.png"
    
    def save_custom_machine(self, machine: Machine) -> bool:
        """Save custom machine to CSV file."""
        try:
            custom_machines_csv = resource_path("STIR/csv_custom_machines.csv")
            
            # Create file with headers if it doesn't exist
            if not os.path.exists(custom_machines_csv):
                with open(custom_machines_csv, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['name', 'rotates', 'depth', 'depth_uom', 'speed', 'speed_uom', 
                                   'surface_area_disturbed', 'tillage_type_factor', 'picture'])
            
            # Append custom machine
            with open(custom_machines_csv, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    machine.name,
                    'TRUE' if machine.rotates else 'FALSE',
                    machine.depth,
                    machine.depth_uom,
                    machine.speed,
                    machine.speed_uom,
                    machine.surface_area_disturbed,
                    machine.tillage_type_factor,
                    machine.picture
                ])
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save custom machine: {str(e)}")
            return False
    
    def populate_edit_fields(self):
        """Populate dialog fields when editing an existing machine."""
        if not self.machine_to_edit:
            return
            
        # Set basic machine parameters
        self.name_edit.setText(self.machine_to_edit.name)
        self.rotates_checkbox.setChecked(self.machine_to_edit.rotates)
        
        # Set depth and depth unit
        self.depth_spinbox.setValue(self.machine_to_edit.depth)
        self.depth_uom_combo.setCurrentText(self.machine_to_edit.depth_uom)
        
        # Set speed and speed unit
        self.speed_spinbox.setValue(self.machine_to_edit.speed)
        self.speed_uom_combo.setCurrentText(self.machine_to_edit.speed_uom)
        
        # Set surface area disturbed
        self.surface_area_spinbox.setValue(int(self.machine_to_edit.surface_area_disturbed))
        
        # Set tillage factor in slider
        tillage_value = int(self.machine_to_edit.tillage_type_factor * 100)  # Convert to integer
        self.tillage_slider.setValue(tillage_value)
        self.update_tillage_display()  # Update the display label
        
        # Set picture information
        if self.machine_to_edit.picture:
            picture_path = resource_path(f"STIR/images/custom_machines/{self.machine_to_edit.picture}")
            if os.path.exists(picture_path):
                self.picture_label.setText(f"Current: {self.machine_to_edit.picture}")
                self.picture_label.setStyleSheet("color: #2196f3; font-weight: bold;")
            else:
                self.picture_label.setText(f"Missing: {self.machine_to_edit.picture}")
                self.picture_label.setStyleSheet("color: #f44336; font-weight: bold;")
        else:
            self.picture_label.setText("No picture assigned")
            self.picture_label.setStyleSheet("color: #666; font-style: italic;")
