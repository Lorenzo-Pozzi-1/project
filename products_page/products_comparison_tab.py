"""
Products comparison tab for the LORENZO POZZI Pesticide App.

This module defines the ProductsComparisonTab class which displays a side-by-side
comparison of selected products using the ComparisonTable widget.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from common.widgets import ContentFrame
from products_page.widgets.comparison_table import ComparisonView


class ProductsComparisonTab(QWidget):
    """
    Products comparison tab for comparing selected products.
    
    This tab displays a table comparing the properties of selected products
    side by side using the ComparisonView widget.
    """
    def __init__(self, parent=None):
        """Initialize the products comparison tab."""
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Wrap comparison view in ContentFrame
        comparison_frame = ContentFrame()
        comparison_layout = QVBoxLayout()
        
        # Use the ComparisonView widget
        self.comparison_view = ComparisonView()
        comparison_layout.addWidget(self.comparison_view)
        
        comparison_frame.layout.addLayout(comparison_layout)
        main_layout.addWidget(comparison_frame)
    
    def update_comparison_view(self, selected_products):
        """
        Update the comparison view with the selected products.
        
        Args:
            selected_products: List of product objects to compare
        """
        self.comparison_view.update_comparison(selected_products)
    
    def clear_comparison(self):
        """Clear the comparison view."""
        self.comparison_view.clear()