"""
Utility functions for the Lorenzo Pozzi Pesticide App.

This module handles mostly application configuration, plus resources paths generation.
"""

import json, os, sys
from pathlib import Path
from PySide6.QtCore import QObject, QEvent

# Default configuration
DEFAULT_CONFIG = {
    "user_preferences": {
        "default_country": "Canada",
        "default_region": "None of these",
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
        config_path = os.path.join(exe_dir, "config.json")
        
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
            return os.path.join(app_config_dir, "config.json")
    else:
        # Running in development - use current directory
        return "config.json"

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
            print(f"Error loading config: {e}")
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
        print(f"Error saving config to {config_path}: {e}")
        
        # Fallback: try saving to a temp directory
        try:
            import tempfile
            temp_dir = tempfile.gettempdir()
            fallback_path = os.path.join(temp_dir, "mccain_pesticides_config.json")
            print(f"Trying fallback location: {fallback_path}")
            
            with open(fallback_path, 'w') as file:
                json.dump(config, file, indent=4)
            print(f"Config saved to fallback location: {fallback_path}")
            return True
        except Exception as fallback_error:
            print(f"Fallback save also failed: {fallback_error}")
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