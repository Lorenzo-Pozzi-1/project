"""
Custom Machine Creation Dialog.

Provides a dialog for creating custom machines by combining implements
and specifying operational parameters.
"""

import csv
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QDoubleSpinBox, QComboBox, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QDialogButtonBox, QLabel, QMessageBox, QSpinBox)
from PySide6.QtCore import Qt, Signal
from typing import List, Tuple
from ..model_implement import Implement, TILLAGE_TYPE_OPTIONS, load_implements_from_csv
from ..model_machine import Machine
from common.utils import resource_path


class CustomMachineDialog(QDialog):
    """Dialog for creating custom machines by combining implements."""
    
    machine_created = Signal(Machine)  # Emits the created custom machine
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.implements = []
        self.selected_implements = []  # List of tuples: (implement_name, tillage_factor)
        
        self.setWindowTitle("Create Custom Machine")
        self.setModal(True)
        self.resize(600, 500)
        
        self.load_implements()
        self.setup_ui()
        
    def load_implements(self):
        """Load available implements from CSV."""
        implements_csv = resource_path("STIR/csv_implements.csv")
        self.implements = load_implements_from_csv(implements_csv)
        
    def setup_ui(self):
        """Set up the dialog user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Create Custom Machine")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Machine parameters form
        form_layout = QFormLayout()
        
        # Machine name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter custom machine name")
        form_layout.addRow("Machine Name:", self.name_edit)
        
        # Speed
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setRange(0.1, 50.0)
        self.speed_spinbox.setValue(8.0)
        self.speed_spinbox.setSuffix(" km/h")
        self.speed_spinbox.setDecimals(1)
        form_layout.addRow("Operating Speed:", self.speed_spinbox)
        
        # Working depth
        self.depth_spinbox = QDoubleSpinBox()
        self.depth_spinbox.setRange(0.1, 100.0)
        self.depth_spinbox.setValue(15.0)
        self.depth_spinbox.setSuffix(" cm")
        self.depth_spinbox.setDecimals(1)
        form_layout.addRow("Working Depth:", self.depth_spinbox)
        
        # Surface area disturbed
        self.surface_area_spinbox = QSpinBox()
        self.surface_area_spinbox.setRange(1, 100)
        self.surface_area_spinbox.setValue(100)
        self.surface_area_spinbox.setSuffix(" %")
        form_layout.addRow("Surface Area Disturbed:", self.surface_area_spinbox)
        
        layout.addLayout(form_layout)
        
        # Implements section
        implements_label = QLabel("Select Implements:")
        implements_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(implements_label)
        
        # Add implement controls
        add_layout = QHBoxLayout()
        
        self.implement_combo = QComboBox()
        self.implement_combo.addItem("Select an implement...")
        for implement in self.implements:
            self.implement_combo.addItem(implement.name)
        add_layout.addWidget(self.implement_combo)
        
        self.tillage_combo = QComboBox()
        for factor, description in TILLAGE_TYPE_OPTIONS:
            self.tillage_combo.addItem(description, factor)
        add_layout.addWidget(self.tillage_combo)
        
        add_button = QPushButton("Add Implement")
        add_button.clicked.connect(self.add_implement)
        add_layout.addWidget(add_button)
        
        layout.addLayout(add_layout)
        
        # Implements table
        self.implements_table = QTableWidget()
        self.implements_table.setColumnCount(3)
        self.implements_table.setHorizontalHeaderLabels(["Implement", "Tillage Type", "Remove"])
        self.implements_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.implements_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.implements_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.implements_table.setMaximumHeight(200)
        layout.addWidget(self.implements_table)
        
        # Calculated tillage factor display
        self.tillage_factor_label = QLabel("Calculated Tillage Factor: 0.0")
        self.tillage_factor_label.setStyleSheet("font-weight: bold; color: #1976d2; margin: 10px;")
        layout.addWidget(self.tillage_factor_label)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_custom_machine)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def add_implement(self):
        """Add selected implement to the table."""
        implement_index = self.implement_combo.currentIndex()
        if implement_index <= 0:  # "Select an implement..." is at index 0
            QMessageBox.warning(self, "Warning", "Please select an implement.")
            return
            
        implement_name = self.implement_combo.currentText()
        tillage_factor = self.tillage_combo.currentData()
        tillage_description = self.tillage_combo.currentText()
        
        # Check if implement already added
        for selected_implement, _ in self.selected_implements:
            if selected_implement == implement_name:
                QMessageBox.warning(self, "Warning", f"'{implement_name}' is already added.")
                return
        
        # Add to selected implements
        self.selected_implements.append((implement_name, tillage_factor))
        
        # Add row to table
        row = self.implements_table.rowCount()
        self.implements_table.insertRow(row)
        
        # Implement name
        self.implements_table.setItem(row, 0, QTableWidgetItem(implement_name))
        
        # Tillage type
        self.implements_table.setItem(row, 1, QTableWidgetItem(tillage_description))
        
        # Remove button
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_implement(row))
        self.implements_table.setCellWidget(row, 2, remove_button)
        
        # Update calculated tillage factor
        self.update_tillage_factor()
        
        # Reset combo boxes
        self.implement_combo.setCurrentIndex(0)
        self.tillage_combo.setCurrentIndex(0)
        
    def remove_implement(self, row: int):
        """Remove implement from the table."""
        if 0 <= row < len(self.selected_implements):
            # Remove from selected implements
            del self.selected_implements[row]
            
            # Remove from table
            self.implements_table.removeRow(row)
            
            # Update all remove button connections (row indices changed)
            for i in range(self.implements_table.rowCount()):
                remove_button = self.implements_table.cellWidget(i, 2)
                if remove_button:
                    remove_button.clicked.disconnect()
                    remove_button.clicked.connect(lambda checked, r=i: self.remove_implement(r))
            
            # Update calculated tillage factor
            self.update_tillage_factor()
    
    def update_tillage_factor(self):
        """Update the calculated tillage factor display."""
        if not self.selected_implements:
            max_factor = 0.0
        else:
            max_factor = max(factor for _, factor in self.selected_implements)
        
        self.tillage_factor_label.setText(f"Calculated Tillage Factor: {max_factor}")
    
    def accept_custom_machine(self):
        """Validate inputs and create custom machine."""
        # Validate machine name
        machine_name = self.name_edit.text().strip()
        if not machine_name:
            QMessageBox.warning(self, "Warning", "Please enter a machine name.")
            return
            
        # Validate implements
        if not self.selected_implements:
            QMessageBox.warning(self, "Warning", "Please add at least one implement.")
            return
            
        # Calculate tillage factor (highest from selected implements)
        max_tillage_factor = max(factor for _, factor in self.selected_implements)
        
        # Create custom machine
        custom_machine = Machine(
            name=machine_name,
            depth=self.depth_spinbox.value(),
            depth_uom="cm",
            speed=self.speed_spinbox.value(),
            speed_uom="km/h",
            surface_area_disturbed=float(self.surface_area_spinbox.value()),
            tillage_type_factor=max_tillage_factor,
            picture="custom_machine.png",  # Placeholder for now
            rotates=False  # Default for custom machines
        )
        
        # Save to custom machines CSV
        if self.save_custom_machine(custom_machine):
            self.machine_created.emit(custom_machine)
            self.accept()
        
    def save_custom_machine(self, machine: Machine) -> bool:
        """Save custom machine to CSV file."""
        try:
            custom_machines_csv = resource_path("STIR/csv_custom_machines.csv")
            
            # Create file with headers if it doesn't exist
            if not os.path.exists(custom_machines_csv):
                with open(custom_machines_csv, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['name', 'rotates', 'depth', 'depth_uom', 'speed', 'speed_uom', 
                                   'surface_area_disturbed', 'tillage_type_factor', 'picture', 
                                   'implements'])
            
            # Append custom machine
            with open(custom_machines_csv, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                implements_str = "|".join([f"{name}:{factor}" for name, factor in self.selected_implements])
                writer.writerow([
                    machine.name,
                    'FALSE',  # Custom machines default to non-rotating
                    machine.depth,
                    machine.depth_uom,
                    machine.speed,
                    machine.speed_uom,
                    machine.surface_area_disturbed,
                    machine.tillage_type_factor,
                    machine.picture,
                    implements_str
                ])
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save custom machine: {str(e)}")
            return False
