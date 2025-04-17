"""
Common styles for the LORENZO POZZI Pesticide App

This module provides consistent styling across the application including
colors, fonts, and dimensions.
"""

from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtCore import Qt

# Primary color palette
PRIMARY_COLOR = "#007C3E"       # Green
SECONDARY_COLOR = "#FFD100"     # Yellow accent
TEXT_COLOR = "#333333"          # Dark gray for text
LIGHT_BG_COLOR = "#F5F5F5"      # Light background
WHITE = "#FFFFFF"               # White
RED_HIGHLIGHT = "#FF5252"       # Red for warnings/high values
YELLOW_MEDIUM = "#FFC107"       # Yellow for medium values
GREEN_GOOD = "#4CAF50"          # Green for good/low values

# EIQ color coding
EIQ_LOW_COLOR = QColor(200, 255, 200)     # Light green for low EIQ
EIQ_MEDIUM_COLOR = QColor(255, 255, 200)  # Light yellow for medium EIQ
EIQ_HIGH_COLOR = QColor(255, 200, 200)    # Light red for high EIQ

# Spacing and sizes
MARGIN_SMALL = 5
MARGIN_MEDIUM = 10
MARGIN_LARGE = 20
SPACING_SMALL = 5
SPACING_MEDIUM = 10
SPACING_LARGE = 15
SPACING_XLARGE = 20

BUTTON_MIN_WIDTH = 120
BUTTON_MIN_HEIGHT = 40
FEATURE_BUTTON_SIZE = 180       # Size for large feature buttons on home page

# Font configurations
def get_title_font(size=24, bold=True):
    """Returns a font configured for titles."""
    font = QFont()
    font.setPointSize(size)
    font.setBold(bold)
    return font

def get_subtitle_font(size=18, bold=True):
    """Returns a font configured for subtitles."""
    font = QFont()
    font.setPointSize(size)
    font.setBold(bold)
    return font

def get_body_font(size=11, bold=False):
    """Returns a font configured for body text."""
    font = QFont("Arial", size)
    font.setBold(bold)
    return font

def get_small_font(size=9, bold=False):
    """Returns a font configured for small text."""
    font = QFont("Arial", size)
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
        background-color: #E6F2EA;
        border: 2px solid {PRIMARY_COLOR};
    }}
    QPushButton:pressed {{
        background-color: #D6EAE0;
    }}
"""

PRIMARY_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {PRIMARY_COLOR};
        color: {WHITE};
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #006633;
    }}
    QPushButton:pressed {{
        background-color: #005729;
    }}
    QPushButton:disabled {{
        background-color: #CCCCCC;
        color: #666666;
    }}
"""

SECONDARY_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {WHITE};
        color: {PRIMARY_COLOR};
        border: 1px solid {PRIMARY_COLOR};
        border-radius: 4px;
        padding: 8px 16px;
    }}
    QPushButton:hover {{
        background-color: #E6F2EA;
    }}
    QPushButton:pressed {{
        background-color: #D6EAE0;
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
        background-color: {LIGHT_BG_COLOR};
        border: 1px solid #DDDDDD;
        border-radius: 4px;
        padding: 10px;
    }}
"""

# Function to set up application-wide palette
def setup_app_palette(app):
    """Configure the application-wide color palette."""
    palette = QPalette()
    
    # Set up the color palette
    palette.setColor(QPalette.Window, QColor(LIGHT_BG_COLOR))
    palette.setColor(QPalette.WindowText, QColor(TEXT_COLOR))
    palette.setColor(QPalette.Base, QColor(WHITE))
    palette.setColor(QPalette.AlternateBase, QColor(LIGHT_BG_COLOR))
    palette.setColor(QPalette.Text, QColor(TEXT_COLOR))
    palette.setColor(QPalette.Button, QColor(LIGHT_BG_COLOR))
    palette.setColor(QPalette.ButtonText, QColor(TEXT_COLOR))
    palette.setColor(QPalette.Link, QColor(PRIMARY_COLOR))
    palette.setColor(QPalette.Highlight, QColor(PRIMARY_COLOR))
    palette.setColor(QPalette.HighlightedText, QColor(WHITE))
    
    # Apply the palette
    app.setPalette(palette)