"""
Numeric Delegate for STIR Operations Table.

Provides specialized numeric input handling for different column types:
- Depth: decimal values (e.g., 15.5)
- Speed: decimal values (e.g., 8.0)
- Area Disturbed: percentage values (0-100)
- % Field Tilled: percentage values (0-100)
- Number of Passes: integer values (1, 2, 3, etc.)
"""

from PySide6.QtWidgets import QStyledItemDelegate, QDoubleSpinBox, QSpinBox
from PySide6.QtCore import Qt
from typing import Optional


class NumericDelegate(QStyledItemDelegate):
    """Custom delegate for numeric input with type-specific validation."""
    
    # Column types definition
    COLUMN_TYPES = {
        2: "depth",          # Depth column - decimal
        3: "speed",          # Speed column - decimal  
        4: "area",           # Area Disturbed column - percentage
        5: "field_tilled",   # % Field Tilled column - percentage
        6: "passes"          # Number of Passes column - integer
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        """Create appropriate numeric editor based on column type."""
        column = index.column()
        column_type = self.COLUMN_TYPES.get(column)
        
        if column_type == "passes":
            # Integer spinner for number of passes
            editor = QSpinBox(parent)
            editor.setMinimum(1)
            editor.setMaximum(10)  # Reasonable maximum for field passes
            editor.setSingleStep(1)
            editor.setValue(1)
            
        elif column_type in ["area", "field_tilled"]:
            # Percentage spinner for area disturbed and field tilled
            editor = QDoubleSpinBox(parent)
            editor.setMinimum(0.0)
            editor.setMaximum(100.0)
            editor.setSingleStep(1.0)
            editor.setDecimals(0)  # Whole percentages
            editor.setSuffix("%")
            editor.setValue(100.0)
            
        elif column_type in ["depth", "speed"]:
            # Decimal spinner for depth and speed
            editor = QDoubleSpinBox(parent)
            editor.setMinimum(0.0)
            editor.setMaximum(999.9)  # Reasonable maximum
            editor.setSingleStep(0.1)
            editor.setDecimals(1)
            editor.setValue(0.0)
            
            # No suffix needed since UOM is now in column header
        
        else:
            # Fallback to default editor
            return super().createEditor(parent, option, index)
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
        column = index.column()
        column_type = self.COLUMN_TYPES.get(column)
        
        # Get the current value from the model
        current_text = index.model().data(index, Qt.EditRole) or ""
        
        if column_type == "passes":
            # Parse integer value
            try:
                value = int(current_text) if current_text else 1
                editor.setValue(value)
            except ValueError:
                editor.setValue(1)
                
        elif column_type in ["area", "field_tilled"]:
            # Parse percentage value (remove % symbol if present)
            try:
                value_str = current_text.replace("%", "").strip()
                value = float(value_str) if value_str else 100.0
                editor.setValue(value)
            except ValueError:
                editor.setValue(100.0)
                
        elif column_type in ["depth", "speed"]:
            # Parse decimal value
            try:
                value = float(current_text) if current_text else 0.0
                editor.setValue(value)
            except ValueError:
                editor.setValue(0.0)
    
    def setModelData(self, editor, model, index):
        """Set the model data from the editor."""
        column = index.column()
        column_type = self.COLUMN_TYPES.get(column)
        
        if column_type == "passes":
            # Integer value
            value = editor.value()
            model.setData(index, str(value), Qt.EditRole)
            
        elif column_type in ["area", "field_tilled"]:
            # Percentage value (store without % symbol in model)
            value = editor.value()
            model.setData(index, f"{value:.0f}%", Qt.EditRole)
            
        elif column_type in ["depth", "speed"]:
            # Decimal value
            value = editor.value()
            model.setData(index, f"{value:.1f}", Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update the editor geometry."""
        editor.setGeometry(option.rect)
    
    def displayText(self, value, locale):
        """Format the display text based on column type."""
        # This method can be used to format how values are displayed
        # when not being edited
        return str(value) if value is not None else ""
