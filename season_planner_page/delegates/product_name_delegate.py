"""
Product Name Delegate for the Season Planner.

QStyledItemDelegate that provides product selection through an editable combobox
with autocomplete functionality, filtered by product type when specified.
Now displays suggestions in "Name - Method" format.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QComboBox, QCompleter, QMessageBox
from PySide6.QtCore import Qt
from data.repository_product import ProductRepository


class ProductNameDelegate(QStyledItemDelegate):
    """
    Delegate for product name selection using an editable combobox.
    
    Provides autocomplete functionality and filters products by type when
    a product type is selected in the same row. Displays suggestions in
    "Product Name - Application Method" format.
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
            QMessageBox.warning(self, "Error", f"Error loading products in ProductDelegate: {e}")
            self._all_products = []
    
    def _get_filtered_product_names(self, model, row):
        """
        Get product names filtered by the product type in the same row.
        
        Args:
            model: The table model
            row: Current row index
            
        Returns:
            list: Filtered product names in "Name - Method" format
        """
        try:
            # Get the product type from the same row using the model's column indexing method
            if hasattr(model, '_col_index'):
                type_col_index = model._col_index("Product Type")
                type_index = model.index(row, type_col_index)
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
            
            # Create display names in "Name - Method" format
            display_names = []
            
            for product in filtered_products:
                # Create display name in "Name - Method" format
                method = product.application_method or 'General'
                display_name = f"{product.product_name} - {method}"
                display_names.append(display_name)
            
            # Sort display names for consistent ordering
            display_names.sort()
            
            return display_names
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error filtering products by type: {e}")
            # Fallback to all products
            display_names = []
            
            for product in self._all_products:
                method = product.application_method or 'General'
                display_name = f"{product.product_name} - {method}"
                display_names.append(display_name)
            
            display_names.sort()
            return display_names
    
    def _get_product_mapping(self, model, row):
        """
        Get mapping from display names to product objects.
        
        Args:
            model: The table model
            row: Current row index
            
        Returns:
            dict: Maps "Name - Method" display strings to Product objects
        """
        try:
            # Get the product type from the same row
            if hasattr(model, '_col_index'):
                type_col_index = model._col_index("Product Type")
                type_index = model.index(row, type_col_index)
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
                filtered_products = self._all_products
            
            # Create mapping
            product_mapping = {}
            for product in filtered_products:
                method = product.application_method or 'General'
                display_name = f"{product.product_name} - {method}"
                product_mapping[display_name] = product
            
            return product_mapping
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error creating product mapping: {e}")
            # Fallback to all products
            product_mapping = {}
            for product in self._all_products:
                method = product.application_method or 'General'
                display_name = f"{product.product_name} - {method}"
                product_mapping[display_name] = product
            
            return product_mapping
    
    def createEditor(self, parent, option, index):
        """Create an editable QComboBox editor with autocomplete."""
        model = index.model()
        row = index.row()
        
        # Get filtered product names (now in "Name - Method" format)
        product_names = self._get_filtered_product_names(model, row)
        
        # Get product mapping for conversion between display and storage formats
        product_mapping = self._get_product_mapping(model, row)
        
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
        
        # Make the dropdown wider to show full product names with methods
        editor.view().setMinimumWidth(400)  # Increased width for "Name - Method"
        
        # Store the filtered products for validation (backward compatibility)
        editor._filtered_product_names = product_names
        # Store the product mapping for conversion
        editor._product_mapping = product_mapping
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
        if not isinstance(editor, QComboBox):
            return
        
        # Get the current product name from the model
        current_product_name = index.data(Qt.EditRole) or ""
        
        if not current_product_name:
            editor.setCurrentIndex(0)  # Select empty option
            return
        
        # Try to find the matching display name for this product
        product_mapping = getattr(editor, '_product_mapping', {})
        
        # Find the display name that corresponds to this product name
        matching_display_name = ""
        for display_name, product in product_mapping.items():
            if product.product_name == current_product_name:
                matching_display_name = display_name
                break
        
        if matching_display_name:
            # Try to find exact match in combo box
            index_in_combo = editor.findText(matching_display_name, Qt.MatchExactly)
            if index_in_combo >= 0:
                editor.setCurrentIndex(index_in_combo)
            else:
                editor.setEditText(matching_display_name)
        else:
            # Product not found in current filtered list, set as custom text
            editor.setEditText(current_product_name)
    
    def setModelData(self, editor, model, index):
        """Set the model data from the editor."""
        if not isinstance(editor, QComboBox):
            return
        
        # Get the current text (either selected or typed)
        display_text = editor.currentText().strip()
        
        if not display_text:
            # Empty selection
            model.setData(index, "", Qt.EditRole)
            return
        
        # Get the product mapping from the editor
        product_mapping = getattr(editor, '_product_mapping', {})
        
        # Check if this is a valid display name from our mapping
        if display_text in product_mapping:
            # Valid selection - extract the actual product name
            selected_product = product_mapping[display_text]
            product_name = selected_product.product_name
            
            # Set the product name in the model (not the display format)
            model.setData(index, product_name, Qt.EditRole)
            
            # Auto-populate other fields from the selected product
            if hasattr(model, 'auto_populate_from_product'):
                model.auto_populate_from_product(index.row(), product_name)
        else:
            # User typed something that's not in our list
            # This could be a partial match or a custom entry
            
            # Try to extract product name if it's in "Name - Method" format
            if " - " in display_text:
                potential_product_name = display_text.split(" - ")[0].strip()
            else:
                potential_product_name = display_text
            
            # Validate against our product database
            all_product_names = [p.product_name for p in self._all_products]
            
            if potential_product_name in all_product_names:
                # Valid product name, just not in current filtered view
                QMessageBox.warning(self, "Warning", f"Selected product '{potential_product_name}' doesn't match the selected product type")
                model.setData(index, potential_product_name, Qt.EditRole)
                
                # Auto-populate from product data
                if hasattr(model, 'auto_populate_from_product'):
                    model.auto_populate_from_product(index.row(), potential_product_name)
            else:
                # Backward compatibility: validate against filtered names (old behavior)
                filtered_names = getattr(editor, '_filtered_product_names', [])
                
                # Extract product names from display format for backward compatibility
                filtered_product_names_only = []
                for display_name in filtered_names:
                    if " - " in display_name:
                        product_only = display_name.split(" - ")[0].strip()
                        filtered_product_names_only.append(product_only)
                    else:
                        filtered_product_names_only.append(display_name)
                
                if potential_product_name not in filtered_product_names_only:
                    # Check if it exists in the full product list (original validation logic)
                    if potential_product_name in all_product_names:
                        # Product exists but is filtered out by type - allow it but show warning
                        QMessageBox.warning(self, "Warning", f"Selected product '{potential_product_name}' doesn't match the selected product type")
                    else:
                        # Product doesn't exist at all - still allow for import scenarios
                        QMessageBox.warning(self, "Warning", f"Product '{potential_product_name}' not found in database")

                # Set the product name (maintaining original behavior)
                model.setData(index, potential_product_name, Qt.EditRole)
                
                # Auto-populate if possible
                if hasattr(model, 'auto_populate_from_product'):
                    model.auto_populate_from_product(index.row(), potential_product_name)
    
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