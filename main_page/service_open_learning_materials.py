"""
Learning Materials opener for the EIQ & STIR App.

This module opens the learning materials HTML file via system browser,
following the same pattern as the user manual.
"""

import os
import webbrowser
import tempfile
import shutil
from PySide6.QtWidgets import QMessageBox
from common.utils import resource_path

def open_learning_materials(parent=None):
    """Open the learning materials in the system's default web browser."""
    try:
        # Get the learning materials HTML file path
        materials_path = resource_path("main_page/learning_materials.html")
        
        if not os.path.exists(materials_path):
            show_error_message(parent, "Learning materials file not found.")
            return False
            
        # Get the materials directory to copy associated assets
        materials_dir = os.path.dirname(materials_path)
        
        # Create a temporary directory for the materials
        temp_dir = tempfile.mkdtemp(prefix="eiq_stir_materials_")
        
        # Copy the entire materials directory to temp location
        # This ensures CSS, JS, images, and other assets are included
        temp_materials_dir = os.path.join(temp_dir, "materials")
        shutil.copytree(materials_dir, temp_materials_dir)
        
        # Path to the copied HTML file
        temp_materials_path = os.path.join(temp_materials_dir, "learning_materials.html")
        
        # Open in browser
        webbrowser.open(f"file://{temp_materials_path}")
        
        return True
        
    except Exception as e:
        show_error_message(parent, f"Failed to open learning materials: {str(e)}")
        return False

def show_error_message(parent, message):
    """Show error message to user."""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("Learning Materials Error")
    msg_box.setText(message)
    msg_box.exec()