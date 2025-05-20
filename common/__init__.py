"""
Common components for the LORENZO POZZI Pesticide App.

This package provides common UI components, styles, and utility functions
shared across the application.

Usage:
    from common import PRIMARY_BUTTON_STYLE, ContentFrame, get_subtitle_font
"""

# Re-export all config utilities
from common.config_utils import (
    get_config, 
    load_config, 
    save_config
)

# Re-export all style components
from common.styles import (
    # Colors
    YELLOW, YELLOW_HOVER, BLACK, WHITE, GREEN, BLUE, BLUE_HOVER, 
    LIGHT_GRAY, BEIGE, RED,
    
    # Styles
    PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE, GENERIC_TABLE_STYLE,
    
    # Font functions
    get_title_font, get_subtitle_font, get_body_font,
)

# Re-export common widgets and their functions
from common.widgets.widgets import (
    ContentFrame, 
    HeaderWithHomeButton,
    create_button
)
from common.widgets.scorebar import ScoreBar

# Define what gets imported with "from common import *"
__all__ = [
    # Config utilities
    'get_config', 'load_config', 'save_config',
    
    # Colors
    'YELLOW', 'YELLOW_HOVER', 'BLACK', 'WHITE', 'GREEN', 'BLUE', 
    'BLUE_HOVER', 'LIGHT_GRAY', 'BEIGE', 'RED',
    
    # Styles
    'PRIMARY_BUTTON_STYLE', 'SECONDARY_BUTTON_STYLE', 'GENERIC_TABLE_STYLE',
    
    # Font functions
    'get_title_font', 'get_subtitle_font', 'get_body_font',
    
    # Style utility functions
    'create_button',
    
    # Widgets
    'ContentFrame', 'HeaderWithHomeButton', 'ScoreBar'
]