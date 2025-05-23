"""
Common widgets for the LORENZO POZZI Pesticide App.

This package contains reusable UI components used throughout the application.
All widgets are made available at the package level for easy importing.

Usage:
    # Import specific widgets
    from common.widgets import ContentFrame, ScoreBar
    
    # Import all widgets
    from common.widgets import *
"""

# Import and re-export the ContentFrame and HeaderWithHomeButton
from common.widgets.header_and_frame import (
    ContentFrame, 
    HeaderWithHomeButton,
    create_button
)

# Import and re-export the ProductSelectionWidget
from common.widgets.product_selection import ProductSelectionWidget

# Import and re-export the ApplicationParamsWidget
from common.widgets.application_params import ApplicationParamsWidget

# Import and re-export the ScoreBar
from common.widgets.scorebar import ScoreBar

# Import and re-export the SmartUOMComboBox
from common.widgets.SmartUOMComboBox import SmartUOMComboBox

# Define what gets imported with "from common.widgets import *"
__all__ = [
    'ContentFrame',
    'HeaderWithHomeButton',
    'ScoreBar',
    'create_button',
    'ProductSelectionWidget',
    'ApplicationParamsWidget',
    'SmartUOMComboBox'
]