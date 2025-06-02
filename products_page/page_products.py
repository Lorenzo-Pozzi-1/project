"""
Main products page for the LORENZO POZZI Pesticide App.

This module defines the ProductsPage class which acts as a container for the
product listing and comparison tabs, coordinating between them.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from common import HeaderWithHomeButton, create_button, get_medium_font
from common.constants import get_margin_large, get_spacing_medium
from products_page.tab_products_list import ProductsListTab
from products_page.tab_products_comparison import ProductsComparisonTab
from data import ProductRepository

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
        main_layout.setContentsMargins(get_margin_large(), get_margin_large(), get_margin_large(), get_margin_large())
        main_layout.setSpacing(get_spacing_medium())
                
        # Header with back button
        header = HeaderWithHomeButton("Products List and Comparison")
        header.back_clicked.connect(lambda: self.parent.navigate_to_page(0))
        
        # Add Reset button directly to the header
        reset_button = create_button(text="Reset", callback=self.reset, style="white")
        reset_button.setMaximumWidth(150)
        
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
        self.tabs.setFont(get_medium_font())
        
        main_layout.addWidget(self.tabs)
    
    def reset(self):
        """Reset the page and refresh product data."""
        products_repo = ProductRepository.get_instance()
        if products_repo.refresh_from_csv():
            # Clear any selections
            self.selected_products = []
            
            # Reload the product data in the list tab
            self.products_list_tab.load_product_data()
            
            # Reset the filters
            self.products_list_tab.reset_filters()
            
            # Reset the comparison tab
            self.comparison_tab.clear_comparison()

            # Go back to products list tab if user is in comparison tab
            if self.tabs.currentIndex() == 1:
                self.tabs.setCurrentIndex(0)

    def refresh_product_data(self):
        """Refresh product data based on the updated filtered products."""
        # Clear any selections
        self.selected_products = []
        
        # Reload the product data in the list tab
        self.products_list_tab.load_product_data()
        
        # Reset the comparison tab
        self.comparison_tab.clear_comparison()