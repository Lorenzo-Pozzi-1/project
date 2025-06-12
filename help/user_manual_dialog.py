"""
User Manual Dialog for the Pesticides App.

This module provides a comprehensive HTML-based user manual that replaces
the current help overlay system.
"""

import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from common import resource_path

class UserManualDialog(QDialog):
    """Comprehensive user manual dialog with HTML content and navigation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_manual_content()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Pesticides App - User Manual")
        self.setModal(True)
        
        # Set a large default size instead of maximizing
        # This allows normal window controls while still being large
        self.resize(1000, 500)
        
        # Enable maximize and close window buttons
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        
        # Web view for HTML content
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
    def load_manual_content(self):
        """Load the HTML manual content."""
        manual_path = resource_path("help/user_manual.html")
        if os.path.exists(manual_path):
            self.web_view.load(QUrl.fromLocalFile(manual_path))


def create_user_manual_dialog(main_window):
    """Create and return a user manual dialog for the main window."""
    return UserManualDialog(main_window)
