"""
Widget exports for the Products page.

This module exposes all the widget classes from the widgets subfolder.
"""

from products_page.widgets.filter_row import FilterRow
from products_page.widgets.products_table import ProductTable
from products_page.widgets.comparison_table import ComparisonTable, ComparisonView
from common.styles import GENERIC_TABLE_STYLE

__all__ = [
    'FilterRow',
    'ProductTable',
    'ComparisonTable',
    'ComparisonView',
    'GENERIC_TABLE_STYLE'
]