"""
Main EIQ Calculator page for the LORENZO POZZI Pesticide App.

This module defines the EiqCalculatorPage class which serves as a container for
two EIQ calculator components:
- Single Product Calculator
- Product Comparison Calculator
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from common.widgets.header_frame_buttons import HeaderWithHomeButton
from common.constants import get_margin_large, get_spacing_medium
from eiq_calculator_page.tab_single_calculator import SingleProductCalculatorTab
from eiq_calculator_page.tab_multi_calculator import ProductComparisonCalculatorTab


class EiqCalculatorPage(QWidget):
    """
    EIQ Calculator page for calculating environmental impact.
    
    This page contains tabs for different EIQ calculation methods.
    """
    def __init__(self, parent=None):
        """Initialize the EIQ calculator page."""
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(get_margin_large(), get_margin_large(), get_margin_large(), get_margin_large())
        main_layout.setSpacing(get_spacing_medium())
        
        # Header with back button
        header = HeaderWithHomeButton("EIQ Calculator")
        header.back_clicked.connect(lambda: self.parent.navigate_to_page(0))
        main_layout.addWidget(header)
        
        # Create tabs for different EIQ calculation methods
        self.tabs = QTabWidget()
        
        # Single product calculator tab
        self.single_product_calculator = SingleProductCalculatorTab(self)
        self.tabs.addTab(self.single_product_calculator, "Single Product Calculator")
        
        # Comparison calculator tab
        self.product_comparison_calculator = ProductComparisonCalculatorTab(self)
        self.tabs.addTab(self.product_comparison_calculator, "Product Comparison")
        
        main_layout.addWidget(self.tabs)
    
    def refresh_product_data(self):
        """
        Refresh product data based on the filtered products.
        This method is called when filtered data has changed in the main window.
        """
        # Update both calculator tabs with the current filtered data
        self.single_product_calculator.refresh_product_data()
        self.product_comparison_calculator.refresh_product_data()