"""
Products list tab for the LORENZO POZZI Pesticide App with improved component architecture.

This module defines the ProductsListTab class that provides product listing
and filtering functionality using a table-based view.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from common import ContentFrame, create_button
from data import ProductRepository
from products_page.widgets.filter_row import FilterRowContainer
from products_page.widgets.products_table import ProductTable


class ProductsListTab(QWidget):
    """
    Products list tab for displaying and filtering products.
    
    This tab provides a searchable table of products with filtering capabilities,
    allowing the user to select products for comparison.
    """
    
    def __init__(self, parent=None):
        """Initialize the products list tab."""
        super().__init__(parent)
        self.parent = parent
        self.all_products = []
        self.setup_ui()
        self.load_product_data()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # Filter section
        filter_frame = ContentFrame()
        filter_layout = QVBoxLayout()
        
        # Use the FilterRowContainer widget
        self.filter_container = FilterRowContainer()
        self.filter_container.filters_changed.connect(self.apply_filters)
        filter_layout.addWidget(self.filter_container)
        
        # Add layout to the frame
        filter_frame.layout.addLayout(filter_layout)
        main_layout.addWidget(filter_frame)
        
        # Products table
        table_frame = ContentFrame()
        table_layout = QVBoxLayout()
        
        self.products_table = ProductTable()
        self.products_table.selection_changed.connect(self.on_selection_changed)
        table_layout.addWidget(self.products_table)
        
        table_frame.layout.addLayout(table_layout)
        main_layout.addWidget(table_frame, 1)  # Give stretch factor
        
        # Compare button
        button_frame = ContentFrame()
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)  # Align to right
        compare_button = create_button(
            text="View facts sheet / Compare Selected Products", style="yellow", 
            callback=self.compare_selected_products, parent=self
        )
        button_layout.addWidget(compare_button)
        button_frame.layout.addLayout(button_layout)
        main_layout.addWidget(button_frame)
    
    def load_product_data(self):
        """Load product data from repository."""
        # Get products
        products_repo = ProductRepository.get_instance()
        products = products_repo.get_filtered_products()
        if not products:
            return
                
        self.all_products = products
        
        # Get columns from first product
        first_product = products[0].to_dict()
        column_keys = list(first_product.keys())
        
        # Set products in the table with default configuration
        self.products_table.set_products(products, column_keys)
        
        # Retrieve visible columns and mapping for filters
        visible_columns, field_to_column_map = self.products_table.get_visible_columns()
        
        # Set filter data in the container
        self.filter_container.set_filter_data(visible_columns, field_to_column_map)
    
    def apply_filters(self):
        """Apply all active filters."""
        # Get filter criteria from the container
        filters = self.filter_container.get_filter_criteria()
        
        # Apply filters to the table
        self.products_table.apply_filters(filters)
    
    def reset_filters(self):
        """Reset all filters and show all products."""
        # Reset filters in container
        self.filter_container.reset_filters()
        
        # Show all rows in the table
        for row in range(self.products_table.rowCount()):
            self.products_table.showRow(row)
    
    def on_selection_changed(self, selected_products):
        """Handle selection changes from the table."""
        self.parent.selected_products = selected_products

    def compare_selected_products(self):
        """Handle the compare button click."""
        selected_products = self.parent.selected_products
        if not selected_products:
            return
        
        # Load selected products into the comparison tab
        self.parent.comparison_tab.update_comparison_view(selected_products)

        # Navigate to the comparison tab
        self.parent.tabs.setCurrentIndex(1)