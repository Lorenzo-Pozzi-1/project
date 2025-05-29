"""
Contextual UOM Selector for the LORENZO POZZI Pesticide App.

This module provides a UOM selector that displays only relevant
units based on a specified context.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QDialog, QVBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QDialogButtonBox, QLineEdit
)
from PySide6.QtCore import Signal
from common.styles import get_medium_font

# Predefined UOM categories based on usage patterns from the app
UOM_CATEGORIES = {
    "application_rate": [
        "fl oz/acre", "fl oz/cwt", "fl oz/1000ft", "g/cwt", "g/ha", 
        "gal/acre", "kg/ha", "l/ha", "lb/acre", "lb/cwt", "ml/100kg", 
        "ml/100m", "ml/acre", "ml/ha", "oz/acre", "oz/cwt", "pt/acre", "qt/acre"
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
    """Dialog for selecting UOM from a single categorized list."""
    
    def __init__(self, parent=None, uom_list=None, title="Select Unit of Measure"):
        super().__init__(parent)
        self.uom_list_data = uom_list or []
        self.selected_uom = None
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 500)
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
        self.uom_list.itemDoubleClicked.connect(self.accept)
        
        # Populate list
        for uom in self.uom_list_data:
            item = QListWidgetItem(uom)
            self.uom_list.addItem(item)
        
        layout.addWidget(self.uom_list)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initially disable OK button
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(False)
        self.uom_list.itemSelectionChanged.connect(self.on_uom_selection_changed)
    
    def filter_uoms(self, text):
        """Filter UOM list based on search text."""
        for i in range(self.uom_list.count()):
            item = self.uom_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def on_uom_selection_changed(self):
        """Handle UOM selection change."""
        has_selection = len(self.uom_list.selectedItems()) > 0
        self.ok_button.setEnabled(has_selection)
    
    def accept(self):
        """Accept dialog and store selected UOM."""
        selected_items = self.uom_list.selectedItems()
        if selected_items:
            self.selected_uom = selected_items[0].text()
        super().accept()
    
    def get_selected_uom(self):
        """Get the selected UOM."""
        return self.selected_uom


class SmartUOMSelector(QWidget):
    """
    Context-aware UOM selector button that opens a dialog with a specific UOM list.
    
    This widget replaces the old SmartUOMSelector with a simpler, more reliable approach.
    """
    
    currentTextChanged = Signal(str)  # Emitted when UOM selection changes
    
    def __init__(self, parent=None, uom_type=None):
        """
        Initialize the contextual UOM selector.
        
        Args:
            parent: Parent widget
            uom_type: Category of UOMs to show (e.g., "application_rate", "area")
        """
        super().__init__(parent)
        self.uom_type = uom_type or "application_rate"
        self.current_uom = ""
        self.uom_list = UOM_CATEGORIES.get(self.uom_type, [])
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the widget UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main button showing current selection
        self.button = QPushButton("-- Select unit --")
        self.button.setFont(get_medium_font())
        self.button.clicked.connect(self.open_dialog)
        self.button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 5px;
                border: 1px solid #ccc;
                background-color: white;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)
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
            self.current_uom = text
            self.button.setText(text if text else "-- Select unit --")
            if text:  # Only emit if not empty
                self.currentTextChanged.emit(text)
    
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
        self.setCurrentText("")
    
    def findText(self, text):
        """Find text in available options (for compatibility with QComboBox interface)."""
        return 0 if text in self.uom_list else -1