"""
Widget exports for the Products page.

This module exposes all the widget classes from the widgets subfolder.
"""

from products_page.widgets.filter_row import FilterRow, FilterRowContainer
from products_page.widgets.products_table import ProductTable
from products_page.widgets.comparison_table import ComparisonTable, ComparisonView

__all__ = [
    'FilterRow',
    'FilterRowContainer',
    'ProductTable',
    'ComparisonTable',
    'ComparisonView',
]