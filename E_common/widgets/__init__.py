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
from E_common.widgets.widgets import (
    ContentFrame, 
    HeaderWithHomeButton,
    create_button
)

# Import and re-export the ScoreBar
from E_common.widgets.scorebar import ScoreBar

# Define what gets imported with "from common.widgets import *"
__all__ = [
    'ContentFrame',
    'HeaderWithHomeButton',
    'ScoreBar',
    'create_button'
]