"""
Products page for the Lorenzo Pozzi Pesticide App

This module defines the ProductsPage class which acts as a container for the
product listing and comparison tabs, using Qt's Model/View architecture.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget
from common.styles import MARGIN_LARGE, SPACING_MEDIUM, SECONDARY_BUTTON_STYLE
from common.widgets import HeaderWithBackButton
from products_table.products_list_tab import ProductsListTab
from products_table.products_comparison_tab import ProductsComparisonTab
from data.product_repository import ProductRepository

class ProductsPage(QWidget):
    """
    Products page for listing, filtering, and comparing products.
    
    This class acts as a container for the product listing and comparison tabs,
    and coordinates between them using Qt's Model/View architecture.
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
        
        # Create a horizontal layout for the header section
        header_layout = QHBoxLayout()
        
        # Header with back button
        header = HeaderWithBackButton("Products List and Comparison")
        header.back_clicked.connect(self.parent.go_home)
        
        # Add Reset button directly to the header
        reset_button = QPushButton("Reset")
        reset_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        reset_button.setMaximumWidth(150)
        reset_button.clicked.connect(self.reset)
        
        # Add the Reset button to the header's layout (right side)
        header.layout().addWidget(reset_button)
        
        # Add the full header to the main layout
        main_layout.addWidget(header)
        
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
    
    def reset(self):
        """Refresh product data from CSV file and reload the products list."""
        repo = ProductRepository.get_instance()
        if repo.refresh_from_csv():
            # Clear any selections
            self.selected_products = []
            
            # Reload the product data in the list tab
            self.products_list_tab.refresh_product_data()
            
            # Reset the comparison tab
            self.comparison_tab.clear_comparison()

    def refresh_product_data(self):
        """Refresh product data based on the updated filtered products."""
        # Clear any selections
        self.selected_products = []
        
        # Reload the product data in the list tab
        self.products_list_tab.refresh_product_data()
        
        # Reset the comparison tab
        self.comparison_tab.clear_comparison()