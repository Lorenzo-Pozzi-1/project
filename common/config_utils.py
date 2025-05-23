"""
Configuration management for the Lorenzo Pozzi Pesticide App.

This module handles loading, saving, and accessing application configuration.
"""

import json, os, sys
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    "user_preferences": {
        "default_country": "Canada",
        "default_region": "None of these",
        "default_row_spacing": 34.0,
        "default_row_spacing_unit": "inch",
        "default_seeding_rate": 2000,
        "default_seeding_rate_unit": "kg/ha",
    }
}

# Configuration file path
CONFIG_FILE = "config.json"

def load_config():
    """
    Load configuration from file or create default if it doesn't exist.
    
    Returns:
        dict: The application configuration
    """
    config_path = Path(CONFIG_FILE)
    
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
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)
        return True
    except IOError as e:
        print(f"Error saving config: {e}")
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