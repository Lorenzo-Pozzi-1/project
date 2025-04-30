"""
Products page for the Lorenzo Pozzi Pesticide App

This module defines the ProductsPage class which acts as a container for the
product listing and comparison tabs, coordinating between them.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget
from PySide6.QtCore import Qt

from common.styles import MARGIN_LARGE, SPACING_MEDIUM, SECONDARY_BUTTON_STYLE
from common.widgets import HeaderWithBackButton
from products.products_list_tab import ProductsListTab
from products.products_comparison_tab import ProductsComparisonTab
from data.products_data import refresh_from_csv as refresh_products_from_csv


class ProductsPage(QWidget):
    """
    Products page for listing, filtering, and comparing products.
    
    This class acts as a container for the product listing and comparison tabs,
    and coordinates between them.
    """
    def __init__(self, parent=None):
        """Initialize the products page."""
        super().__init__(parent)
        self.parent = parent
        self.selected_products = []
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        main_layout.setSpacing(SPACING_MEDIUM)
        
        # Header with back button
        header = HeaderWithBackButton("Products List and Comparison")
        header.back_clicked.connect(self.parent.go_home)
        main_layout.addWidget(header)
        
        # Top controls area (Only Refresh Button)
        top_controls = QHBoxLayout()
        
        # Add Refresh from CSV button
        refresh_button = QPushButton("Refresh from CSV")
        refresh_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        refresh_button.setMaximumWidth(150)
        refresh_button.clicked.connect(self.refresh_from_csv)
        
        top_controls.addStretch(1)
        top_controls.addWidget(refresh_button)
        
        main_layout.addLayout(top_controls)
        
        # Create tabs for list and comparison
        self.tabs = QTabWidget()
        
        # Create the product list tab
        self.products_list_tab = ProductsListTab(self)
        
        # Create the comparison tab
        self.comparison_tab = ProductsComparisonTab(self)
        
        # Add tabs to the tab widget
        self.tabs.addTab(self.products_list_tab, "Products List")
        self.tabs.addTab(self.comparison_tab, "Comparison")
        
        main_layout.addWidget(self.tabs)
    
    def compare_selected_products(self):
        """Switch to comparison tab and update the comparison view."""
        # Pass the selected products to the comparison tab
        self.comparison_tab.update_comparison_view(self.selected_products)
        
        # Switch to comparison tab
        self.tabs.setCurrentIndex(1)
    
    def refresh_from_csv(self):
        """Refresh product data from CSV file and reload the products list."""
        if refresh_products_from_csv():
            # Clear any selections
            self.selected_products = []
            
            # Reload the product data in the list tab
            self.products_list_tab.load_product_data()
            
            # Reset the comparison tab
            self.comparison_tab.clear_comparison()
    
    def update_country_filter(self, country):
        """Update the country filter based on the selected country."""
        # This method can be called when the country changes in the HomePage
        # It will reload the product data with the new country filter
        self.products_list_tab.load_product_data()
        
        # Reset selections
        self.selected_products = []
        
        # Reset the comparison tab
        self.comparison_tab.clear_comparison()