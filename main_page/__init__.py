"""
Main window package for the LORENZO POZZI Pesticide App.

This package provides the main application window and home page.
"""

from main_page.window_main import MainWindow
from main_page.page_home import HomePage

# Import widgets
from main_page.widget_preferences_row import PreferencesRow

__all__ = [
    # Main page components
    'MainWindow', 
    'HomePage',
    
    # Widget components
    'PreferencesRow'
]