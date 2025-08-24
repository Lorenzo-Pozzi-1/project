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
from ..data.model_custom_machine import CustomMachine
from ..data.repository_custom_machine import CustomMachineRepository
from .new_custom_machine_dialog import NewCustomMachineDialog
from common.utils import resource_path


class CustomMachineCard(QFrame):
    """Card widget for displaying custom machine information."""
    
    edit_requested = Signal(CustomMachine)
    delete_requested = Signal(CustomMachine)
    
    def __init__(self, machine: CustomMachine, parent=None):
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
            custom_image_path = resource_path(f"STIR/data/images/custom_machines/{self.machine.picture}")
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
        
        # Machine details in a formatted way - custom machines have multiple tools
        active_tools = self.machine.get_active_tools()
        
        if active_tools:
            # Get aggregated values
            depths = [tool.depth for tool in active_tools]
            areas = [tool.surface_area_disturbed for tool in active_tools]
            tool_names = [tool.name for tool in active_tools]
            
            max_depth = max(depths)
            max_area = max(areas)
            has_pto = any(tool.rotates for tool in active_tools)
            avg_tillage_factor = sum(tool.tillage_type_factor for tool in active_tools) / len(active_tools)
            
            details_text = f"""<b>Speed:</b> {self.machine.speed} {self.machine.speed_uom}<br>
<b>Tools:</b> {', '.join(tool_names[:3])}{'...' if len(tool_names) > 3 else ''}<br>
<b>Max Depth:</b> {max_depth} cm<br>
<b>Max Area Disturbed:</b> {max_area}%<br>
<b>PTO operated:</b> {'Yes' if has_pto else 'No'}<br>
<b>Avg Tillage Factor:</b> {avg_tillage_factor:.2f}"""
        else:
            details_text = f"""<b>Speed:</b> {self.machine.speed} {self.machine.speed_uom}<br>
<b>Tools:</b> No tools configured<br>
<b>Status:</b> Configuration incomplete"""
        
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
            custom_machines_csv = resource_path("STIR/data/csv_custom_machines.csv")
            
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
        self.machine_repo = CustomMachineRepository()
        
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
        custom_machines = self.machine_repo.load_all()
        
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
    
    def is_custom_machine(self, machine: CustomMachine) -> bool:
        """Check if a machine is a custom machine."""
        # All machines in this dialog are custom machines now
        return True
    
    def add_new_machine(self):
        """Open dialog to add a new custom machine."""
        dialog = NewCustomMachineDialog(self)
        dialog.machine_created.connect(self.on_machine_created)
        dialog.exec()
    
    def edit_machine(self, machine: CustomMachine):
        """Open dialog to edit a custom machine."""
        dialog = NewCustomMachineDialog(self, machine_to_edit=machine)
        dialog.machine_created.connect(lambda new_machine: self.on_machine_edited(machine, new_machine))
        dialog.exec()
    
    def delete_machine(self, machine: CustomMachine):
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
                    image_path = resource_path(f"STIR/data/images/custom_machines/{machine.picture}")
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                        except Exception as e:
                            print(f"Warning: Could not remove image file: {e}")
                
                # Refresh UI
                self.refresh_machines()
            else:
                QMessageBox.critical(self, "Error", f"Failed to delete machine '{machine.name}'.")
    
    def remove_machine_from_csv(self, machine: CustomMachine) -> bool:
        """Remove a machine from the custom machines CSV file."""
        try:
            return self.machine_repo.delete_machine(machine.name)
        except Exception as e:
            print(f"Error removing machine from CSV: {e}")
            return False
    
    def on_machine_created(self, machine: CustomMachine):
        """Handle when a new machine is created."""
        self.refresh_machines()
    
    def on_machine_edited(self, old_machine: CustomMachine, new_machine: CustomMachine):
        """Handle when a machine is edited."""
        # Handle picture renaming if machine name changed
        if old_machine.name != new_machine.name and new_machine.picture:
            self.rename_machine_picture(old_machine, new_machine)
        
        self.refresh_machines()
    
    def generate_safe_filename(self, machine_name: str, extension: str) -> str:
        """Generate a safe filename based on machine name and extension."""
        safe_name = "".join(c for c in machine_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')  # Replace spaces with underscores
        return f"{safe_name}{extension}"
    
    def rename_machine_picture(self, old_machine: CustomMachine, new_machine: CustomMachine):
        """Rename a machine's picture file to match the new machine name."""
        try:
            # Get old picture path
            old_picture_path = resource_path(f"STIR/data/images/custom_machines/{old_machine.picture}")
            
            if not os.path.exists(old_picture_path):
                return  # Picture doesn't exist, nothing to rename
            
            # Get file extension from old picture
            _, ext = os.path.splitext(old_machine.picture)
            
            # Create new filename based on new machine name
            new_filename = self.generate_safe_filename(new_machine.name, ext)
            
            # New picture path
            new_picture_path = resource_path(f"STIR/data/images/custom_machines/{new_filename}")
            
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
    
    def browse_and_set_picture(self, machine: CustomMachine):
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
    
    def copy_and_set_image(self, machine: CustomMachine, source_path: str) -> bool:
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
            dest_path = resource_path(f"STIR/data/images/custom_machines/{new_filename}")
            
            # Remove old picture if it exists and is different from new one
            if machine.picture and machine.picture != new_filename:
                old_picture_path = resource_path(f"STIR/data/images/custom_machines/{machine.picture}")
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
    
    def update_machine_picture_in_csv(self, machine: CustomMachine):
        """Update a machine's picture in the CSV file."""
        try:
            # Update the machine in the repository
            success = self.machine_repo.update_machine(machine.name, machine)
            
            if success:
                self.refresh_machines()
                QMessageBox.information(self, "Success", f"Picture updated for '{machine.name}'.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to update picture for '{machine.name}'.")
                
        except Exception as e:
            print(f"Error updating machine picture: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update picture for '{machine.name}': {str(e)}")

    def get_machine_notes_from_csv(self, machine_name: str) -> str:
        """Get notes for a machine from the CSV file."""
        try:
            import csv
            custom_machines_csv = resource_path("STIR/data/csv_custom_machines.csv")
            
            if not os.path.exists(custom_machines_csv):
                return ""
            
            with open(custom_machines_csv, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('name', '').strip() == machine_name:
                        return row.get('notes', '').strip()
            
            return ""
            
        except Exception as e:
            print(f"Error reading notes from CSV: {e}")
            return ""
