"""
Configuration management for the Lorenzo Pozzi Pesticide App.

This module handles loading, saving, and accessing application configuration.
"""

import os
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


def get_config_value(config, key, default=None):
    """
    Get a configuration value with a fallback default.
    
    Args:
        config (dict): The configuration dictionary
        key (str): The configuration key to retrieve
        default: The default value if key is not found
    
    Returns:
        The configuration value or default
    """
    return config.get(key, default)


def update_config_value(config, key, value):
    """
    Update a configuration value and save the configuration.
    
    Args:
        config (dict): The configuration dictionary
        key (str): The configuration key to update
        value: The new value
    
    Returns:
        bool: True if successful, False otherwise
    """
    config[key] = value
    return save_config(config)