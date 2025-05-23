"""
Products package for the LORENZO POZZI Pesticide App.

This package provides product listing and comparison functionality.
"""

from products_page.page_products import ProductsPage
from products_page.tab_products_list import ProductsListTab
from products_page.tab_products_comparison import ProductsComparisonTab

# Import widgets
from products_page.widget_filter_row import FilterRow, FilterRowContainer
from products_page.widget_products_table import ProductTable
from products_page.widget_comparison_table import ComparisonTable, ComparisonView

__all__ = [
    # Main page and tabs
    'ProductsPage', 
    'ProductsListTab', 
    'ProductsComparisonTab',
    
    # Widget components
    'FilterRow',
    'FilterRowContainer',
    'ProductTable',
    'ComparisonTable',
    'ComparisonView'
]