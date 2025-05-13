"""
Product selection widgets for the LORENZO POZZI Pesticide App.

This module provides reusable widgets for selecting pesticide products.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QListWidget, QFrame, QScrollArea, 
                              QApplication, QComboBox, QFormLayout)
from PySide6.QtCore import Qt, Signal, QTimer
from common.styles import get_body_font
from data.product_repository import ProductRepository


class ProductSearchField(QWidget):
    """
    A custom search field with popup suggestions for product selection.
    
    This widget provides a text input field with autocomplete suggestions
    that appear in a popup that's not constrained by parent containers.
    """
    
    # Signal emitted when a product is selected
    product_selected = Signal(str)
    
    def __init__(self, parent=None, min_popup_width=250):
        """
        Initialize the product search field.
        
        Args:
            parent (QWidget): Parent widget
            min_popup_width (int): Minimum width for the popup suggestions list
        """
        super().__init__(parent)
        self.all_items = []  # All available products
        self.filtered_items = []  # Filtered products based on search
        self.min_popup_width = min_popup_width
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
        self.search_field.textChanged.connect(self.update_suggestions)
        
        # Add focus events to show/hide suggestions
        self.search_field.focusInEvent = self.on_focus_in
        self.search_field.focusOutEvent = self.on_focus_out
        
        layout.addWidget(self.search_field)
        
        # Create suggestions popup as a child of the application's top-level window
        # so it can float over other widgets without being constrained
        self.suggestions_container = QFrame(QApplication.instance().activeWindow())
        self.suggestions_container.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.suggestions_container.setFrameStyle(QFrame.StyledPanel)
        self.suggestions_container.setStyleSheet("""
            QFrame {
                border: 1px solid #CCCCCC;
                background-color: white;
                border-radius: 3px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }
        """)
        
        # Scroll area for suggestions to handle large lists
        scroll_area = QScrollArea(self.suggestions_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Suggestions list
        self.suggestions_list = QListWidget()
        self.suggestions_list.setFrameStyle(QFrame.NoFrame)
        self.suggestions_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.suggestions_list.setStyleSheet("""
            QListWidget {
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #F5F5F5;
            }
            QListWidget::item:selected {
                background-color: #E0E0E0;
            }
        """)
        self.suggestions_list.itemClicked.connect(self.select_suggestion)
        scroll_area.setWidget(self.suggestions_list)
        
        # Add scroll area to suggestions container
        suggestions_layout = QVBoxLayout(self.suggestions_container)
        suggestions_layout.setContentsMargins(0, 0, 0, 0)
        suggestions_layout.addWidget(scroll_area)
        
        # Initially hide suggestions
        self.suggestions_container.setVisible(False)
    
    def on_focus_in(self, event):
        """Handle focus in event for the search field."""
        self.handle_focus(event, is_focused=True)

    def on_focus_out(self, event):
        """Handle focus out event for the search field."""
        self.handle_focus(event, is_focused=False)

    def handle_focus(self, event, is_focused):
        """
        Handle focus in/out events.
        
        Args:
            event (QFocusEvent): The focus event
            is_focused (bool): Whether the widget is gaining focus
        """
        if is_focused:
            QLineEdit.focusInEvent(self.search_field, event)
            if not self.search_field.text():
                self.filtered_items = self.all_items.copy()
                self.update_suggestions(self.search_field.text())
        else:
            QLineEdit.focusOutEvent(self.search_field, event)
            # Use a short delay before hiding to allow for clicking on suggestions
            QTimer.singleShot(200, lambda: self.suggestions_container.setVisible(False))
    
    def update_suggestions(self, text):
        """
        Update suggestions based on input text.
        
        Args:
            text (str): The search text to filter suggestions
        """
        # Clear selection when search text changes
        self.suggestions_list.clearSelection()
        
        if not text:
            # Show all items when text is cleared
            self.filtered_items = self.all_items.copy()
        else:
            # Filter items based on search text
            self.filtered_items = [
                item for item in self.all_items 
                if text.lower() in item.lower()
            ]
        
        # Update suggestions list
        self.suggestions_list.clear()
        self.suggestions_list.addItems(self.filtered_items)
        
        # Show suggestions if there are any matches
        self.update_suggestions_visibility()
    
    def update_suggestions_visibility(self):
        """Show or hide the suggestions container based on available items."""
        has_suggestions = len(self.filtered_items) > 0
        
        if has_suggestions:
            # Calculate the position of the dropdown relative to the search field
            global_pos = self.search_field.mapToGlobal(self.search_field.rect().bottomLeft())
            
            # Set the size and position of the suggestions container
            width = max(self.search_field.width(), self.min_popup_width)
            item_height = self.suggestions_list.sizeHintForRow(0) if self.filtered_items else 20
            num_visible_items = min(8, len(self.filtered_items))
            height = item_height * num_visible_items + 10
            
            self.suggestions_container.setFixedSize(width, height)
            self.suggestions_container.move(global_pos)
            self.suggestions_container.setVisible(True)
            self.suggestions_container.raise_()
        else:
            self.suggestions_container.setVisible(False)
    
    def select_suggestion(self, item):
        """
        Handle selection of a suggestion.
        
        Args:
            item (QListWidgetItem): The selected item
        """
        selected_text = item.text()
        self.search_field.setText(selected_text)
        self.suggestions_container.setVisible(False)
        self.product_selected.emit(selected_text)
    
    def set_items(self, items):
        """
        Set the full list of available items.
        
        Args:
            items (list): List of string items to show in suggestions
        """
        self.all_items = items
        self.update_suggestions(self.search_field.text())
    
    def clear(self):
        """Clear the search field and hide suggestions."""
        self.search_field.clear()
        self.suggestions_container.setVisible(False)
        
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
        
        layout.addLayout(form_layout)
    
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