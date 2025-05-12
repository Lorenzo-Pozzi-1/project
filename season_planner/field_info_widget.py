"""
Field information widget for the Season Planner.

This module provides a widget for editing field information.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit
from PySide6.QtCore import Signal
from common.styles import get_body_font

class FieldInfoWidget(QWidget):
    """Widget for displaying and editing field information."""
    
    info_changed = Signal()  # Signal when any field is changed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Grower field
        layout.addWidget(QLabel("Grower:"))
        self.grower_edit = QLineEdit()
        self.grower_edit.setFont(get_body_font())
        self.grower_edit.textChanged.connect(self.info_changed.emit)
        layout.addWidget(self.grower_edit)
        
        # Field name
        layout.addWidget(QLabel("Field:"))
        self.field_edit = QLineEdit()
        self.field_edit.setFont(get_body_font())
        self.field_edit.textChanged.connect(self.info_changed.emit)
        layout.addWidget(self.field_edit)
        
        # Variety
        layout.addWidget(QLabel("Variety:"))
        self.variety_edit = QLineEdit()
        self.variety_edit.setFont(get_body_font())
        self.variety_edit.textChanged.connect(self.info_changed.emit)
        layout.addWidget(self.variety_edit)
        
        # Add spacer for future expansion (...)
        layout.addWidget(QLabel("..."))
        layout.addStretch(1)
    
    def get_field_info(self):
        """Get the current field information."""
        return {
            "grower": self.grower_edit.text(),
            "field": self.field_edit.text(),
            "variety": self.variety_edit.text()
        }
    
    def set_field_info(self, grower="", field="", variety=""):
        """Set the field information values."""
        self.grower_edit.setText(grower)
        self.field_edit.setText(field)
        self.variety_edit.setText(variety)