"""
Common components for the LORENZO POZZI Pesticide App.

This package provides common UI components, styles, and utility functions
shared across the application. All components are exported at the package level,
allowing for clean imports like:

    from common import YELLOW_BUTTON_STYLE, ContentFrame, get_subtitle_font, ScoreBar

Usage examples:
    # Import specific items
    from common import ContentFrame, ScoreBar, YELLOW, save_config
    
    # Import everything
    from common import *
"""

# Re-export all config utilities
from common.utils import (
    get_config,
    load_config,
    save_config,
    resource_path
)

# Re-export all style components and functions
from common.styles import (
    # Colors
    YELLOW, YELLOW_HOVER, BLACK, WHITE, GREEN, BLUE, BLUE_HOVER,
    LIGHT_GRAY, BEIGE, RED,
    
    # EIQ Colors
    EIQ_LOW_COLOR, EIQ_MEDIUM_COLOR, EIQ_HIGH_COLOR, EIQ_EXTREME_COLOR,
    ALTERNATE_ROW_COLOR,
    
    # EIQ Thresholds
    EIQ_LOW_THRESHOLD, EIQ_MEDIUM_THRESHOLD, EIQ_HIGH_THRESHOLD,
    
    # EIQ Utility Functions
    get_eiq_color, get_eiq_rating,
    
    # Spacing and Sizes
    MARGIN_SMALL, MARGIN_MEDIUM, MARGIN_LARGE,
    SPACING_SMALL, SPACING_MEDIUM, SPACING_LARGE, SPACING_XLARGE,
    BUTTON_MIN_WIDTH, BUTTON_MIN_HEIGHT, FEATURE_BUTTON_SIZE,
    
    # Font Sizes
    TITLE_FONT_SIZE, SUBTITLE_FONT_SIZE, MEDIUM_TEXT, SMALL_TEXT,
    
    # Font Functions
    get_font, get_title_font, get_subtitle_font, get_small_font, get_medium_font, get_large_font,
    
    # Style Sheets
    FRAME_STYLE, YELLOW_BAR_STYLE, INFO_TEXT_STYLE,
    FEATURE_BUTTON_STYLE, YELLOW_BUTTON_STYLE, WHITE_BUTTON_STYLE,
    SPECIAL_BUTTON_STYLE, REMOVE_BUTTON_STYLE, GENERIC_TABLE_STYLE,
    PRODUCT_CARD_STYLE, SUGGESTIONS_CONTAINER_STYLE, SUGGESTIONS_LIST_STYLE,
    DRAGGING_ROW_STYLE, BLUE_LINE_DROP_STYLE
)

# Re-export common widgets and their functions
from common.widgets import (
    ContentFrame,
    HeaderWithHomeButton,
    ScoreBar,
    create_button,
    ProductSelectionWidget,
    ApplicationParamsWidget,
    SmartUOMComboBox
)
 
# EIQ calculation functions
from common.calculations import (
    eiq_calculator,
    format_eiq_result,
    get_impact_category
)

# UOM system components
from data.repository_UOM import (
    UOMRepository, CompositeUOM
)

# Define what gets imported with "from common import *"
__all__ = [
    # Config utilities
    'get_config', 'load_config', 'save_config', 'resource_path',
    
    # Colors
    'YELLOW', 'YELLOW_HOVER', 'BLACK', 'WHITE', 'GREEN', 'BLUE',
    'BLUE_HOVER', 'LIGHT_GRAY', 'BEIGE', 'RED',
    
    # EIQ Colors
    'EIQ_LOW_COLOR', 'EIQ_MEDIUM_COLOR', 'EIQ_HIGH_COLOR', 'EIQ_EXTREME_COLOR',
    'ALTERNATE_ROW_COLOR',
    
    # EIQ Thresholds
    'EIQ_LOW_THRESHOLD', 'EIQ_MEDIUM_THRESHOLD', 'EIQ_HIGH_THRESHOLD',
    
    # EIQ Utility Functions
    'get_eiq_color', 'get_eiq_rating',
    
    # Spacing and Sizes
    'MARGIN_SMALL', 'MARGIN_MEDIUM', 'MARGIN_LARGE',
    'SPACING_SMALL', 'SPACING_MEDIUM', 'SPACING_LARGE', 'SPACING_XLARGE',
    'BUTTON_MIN_WIDTH', 'BUTTON_MIN_HEIGHT', 'FEATURE_BUTTON_SIZE',
    
    # Font Sizes
    'TITLE_FONT_SIZE', 'SUBTITLE_FONT_SIZE', 'MEDIUM_TEXT', 'SMALL_TEXT',
    
    # Font Functions
    'get_font', 'get_title_font', 'get_subtitle_font', 'get_medium_font', 'get_small_font', 'get_large_font',
    
    # Style Sheets
    'FRAME_STYLE', 'YELLOW_BAR_STYLE', 'INFO_TEXT_STYLE',
    'FEATURE_BUTTON_STYLE', 'YELLOW_BUTTON_STYLE', 'WHITE_BUTTON_STYLE',
    'SPECIAL_BUTTON_STYLE', 'REMOVE_BUTTON_STYLE', 'GENERIC_TABLE_STYLE',
    'PRODUCT_CARD_STYLE', 'SUGGESTIONS_CONTAINER_STYLE', 'SUGGESTIONS_LIST_STYLE',
    'DRAGGING_ROW_STYLE', 'BLUE_LINE_DROP_STYLE',
    
    # Widgets and Widget Functions
    'ContentFrame', 'HeaderWithHomeButton', 'ScoreBar', 'create_button', 'ProductSelectionWidget',
    'ApplicationParamsWidget', 'SmartUOMComboBox',

    # NEW EIQ calculations
    'eiq_calculator',
    'format_eiq_result',
    'get_impact_category',
    
    # UOM system
    'UOMRepository',
    'CompositeUOM'
]