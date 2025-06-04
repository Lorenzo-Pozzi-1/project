"""
Date Delegate for Season Planner V2.

QStyledItemDelegate that provides date input with validation.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QLineEdit
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QValidator


class DateValidator(QValidator):
    """Simple validator for date strings - allows flexible formats."""
    
    def validate(self, input_str, pos):
        """Validate date input - very permissive to allow various formats."""
        # Allow empty string
        if not input_str.strip():
            return QValidator.Acceptable, input_str, pos
        
        # Allow any reasonable date-like string
        # This is intentionally permissive since users might enter descriptions
        if len(input_str) <= 50:  # Reasonable length limit
            return QValidator.Acceptable, input_str, pos
        
        return QValidator.Invalid, input_str, pos


class DateDelegate(QStyledItemDelegate):
    """
    Delegate for date input.
    
    Provides a QLineEdit with placeholder text and basic validation.
    Allows flexible date formats and descriptive text.
    """
    
    def __init__(self, parent=None):
        """Initialize the date delegate."""
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        """Create a QLineEdit editor for date input."""
        editor = QLineEdit(parent)
        editor.setPlaceholderText("Enter date or description (e.g., '24/05/2024' or 'Pre-planting')")
        
        # Set validator
        validator = DateValidator()
        editor.setValidator(validator)
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
        value = index.data(Qt.EditRole) or ""
        editor.setText(str(value))
    
    def setModelData(self, editor, model, index):
        """Set the model data from the editor."""
        value = editor.text().strip()
        model.setData(index, value, Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update editor geometry to match the cell."""
        editor.setGeometry(option.rect)
    
    def displayText(self, value, locale):
        """Format the display text."""
        if value is None or str(value).strip() == "":
            return ""
        return str(value)