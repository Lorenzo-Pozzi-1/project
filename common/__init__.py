"""
Common components for the LORENZO POZZI Pesticide App.

This package provides common UI components, styles, and utility functions
shared across the application.
"""

# Re-export all config utilities
from common.utils import (
    get_config,
    load_config,
    save_config,
    resource_path,
    WheelProtectionFilter,
    # EIQ Utility Functions
    get_eiq_color, get_eiq_rating, get_regen_ag_class
)

# Re-export all constants
from common.constants import (
    # Colors
    YELLOW, YELLOW_HOVER, YELLOW_PRESSED,
    BLACK, WHITE, GREEN, BLUE, BLUE_HOVER,
    LIGHT_GRAY, BEIGE, RED, RED_HOVER, RED_PRESSED,
    
    # EIQ colors
    EIQ_LOW_COLOR, EIQ_MEDIUM_COLOR, EIQ_HIGH_COLOR, EIQ_EXTREME_COLOR,
    ALTERNATE_ROW_COLOR,
    
    # EIQ thresholds
    LEADING, ADVANCED, ENGAGED, ONBOARDING,
    EIQ_LOW_THRESHOLD, EIQ_MEDIUM_THRESHOLD, EIQ_HIGH_THRESHOLD,
        
    # Spacing and margins
    get_spacing_small, get_spacing_medium, get_spacing_large, get_spacing_xlarge,
    get_margin_small, get_margin_medium, get_margin_large
)

# Re-export all style components and functions
from common.styles import (
        
    # Font Functions
    get_font, get_title_font, get_subtitle_font, 
    get_medium_font, get_small_font, get_large_font,
    get_small_text_size, get_medium_text_size, get_large_text_size,
    get_title_text_size, get_subtitle_text_size,
    
    # Style Sheets
    FRAME_STYLE, YELLOW_BAR_STYLE, INFO_TEXT_STYLE,
    FEATURE_BUTTON_STYLE, YELLOW_BUTTON_STYLE, WHITE_BUTTON_STYLE,
    SPECIAL_BUTTON_STYLE, REMOVE_BUTTON_STYLE, GENERIC_TABLE_STYLE,
    PRODUCT_CARD_STYLE, FILTER_CHIP_STYLE
)

# Re-export common widgets and their functions
from common.widgets import (
    ContentFrame,
    HeaderWithHomeButton,
    ScoreBar,
    create_button,
    ProductSelectionWidget,
    ApplicationParamsWidget,
    SmartUOMSelector,
    calculation_tracer, 
    CalculationTraceDialog
)
 
# EIQ calculation functions
from common.calculations import eiq_calculator

# UOM system components
from data.repository_UOM import (
    UOMRepository, CompositeUOM
)

# Define what gets imported with "from common import *"
__all__ = [
    # Config utilities
    'get_config', 'load_config', 'save_config', 'resource_path',
    
    # Colors
    'YELLOW', 'YELLOW_HOVER', 'YELLOW_PRESSED', 
    'BLACK', 'WHITE', 'GREEN', 'BLUE', 'BLUE_HOVER',
    'LIGHT_GRAY', 'BEIGE', 'RED', 'RED_HOVER', 'RED_PRESSED',
    
    # EIQ Colors
    'EIQ_LOW_COLOR', 'EIQ_MEDIUM_COLOR', 'EIQ_HIGH_COLOR', 'EIQ_EXTREME_COLOR',
    'ALTERNATE_ROW_COLOR',
    
    # EIQ Thresholds
    'LEADING', 'ADVANCED', 'ENGAGED', 'ONBOARDING',
    'EIQ_LOW_THRESHOLD', 'EIQ_MEDIUM_THRESHOLD', 'EIQ_HIGH_THRESHOLD',
    
    # EIQ Utility Functions
    'get_eiq_color', 'get_eiq_rating', 'get_regen_ag_class',
            
    # Font Functions
    'get_font', 'get_title_font', 'get_subtitle_font', 'get_medium_font', 'get_small_font', 'get_large_font',
    'get_small_text_size', 'get_medium_text_size', 'get_large_text_size',
    'get_title_text_size', 'get_subtitle_text_size',

    # Spacing and margins
    'get_spacing_small', 'get_spacing_medium', 'get_spacing_large', 'get_spacing_xlarge',
    'get_margin_small', 'get_margin_medium', 'get_margin_large',
    
    # Style Sheets
    'FRAME_STYLE', 'YELLOW_BAR_STYLE', 'INFO_TEXT_STYLE',
    'FEATURE_BUTTON_STYLE', 'YELLOW_BUTTON_STYLE', 'WHITE_BUTTON_STYLE',
    'SPECIAL_BUTTON_STYLE', 'REMOVE_BUTTON_STYLE', 'GENERIC_TABLE_STYLE',
    'PRODUCT_CARD_STYLE', 'FILTER_CHIP_STYLE',
    
    # Widgets and Widget Functions
    'ContentFrame', 'HeaderWithHomeButton', 'ScoreBar', 'create_button', 
    'ProductSelectionWidget', 'ApplicationParamsWidget', 'SmartUOMSelector',
    'calculation_tracer', 'CalculationTraceDialog',
    
    # NEW EIQ calculations
    'eiq_calculator',
    
    # UOM system
    'UOMRepository',
    'CompositeUOM'
]