"""
Numeric Delegate for Season Planner V2.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QDoubleSpinBox
from PySide6.QtCore import Qt


class NumericDelegate(QStyledItemDelegate):
    """
    Numeric delegate that plays nicely with other delegates.
    
    Key fixes:
    - Simplified editor creation
    - No complex signal handling
    - Proper focus management
    """
    
    def __init__(self, parent=None, min_value=0.0, max_value=9999.99, decimals=2, suffix=""):
        """Initialize the numeric delegate."""
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value
        self.decimals = decimals
        self.suffix = suffix
    
    def createEditor(self, parent, option, index):
        """Create a QDoubleSpinBox editor."""
        editor = QDoubleSpinBox(parent)
        editor.setRange(self.min_value, self.max_value)
        editor.setDecimals(self.decimals)
        
        if self.suffix:
            editor.setSuffix(f" {self.suffix}")
        
        # Set reasonable step sizes
        if self.max_value <= 10:
            editor.setSingleStep(0.1)
        elif self.max_value <= 100:
            editor.setSingleStep(1.0)
        else:
            editor.setSingleStep(10.0)
        
        # IMPORTANT: Set focus policy to avoid conflicts
        editor.setFocusPolicy(Qt.StrongFocus)
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
        if not isinstance(editor, QDoubleSpinBox):
            return
            
        value = index.data(Qt.EditRole)
        if value is not None:
            try:
                editor.setValue(float(value))
            except (ValueError, TypeError):
                editor.setValue(0.0)
        else:
            editor.setValue(0.0)
    
    def setModelData(self, editor, model, index):
        """Set the model data from the editor."""
        if not isinstance(editor, QDoubleSpinBox):
            return
            
        # IMPORTANT: Explicitly interpret text before getting value
        editor.interpretText()
        value = editor.value()
        model.setData(index, value, Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update editor geometry to match the cell."""
        editor.setGeometry(option.rect)
    
    def displayText(self, value, locale):
        """Format the display text."""
        try:
            if value is None or value == "":
                return "0.00" if self.decimals > 0 else "0"
            
            num_value = float(value)
            if self.decimals == 0:
                text = str(int(num_value))
            else:
                text = f"{num_value:.{self.decimals}f}"
            
            if self.suffix:
                text += f" {self.suffix}"
            
            return text
        except (ValueError, TypeError):
            return "0.00" if self.decimals > 0 else "0"


class RateDelegate(NumericDelegate):
    """Rate delegate."""
    
    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            min_value=0.0,
            max_value=9999.99,
            decimals=2,
            suffix=""
        )


class AreaDelegate(NumericDelegate):
    """Area delegate."""
    
    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            min_value=0.0,
            max_value=9999.9,
            decimals=1,
            suffix=""
        )