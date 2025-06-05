"""
Method Delegate for the Season Planner.

QStyledItemDelegate that provides application method input with common suggestions.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QComboBox
from PySide6.QtCore import Qt


class MethodDelegate(QStyledItemDelegate):
    """
    Delegate for application method input.
    
    Provides a QComboBox with common application methods but allows
    custom text entry for flexibility.
    """
    
    # Common application methods
    COMMON_METHODS = [
        "",  # Empty option
        "Ground",
        "Aerial", 
        "Broadcast",
        "Band",
        "Foliar",
        "Seed Treatment",
        "In-Furrow",
        "Chemigation",
        "Fertigation",
        "Soil Incorporation"
    ]
    
    def __init__(self, parent=None):
        """Initialize the method delegate."""
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        """Create a QComboBox editor with common methods."""
        editor = QComboBox(parent)
        
        # Make it editable so users can enter custom methods
        editor.setEditable(True)
        editor.setInsertPolicy(QComboBox.NoInsert)
        
        # Add common methods
        editor.addItems(self.COMMON_METHODS)
        
        # Set placeholder text on the line edit
        editor.lineEdit().setPlaceholderText("Select or enter application method")
        
        # DON'T show popup here - do it in updateEditorGeometry after geometry is set
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
        value = index.data(Qt.EditRole) or ""
        
        # Try to find the value in the combo box
        index_in_combo = editor.findText(str(value))
        if index_in_combo >= 0:
            editor.setCurrentIndex(index_in_combo)
        else:
            # Set custom text
            editor.setEditText(str(value))
    
    def setModelData(self, editor, model, index):
        """Set the model data from the editor."""
        value = editor.currentText().strip()
        model.setData(index, value, Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update editor geometry to match the cell and position popup correctly."""
        # Set the editor geometry to match the cell
        editor.setGeometry(option.rect)
        
        # IMPORTANT: Delay the popup show to ensure geometry is set first
        if isinstance(editor, QComboBox):
            # Use QTimer to show popup after geometry is properly set
            from PySide6.QtCore import QTimer
            QTimer.singleShot(10, editor.showPopup)
    
    def displayText(self, value, locale):
        """Format the display text."""
        if value is None or str(value).strip() == "":
            return ""
        return str(value)