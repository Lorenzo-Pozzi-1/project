"""
Styling constants and utility functions for the Products page.

This module provides styling constants and helper functions for Product page components.
"""

from PySide6.QtGui import QColor

# Filter row styling
FILTER_ROW_STYLE = """
    QPushButton {
        color: red;
        font-weight: bold;
        border-radius: 12px;
        border: 1px solid #ccc;
    }
    QPushButton:hover {
        background-color: #ffeeee;
    }
"""

# Comparison table header styling
COMPARISON_HEADER_STYLE = """
    QHeaderView::section {
        background-color: #fee000;
        color: #000000;
        padding: 5px;
        border: 1px solid #dddddd;
        font-weight: bold;
    }
"""

# Color constants
HIGHLIGHT_COLOR = QColor("#fee000")  # Primary yellow color
ALTERNATE_ROW_COLOR = QColor("#f5f5f5")  # Light gray for alternating rows

# Font sizes
TITLE_FONT_SIZE = 16
HEADER_FONT_SIZE = 14
BODY_FONT_SIZE = 12

def get_highlight_brush():
    """Get a brush with the highlight color."""
    return QColor(HIGHLIGHT_COLOR)

def get_alternate_row_brush():
    """Get a brush with the alternate row color."""
    return QColor(ALTERNATE_ROW_COLOR)