"""
Common styles for the LORENZO POZZI Pesticide App

This module provides consistent styling across the application including
colors, fonts, and dimensions.
"""

from PySide6.QtGui import QFont, QColor, QPalette

# Primary color palette 
PRIMARY_COLOR = "#fee000"       # Yellow
SECONDARY_COLOR = "#000000"     # Black
TEXT_COLOR = "#000000"          # Black for text
LIGHT_BG_COLOR = "#F5F5F5"      # Light gray (fixed missing #)
WHITE = "#FFFFFF"               # White
RED_HIGHLIGHT = "#EC3400"       # Red for warnings/high values
YELLOW_MEDIUM = "#fee000"       # Yellow for medium values
GREEN_GOOD = "#009863"          # Green for good/low values

# EIQ color coding
EIQ_LOW_COLOR = QColor(0, 152, 99, 100)    # Light green for low EIQ
EIQ_MEDIUM_COLOR = QColor(254, 224, 0, 100)  # Light yellow for medium EIQ
EIQ_HIGH_COLOR = QColor(236, 52, 0, 100)   # Light red for high EIQ

# Spacing and sizes
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

# Font configurations
def get_title_font(size=24, bold=True):
    """Returns a font configured for titles - Red Hat Display Black."""
    font = QFont("Red Hat Display")
    font.setPointSize(size)
    font.setBold(bold)
    font.setWeight(QFont.Black)
    return font

def get_subtitle_font(size=18, bold=True):
    """Returns a font configured for subtitles."""
    font = QFont("Red Hat Display")
    font.setPointSize(size)
    font.setBold(bold)
    return font

def get_body_font(size=12, bold=False):
    """Returns a default system font for body text."""
    font = QFont()
    font.setPointSize(size)
    font.setBold(bold)
    return font

def get_small_font(size=9, bold=False):
    """Returns a default system font for small text."""
    font = QFont()
    font.setPointSize(size)
    font.setBold(bold)
    return font

# Style sheets
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

FRAME_STYLE = f"""
    QFrame {{
        background-color: {WHITE};
        border: 1px solid #DDDDDD;
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

# Yellow bar style for bottom of pages
YELLOW_BAR_STYLE = f"""
    QFrame {{
        background-color: {PRIMARY_COLOR};
        min-height: 25px;
        max-height: 25px;
    }}
"""

# Function to set up application-wide palette
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