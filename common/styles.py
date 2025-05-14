"""
Common styles for the LORENZO POZZI Pesticide App

This module provides consistent styling across the application including
colors, fonts, dimensions, and style sheets for various components.
It serves as the single source of truth for all styling in the application.
"""

from PySide6.QtGui import QFont, QColor, QPalette, QBrush
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QFormLayout

# ----------------------
# COLOR DEFINITIONS
# ----------------------

# Primary color palette 
PRIMARY_COLOR = "#fee000"       # Yellow
SECONDARY_COLOR = "#000000"     # Black
TEXT_COLOR = "#000000"          # Black for text
LIGHT_BG_COLOR = "#F5F5F5"      # Light gray
WHITE = "#FFFFFF"               # White
RED_HIGHLIGHT = "#EC3400"       # Red for warnings/high values
YELLOW_MEDIUM = "#fee000"       # Yellow for medium values
GREEN_GOOD = "#009863"          # Green for good/low values

# EIQ color coding using QColor objects
EIQ_LOW_COLOR = QColor(0, 152, 99, 100)    # Light green for low EIQ
EIQ_MEDIUM_COLOR = QColor(254, 224, 0, 100)  # Light yellow for medium EIQ
EIQ_HIGH_COLOR = QColor(236, 52, 0, 100)   # Light red for high EIQ
EIQ_EXTREME_COLOR = QColor(139, 0, 0, 100) # Dark red for extreme EIQ

# Table and list styling colors
HIGHLIGHT_COLOR = QColor(PRIMARY_COLOR)  # Primary yellow color for highlighting
ALTERNATE_ROW_COLOR = QColor(LIGHT_BG_COLOR)  # Light gray for alternating rows

# ----------------------
# THRESHOLDS AND CONSTANTS
# ----------------------

# EIQ threshold constants
EIQ_LOW_THRESHOLD = 33.3
EIQ_MEDIUM_THRESHOLD = 66.6
EIQ_HIGH_THRESHOLD = 100.0

# ----------------------
# SPACING AND SIZES
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
# FONT CONFIGURATIONS
# ----------------------

# Font sizes
TITLE_FONT_SIZE = 24
SUBTITLE_FONT_SIZE = 18
BODY_FONT_SIZE = 12
SMALL_FONT_SIZE = 9

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

def get_title_font(size=TITLE_FONT_SIZE, bold=True):
    """Returns a font suitable for page titles."""
    return get_font(size, bold, "Red Hat Display", QFont.Black)

def get_subtitle_font(size=SUBTITLE_FONT_SIZE, bold=True):
    """Returns a font suitable for section titles."""
    return get_font(size, bold, "Red Hat Display")

def get_body_font(size=BODY_FONT_SIZE, bold=False):
    """Returns a font suitable for regular text."""
    return get_font(size, bold)

def get_small_font(size=SMALL_FONT_SIZE, bold=False):
    """Returns a font suitable for small text."""
    return get_font(size, bold)

# ----------------------
# STYLE SHEETS
# ----------------------

# Buttons to pages styles
FEATURE_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {WHITE};
        border: 2px solid {PRIMARY_COLOR};
        border-radius: 8px;
        padding: 10px;
    }}
    QPushButton:hover {{
        background-color: #FFF8D9;
        border: 2px solid {PRIMARY_COLOR};
    }}
    QPushButton:pressed {{
        background-color: #FFF2B3;
    }}
"""

PRIMARY_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {PRIMARY_COLOR};
        color: {SECONDARY_COLOR};
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #ffea66;
    }}
    QPushButton:pressed {{
        background-color: #e6ca00;
    }}
    QPushButton:disabled {{
        background-color: #CCCCCC;
        color: #666666;
    }}
"""

SECONDARY_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {WHITE};
        color: {SECONDARY_COLOR};
        border: 1px solid {SECONDARY_COLOR};
        border-radius: 4px;
        padding: 8px 16px;
    }}
    QPushButton:hover {{
        background-color: #F5F5F5;
    }}
    QPushButton:pressed {{
        background-color: #E0E0E0;
    }}
"""

# Frame styles
FRAME_STYLE = f"""
    QFrame {{
        background-color: {WHITE};
        border: 1px solid transparent;
        border-radius: 4px;
    }}
"""

FILTER_FRAME_STYLE = f"""
    QFrame {{
        background-color: {WHITE};
        border: 1px solid #DDDDDD;
        border-radius: 4px;
        padding: 10px;
    }}
"""

# Remove button in filter row
FILTER_ROW_STYLE = f"""
    QPushButton {{
        color: red;
        font-weight: bold;
        border-radius: 12px;
        border: 1px solid #ccc;
    }}
    QPushButton:hover {{
        background-color: #ffeeee;
    }}
"""

# Application row style
APPLICATION_ROW_STYLE = """
    QFrame {
        border: none;
        border-bottom: 1px solid #E0E5EB;
        background-color: transparent;
        padding: 2px;
    }
    QFrame:hover {
        background-color: #EAEFF5;
    }
"""

# Yellow bar style for bottom of pages
YELLOW_BAR_STYLE = f"""
    QFrame {{
        background-color: {PRIMARY_COLOR};
        min-height: 25px;
        max-height: 25px;
    }}
"""

# Table header styles
COMPARISON_HEADER_STYLE = f"""
    QHeaderView::section {{
        background-color: {PRIMARY_COLOR};
        color: {SECONDARY_COLOR};
        padding: 5px;
        border: 1px solid #dddddd;
        font-weight: bold;
    }}
"""

# Product card style
PRODUCT_CARD_STYLE = f"""
    QFrame {{
        background-color: {WHITE};
        border: 1px solid #DDDDDD;
        border-radius: 4px;
    }}
"""

# Remove button style
REMOVE_BUTTON_STYLE = """
    QPushButton {
        background-color: #f44336;
        color: white;
        border-radius: 12px;
        font-weight: bold;
        font-size: 16px;
    }
    QPushButton:hover {
        background-color: #d32f2f;
    }
"""

# Warning title style
WARNING_TITLE_STYLE = f"""
    color: red; 
    font-weight: bold; 
    background-color: #FFEEEE; 
    padding: 5px;
"""

# Suggestions container style
SUGGESTIONS_CONTAINER_STYLE = f"""
    QFrame {{
        border: 1px solid #CCCCCC;
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
    }}
    QListWidget::item {{
        padding: 5px;
    }}
    QListWidget::item:hover {{
        background-color: {LIGHT_BG_COLOR};
    }}
    QListWidget::item:selected {{
        background-color: #E0E0E0;
    }}
"""

# Row dragging styles
DRAGGING_ROW_STYLE = """
    QFrame {
        background-color: #f0f9ff;
        border: 1px solid #ccc;
        border-left: 3px solid #3b82f6;
        border-right: 3px solid #3b82f6;
        border-radius: 4px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
"""

DROP_INDICATOR_STYLE = """
    QFrame#dropIndicator {
        background-color: #3b82f6;
        height: 3px;
        border-radius: 1px;
    }
"""

# ----------------------
# UTILITY FUNCTIONS
# ----------------------

def setup_app_palette(app):
    """Configure the application-wide color palette."""
    palette = QPalette()
    
    # Set up the color palette with white background
    palette.setColor(QPalette.Window, QColor(WHITE)) 
    palette.setColor(QPalette.WindowText, QColor(TEXT_COLOR))
    palette.setColor(QPalette.Base, QColor(WHITE))
    palette.setColor(QPalette.AlternateBase, QColor(LIGHT_BG_COLOR)) 
    palette.setColor(QPalette.Text, QColor(TEXT_COLOR))
    palette.setColor(QPalette.Button, QColor(WHITE))
    palette.setColor(QPalette.ButtonText, QColor(TEXT_COLOR))
    palette.setColor(QPalette.Link, QColor(PRIMARY_COLOR))
    palette.setColor(QPalette.Highlight, QColor(PRIMARY_COLOR))
    palette.setColor(QPalette.HighlightedText, QColor(SECONDARY_COLOR))
    
    # Apply the palette
    app.setPalette(palette)

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

def get_highlight_brush():
    """Get a brush with the highlight color."""
    return QBrush(HIGHLIGHT_COLOR)

def get_alternate_row_brush():
    """Get a brush with the alternate row color."""
    return QBrush(ALTERNATE_ROW_COLOR)

# ----------------------
# WIDGET FACTORY FUNCTIONS
# ----------------------

def create_primary_button(text, callback=None, parent=None):
    """Create a primary button with consistent styling."""
    button = QPushButton(text, parent)
    button.setStyleSheet(PRIMARY_BUTTON_STYLE)
    if callback:
        button.clicked.connect(callback)
    return button

def create_secondary_button(text, callback=None, parent=None):
    """Create a secondary button with consistent styling."""
    button = QPushButton(text, parent)
    button.setStyleSheet(SECONDARY_BUTTON_STYLE)
    if callback:
        button.clicked.connect(callback)
    return button

def create_form_layout(parent=None):
    """Create a form layout with consistent styling."""
    form_layout = QFormLayout(parent)
    form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form_layout.setContentsMargins(MARGIN_MEDIUM, MARGIN_MEDIUM, MARGIN_MEDIUM, MARGIN_MEDIUM)
    form_layout.setSpacing(SPACING_MEDIUM)
    return form_layout

def apply_table_header_style(header):
    """Apply consistent styling to a table header."""
    header.setStyleSheet(COMPARISON_HEADER_STYLE)
    header.setDefaultAlignment(Qt.AlignCenter)