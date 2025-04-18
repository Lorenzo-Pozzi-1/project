"""
Main EIQ Calculator page for the LORENZO POZZI Pesticide App.

This module defines the EiqCalculatorPage class which serves as a container for
the three EIQ calculator components:
- Single Product Calculator
- Product Comparison Calculator
- Seasonal EIQ Calculator
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Qt

from ui.common.styles import MARGIN_LARGE, SPACING_MEDIUM
from ui.common.widgets import HeaderWithBackButton

# Import EIQ calculator components
from ui.eiq.single_product_calculator import SingleProductCalculator
from ui.eiq.product_comparison import ProductComparisonCalculator
from ui.eiq.seasonal_eiq import SeasonalEIQCalculator


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
        main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        main_layout.setSpacing(SPACING_MEDIUM)
        
        # Header with back button
        header = HeaderWithBackButton("EIQ Calculator")
        header.back_clicked.connect(self.parent.go_home)
        main_layout.addWidget(header)
        
        # Create tabs for different EIQ calculation methods
        self.tabs = QTabWidget()
        
        # Single product calculator tab
        self.single_product_calculator = SingleProductCalculator(self)
        self.tabs.addTab(self.single_product_calculator, "Single Product Calculator")
        
        # Comparison calculator tab
        self.product_comparison_calculator = ProductComparisonCalculator(self)
        self.tabs.addTab(self.product_comparison_calculator, "Product Comparison")
        
        # Season calculator tab
        self.seasonal_eiq_calculator = SeasonalEIQCalculator(self)
        self.tabs.addTab(self.seasonal_eiq_calculator, "Seasonal EIQ")
        
        main_layout.addWidget(self.tabs)