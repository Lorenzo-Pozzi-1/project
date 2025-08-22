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
                               QFrame, QSizePolicy)
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
    
    def __init__(self, machine: Machine, parent=None):
        super().__init__(parent)
        self.machine = machine
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the card UI."""
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet("""
            QFrame {
                border: none;
                border-radius: 8px;
                background-color: white;
                margin: 5px;
            }
        """)
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Image section (left side)
        image_label = QLabel()
        image_label.setFixedSize(200, 160)  # Larger image size
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("border: none; border-radius: 4px; background-color: #f9f9f9;")
        
        # Try to load machine image
        if self.machine.picture:
            # Try custom machines folder first
            custom_image_path = resource_path(f"STIR/images/custom_machines/{self.machine.picture}")
            if os.path.exists(custom_image_path):
                pixmap = QPixmap(custom_image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(190, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_label.setPixmap(scaled_pixmap)
                else:
                    image_label.setText("Missing\npicture")
            else:
                image_label.setText("Missing\npicture")
        else:
            image_label.setText("No\npicture")
            
        main_layout.addWidget(image_label)
        
        # Right side container with two columns
        right_container = QHBoxLayout()
        right_container.setSpacing(15)
        
        # Left column: Machine details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(4)
        
        # Machine name
        name_label = QLabel(self.machine.name)
        name_label.setAlignment(Qt.AlignLeft)
        name_label.setStyleSheet("font-weight: bold; font-size: 20px; color: #333; margin-bottom:4px;")
        name_label.setWordWrap(True)
        details_layout.addWidget(name_label)
        
        # Machine details in a formatted way
        details_text = f"""<b>Speed:</b> {self.machine.speed} {self.machine.speed_uom}<br>
<b>Depth:</b> {self.machine.depth} {self.machine.depth_uom}<br>
<b>PTO operated:</b> {'Yes' if self.machine.rotates else 'No'}<br>
<b>Surface Area Disturbed:</b> {self.machine.surface_area_disturbed}%<br>
<b>Tillage Factor:</b> {self.machine.tillage_type_factor}"""
        
        details_label = QLabel(details_text)
        details_label.setAlignment(Qt.AlignLeft)
        details_label.setStyleSheet("font-size: 14px; color: #666; line-height: 1.5;")
        details_label.setWordWrap(True)
        details_layout.addWidget(details_label)
        
        # Add stretch to push buttons to bottom
        details_layout.addStretch()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)
        
        edit_button = QPushButton("Edit")
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: bold;
                font-size: 13px;
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
                padding: 8px 14px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        delete_button.clicked.connect(lambda: self.delete_requested.emit(self.machine))
        
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addStretch()  # Push buttons to the left
        
        details_layout.addLayout(buttons_layout)
        
        # Add details column to right container
        right_container.addLayout(details_layout)
        
        # Right column: Notes section
        notes_layout = QVBoxLayout()
        notes_layout.setSpacing(4)
        
        # Notes header
        notes_header = QLabel("Notes")
        notes_header.setStyleSheet("font-weight: bold; font-size: 16px; color: #333; margin-bottom: 4px;")
        notes_layout.addWidget(notes_header)
        
        # Notes content (read from CSV)
        notes_text = self.get_machine_notes()
        notes_label = QLabel(notes_text if notes_text else "No notes")
        notes_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        notes_label.setStyleSheet("font-size: 13px; color: #666; line-height: 1.4; background-color: #f9f9f9; padding: 8px; border-radius: 4px;")
        notes_label.setWordWrap(True)
        notes_label.setMaximumHeight(140)  # Limit height to match details section
        notes_layout.addWidget(notes_label)
        
        # Add stretch to align with details column
        notes_layout.addStretch()
        
        # Add notes column to right container
        right_container.addLayout(notes_layout)
        
        # Add the complete right container to main layout
        main_layout.addLayout(right_container)
    
    def get_machine_notes(self) -> str:
        """Get notes for this machine from the custom machines CSV."""
        try:
            import csv
            custom_machines_csv = resource_path("STIR/csv_custom_machines.csv")
            
            if not os.path.exists(custom_machines_csv):
                return ""
            
            with open(custom_machines_csv, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('name', '').strip() == self.machine.name:
                        return row.get('notes', '').strip()
            
            return ""
            
        except Exception as e:
            print(f"Error reading notes from CSV: {e}")
            return ""


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
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Widget to contain the cards in vertical layout
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background-color: transparent;")
        self.cards_layout = QVBoxLayout(self.scroll_widget)
        self.cards_layout.setSpacing(5)
        self.cards_layout.setContentsMargins(15, 15, 15, 15)
        
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)
        
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
        
        # Sort custom machines alphabetically by name
        custom_machines.sort(key=lambda machine: machine.name.lower())
        
        if not custom_machines:
            # Show empty state
            empty_label = QLabel("No custom machines found.\\nClick 'Add New Custom Machine' to create one.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("font-size: 14px; color: #666; margin: 50px;")
            self.cards_layout.addWidget(empty_label)
            return

        # Display custom machines in vertical stack
        for machine in custom_machines:
            card = CustomMachineCard(machine)
            card.edit_requested.connect(self.edit_machine)
            card.delete_requested.connect(self.delete_machine)
            
            self.cards_layout.addWidget(card)
        
        # Add stretch at the end to push cards to the top
        self.cards_layout.addStretch()
        
        # Reset scroll position to top
        self.scroll_area.verticalScrollBar().setValue(0)
    
    def is_custom_machine(self, machine: Machine) -> bool:
        """Check if a machine is a custom machine."""
        import csv
        import os
        from common.utils import resource_path
        
        # Check if machine exists in custom machines CSV
        custom_machines_csv = resource_path("STIR/csv_custom_machines.csv")
        if os.path.exists(custom_machines_csv):
            try:
                with open(custom_machines_csv, 'r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row.get('name', '').strip() == machine.name:
                            return True
            except Exception:
                # If there's an error reading the file, fall back to heuristic
                pass
        
        # If not found in custom machines CSV, check if it exists in standard machines CSV
        # If it's not in standard machines either, it might be a custom machine
        standard_machines_csv = resource_path("STIR/csv_machines.csv")
        if os.path.exists(standard_machines_csv):
            try:
                with open(standard_machines_csv, 'r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row.get('name', '').strip() == machine.name:
                            return False  # Found in standard machines, so it's not custom
            except Exception:
                # If there's an error reading the file, fall back to heuristic
                pass
        
        # Fallback heuristic if CSV reading fails
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
            f"Are you sure you want to delete '{machine.name}'?\n\n"
            f"This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.remove_machine_from_csv(machine):
                # Remove machine image if it exists
                if machine.picture:
                    image_path = resource_path(f"STIR/images/custom_machines/{machine.picture}")
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                        except Exception as e:
                            print(f"Warning: Could not remove image file: {e}")
                
                # Refresh repository and UI
                self.machine_repo.reload_data()
                self.refresh_machines()
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
        # Create a temporary object with all the machine details
        temp_machine_data = {
            'name': new_machine.name,
            'depth': new_machine.depth,
            'depth_uom': new_machine.depth_uom,
            'speed': new_machine.speed,
            'speed_uom': new_machine.speed_uom,
            'surface_area_disturbed': new_machine.surface_area_disturbed,
            'tillage_type_factor': new_machine.tillage_type_factor,
            'picture': new_machine.picture,
            'rotates': new_machine.rotates
        }
        
        # Check if machine name changed and handle picture renaming
        if old_machine.name != new_machine.name and new_machine.picture:
            self.rename_machine_picture(old_machine, new_machine)
            # Update the picture name in temp data after renaming
            temp_machine_data['picture'] = new_machine.picture
        
        # Step 1: Remove the old machine first
        if not self.remove_machine_from_csv(old_machine):
            QMessageBox.critical(self, "Error", "Failed to remove old machine data.")
            return
            
        # Step 2: Add the new machine with updated data
        if self.add_machine_to_csv(temp_machine_data):
            self.machine_repo.reload_data()
            self.refresh_machines()
        else:
            # If adding the new machine fails, we have a problem - try to restore the old one
            QMessageBox.critical(self, "Error", "Failed to save updated machine. Please check your data and try again.")
            # Attempt to restore old machine (best effort)
            self.restore_machine_after_failure(old_machine)
    
    def add_machine_to_csv(self, machine_data: dict) -> bool:
        """Add a machine to the CSV file using dictionary data."""
        try:
            import csv
            
            custom_machines_csv = resource_path("STIR/csv_custom_machines.csv")
            
            # Create file with headers if it doesn't exist
            if not os.path.exists(custom_machines_csv):
                with open(custom_machines_csv, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['name', 'rotates', 'depth', 'depth_uom', 'speed', 'speed_uom', 
                                   'surface_area_disturbed', 'tillage_type_factor', 'picture', 'notes'])
            
            # Append the machine
            with open(custom_machines_csv, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    machine_data['name'],
                    'TRUE' if machine_data['rotates'] else 'FALSE',
                    machine_data['depth'],
                    machine_data['depth_uom'],
                    machine_data['speed'],
                    machine_data['speed_uom'],
                    machine_data['surface_area_disturbed'],
                    machine_data['tillage_type_factor'],
                    machine_data['picture'],
                    machine_data.get('notes', '')  # Include notes, default to empty string
                ])
            
            return True
            
        except Exception as e:
            print(f"Error adding machine to CSV: {e}")
            return False
    
    def restore_machine_after_failure(self, old_machine: Machine):
        """Attempt to restore a machine after a failed edit operation."""
        try:
            restore_data = {
                'name': old_machine.name,
                'depth': old_machine.depth,
                'depth_uom': old_machine.depth_uom,
                'speed': old_machine.speed,
                'speed_uom': old_machine.speed_uom,
                'surface_area_disturbed': old_machine.surface_area_disturbed,
                'tillage_type_factor': old_machine.tillage_type_factor,
                'picture': old_machine.picture,
                'rotates': old_machine.rotates
            }
            
            if self.add_machine_to_csv(restore_data):
                self.machine_repo.reload_data()
                self.refresh_machines()
                QMessageBox.warning(self, "Warning", 
                                  f"Edit failed, but original machine '{old_machine.name}' has been restored.")
            else:
                QMessageBox.critical(self, "Critical Error", 
                                   f"Failed to restore machine '{old_machine.name}'. Please manually re-add it.")
                
        except Exception as e:
            print(f"Error restoring machine: {e}")
            QMessageBox.critical(self, "Critical Error", 
                               f"Failed to restore machine '{old_machine.name}'. Please manually re-add it.")
    
    def generate_safe_filename(self, machine_name: str, extension: str) -> str:
        """Generate a safe filename based on machine name and extension."""
        safe_name = "".join(c for c in machine_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')  # Replace spaces with underscores
        return f"{safe_name}{extension}"
    
    def rename_machine_picture(self, old_machine: Machine, new_machine: Machine):
        """Rename a machine's picture file to match the new machine name."""
        try:
            # Get old picture path
            old_picture_path = resource_path(f"STIR/images/custom_machines/{old_machine.picture}")
            
            if not os.path.exists(old_picture_path):
                return  # Picture doesn't exist, nothing to rename
            
            # Get file extension from old picture
            _, ext = os.path.splitext(old_machine.picture)
            
            # Create new filename based on new machine name
            new_filename = self.generate_safe_filename(new_machine.name, ext)
            
            # New picture path
            new_picture_path = resource_path(f"STIR/images/custom_machines/{new_filename}")
            
            # Only rename if the new filename is different
            if new_filename != old_machine.picture:
                # Check if target filename already exists
                if os.path.exists(new_picture_path):
                    # If target exists, remove it first (overwrite)
                    os.remove(new_picture_path)
                
                # Rename the file
                os.rename(old_picture_path, new_picture_path)
            
            # Update the new machine's picture property
            new_machine.picture = new_filename
            
        except Exception as e:
            print(f"Warning: Could not rename picture file: {e}")
            # If renaming fails, keep the old picture name
            new_machine.picture = old_machine.picture
    
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
            
            # Create new filename using helper method
            new_filename = self.generate_safe_filename(machine.name, ext)
            
            # Destination path
            dest_path = resource_path(f"STIR/images/custom_machines/{new_filename}")
            
            # Remove old picture if it exists and is different from new one
            if machine.picture and machine.picture != new_filename:
                old_picture_path = resource_path(f"STIR/images/custom_machines/{machine.picture}")
                if os.path.exists(old_picture_path):
                    try:
                        os.remove(old_picture_path)
                    except Exception as e:
                        print(f"Warning: Could not remove old picture file: {e}")
            
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
