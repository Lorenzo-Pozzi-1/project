"""
User Manual Dialog for the Pesticides App.

This module provides a comprehensive HTML-based user manual via system browser.
"""

import os
import webbrowser
import tempfile
import shutil
from PySide6.QtWidgets import QMessageBox
from common.utils import resource_path

def open_user_manual(parent=None):
    """Open the user manual in the system's default web browser."""
    try:
        # Get the manual HTML file path
        manual_path = resource_path("user_manual/user_manual.html")
        
        if not os.path.exists(manual_path):
            show_error_message(parent, "User manual file not found.")
            return False
            
        # Get the manual directory to copy associated assets
        manual_dir = os.path.dirname(manual_path)
        
        # Create a temporary directory for the manual
        temp_dir = tempfile.mkdtemp(prefix="pesticides_manual_")
        
        # Copy the entire manual directory to temp location
        # This ensures CSS, JS, images, and other assets are included
        temp_manual_dir = os.path.join(temp_dir, "manual")
        shutil.copytree(manual_dir, temp_manual_dir)
        
        # Path to the copied HTML file
        temp_manual_path = os.path.join(temp_manual_dir, "user_manual.html")
        
        # Open in browser
        webbrowser.open(f"file://{temp_manual_path}")
        
        return True
        
    except Exception as e:
        show_error_message(parent, f"Failed to open user manual: {str(e)}")
        return False

def show_error_message(parent, message):
    """Show error message to user."""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("User Manual Error")
    msg_box.setText(message)
    msg_box.exec()
