"""
Utility functions for the Lorenzo Pozzi EIQ App.

This module handles mostly application configuration, plus resources paths generation.
"""

import json, os, sys
from pathlib import Path
from PySide6.QtCore import QObject, QEvent
from PySide6.QtWidgets import QMessageBox
from common.constants import (ADVANCED, EIQ_EXTREME_COLOR, EIQ_HIGH_COLOR, EIQ_HIGH_THRESHOLD, 
                              EIQ_LOW_COLOR, EIQ_MEDIUM_COLOR, ENGAGED, LEADING, ONBOARDING, 
                              EIQ_MEDIUM_THRESHOLD, EIQ_LOW_THRESHOLD)

# Default configuration
DEFAULT_CONFIG = {
    "user_preferences": {
        "default_country": "Canada",
        "default_region": "New Brunswick",
        "default_row_spacing": 34.0,
        "default_row_spacing_unit": "inch",
        "default_seeding_rate": 20,
        "default_seeding_rate_unit": "cwt/acre",
    }
}

def get_config_file_path():
    """
    Get the appropriate path for the config file.
    Uses a writable location that works for both dev and compiled versions.
    
    Returns:
        str: Path to the config file
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # Get the directory where the executable is located
        exe_dir = os.path.dirname(sys.executable)
        config_path = os.path.join(exe_dir, "user_preferences.json")
        
        # Test if we can write to the exe directory
        try:
            test_file = os.path.join(exe_dir, "test_write.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return config_path
        except (OSError, IOError):
            # Can't write to exe directory, use user's home directory
            home_dir = os.path.expanduser("~")
            app_config_dir = os.path.join(home_dir, ".project")
            os.makedirs(app_config_dir, exist_ok=True)
            return os.path.join(app_config_dir, "user_preferences.json")
    else:
        # Running in development - use current directory
        return "user_preferences.json"

def load_config():
    """
    Load configuration from file or create default if it doesn't exist.
    
    Returns:
        dict: The application configuration
    """
    config_path = Path(get_config_file_path())
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as file:
                config = json.load(file)
                
                # Merge with default config to ensure all keys exist
                # (in case the config file is from an older version)
                return {**DEFAULT_CONFIG, **config}
        except (json.JSONDecodeError, IOError) as e:
            QMessageBox.warning(None, "Error", f"Error loading config: {e}")
            return DEFAULT_CONFIG
    else:
        # Create default config file
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    """
    Save configuration to file.
    
    Args:
        config (dict): The configuration to save
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        config_path = get_config_file_path()
        
        # Ensure the directory exists
        config_dir = os.path.dirname(config_path)
        if config_dir:  # Only create if there's actually a directory part
            os.makedirs(config_dir, exist_ok=True)
        
        with open(config_path, 'w') as file:
            json.dump(config, file, indent=4)
        return True
    except (IOError, OSError) as e:
        QMessageBox.warning(None, "Error", f"Error saving config to {config_path}: {e}")

        # Fallback: try saving to a temp directory
        try:
            import tempfile
            temp_dir = tempfile.gettempdir()
            fallback_path = os.path.join(temp_dir, "mccain_pesticides_config.json")
            QMessageBox.warning(None, "Warning", f"Trying fallback location: {fallback_path}")
            
            with open(fallback_path, 'w') as file:
                json.dump(config, file, indent=4)
            QMessageBox.warning(None, "Warning", f"Config saved to fallback location: {fallback_path}")
            return True
        except Exception as fallback_error:
            QMessageBox.critical(None, "Critical Error", f"Failed to save config: {fallback_error}")
            return False

def get_config(key, default=None):
    """
    Get a configuration value.
    
    Args:
        key (str): The configuration key
        default: The default value if the key doesn't exist
    
    Returns:
        The configuration value or default
    """
    config = load_config()
    return config.get(key, default)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class WheelProtectionFilter(QObject):
    """Prevents widgets from changing values when scrolling without clicking first."""
    
    def __init__(self) -> None:
        super().__init__()
        self.clicked_widgets = set()  # Track which widgets have been clicked

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        # Track widgets that have been clicked
        if event.type() in (QEvent.MouseButtonPress, QEvent.KeyPress):
            self.clicked_widgets.add(obj)
        
        # Block wheel events for widgets that haven't been clicked
        elif event.type() == QEvent.Wheel and obj not in self.clicked_widgets:
            return True  # Block the event
        
        # Reset clicked state when dropdown closes or focus is lost
        elif event.type() == QEvent.Hide and hasattr(obj, 'view'):
            self.clicked_widgets.discard(obj)
        elif event.type() == QEvent.FocusOut:
            self.clicked_widgets.discard(obj)
        
        # Let other events pass through
        return super().eventFilter(obj, event)
    
# ----------------------
# EIQ UTILITY FUNCTIONS
# ----------------------

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

def get_regen_ag_class(eiq_value) -> str:
        """
        Get regenerative agriculture framework class based on EIQ value.
        
        Args:
            eiq_value (float): The EIQ value
            
        Returns:
            str: The framework class ("Leading", "Advanced", "Engaged", "Onboarding")
        """
        if eiq_value < LEADING:
            return "Leading"
        elif eiq_value < ADVANCED:
            return "Advanced"
        elif eiq_value < ENGAGED:
            return "Engaged"
        elif eiq_value < ONBOARDING:
            return "Onboarding"
        else:
            return "Out of range"