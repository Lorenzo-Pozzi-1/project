"""
Fixed Product Delegate for Season Planner V2.

QStyledItemDelegate that provides product selection through an editable combobox
with autocomplete functionality, filtered by product type when specified.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QComboBox, QCompleter
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtGui import QStandardItemModel, QStandardItem
from data import ProductRepository


class ProductNameDelegate(QStyledItemDelegate):
    """
    Fixed delegate for product selection using an editable combobox.
    
    Provides autocomplete functionality and filters products by type when
    a product type is selected in the same row.
    """
    
    def __init__(self, parent=None):
        """Initialize the product delegate."""
        super().__init__(parent)
        self._all_products = []
        self._load_products()
    
    def _load_products(self):
        """Load all products from repository."""
        try:
            products_repo = ProductRepository.get_instance()
            filtered_products = products_repo.get_filtered_products()
            self._all_products = filtered_products
        except Exception as e:
            print(f"Error loading products in ProductDelegate: {e}")
            self._all_products = []
    
    def _get_filtered_product_names(self, model, row):
        """
        Get product names filtered by the product type in the same row.
        
        Args:
            model: The table model
            row: Current row index
            
        Returns:
            list: Filtered product names
        """
        try:
            # Get the product type from the same row
            if hasattr(model, 'COL_PRODUCT_TYPE'):
                type_index = model.index(row, model.COL_PRODUCT_TYPE)
                selected_type = model.data(type_index, Qt.EditRole) or ""
                selected_type = selected_type.strip()
            else:
                selected_type = ""
            
            # Filter products by type if specified
            if selected_type:
                filtered_products = [
                    p for p in self._all_products 
                    if p.product_type == selected_type
                ]
            else:
                # No type specified - show all products
                filtered_products = self._all_products
            
            # Return sorted product names
            return sorted([p.product_name for p in filtered_products])
            
        except Exception as e:
            print(f"Error filtering products by type: {e}")
            # Fallback to all products
            return sorted([p.product_name for p in self._all_products])
    
    def createEditor(self, parent, option, index):
        """Create an editable QComboBox editor with autocomplete."""
        model = index.model()
        row = index.row()
        
        # Get filtered product names based on the selected type
        product_names = self._get_filtered_product_names(model, row)
        
        editor = QComboBox(parent)
        editor.setEditable(True)
        editor.setInsertPolicy(QComboBox.NoInsert)
        
        # Add empty option first, then filtered products
        editor.addItem("")  # Empty option for clearing selection
        editor.addItems(product_names)
        
        # Set up autocomplete
        completer = QCompleter(product_names, editor)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        editor.setCompleter(completer)
        
        # Set placeholder text
        editor.lineEdit().setPlaceholderText("Type to search products...")
        
        # Make the dropdown wider to show full product names
        editor.view().setMinimumWidth(300)
        
        # Store the filtered products for validation
        editor._filtered_product_names = product_names
        
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
        
        # Validate that the product exists in the filtered list if not empty
        if value:
            filtered_names = getattr(editor, '_filtered_product_names', [])
            if value not in filtered_names:
                # Product doesn't exist in filtered list
                # Check if it exists in the full product list
                all_names = [p.product_name for p in self._all_products]
                if value in all_names:
                    # Product exists but is filtered out by type - allow it but show warning
                    print(f"Warning: Selected product '{value}' doesn't match the selected product type")
                else:
                    # Product doesn't exist at all - still allow for import scenarios
                    print(f"Warning: Product '{value}' not found in database")
        
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