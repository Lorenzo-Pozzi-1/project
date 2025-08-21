"""
Custom Machine Manager Dialog.

Provides a card-based interface for managing custom machines including
viewing, editing, deleting, and picture management.
"""

import os
import shutil
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QScrollArea,
                               QWidget, QPushButton, QLabel, QGridLayout,
                               QDialogButtonBox, QFileDialog, QMessageBox,
                               QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from typing import List
from ..model_machine import Machine
from ..repository_machine import MachineRepository
from .custom_machine_creation_dialog import CustomMachineDialog
from common.utils import resource_path


class CustomMachineCard(QFrame):
    """Card widget for displaying custom machine information."""
    
    edit_requested = Signal(Machine)
    delete_requested = Signal(Machine)
    picture_change_requested = Signal(Machine)
    
    def __init__(self, machine: Machine, parent=None):
        super().__init__(parent)
        self.machine = machine
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the card UI."""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                margin: 5px;
            }
            QFrame:hover {
                border: 2px solid #1976d2;
            }
        """)
        self.setFixedSize(280, 320)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Image section
        image_label = QLabel()
        image_label.setFixedSize(250, 150)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("border: 1px solid #ddd; border-radius: 4px; background-color: #f9f9f9;")
        
        # Try to load machine image
        if self.machine.picture and self.machine.picture != "custom_machine.png":
            # Try custom machines folder first
            custom_image_path = resource_path(f"STIR/images/custom_machines/{self.machine.picture}")
            if os.path.exists(custom_image_path):
                pixmap = QPixmap(custom_image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(240, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_label.setPixmap(scaled_pixmap)
                else:
                    image_label.setText("Missing picture")
            else:
                image_label.setText("Missing picture")
        else:
            image_label.setText("Missing picture")
            
        layout.addWidget(image_label)
        
        # Machine name
        name_label = QLabel(self.machine.name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # Machine details
        details_text = f"""Speed: {self.machine.speed} {self.machine.speed_uom}
Depth: {self.machine.depth} {self.machine.depth_uom}
Surface Area: {self.machine.surface_area_disturbed}%
Tillage Factor: {self.machine.tillage_type_factor}"""
        
        details_label = QLabel(details_text)
        details_label.setAlignment(Qt.AlignLeft)
        details_label.setStyleSheet("font-size: 11px; color: #666;")
        layout.addWidget(details_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        # Change picture button
        picture_button = QPushButton("📷")
        picture_button.setToolTip("Change Picture")
        picture_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        picture_button.setFixedSize(35, 35)
        picture_button.clicked.connect(lambda: self.picture_change_requested.emit(self.machine))
        
        edit_button = QPushButton("Edit")
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        edit_button.clicked.connect(lambda: self.edit_requested.emit(self.machine))
        
        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        delete_button.clicked.connect(lambda: self.delete_requested.emit(self.machine))
        
        buttons_layout.addWidget(picture_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)
        layout.addLayout(buttons_layout)


class CustomMachineManagerDialog(QDialog):
    """Dialog for managing custom machines with card-based interface."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.machine_repo = MachineRepository.get_instance()
        
        self.setWindowTitle("Manage Custom Machines")
        self.setModal(True)
        self.resize(900, 700)
        
        self.setup_ui()
        self.refresh_machines()
        
    def setup_ui(self):
        """Set up the dialog user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Custom Machine Manager")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add new machine button
        add_button = QPushButton("Add New Custom Machine")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_button.clicked.connect(self.add_new_machine)
        layout.addWidget(add_button)
        
        # Scroll area for machine cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Widget to contain the cards grid
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background-color: transparent;")
        self.cards_layout = QGridLayout(self.scroll_widget)
        self.cards_layout.setSpacing(15)
        self.cards_layout.setContentsMargins(15, 15, 15, 15)
        
        scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(scroll_area)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)
        
    def refresh_machines(self):
        """Refresh the display of custom machines."""
        # Clear existing cards
        for i in reversed(range(self.cards_layout.count())):
            child = self.cards_layout.itemAt(i)
            if child:
                widget = child.widget()
                if widget:
                    widget.setParent(None)
        
        # Get custom machines
        all_machines = self.machine_repo.get_all_machines()
        custom_machines = [m for m in all_machines if self.is_custom_machine(m)]
        
        if not custom_machines:
            # Show empty state
            empty_label = QLabel("No custom machines found.\\nClick 'Add New Custom Machine' to create one.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("font-size: 14px; color: #666; margin: 50px;")
            self.cards_layout.addWidget(empty_label, 0, 0, 1, 3)  # Span 3 columns
            return
        
        # Display custom machines in cards
        columns = 3
        for i, machine in enumerate(custom_machines):
            row = i // columns
            col = i % columns
            
            card = CustomMachineCard(machine)
            card.edit_requested.connect(self.edit_machine)
            card.delete_requested.connect(self.delete_machine)
            card.picture_change_requested.connect(self.change_machine_picture)
            
            self.cards_layout.addWidget(card, row, col)
    
    def is_custom_machine(self, machine: Machine) -> bool:
        """Check if a machine is a custom machine."""
        return "custom" in machine.name.lower() or machine.picture == "custom_machine.png"
    
    def add_new_machine(self):
        """Open dialog to add a new custom machine."""
        dialog = CustomMachineDialog(self)
        dialog.machine_created.connect(self.on_machine_created)
        dialog.exec()
    
    def edit_machine(self, machine: Machine):
        """Open dialog to edit a custom machine."""
        dialog = CustomMachineDialog(self, machine_to_edit=machine)
        dialog.machine_created.connect(lambda new_machine: self.on_machine_edited(machine, new_machine))
        dialog.exec()
    
    def delete_machine(self, machine: Machine):
        """Delete a custom machine with confirmation."""
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Delete Custom Machine",
            f"Are you sure you want to delete '{machine.name}'?\\n\\n"
            f"This will remove any operations using this machine from all scenarios.\\n"
            f"This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.remove_machine_from_csv(machine):
                # Remove machine image if it exists
                if machine.picture and machine.picture != "custom_machine.png":
                    image_path = resource_path(f"STIR/images/custom_machines/{machine.picture}")
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                        except Exception as e:
                            print(f"Warning: Could not remove image file: {e}")
                
                # Refresh repository and UI
                self.machine_repo.reload_data()
                self.refresh_machines()
                
                QMessageBox.information(self, "Success", f"Machine '{machine.name}' has been deleted.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to delete machine '{machine.name}'.")
    
    def remove_machine_from_csv(self, machine: Machine) -> bool:
        """Remove a machine from the custom machines CSV file."""
        try:
            import csv
            import tempfile
            
            custom_machines_csv = resource_path("STIR/csv_custom_machines.csv")
            
            if not os.path.exists(custom_machines_csv):
                return False
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, newline='', encoding='utf-8')
            
            with open(custom_machines_csv, 'r', encoding='utf-8-sig') as input_file:
                reader = csv.DictReader(input_file)
                writer = csv.DictWriter(temp_file, fieldnames=reader.fieldnames)
                writer.writeheader()
                
                for row in reader:
                    # Skip the machine we want to delete
                    if row.get('name', '').strip() != machine.name:
                        writer.writerow(row)
            
            temp_file.close()
            
            # Replace original file with temp file
            shutil.move(temp_file.name, custom_machines_csv)
            
            return True
            
        except Exception as e:
            print(f"Error removing machine from CSV: {e}")
            # Clean up temp file if it exists
            try:
                if 'temp_file' in locals():
                    os.unlink(temp_file.name)
            except:
                pass
            return False
    
    def on_machine_created(self, machine: Machine):
        """Handle when a new machine is created."""
        self.machine_repo.reload_data()
        self.refresh_machines()
    
    def on_machine_edited(self, old_machine: Machine, new_machine: Machine):
        """Handle when a machine is edited."""
        # Remove the old machine
        if self.remove_machine_from_csv(old_machine):
            self.machine_repo.reload_data()
            self.refresh_machines()
        else:
            QMessageBox.critical(self, "Error", "Failed to update machine.")
    
    def change_machine_picture(self, machine: Machine):
        """Change the picture for a custom machine."""
        self.browse_and_set_picture(machine)
    
    def browse_and_set_picture(self, machine: Machine):
        """Browse for an image file and set it for the machine."""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Image files (*.png *.jpg *.jpeg *.bmp *.gif)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setWindowTitle("Select Machine Picture")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                source_path = selected_files[0]
                if self.copy_and_set_image(machine, source_path):
                    # Update the machine's picture in the CSV
                    self.update_machine_picture_in_csv(machine)
    
    def copy_and_set_image(self, machine: Machine, source_path: str) -> bool:
        """Copy image to custom machines folder and update machine."""
        try:
            # Get file extension
            _, ext = os.path.splitext(source_path)
            if not ext.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
                QMessageBox.warning(self, "Invalid File", "Please select a valid image file.")
                return False
            
            # Create new filename (machine name + extension)
            safe_name = "".join(c for c in machine.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')  # Replace spaces with underscores
            new_filename = f"{safe_name}{ext}"
            
            # Destination path
            dest_path = resource_path(f"STIR/images/custom_machines/{new_filename}")
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            
            # Update machine picture
            machine.picture = new_filename
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy image: {str(e)}")
            return False
    
    def update_machine_picture_in_csv(self, machine: Machine):
        """Update a machine's picture in the CSV file."""
        try:
            import csv
            import tempfile
            
            custom_machines_csv = resource_path("STIR/csv_custom_machines.csv")
            
            if not os.path.exists(custom_machines_csv):
                return False
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, newline='', encoding='utf-8')
            
            updated = False
            with open(custom_machines_csv, 'r', encoding='utf-8-sig') as input_file:
                reader = csv.DictReader(input_file)
                writer = csv.DictWriter(temp_file, fieldnames=reader.fieldnames)
                writer.writeheader()
                
                for row in reader:
                    # Update the machine's picture if this is the right machine
                    if row.get('name', '').strip() == machine.name:
                        row['picture'] = machine.picture
                        updated = True
                    writer.writerow(row)
            
            temp_file.close()
            
            if updated:
                # Replace original file with temp file
                shutil.move(temp_file.name, custom_machines_csv)
                
                # Refresh repository and UI
                self.machine_repo.reload_data()
                self.refresh_machines()
                
                QMessageBox.information(self, "Success", f"Picture updated for '{machine.name}'.")
                return True
            else:
                os.unlink(temp_file.name)
                return False
            
        except Exception as e:
            print(f"Error updating machine picture in CSV: {e}")
            # Clean up temp file if it exists
            try:
                if 'temp_file' in locals():
                    os.unlink(temp_file.name)
            except:
                pass
            return False
