"""
Numeric Delegate for Season Planner V2.

QStyledItemDelegate that provides numeric input with appropriate ranges and validation.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QDoubleSpinBox
from PySide6.QtCore import Qt


class NumericDelegate(QStyledItemDelegate):
    """
    Delegate for numeric input with validation.
    
    Provides QDoubleSpinBox editors with appropriate ranges for different
    types of numeric data (rates, areas, etc.).
    """
    
    def __init__(self, parent=None, min_value=0.0, max_value=9999.99, decimals=2, suffix=""):
        """
        Initialize the numeric delegate.
        
        Args:
            parent: Parent widget
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            decimals: Number of decimal places
            suffix: Optional suffix to display (e.g., "kg")
        """
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
        
        # Set some reasonable step sizes based on the range
        if self.max_value <= 10:
            editor.setSingleStep(0.1)
        elif self.max_value <= 100:
            editor.setSingleStep(1.0)
        else:
            editor.setSingleStep(10.0)
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
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
    """Specialized numeric delegate for application rates."""
    
    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            min_value=0.0,
            max_value=9999.99,
            decimals=2,
            suffix=""
        )


class AreaDelegate(NumericDelegate):
    """Specialized numeric delegate for areas."""
    
    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            min_value=0.0,
            max_value=9999.9,
            decimals=1,
            suffix=""
        )