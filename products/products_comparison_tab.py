"""
Products comparison tab for the Lorenzo Pozzi Pesticide App

This module defines the ProductsComparisonTab class which handles the product
comparison functionality using Qt's Model/View architecture.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableView, QHeaderView, QSizePolicy
from PySide6.QtCore import Qt
from common.styles import get_body_font
from data.models import ProductComparisonModel


class ProductsComparisonTab(QWidget):
    """
    Products comparison tab for comparing selected products.
    
    This tab displays a table comparing the properties of selected products
    side by side using the Model/View architecture.
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
        
        # Message for when no products are selected
        self.no_selection_label = QLabel("Select products from the list tab and click 'Compare Selected Products'")
        self.no_selection_label.setAlignment(Qt.AlignCenter)
        self.no_selection_label.setFont(get_body_font())
        main_layout.addWidget(self.no_selection_label)
        
        # Create the model
        self.comparison_model = ProductComparisonModel()
        
        # Comparison table view (initially hidden)
        self.comparison_table = QTableView()
        self.comparison_table.setModel(self.comparison_model)
        self.comparison_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.comparison_table.setVisible(False)
        self.comparison_table.setAlternatingRowColors(True)
        
        # Configure the header to stretch columns evenly
        header = self.comparison_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Property column
        header.setStretchLastSection(False)  # Don't stretch the last section only
        
        # Configure vertical header - rows should resize to content
        self.comparison_table.verticalHeader().setVisible(False)
        self.comparison_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        main_layout.addWidget(self.comparison_table)
    
    def update_comparison_view(self, selected_products):
        """Update the comparison view with the selected products."""
        if not selected_products:
            # If no products selected, show message
            self.no_selection_label.setText("No products selected for comparison. Please select at least one product.")
            self.no_selection_label.setVisible(True)
            self.comparison_table.setVisible(False)
            return
        
        # Hide the "no selection" message
        self.no_selection_label.setVisible(False)
        
        # Show and update the comparison table
        self.comparison_table.setVisible(True)
        
        # Update the model with the selected products
        self.comparison_model.setProducts(selected_products)
        
        # Resize columns to fit content
        header = self.comparison_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Property column
        
        # Distribute remaining width evenly among product columns
        for col in range(1, self.comparison_model.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
    
    def clear_comparison(self):
        """Clear the comparison table and show the no selection message."""
        self.no_selection_label.setText("Select products from the list tab and click 'Compare Selected Products'")
        self.no_selection_label.setVisible(True)
        self.comparison_table.setVisible(False)
        self.comparison_model.setProducts([])