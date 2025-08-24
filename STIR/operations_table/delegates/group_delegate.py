"""
Group Selection Delegate for STIR Operations Table.

Provides a QComboBox for selecting operation groups (pre-plant, in-season, harvest).
"""

from PySide6.QtWidgets import QStyledItemDelegate, QComboBox
from PySide6.QtCore import Qt


class GroupSelectionDelegate(QStyledItemDelegate):
    """Custom delegate for operation group selection with QComboBox."""
    
    # Predefined operation groups
    OPERATION_GROUPS = [
        "pre-plant",
        "in-season", 
        "harvest"
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        """Create a QComboBox editor with available operation groups."""
        editor = QComboBox(parent)
        editor.setEditable(False)
        
        # Add all operation groups
        for group in self.OPERATION_GROUPS:
            editor.addItem(group)
        
        # Schedule the dropdown to open after the editor is fully created
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, editor.showPopup)
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
        current_text = index.model().data(index, Qt.EditRole) or "pre-plant"
        
        # Find the index of the current text
        index_pos = editor.findText(current_text)
        if index_pos >= 0:
            editor.setCurrentIndex(index_pos)
        else:
            # Default to pre-plant if not found
            editor.setCurrentIndex(0)
    
    def setModelData(self, editor, model, index):
        """Set the model data from the editor."""
        selected_group = editor.currentText()
        model.setData(index, selected_group, Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update the editor geometry."""
        editor.setGeometry(option.rect)
    
    def displayText(self, value, locale):
        """Format the display text."""
        if value is None or str(value).strip() == "":
            return "pre-plant"
        return str(value)