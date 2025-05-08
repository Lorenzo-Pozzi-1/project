"""
Configuration management for the Lorenzo Pozzi Pesticide App.

This module handles loading, saving, and accessing application configuration.
"""

import json
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    "data_directory": "data",
    "theme": "light",
    "auto_save": True,
    "backup_count": 5,
    "last_view": "products"
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
                merged_config = DEFAULT_CONFIG.copy()
                merged_config.update(config)
                return merged_config
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