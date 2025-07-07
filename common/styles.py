"""Style functions and stylesheets for the LORENZO POZZI Pesticide App"""

from PySide6.QtGui import QFont
from common.constants import (
    BEIGE, BLACK, BLUE, BLUE_HOVER, LIGHT_GRAY, RED, RED_HOVER, RED_PRESSED,
    WHITE, YELLOW, YELLOW_HOVER, get_large_text_size, get_margin_small,
    get_medium_text_size, get_small_text_size, get_subtitle_text_size,
    get_title_text_size
)

# ----------------------
# FONT FUNCTIONS
# ----------------------

def get_font(size=get_medium_text_size(), bold=False, family=None, weight=None):
    """Returns a configured font based on parameters.
    
    Args:
        size (int): Point size of the font
        bold (bool): Whether the font should be bold
        family (str): Font family name (None for system default)
        weight (int): Font weight (None for default)
    
    Returns:
        QFont: Configured font
    """
    font = QFont(family) if family else QFont()
    font.setPointSize(size)
    font.setBold(bold)
    if weight:
        font.setWeight(weight)
    return font

# Quick font functions
def get_title_font(size=get_title_text_size(), bold=True): 
    return get_font(size, bold, "Red Hat Display", QFont.Black)

def get_subtitle_font(size=get_subtitle_text_size(), bold=True): 
    return get_font(size, bold, "Red Hat Display")

def get_large_font(size=get_large_text_size(), bold=False): 
    return get_font(size, bold)

def get_medium_font(size=get_medium_text_size(), bold=False): 
    return get_font(size, bold)

def get_small_font(size=get_small_text_size(), bold=False): 
    return get_font(size, bold)

# ----------------------
# STYLESHEETS
# ----------------------

# Pages setup styles
FRAME_STYLE = f"""
    QFrame {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 0px;
    }}
"""

PREFERENCES_FRAME_STYLE = f"""
    QFrame {{
        background-color: {WHITE};
        border: 2px solid {YELLOW};
        border-radius: 10px;
    }}
"""

YELLOW_BAR_STYLE = f"""
    QFrame {{
        background-color: {YELLOW};
        min-height: 25px;
        max-height: 25px;
    }}
"""

INFO_TEXT_STYLE = f"""
    QFrame {{
        background-color: {WHITE};
        border: 1px solid transparent;
        border-radius: 10px;
        margin: {get_margin_small()}px;
    }}
"""

# General buttons styles
FEATURE_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {WHITE};
        border: 4px solid {YELLOW};
        border-radius: 30px;
        padding: 10px;
    }}
    QPushButton:hover {{
        background-color: {LIGHT_GRAY};
        border: 2px solid {YELLOW};
    }}
    QPushButton:pressed {{
        background-color: {BEIGE};
    }}
"""

YELLOW_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {YELLOW};
        color: {BLACK};
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {YELLOW_HOVER};
    }}
    QPushButton:pressed {{
        background-color: {BEIGE};
    }}
"""

WHITE_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {WHITE};
        color: {BLACK};
        border: 1px solid {BLACK};
        border-radius: 4px;
        padding: 8px 16px;
    }}
    QPushButton:hover {{
        background-color: {LIGHT_GRAY};
    }}
    QPushButton:pressed {{
        background-color: {BEIGE};
    }}
"""

SPECIAL_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {BLUE};
        color: {BLACK};
        border: 1px solid {BLACK};
        border-radius: 4px;
        padding: 8px 16px;
    }}
    QPushButton:hover {{
        background-color: {BLUE_HOVER};
    }}
    QPushButton:pressed {{
        background-color: {BEIGE};
    }}
"""

REMOVE_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {RED};
        color: {WHITE};
        border-radius: 10px;
        font-weight: bold;
        font-size: 18px;
        padding-bottom: 3.5px;
        line-height: 1;
        text-align: center;
    }}
    QPushButton:hover {{
        background-color: {RED_HOVER};
    }}
    QPushButton:pressed {{
        background-color: {RED_PRESSED};
    }}
"""

UOM_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: transparent;
        color: {BLACK};
        border: 1px solid {BLACK};
        border-radius: 4px;
    }}
    QPushButton:hover {{
        background-color: {LIGHT_GRAY};
    }}
"""

TINY_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: transparent;
        color: {BLACK};
        padding-bottom: 3px;
        border-radius: 10px;
        border: transparent;
        font-weight: bold;
        text-align: center;
    }}
    QPushButton:hover {{
        background-color: {BLACK};
        color: {WHITE};
        padding-bottom: 3px;
        border-radius: 10px;
        border: transparent;
        font-weight: bold;
        text-align: center;
    }}
"""

# Tables style
GENERIC_TABLE_STYLE = f"""
    /* Main table styling */
    QTableWidget {{
        background-color: {WHITE};
        gridline-color: {LIGHT_GRAY};
        border: 1px solid {LIGHT_GRAY};
        border-radius: 4px;
        selection-background-color: {LIGHT_GRAY};
        selection-color: {BLACK};
        alternate-background-color: #F5F5F5;
    }}
    
    /* Header styling */
    QHeaderView::section {{
        background-color: {YELLOW};
        color: {BLACK};
        padding: 5px;
        border: 1px solid {LIGHT_GRAY};
        font-weight: bold;
        font-size: {get_medium_text_size()}pt;
        text-align: center;
        height: 25px;
    }}
    
    /* Row styling */
    QTableWidget::item {{
        padding: 5px;
        border-bottom: 1px solid {LIGHT_GRAY};
    }}
    
    QTableView::item:selected {{
        background-color: #D9DAE4;
        color: {BLACK};
    }}
    
    QTableWidget::item:hover {{
        background-color: {LIGHT_GRAY};
    }}
    
    /* Scroll bars */
    QScrollBar:horizontal {{
        border: none;
        background: {WHITE};
        height: 12px;
    }}
    
    QScrollBar:vertical {{
        border: none;
        background: {WHITE};
        width: 12px;
    }}
    
    QScrollBar::handle:horizontal, QScrollBar::handle:vertical {{
        background: {BEIGE};
        border-radius: 6px;
        min-width: 20px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:horizontal:hover, QScrollBar::handle:vertical:hover {{
        background: {LIGHT_GRAY};
    }}
    
    /* Scroll bar arrows */
    QScrollBar::add-line, QScrollBar::sub-line {{
        background: none;
        border: none;
    }}
    
    /* Corner between scrollbars */
    QTableCornerButton::section {{
        background-color: {LIGHT_GRAY};
        border: 1px solid {LIGHT_GRAY};
    }}
    
    /* Cell editing */
    QTableWidget QLineEdit {{
        border: 1px solid {BLUE};
        border-radius: 2px;
        padding: 2px;
        selection-background-color: {BLUE};
        selection-color: {WHITE};
    }}
    
    /* Checkbox in table */
    QTableWidget QCheckBox {{
        margin-left: 0px;
    }}
    
    /* Focus outline */
    QTableWidget:focus {{
        outline: none;
        border: 1px solid {BLUE};
    }}
"""

# Product card style
PRODUCT_CARD_STYLE = f"""
    QFrame {{
        background-color: {WHITE};
        border: 1px solid {LIGHT_GRAY};
        border-radius: 4px;
    }}
"""

# Filter chip style
FILTER_CHIP_STYLE = f"""
    FilterChip {{
        background-color: {WHITE};
        border: 1px solid {BLACK};
        border-radius: 15px;
        margin: 2px;
        padding: 4px;
    }}
    FilterChip:hover {{
        background-color: {LIGHT_GRAY};
    }}
    FilterChip QLineEdit {{
        border: none;
        background: transparent;
        padding: 2px;
    }}
    FilterChip QPushButton {{
        border: none;
        background: transparent;
        color: #666;
        font-weight: bold;
        border-radius: 10px;
    }}
    FilterChip QPushButton:hover {{
        background-color: {RED};
        color: {WHITE};
    }}
"""


# Calculation Trace Dialog Styles
CALCULATION_TRACE_DIALOG_STYLE = f"""
QDialog {{
    background-color: {LIGHT_GRAY};
    border: 1px solid #dcdcdc;
    border-radius: 12px;
    padding: 16px;
}}

QDialog QLabel {{
    color: {BLACK};
    font-weight: 500;
    font-size: {get_medium_text_size()}pt;
}}
"""

CALCULATION_TRACE_TEXT_AREA_STYLE = f"""
QTextEdit {{
    background-color: {WHITE};
    color: {BLACK};
    border: 1px solid #dcdcdc;
    border-radius: 8px;
    padding: 12px;
    font-size: {get_medium_text_size()}pt;
    line-height: 1.5;
    selection-background-color: #eaf6ff;
    selection-color: #1565c0;
}}

QTextEdit:focus {{
    border: 1px solid #1565c0;
    outline: none;
}}
"""

CALCULATION_TRACE_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {WHITE};
    border: 1px solid {LIGHT_GRAY};
    border-radius: 4px;
    padding: 8px 16px;
    color: {BLACK};
    font-weight: bold;
    min-height: 24px;
}}

QPushButton:hover {{
    background-color: {LIGHT_GRAY};
    border-color: {BLUE};
}}

QPushButton:pressed {{
    background-color: {BEIGE};
    border-color: {BLUE};
}}

QPushButton[text="Clear Terminal"] {{
    background-color: {RED};
    color: {WHITE};
    border-color: {RED};
}}

QPushButton[text="Clear Terminal"]:hover {{
    background-color: {RED_HOVER};
    border-color: {RED_HOVER};
}}

QPushButton[text="Clear Terminal"]:pressed {{
    background-color: {RED_PRESSED};
    border-color: {RED_PRESSED};
}}
"""