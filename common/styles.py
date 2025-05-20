"""
Common styles for the LORENZO POZZI Pesticide App

This module provides consistent styling across the application including
colors, fonts, dimensions, and style sheets for various components.
It serves as the single source of truth for all styling in the application.
"""

from PySide6.QtGui import QFont, QColor

# ----------------------
#region COLOR DEFINITIONS
# ----------------------

# Primary color palette 
YELLOW          = "#fee000"
YELLOW_HOVER    = "#ffea66"
YELLOW_PRESSED  = "#eccd00"
BLACK           = "#000000"
WHITE           = "#FFFFFF"
GREEN           = "#009863"
BLUE            = "#5D89E9"
BLUE_HOVER      = "#789ded"
LIGHT_GRAY      = "#D9DAE4"
BEIGE           = "#C9BFB0"
RED             = "#EC3400"
RED_HOVER       = "#FF6B6B"
RED_PRESSED     = "#CC2A22"

# EIQ color coding using hex color codes
EIQ_LOW_COLOR = QColor(200, 255, 200)      # Pastel green for low EIQ
EIQ_MEDIUM_COLOR = QColor(255, 255, 200)   # Pastel yellow for medium EIQ  
EIQ_HIGH_COLOR = QColor(255, 200, 200)     # Pastel red for high EIQ
EIQ_EXTREME_COLOR = QColor("#D19B9B")    # Pastel dark red for extreme EIQ

# Table and list styling colors
ALTERNATE_ROW_COLOR = QColor(BEIGE)  # Beige for alternating rows

# ----------------------
#region EIQ THRESHOLDS, COLORS AND RATINGS
# ----------------------

# EIQ threshold constants
EIQ_LOW_THRESHOLD = 33.3
EIQ_MEDIUM_THRESHOLD = 66.6
EIQ_HIGH_THRESHOLD = 100.0

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
#region SPACING AND SIZES
# ----------------------

# Margins and spacing
MARGIN_SMALL = 5
MARGIN_MEDIUM = 10
MARGIN_LARGE = 20
SPACING_SMALL = 5
SPACING_MEDIUM = 10
SPACING_LARGE = 15
SPACING_XLARGE = 20

# Standard element dimensions
BUTTON_MIN_WIDTH = 120
BUTTON_MIN_HEIGHT = 40
FEATURE_BUTTON_SIZE = 180       # Size for large feature buttons on home page

# ----------------------
#region FONT CONFIGURATIONS
# ----------------------

# Font sizes
TITLE_FONT_SIZE = 24
SUBTITLE_FONT_SIZE = 18
BODY_FONT_SIZE = 14
SMALL_FONT_SIZE = 12

def get_font(size=BODY_FONT_SIZE, bold=False, family=None, weight=None):
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
def get_title_font(size=TITLE_FONT_SIZE, bold=True): return get_font(size, bold, "Red Hat Display", QFont.Black)
def get_subtitle_font(size=SUBTITLE_FONT_SIZE, bold=True): return get_font(size, bold, "Red Hat Display")
def get_body_font(size=BODY_FONT_SIZE, bold=False): return get_font(size, bold)
def get_small_font(size=SMALL_FONT_SIZE, bold=False): return get_font(size, bold)

# ----------------------
#region STYLE SHEETS
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
        margin: {MARGIN_SMALL}px;
    }}
"""

# Buttons styles
FEATURE_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {WHITE};
        border: 4px solid {YELLOW};
        border-radius: 8px;
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

PRIMARY_BUTTON_STYLE = f"""
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

SECONDARY_BUTTON_STYLE = f"""
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
        font-size: {BODY_FONT_SIZE}pt;
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
        margin-left: 7px;
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

# Suggestions container style
SUGGESTIONS_CONTAINER_STYLE = f"""
    QFrame {{
        border: 1px solid {LIGHT_GRAY};
        background-color: {WHITE};
        border-radius: 3px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }}
"""

# Suggestions list style
SUGGESTIONS_LIST_STYLE = f"""
    QListWidget {{
        border: none;
        outline: none;
        color: {BLACK};
        font-size: {SMALL_FONT_SIZE}pt;
    }}
    QListWidget::item {{
        padding: 5px;
    }}
    QListWidget::item:hover {{
        background-color: {LIGHT_GRAY};
    }}
    QListWidget::item:selected {{
        background-color: {LIGHT_GRAY};
    }}
"""

# Row dragging styles
DRAGGING_ROW_STYLE = """
    QFrame {
        background-color: #f0f9ff;
        border: 1px solid #ccc;
        border-left: 3px solid {BLUE};
        border-right: 3px solid {BLUE};
        border-radius: 4px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
"""

BLUE_LINE_DROP_STYLE = """
    QFrame#dropIndicator {
        background-color: {BLUE};
        height: 3px;
        border: 1px solid {BLUE};
        border-radius: 1px;
    }
"""

