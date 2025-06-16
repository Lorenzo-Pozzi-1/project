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

def create_user_manual_dialog(main_window):
    """
    Legacy compatibility function.
    Now opens manual in browser instead of creating dialog.
    """
    return open_user_manual(main_window)

# Alternative approach if you want the manual to persist in a user directory
def open_user_manual_persistent(parent=None):
    """
    Open user manual in browser using persistent user directory.
    Use this if you want the manual to remain accessible after app closes.
    """
    try:
        manual_path = resource_path("user_manual/user_manual.html")
        
        if not os.path.exists(manual_path):
            show_error_message(parent, "User manual file not found.")
            return False
            
        # Create manual directory in user's documents or app data
        import platform
        if platform.system() == "Windows":
            user_docs = os.path.expanduser("~/Documents")
            manual_dest_dir = os.path.join(user_docs, "Lorenzo Pozzi Pesticides App", "Manual")
        else:
            manual_dest_dir = os.path.expanduser("~/.pesticides_app/manual")
        
        # Ensure destination directory exists
        os.makedirs(manual_dest_dir, exist_ok=True)
        
        # Copy manual files to user directory
        manual_dir = os.path.dirname(manual_path)
        for item in os.listdir(manual_dir):
            src = os.path.join(manual_dir, item)
            dst = os.path.join(manual_dest_dir, item)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
            elif os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
        
        # Open the manual
        manual_file = os.path.join(manual_dest_dir, "user_manual.html")
        webbrowser.open(f"file://{manual_file}")
        
        return True
        
    except Exception as e:
        show_error_message(parent, f"Failed to open user manual: {str(e)}")
        return False