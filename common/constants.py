"""Constants and color definitions for the LORENZO POZZI Pesticide App"""

from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtCore import QSize

# ----------------------
# COLOR DEFINITIONS
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
EIQ_EXTREME_COLOR = QColor("#D19B9B")       # Pastel dark red for extreme EIQ

# Table and list styling colors
ALTERNATE_ROW_COLOR = QColor(BEIGE)  # Beige for alternating rows

# ----------------------
# EIQ THRESHOLDS
# ----------------------

# EIQ threshold constants
EIQ_LOW_THRESHOLD = 33.3
EIQ_MEDIUM_THRESHOLD = 66.6
EIQ_HIGH_THRESHOLD = 100.0

# ----------------------
# SCREEN SIZE DETECTION
# ----------------------

def get_screen_size(test_width = None, test_height = None):
    """Get the primary screen size with testing override capability.
    
    Set environment variables to simulate different screen sizes:
    - TEST_SCREEN_WIDTH: Override screen width  
    - TEST_SCREEN_HEIGHT: Override screen height
    
    Returns:
        QSize: Screen size (actual or simulated)
    """
    import os
        
    if test_width and test_height:
        try:
            width = int(test_width)
            height = int(test_height)
            print(f"🧪 TESTING MODE: Simulating screen size {width}x{height}")
            return QSize(width, height)
        except ValueError:
            print("⚠️  Invalid test screen size values, using actual screen")
    
    # Original screen detection logic
    try:
        app = QGuiApplication.instance()
        if app is None:
            return QSize(1920, 1080)
        
        screen = app.primaryScreen()
        if screen:
            return screen.size()
        else:
            return QSize(1920, 1080)  # Fallback
    except:
        return QSize(1920, 1080)  # Fallback

def get_screen_scale_factor():
    """Get scaling factor based on screen size.
    
    Returns:
        float: Scale factor (1.0 for standard screens, higher for larger screens)
    """
    screen_size = get_screen_size()
    width = screen_size.width()
    height = screen_size.height()
    
    # Base resolution: 1920x1080
    base_width = 1920
    base_height = 1080
    
    # Calculate scale based on screen area (more balanced than just width or height)
    screen_area = width * height
    base_area = base_width * base_height
    area_ratio = screen_area / base_area
    
    # Apply square root to make scaling less aggressive
    scale_factor = area_ratio ** 0.5
    
    # Clamp between reasonable bounds
    return max(0.7, min(scale_factor, 2.5))

# ----------------------
# RESPONSIVE SPACING AND SIZES
# ----------------------

def get_picture_size():
    """Get picture size scaled to screen size."""
    base_size = 150
    return int(base_size * get_screen_scale_factor())

def get_margin_small():
    """Get small margin scaled to screen size."""
    base_margin = 5
    return int(base_margin * get_screen_scale_factor())

def get_margin_medium():
    """Get medium margin scaled to screen size."""
    base_margin = 10
    return int(base_margin * get_screen_scale_factor())

def get_margin_large():
    """Get large margin scaled to screen size."""
    base_margin = 20
    return int(base_margin * get_screen_scale_factor())

def get_spacing_small():
    """Get small spacing scaled to screen size."""
    base_spacing = 5
    return int(base_spacing * get_screen_scale_factor())

def get_spacing_medium():
    """Get medium spacing scaled to screen size."""
    base_spacing = 10
    return int(base_spacing * get_screen_scale_factor())

def get_spacing_large():
    """Get large spacing scaled to screen size."""
    base_spacing = 15
    return int(base_spacing * get_screen_scale_factor())

def get_spacing_xlarge():
    """Get extra large spacing scaled to screen size."""
    base_spacing = 40
    return int(base_spacing * get_screen_scale_factor())

# Standard element dimensions (responsive)
def get_button_min_width():
    """Get minimum button width scaled to screen size."""
    base_width = 120
    return int(base_width * get_screen_scale_factor())

def get_button_min_height():
    """Get minimum button height scaled to screen size."""
    base_height = 35
    return int(base_height * get_screen_scale_factor())

def get_feature_button_size():
    """Get feature button size scaled to screen size."""
    base_size = 180
    return int(base_size * get_screen_scale_factor())

# ----------------------
# RESPONSIVE FONT SIZES
# ----------------------

def get_title_text_size():
    """Get title font size scaled to screen size."""
    base_size = 24
    scale = get_screen_scale_factor()
    
    # Font scaling is less aggressive than spacing
    font_scale = 1.0 + (scale - 1.0) * 0.7
    return int(base_size * font_scale)

def get_subtitle_text_size():
    """Get subtitle font size scaled to screen size."""
    base_size = 18
    scale = get_screen_scale_factor()
    font_scale = 1.0 + (scale - 1.0) * 0.7
    return int(base_size * font_scale)

def get_large_text_size():
    """Get large text size scaled to screen size."""
    base_size = 14
    scale = get_screen_scale_factor()
    font_scale = 1.0 + (scale - 1.0) * 0.7
    return int(base_size * font_scale)

def get_medium_text_size():
    """Get medium text size scaled to screen size."""
    base_size = 12
    scale = get_screen_scale_factor()
    font_scale = 1.0 + (scale - 1.0) * 0.7
    return int(base_size * font_scale)

def get_small_text_size():
    """Get small text size scaled to screen size."""
    base_size = 10
    scale = get_screen_scale_factor()
    font_scale = 1.0 + (scale - 1.0) * 0.7
    return max(8, int(base_size * font_scale))  # Minimum readable size
