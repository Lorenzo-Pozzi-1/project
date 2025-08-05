"""
Product selection widgets for the LORENZO POZZI EIQ App.

This module provides improved product search with ranking and better suggestion formatting.
"""

from PySide6.QtCore import Qt, Signal, QStringListModel, QEvent
from PySide6.QtWidgets import (
    QComboBox, QCompleter, QFormLayout, QLineEdit, QVBoxLayout, 
    QWidget, QHBoxLayout, QLabel, QAbstractItemView, QMessageBox
)
from common.styles import get_medium_font, get_small_font
from common.widgets.header_frame_buttons import ContentFrame
from data.repository_product import ProductRepository


class RankedProductCompleter(QCompleter):
    """
    Custom completer that ranks search results by relevance.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_products = []
        self.product_display_map = {}  # Maps "Product - Method" to Product object
        self.all_display_items = []  # Store all display items
        
    def set_products(self, products):
        """Set the list of products for searching."""
        self.all_products = products
        self.product_display_map = {}
        
        # Create display strings and mapping
        self.all_display_items = []
        for product in products:
            display_name = f"{product.product_name} - {product.application_method or 'General'}"
            self.all_display_items.append(display_name)
            self.product_display_map[display_name] = product
        
        # Start with all items
        self._update_model_with_ranking("")
    
    def get_product_from_display(self, display_text):
        """Get the Product object from a display string."""
        return self.product_display_map.get(display_text)
    
    def splitPath(self, path):
        """Override to provide custom filtering with ranking."""
        search_term = path.lower().strip() if path else ""
        
        # Update model with ranked results
        self._update_model_with_ranking(search_term)
        
        # Return empty list to prevent Qt's default filtering
        # since we're handling filtering ourselves
        return []
    
    def _update_model_with_ranking(self, search_term):
        """Update the model with ranked results based on search term."""
        if not search_term:
            # Show all items when no search term
            ranked_results = sorted(self.all_display_items)
        else:
            # Rank and filter results
            ranked_results = self._rank_products(search_term)
        
        # Update model with ranked results
        model = QStringListModel(ranked_results, self)
        self.setModel(model)
    
    def _rank_products(self, search_term):
        """
        Rank products by search relevance.
        
        Args:
            search_term: The search string (already lowercase)
            
        Returns:
            List of display strings ranked by relevance
        """
        exact_matches = []
        starts_with_matches = []
        contains_matches = []
        
        for product in self.all_products:
            product_name_lower = product.product_name.lower()
            display_name = f"{product.product_name} - {product.application_method or 'General'}"
            
            # Check relevance level
            if product_name_lower == search_term:
                exact_matches.append(display_name)
            elif product_name_lower.startswith(search_term):
                starts_with_matches.append(display_name)
            elif search_term in product_name_lower:
                contains_matches.append(display_name)
        
        # Sort each category alphabetically for consistency
        exact_matches.sort()
        starts_with_matches.sort()
        contains_matches.sort()
        
        # Combine in priority order
        return exact_matches + starts_with_matches + contains_matches


class ProductSearchField(QWidget):
    """
    Search field with ranked popup suggestions for product selection.
    Uses the new "Product Name - Method" format and ranking system.
    """
    
    product_selected = Signal(str)  # Emits the product name (without method)
    
    def __init__(self, parent=None):
        """Initialize the product search field."""
        super().__init__(parent)
        self.all_products = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Search field
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Type to search products...")
        self.search_field.setFont(get_medium_font())
        layout.addWidget(self.search_field)
        
        # Create and configure completer
        self.completer = RankedProductCompleter(self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        # Removed maxVisibleItems limit as requested
        
        # Style and configure the popup
        popup = self.completer.popup()
        popup.setMaximumHeight(300)
        popup.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        popup.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)
        popup.setMinimumHeight(50)
        
        # Connect completer to search field
        self.search_field.setCompleter(self.completer)
        
        # Connect signals
        self.completer.activated.connect(self._on_item_selected)
        self.search_field.returnPressed.connect(self._on_return_pressed)
        self.search_field.textChanged.connect(self._on_text_changed)
        
        # Custom focus events to show suggestions on focus
        self.search_field.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Event filter to handle focus events for the search field."""
        if obj == self.search_field and event.type() == QEvent.Type.FocusIn:
            # Show all suggestions when field gets focus
            self.completer.complete()
        return super().eventFilter(obj, event)
    
    def _on_item_selected(self, display_text):
        """Handle selection of an item from the completer."""
        # Extract the product object from the display text
        product = self.completer.get_product_from_display(display_text)
        if product:
            # Set the display text in the field
            self.search_field.setText(display_text)
            # Emit just the product name for backward compatibility
            self.product_selected.emit(product.product_name)
    
    def _on_return_pressed(self):
        """Handle return key press in the search field."""
        display_text = self.search_field.text()
        if display_text:
            # Try to find exact match first
            product = self.completer.get_product_from_display(display_text)
            if product:
                self.product_selected.emit(product.product_name)
            else:
                # If no exact match, try to find by product name alone
                product_name = display_text.split(' - ')[0] if ' - ' in display_text else display_text
                self.product_selected.emit(product_name)
    
    def _on_text_changed(self, text):
        """Handle text changes to trigger ranked search."""
        # The RankedProductCompleter handles the ranking automatically
        # through its splitPath override
        pass
    
    def set_products(self, products):
        """Set the list of available products for search."""
        self.all_products = products
        self.completer.set_products(products)
        
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
        """Set the text in the search field. Handles both product names and display format."""
        if not value:
            self.search_field.setText("")
            return
            
        # If the value is just a product name, try to find the full display format
        if ' - ' not in value:
            # Look for a product with this name and use the first match
            for display_text, product in self.completer.product_display_map.items():
                if product.product_name == value:
                    self.search_field.setText(display_text)
                    return
        
        # If it's already in display format or no match found, use as-is
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
        self.setFont(get_medium_font())
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
            QMessageBox.warning(None, "Warning", f"Error loading product types: {e}")


class ProductSelectionWidget(QWidget):
    """Widget combining product type selection and ranked product search."""
    
    product_selected = Signal(str)
    
    def __init__(self, parent=None, orientation='vertical', style_config=None, show_labels=True):
        """Initialize the product selection widget with search capabilities."""
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
        
        # Choose layout based on orientation and label preferences
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
        """Update the product list based on selected product type with filtering."""
        try:
            products_repo = ProductRepository.get_instance()
            all_products = products_repo.get_filtered_products() or []
            
            # Filter products by type if not "All Types"
            product_type = self.type_selector.currentText()
            filtered_products = (
                all_products if product_type == "All Types" 
                else [p for p in all_products if p.product_type == product_type]
            )
            
            # Update search field with filtered products (now handles ranking internally)
            self.product_search.set_products(filtered_products)
            
        except Exception as e:
            QMessageBox.warning(None, "Warning", f"Error updating product list: {e}")
            self.product_search.set_products([])
    
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
        """Get the currently selected product name (without method suffix)."""
        display_text = self.product_search.text
        if ' - ' in display_text:
            return display_text.split(' - ')[0]
        return display_text
    
    def set_selected_product(self, product_name):
        """Set the selected product and automatically set its type."""
        if not product_name:
            self.product_search.text = ""
            return
            
        # First, try to find the product in the repository to get its type
        try:
            products_repo = ProductRepository.get_instance()
            filtered_products = products_repo.get_filtered_products()
            
            # Find the product to get its type
            product = None
            for filtered_product in filtered_products:
                if filtered_product.product_name == product_name:
                    product = filtered_product
                    break
            
            if product and product.product_type:
                # Set the type first (this will filter the product list)
                type_index = self.type_selector.findText(product.product_type)
                if type_index >= 0:
                    self.type_selector.setCurrentIndex(type_index)
                    # This triggers _update_product_list() which updates available products
        
        except Exception as e:
            QMessageBox.warning(None, "Warning", f"Could not set product type for {product_name}: {e}")

        # Set the product name (the search field will handle formatting)
        self.product_search.text = product_name