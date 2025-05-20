"""
Product selection widgets for the LORENZO POZZI Pesticide App.

This module provides reusable widgets for selecting pesticide products.
"""

from PySide6.QtCore import Qt, Signal, QStringListModel, QEvent
from PySide6.QtWidgets import QComboBox, QCompleter, QFormLayout, QLineEdit, QVBoxLayout, QWidget, QAbstractItemView
from common import get_body_font, SUGGESTIONS_LIST_STYLE, ContentFrame
from data.product_repository import ProductRepository


class ProductSearchField(QWidget):
    """
    A search field with filtered popup suggestions for product selection.
    Shows all available items when focused even without user input.
    """
    
    # Signal emitted when a product is selected
    product_selected = Signal(str)
    
    def __init__(self, parent=None):
        """
        Initialize the product search field.
        
        Args:
            parent (QWidget): Parent widget
        """
        super().__init__(parent)
        self.all_items = []
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Search field
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Type to search products...")
        self.search_field.setFont(get_body_font())
        layout.addWidget(self.search_field)
        
        # Create completer for suggestions
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        
        # Style the popup and configure its height behavior
        popup = self.completer.popup()
        popup.setStyleSheet(SUGGESTIONS_LIST_STYLE)
        
        # Set maximum height but allow it to resize based on content
        popup.setMaximumHeight(300)  # Maximum height (adjust as needed)
        popup.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        popup.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)
        popup.setMinimumHeight(50)  # Minimum height for very few items
        
        # Connect completer to search field
        self.search_field.setCompleter(self.completer)
        
        # Connect signals
        self.completer.activated.connect(self.on_item_selected)
        self.search_field.returnPressed.connect(self.on_return_pressed)
        
        # Custom focus events to show all suggestions on focus
        self.search_field.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """
        Event filter to handle focus events for the search field.
        Shows all suggestions when the field receives focus.
        """
        if obj == self.search_field and event.type() == QEvent.Type.FocusIn:
            # Show all items when the field gets focus
            self.completer.complete()
            return False  # Let the event continue to be processed
        return super().eventFilter(obj, event)
    
    def on_item_selected(self, text):
        """
        Handle selection of an item from the completer.
        
        Args:
            text (str): The selected text
        """
        self.search_field.setText(text)
        self.product_selected.emit(text)
    
    def on_return_pressed(self):
        """Handle return key press in the search field."""
        text = self.search_field.text()
        if text:
            self.product_selected.emit(text)
    
    def set_items(self, items):
        """
        Set the list of available items for autocomplete.
        
        Args:
            items (list): List of string items to show in suggestions
        """
        self.all_items = items
        model = QStringListModel(items, self.completer)
        self.completer.setModel(model)
        
        # Show popup if field is focused
        if self.search_field.hasFocus():
            self.completer.complete()
    
    def clear(self):
        """Clear the search field."""
        self.search_field.clear()
    
    def text(self):
        """Get the current text in the search field."""
        return self.search_field.text()
        
    def setText(self, text):
        """
        Set the text in the search field.
        
        Args:
            text (str): Text to set
        """
        self.search_field.setText(text)

class ProductTypeSelector(QComboBox):
    """
    A combo box specialized for selecting product types.
    
    This widget provides a combo box pre-populated with product types
    from the product repository.
    """
    
    def __init__(self, parent=None, include_all_option=True):
        """
        Initialize the product type selector.
        
        Args:
            parent (QWidget): Parent widget
            include_all_option (bool): Whether to include an "All Types" option
        """
        super().__init__(parent)
        self.include_all_option = include_all_option
        self.setFont(get_body_font())
        self.refresh_types()
    
    def refresh_types(self):
        """Refresh the list of product types from the repository."""
        # Store current selection if possible
        current_text = self.currentText()
        
        # Clear existing items
        self.clear()
        
        # Add "All Types" option if requested
        if self.include_all_option:
            self.addItem("All Types")
        
        # Get product types from repository
        try:
            products_repo = ProductRepository.get_instance()
            products = products_repo.get_filtered_products()
            
            if products:
                # Extract unique product types and sort them
                product_types = sorted(list(set(p.product_type for p in products if p.product_type)))
                self.addItems(product_types)
        except Exception as e:
            print(f"Error loading product types: {e}")
        
        # Try to restore previous selection
        if current_text:
            index = self.findText(current_text)
            if index >= 0:
                self.setCurrentIndex(index)

class ProductSelectionWidget(QWidget):
    """
    A widget combining product type selection and product search.
    
    This widget provides a unified interface for selecting a product by first
    selecting a product type and then searching for a specific product.
    """
    
    # Signal emitted when a product is selected
    product_selected = Signal(str)
    
    def __init__(self, parent=None):
        """Initialize the product selection widget."""
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Wrap the content in ContentFrame
        content_frame = ContentFrame()
        
        # Form layout for inputs
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Product type selector
        self.type_selector = ProductTypeSelector(self)
        self.type_selector.currentIndexChanged.connect(self.update_product_list)
        form_layout.addRow("Product Type:", self.type_selector)
        
        # Product search field
        self.product_search = ProductSearchField(self)
        self.product_search.product_selected.connect(self.on_product_selected)
        form_layout.addRow("Product:", self.product_search)
        
        content_frame.layout.addLayout(form_layout)
        layout.addWidget(content_frame)
    
    def update_product_list(self):
        """Update the product list based on selected product type."""
        try:
            # Get all products from repository
            products_repo = ProductRepository.get_instance()
            all_products = products_repo.get_filtered_products()
            
            if not all_products:
                self.product_search.set_items([])
                return
                
            # Get selected product type
            product_type = self.type_selector.currentText()
            
            # Filter products by type if not "All Types"
            if product_type == "All Types":
                filtered_products = all_products
            else:
                filtered_products = [p for p in all_products if p.product_type == product_type]
            
            # Update search field with filtered products
            product_names = [p.product_name for p in filtered_products]
            self.product_search.set_items(product_names)
            
        except Exception as e:
            print(f"Error updating product list: {e}")
            self.product_search.set_items([])
    
    def on_product_selected(self, product_name):
        """
        Handle product selection.
        
        Args:
            product_name (str): The selected product name
        """
        # Forward the selection signal
        self.product_selected.emit(product_name)
    
    def clear(self):
        """Clear the product selection."""
        self.product_search.clear()
    
    def refresh_data(self):
        """Refresh the widget with current data from repository."""
        # Refresh product types
        self.type_selector.refresh_types()
        
        # Update product list based on selected type
        self.update_product_list()
        
        # Clear product selection
        self.product_search.clear()
    
    def get_selected_product(self):
        """
        Get the currently selected product.
        
        Returns:
            str: The selected product name, or empty string if none selected
        """
        return self.product_search.text()
    
    def set_selected_product(self, product_name):
        """
        Set the selected product.
        
        Args:
            product_name (str): The product name to select
        """
        self.product_search.setText(product_name)