"""Style functions and stylesheets for the LORENZO POZZI Pesticide App"""

from PySide6.QtGui import QFont
from .constants import *

# ----------------------
# EIQ UTILITY FUNCTIONS
# ----------------------

def get_eiq_color(eiq_value, low_threshold=EIQ_LOW_THRESHOLD, 
                  medium_threshold=EIQ_MEDIUM_THRESHOLD, high_threshold=EIQ_HIGH_THRESHOLD):
    """
    Get appropriate color for an EIQ value based on thresholds.
    
    Args:
        eiq_value (float): The EIQ value to get a color for
        low_threshold (float): Threshold between low and medium impact
        medium_threshold (float): Threshold between medium and high impact
        high_threshold (float): Threshold between high and extreme impact
        
    Returns:
        QColor: Color corresponding to the EIQ value's impact level
    """
    if eiq_value < low_threshold:
        return EIQ_LOW_COLOR
    elif eiq_value < medium_threshold:
        return EIQ_MEDIUM_COLOR
    elif eiq_value < high_threshold:
        return EIQ_HIGH_COLOR
    else:
        return EIQ_EXTREME_COLOR

def get_eiq_rating(eiq_value, low_threshold=EIQ_LOW_THRESHOLD, 
                  medium_threshold=EIQ_MEDIUM_THRESHOLD, high_threshold=EIQ_HIGH_THRESHOLD):
    """
    Get text rating for an EIQ value based on thresholds.
    
    Args:
        eiq_value (float): The EIQ value to get a rating for
        low_threshold (float): Threshold between low and medium impact
        medium_threshold (float): Threshold between medium and high impact
        high_threshold (float): Threshold between high and extreme impact
        
    Returns:
        str: Rating as text ("Low", "Medium", "High", or "Extreme")
    """
    if eiq_value < low_threshold:
        return "Low"
    elif eiq_value < medium_threshold:
        return "Medium"
    elif eiq_value < high_threshold:
        return "High"
    else:
        return "Extreme"

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
    
    QTableWidget::item:selected {{
        background-color: #E0E8F0;
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

# Calculation Trace Dialog Styles
TINY_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: transparent;
        color: {BLACK};
        padding-bottom: 3px;
        border-radius: 5px;
        border: 1px solid {BLACK};
        font-weight: bold;
        text-align: center;
    }}
    QPushButton:hover {{
        background-color: {BLACK};
        color: {WHITE};
        padding-bottom: 3px;
        border-radius: 5px;
        border: 1px solid {BLACK};
        font-weight: bold;
        text-align: center;
    }}
"""

CALCULATION_TRACE_DIALOG_STYLE = f"""
QDialog {{
    background-color: {WHITE};
    border: 1px solid {LIGHT_GRAY};
    border-radius: 4px;
}}

QDialog QLabel {{
    color: {BLACK};
    font-weight: bold;
}}
"""

CALCULATION_TRACE_TEXT_AREA_STYLE = f"""
QTextEdit {{
    background-color: {BLACK};
    color: {WHITE};
    border: 1px solid {LIGHT_GRAY};
    border-radius: 4px;
    padding: 8px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: {get_medium_text_size()}pt;
    line-height: 1.4;
    selection-background-color: {BLUE};
    selection-color: {WHITE};
}}

QTextEdit:focus {{
    border: 2px solid {BLUE};
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