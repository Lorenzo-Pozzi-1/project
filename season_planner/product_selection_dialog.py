"""
Product selection dialog for the Season Planner.

This module provides a dialog for selecting products from the repository.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QLineEdit, QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, Signal
from common.styles import PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
from data.product_repository import ProductRepository

class ProductSelectionDialog(QDialog):
    """Dialog for selecting a product from the repository."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Control Product")
        self.selected_product = None
        self.setup_ui()
        self.load_products()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Set size
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search products...")
        self.search_input.textChanged.connect(self.filter_products)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Products list
        self.products_list = QListWidget()
        self.products_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.products_list)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        cancel_button.clicked.connect(self.reject)
        
        select_button = QPushButton("Select")
        select_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        select_button.clicked.connect(self.accept)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(select_button)
        
        layout.addLayout(buttons_layout)
    
    def load_products(self):
        """Load products from the repository."""
        products_repo = ProductRepository.get_instance()
        self.all_products = products_repo.get_filtered_products()
        
        # Clear and populate the list
        self.products_list.clear()
        for product in self.all_products:
            item = QListWidgetItem(product.display_name)
            item.setData(Qt.UserRole, product)  # Store the actual product object
            self.products_list.addItem(item)
    
    def filter_products(self):
        """Filter products based on search text."""
        search_text = self.search_input.text().lower()
        
        for i in range(self.products_list.count()):
            item = self.products_list.item(i)
            if not search_text or search_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def accept(self):
        """Handle OK button or double-click."""
        selected_items = self.products_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            self.selected_product = item.data(Qt.UserRole)
        
        super().accept()
    
    def get_selected_product(self):
        """Return the selected product."""
        return self.selected_product