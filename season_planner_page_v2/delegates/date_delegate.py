"""
Date Delegate for Season Planner V2.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QValidator


class DateValidator(QValidator):
    """Simple validator for date strings - allows flexible formats."""
    
    def validate(self, input_str, pos):
        """Validate date input - very permissive to allow various formats."""
        # Allow empty string
        if not input_str.strip():
            return QValidator.Acceptable, input_str, pos
        
        # Allow any reasonable date-like string
        if len(input_str) <= 50:  # Reasonable length limit
            return QValidator.Acceptable, input_str, pos
        
        return QValidator.Invalid, input_str, pos


class DateDelegate(QStyledItemDelegate):
    """
    Date delegate for Season Planner V2.
    """
    
    def __init__(self, parent=None):
        """Initialize the date delegate."""
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        """Create a QLineEdit editor for date input."""
        editor = QLineEdit(parent)
        editor.setPlaceholderText("Enter date (e.g., '24/05/2024')")
        
        # Set validator
        validator = DateValidator()
        editor.setValidator(validator)
        
        # IMPORTANT: Don't install event filters or custom event handling
        # that might interfere with other delegates
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
        if not isinstance(editor, QLineEdit):
            return
            
        value = index.data(Qt.EditRole) or ""
        editor.setText(str(value))
    
    def setModelData(self, editor, model, index):
        """Set the model data from the editor."""
        if not isinstance(editor, QLineEdit):
            return
            
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
    
    # REMOVED: Custom event handling that might interfere with other delegates