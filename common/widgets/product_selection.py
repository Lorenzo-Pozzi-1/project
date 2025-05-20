"""
Product selection widgets for the LORENZO POZZI Pesticide App.

This module provides reusable widgets for selecting pesticide products.
"""

from PySide6.QtCore import Qt, Signal, QStringListModel, QEvent
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (
    QComboBox, QCompleter, QFormLayout, QLineEdit, QVBoxLayout, 
    QWidget, QHBoxLayout, QLabel, QAbstractItemView
)
from common.styles import get_body_font, SUGGESTIONS_LIST_STYLE, get_small_font
from common.widgets.widgets import ContentFrame
from data import ProductRepository


class ProductSearchField(QWidget):
    """
    A search field with filtered popup suggestions for product selection.
    Shows all available items when focused even without user input.
    """
    
    product_selected = Signal(str)
    
    def __init__(self, parent=None):
        """Initialize the product search field."""
        super().__init__(parent)
        self.all_items = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Search field
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Type to search products...")
        self.search_field.setFont(get_body_font())
        layout.addWidget(self.search_field)
        
        # Create and configure completer for suggestions
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        
        # Style and configure the popup
        popup = self.completer.popup()
        popup.setStyleSheet(SUGGESTIONS_LIST_STYLE)
        popup.setMaximumHeight(300)
        popup.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        popup.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)
        popup.setMinimumHeight(50)
        
        # Connect completer to search field
        self.search_field.setCompleter(self.completer)
        
        # Connect signals
        self.completer.activated.connect(self._on_item_selected)
        self.search_field.returnPressed.connect(self._on_return_pressed)
        
        # Custom focus events to show all suggestions on focus
        self.search_field.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Event filter to handle focus events for the search field."""
        if obj == self.search_field and event.type() == QEvent.Type.FocusIn:
            self.completer.complete()
        return super().eventFilter(obj, event)
    
    def _on_item_selected(self, text):
        """Handle selection of an item from the completer."""
        self.search_field.setText(text)
        self.product_selected.emit(text)
    
    def _on_return_pressed(self):
        """Handle return key press in the search field."""
        text = self.search_field.text()
        if text:
            self.product_selected.emit(text)
    
    def set_items(self, items):
        """Set the list of available items for autocomplete."""
        self.all_items = items
        model = QStringListModel(items, self.completer)
        self.completer.setModel(model)
        
        # Show popup if field is focused
        if self.search_field.hasFocus():
            self.completer.complete()
    
    # Property-based API
    @property
    def text(self):
        """Get the current text in the search field."""
        return self.search_field.text()
        
    @text.setter
    def text(self, value):
        """Set the text in the search field."""
        self.search_field.setText(value)
    
    def clear(self):
        """Clear the search field."""
        self.search_field.clear()


class ProductTypeSelector(QComboBox):
    """A combo box specialized for selecting product types."""
    
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
                product_types = sorted(list({p.product_type for p in products if p.product_type}))
                self.addItems(product_types)
                
                # Try to restore previous selection
                if current_text:
                    index = self.findText(current_text)
                    if index >= 0:
                        self.setCurrentIndex(index)
        except Exception as e:
            print(f"Error loading product types: {e}")


class ProductSelectionWidget(QWidget):
    """A widget combining product type selection and product search."""
    
    product_selected = Signal(str)
    
    def __init__(self, parent=None, orientation='vertical', style_config=None, show_labels=True):
        """Initialize the product selection widget with flexible layout."""
        super().__init__(parent)
        self._orientation = orientation
        self._style_config = style_config or {}
        self._show_labels = show_labels
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Create content frame
        content_frame = ContentFrame()
        
        # Product type selector
        self.type_selector = ProductTypeSelector(self)
        self.type_selector.currentIndexChanged.connect(self._update_product_list)
        
        # Apply font styling
        type_font = get_small_font()
        self.type_selector.setFont(type_font)
        
        # Product search field
        self.product_search = ProductSearchField(self)
        self.product_search.product_selected.connect(self._on_product_selected)
        self.product_search.search_field.setFont(type_font)
        
        # Create labels if enabled
        labels = {}
        if self._show_labels:
            labels["type"] = QLabel("Product Type:")
            labels["type"].setFont(type_font)
            labels["product"] = QLabel("Product:")
            labels["product"].setFont(type_font)
        
        # Choose layout based on orientation and label settings
        if self._orientation == 'horizontal':
            self._setup_horizontal_layout(content_frame.layout, labels)
        else:
            self._setup_vertical_layout(content_frame.layout, labels)
        
        layout.addWidget(content_frame)
    
    def _setup_horizontal_layout(self, parent_layout, labels):
        """Set up horizontal layout."""
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setSpacing(20)
        
        # Create vertical layouts for each label-field pair
        type_layout = QVBoxLayout()
        if self._show_labels:
            type_layout.addWidget(labels["type"])
        type_layout.addWidget(self.type_selector)
        
        product_layout = QVBoxLayout()
        if self._show_labels:
            product_layout.addWidget(labels["product"])
        product_layout.addWidget(self.product_search)
        
        horizontal_layout.addLayout(type_layout)
        horizontal_layout.addLayout(product_layout)
        parent_layout.addLayout(horizontal_layout)
    
    def _setup_vertical_layout(self, parent_layout, labels):
        """Set up vertical layout."""
        if self._show_labels:
            form_layout = QFormLayout()
            form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
            form_layout.addRow(labels["type"], self.type_selector)
            form_layout.addRow(labels["product"], self.product_search)
            parent_layout.addLayout(form_layout)
        else:
            vertical_layout = QVBoxLayout()
            vertical_layout.addWidget(self.type_selector)
            vertical_layout.addWidget(self.product_search)
            parent_layout.addLayout(vertical_layout)
    
    def _update_product_list(self):
        """Update the product list based on selected product type."""
        try:
            products_repo = ProductRepository.get_instance()
            all_products = products_repo.get_filtered_products() or []
            
            # Filter products by type if not "All Types"
            product_type = self.type_selector.currentText()
            filtered_products = (
                all_products if product_type == "All Types" 
                else [p for p in all_products if p.product_type == product_type]
            )
            
            # Update search field with filtered products
            product_names = [p.product_name for p in filtered_products]
            self.product_search.set_items(product_names)
            
        except Exception as e:
            print(f"Error updating product list: {e}")
            self.product_search.set_items([])
    
    def _on_product_selected(self, product_name):
        """Handle product selection."""
        self.product_selected.emit(product_name)
    
    def clear(self):
        """Clear the product selection."""
        self.product_search.clear()
    
    def refresh_data(self):
        """Refresh the widget with current data from repository."""
        self.type_selector.refresh_types()
        self._update_product_list()
        self.product_search.clear()
    
    def get_selected_product(self):
        """Get the currently selected product."""
        return self.product_search.text
    
    def set_selected_product(self, product_name):
        """Set the selected product."""
        self.product_search.text = product_name