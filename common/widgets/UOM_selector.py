"""
Contextual UOM Selector for the LORENZO POZZI Pesticide App.

This module provides a UOM selector that displays only relevant
units based on a specified context.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QDialog, QVBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QLineEdit
)
from PySide6.QtCore import Signal
from common.styles import get_medium_font

# Predefined UOM categories based on usage patterns from the app
UOM_CATEGORIES = {
    "application_rate": [
        "fl oz/100kg",  "fl oz/100m",  "fl oz/1000ft",  "fl oz/acre",  "fl oz/cwt",  "fl oz/ha",
        "g/100kg",      "g/100m",      "g/1000ft",      "g/acre",      "g/cwt",      "g/ha",
        "US gal/100kg", "US gal/100m", "US gal/1000ft", "US gal/acre", "US gal/cwt", "US gal/ha",
        "CA gal/100kg", "CA gal/100m", "CA gal/1000ft", "CA gal/acre", "CA gal/cwt", "CA gal/ha",
        "kg/100kg",     "kg/100m",     "kg/1000ft",     "kg/acre",     "kg/cwt",     "kg/ha",
        "l/100kg",      "l/100m",      "l/1000ft",      "l/acre",      "l/cwt",      "l/ha",
        "lb/100kg",     "lb/100m",     "lb/1000ft",     "lb/acre",     "lb/cwt",     "lb/ha",
        "ml/100kg",     "ml/100m",     "ml/1000ft",     "ml/acre",     "ml/cwt",     "ml/ha",
        "oz/100kg",     "oz/100m",     "oz/1000ft",     "oz/acre",     "oz/cwt",     "oz/ha",
        "pt/100kg",     "pt/100m",     "pt/1000ft",     "pt/acre",     "pt/cwt",     "pt/ha",
        "qt/100kg",     "qt/100m",     "qt/1000ft",     "qt/acre",     "qt/cwt",     "qt/ha"
    ],
    "length": [
        "ft", "inch", "m", "cm"
    ],
    "area": [
        "acre", "ha"
    ],
    "seeding_rate": [
        "cwt/acre", "lb/acre", "kg/acre", "kg/ha",  "lb/ha"
    ]
}

class UOMSelectionDialog(QDialog):
    """Dialog for selecting UOM with single-click selection."""
    
    def __init__(self, parent=None, uom_list=None, title="Select Unit of Measure"):
        super().__init__(parent)
        self.uom_list_data = uom_list or []
        self.selected_uom = None
        self.setWindowTitle(title)
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Select a unit of measure:")
        instructions.setFont(get_medium_font(bold=True))
        layout.addWidget(instructions)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search units...")
        self.search_box.setFont(get_medium_font())
        self.search_box.textChanged.connect(self.filter_uoms)
        layout.addWidget(self.search_box)
        
        # UOM list
        self.uom_list = QListWidget()
        self.uom_list.setFont(get_medium_font())
        self.uom_list.setStyleSheet("""
            QListWidget { 
                background-color: white; 
            }
            QListWidget::item:hover { 
                background-color: #ADD8E6; 
            }
        """)
        # Connect single click to accept
        self.uom_list.itemClicked.connect(self.on_item_clicked)
        
        # Populate list
        for uom in self.uom_list_data:
            item = QListWidgetItem(uom)
            self.uom_list.addItem(item)
        
        layout.addWidget(self.uom_list)
        
        # Size the dialog to fit contents
        self.adjustSize()
        
        # Set a reasonable minimum width
        min_width = 250
        if self.width() < min_width:
            self.setMinimumWidth(min_width)
    
    def filter_uoms(self, text):
        """Filter UOM list based on search text."""
        for i in range(self.uom_list.count()):
            item = self.uom_list.item(i)
            item.setHidden(not item.text().lower().startswith(text.lower()))
    
    def on_item_clicked(self, item):
        """Handle item click - select and close dialog."""
        self.selected_uom = item.text()
        self.accept()
    
    def get_selected_uom(self):
        """Get the selected UOM."""
        return self.selected_uom


class SmartUOMSelector(QWidget):
    """
    Context-aware UOM selector button that opens a dialog with a specific UOM list.
    
    This widget replaces the old SmartUOMSelector with a simpler, more reliable approach.
    """
    
    currentTextChanged = Signal(str)  # Emitted when UOM selection changes
    
    # Base state constant
    BASE_UOM_TEXT = "- Select unit -"
    
    def __init__(self, parent=None, uom_type=None):
        """
        Initialize the contextual UOM selector.
        
        Args:
            parent: Parent widget
            uom_type: Category of UOMs to show (e.g., "application_rate", "area")
        """
        super().__init__(parent)
        self.uom_type = uom_type or "application_rate"
        self.current_uom = self.BASE_UOM_TEXT  # Start in base state
        self.uom_list = UOM_CATEGORIES.get(self.uom_type, [])
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the widget UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main button showing current selection
        self.button = QPushButton(self.BASE_UOM_TEXT)
        self.button.setFont(get_medium_font())
        self.button.clicked.connect(self.open_dialog)
        self.button.setStyleSheet("UOM")
        layout.addWidget(self.button)
    
    def open_dialog(self):
        """Open the UOM selection dialog."""
        category_name = self.uom_type.replace("_", " ").title()
        dialog = UOMSelectionDialog(
            self, 
            self.uom_list, 
            f"Select {category_name} Unit"
        )
        if dialog.exec() == QDialog.Accepted:
            selected_uom = dialog.get_selected_uom()
            if selected_uom:
                self.setCurrentText(selected_uom)
    
    def currentText(self):
        """Get the currently selected UOM text."""
        return self.current_uom
    
    def setCurrentText(self, text):
        """Set the current UOM text."""
        if text != self.current_uom:
            old_uom = self.current_uom
            self.current_uom = text if text else self.BASE_UOM_TEXT
            self.button.setText(self.current_uom)
            
            # Only emit signal if changing from a real UOM (not from/to base state)
            # This prevents validation when transitioning through base state
            if (old_uom != self.BASE_UOM_TEXT and 
                self.current_uom != self.BASE_UOM_TEXT):
                self.currentTextChanged.emit(self.current_uom)
            elif (old_uom == self.BASE_UOM_TEXT and 
                  self.current_uom != self.BASE_UOM_TEXT):
                # Transitioning from base to real UOM - emit signal
                self.currentTextChanged.emit(self.current_uom)
    
    def isBaseState(self):
        """Check if the selector is in base state."""
        return self.current_uom == self.BASE_UOM_TEXT
    
    def resetToBase(self):
        """Reset the selector to base state without emitting signals."""
        self.current_uom = self.BASE_UOM_TEXT
        self.button.setText(self.BASE_UOM_TEXT)
    
    def addItem(self, text):
        """Add an item (for compatibility with QComboBox interface)."""
        # For backwards compatibility - no-op since we use predefined categories
        pass
    
    def addItems(self, texts):
        """Add multiple items (for compatibility with QComboBox interface)."""
        # For backwards compatibility - no-op since we use predefined categories
        pass
    
    def clear(self):
        """Clear selection (for compatibility with QComboBox interface)."""
        self.resetToBase()
    
    def findText(self, text):
        """Find text in available options (for compatibility with QComboBox interface)."""
        if text == self.BASE_UOM_TEXT:
            return 0
        return 0 if text in self.uom_list else -1