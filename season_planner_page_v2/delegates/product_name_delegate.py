"""
Fixed Product Delegate for Season Planner V2.

QStyledItemDelegate that provides product selection through an editable combobox
with autocomplete functionality instead of modal dialogs.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QComboBox, QCompleter
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtGui import QStandardItemModel, QStandardItem
from data import ProductRepository


class ProductNameDelegate(QStyledItemDelegate):
    """
    Fixed delegate for product selection using an editable combobox.
    
    Provides autocomplete functionality and integrates properly with Qt's
    editing system without modal dialogs.
    """
    
    def __init__(self, parent=None):
        """Initialize the product delegate."""
        super().__init__(parent)
        self._product_names = []
        self._load_products()
    
    def _load_products(self):
        """Load product names from repository."""
        try:
            products_repo = ProductRepository.get_instance()
            filtered_products = products_repo.get_filtered_products()
            self._product_names = sorted([p.product_name for p in filtered_products])
        except Exception as e:
            print(f"Error loading products in ProductDelegate: {e}")
            self._product_names = []
    
    def createEditor(self, parent, option, index):
        """Create an editable QComboBox editor with autocomplete."""
        editor = QComboBox(parent)
        editor.setEditable(True)
        editor.setInsertPolicy(QComboBox.NoInsert)
        
        # Add empty option first, then all products
        editor.addItem("")  # Empty option for clearing selection
        editor.addItems(self._product_names)
        
        # Set up autocomplete
        completer = QCompleter(self._product_names, editor)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        editor.setCompleter(completer)
        
        # Set placeholder text
        editor.lineEdit().setPlaceholderText("Type to search products...")
        
        # Make the dropdown wider to show full product names
        editor.view().setMinimumWidth(300)
        
        # DON'T show popup here - do it in updateEditorGeometry after geometry is set
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
        if not isinstance(editor, QComboBox):
            return
        
        value = index.data(Qt.EditRole) or ""
        
        # Try to find exact match first
        index_in_combo = editor.findText(value, Qt.MatchExactly)
        if index_in_combo >= 0:
            editor.setCurrentIndex(index_in_combo)
        else:
            # Set custom text
            editor.setEditText(value)
    
    def setModelData(self, editor, model, index):
        """Set the model data from the editor."""
        if not isinstance(editor, QComboBox):
            return
        
        # Get the current text (either selected or typed)
        value = editor.currentText().strip()
        
        # Validate that the product exists if not empty
        if value and value not in self._product_names:
            # Product doesn't exist in repository - still allow it for import scenarios
            # but it will show validation warnings in the model
            pass
        
        # Set the product name
        model.setData(index, value, Qt.EditRole)
        
        # Auto-populate rate and UOM from product label data if they're currently empty/default
        if value and hasattr(model, 'auto_populate_from_product'):
            model.auto_populate_from_product(index.row(), value)
    
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
    
    def refresh_products(self):
        """Refresh the product list from repository."""
        self._load_products()