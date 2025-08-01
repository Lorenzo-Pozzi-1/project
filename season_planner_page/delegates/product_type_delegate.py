"""
Product Type Delegate for the Season Planner.

QStyledItemDelegate that provides product type selection.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QComboBox, QMessageBox
from PySide6.QtCore import Qt
from data.repository_product import ProductRepository


class ProductTypeDelegate(QStyledItemDelegate):
    """
    Delegate for product type input.
    
    Provides a QComboBox with common product types from the database
    but allows custom text entry for flexibility.
    """
    
    def __init__(self, parent=None):
        """Initialize the product type delegate."""
        super().__init__(parent)
        self._product_types = []
        self._load_product_types()
    
    def _load_product_types(self):
        """Load unique product types from repository."""
        try:
            products_repo = ProductRepository.get_instance()
            filtered_products = products_repo.get_filtered_products()
            
            # Extract unique product types
            types = set()
            for product in filtered_products:
                if product.product_type:
                    types.add(product.product_type)
            
            self._product_types = sorted(list(types))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading product types: {e}")
            self._product_types = []
    
    def createEditor(self, parent, option, index):
        """Create a QComboBox editor with common product types."""
        editor = QComboBox(parent)
        
        # Make it editable so users can enter custom types
        editor.setEditable(True)
        editor.setInsertPolicy(QComboBox.NoInsert)
        
        # Add empty option first, then product types
        editor.addItem("")  # Empty option
        editor.addItems(self._product_types)
        
        # Set placeholder text on the line edit
        editor.lineEdit().setPlaceholderText("Select or enter product type")
        
        # DON'T show popup here - do it in updateEditorGeometry after geometry is set
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
        if not isinstance(editor, QComboBox):
            return
            
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
        if not isinstance(editor, QComboBox):
            return
            
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
    
    def refresh_product_types(self):
        """Refresh the product types list from repository."""
        self._load_product_types()