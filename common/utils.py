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


class PreferencesManager:
    """
    Centralized preferences manager that handles safe section-based updates.
    
    This prevents different parts of the application from overwriting each other's
    preferences when saving to the JSON file.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the preferences manager."""
        if self._initialized:
            return
        self._config_cache = None
        self._cache_dirty = False  # Track if cache has unsaved changes
        self._initialized = True
    
    def _get_current_config(self):
        """Get the current configuration (from cache if dirty, otherwise fresh from disk)."""
        if self._cache_dirty and self._config_cache is not None:
            return self._config_cache
        else:
            config = self._load_fresh_config()
            self._config_cache = config.copy()
            self._cache_dirty = False
            return config
    
    def _load_fresh_config(self):
        """Load the configuration from disk, bypassing any cache."""
        try:
            config_path = get_config_file_path()
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    return json.load(file)
            else:
                return DEFAULT_CONFIG.copy()
        except (IOError, OSError, json.JSONDecodeError):
            return DEFAULT_CONFIG.copy()
        """Load the configuration from disk, bypassing any cache."""
        try:
            config_path = get_config_file_path()
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    return json.load(file)
            else:
                return DEFAULT_CONFIG.copy()
        except (IOError, OSError, json.JSONDecodeError):
            return DEFAULT_CONFIG.copy()
    
    def get_preference(self, section, key, default=None):
        """
        Get a specific preference value.
        
        Args:
            section (str): The preference section (e.g., 'user_preferences', 'STIR_preferences')
            key (str): The preference key
            default: The default value if not found
            
        Returns:
            The preference value or default
        """
        config = self._get_current_config()
        section_data = config.get(section, {})
        return section_data.get(key, default)
    
    def get_section(self, section, default=None):
        """
        Get an entire preference section.
        
        Args:
            section (str): The preference section name
            default: The default value if section doesn't exist
            
        Returns:
            dict: The section data or default
        """
        config = self._get_current_config()
        return config.get(section, default if default is not None else {})
    
    def set_preference(self, section, key, value, auto_save=False):
        """
        Set a specific preference value.
        
        Args:
            section (str): The preference section
            key (str): The preference key
            value: The value to set
            auto_save (bool): Whether to automatically save to disk
            
        Returns:
            bool: True if successful (when auto_save=True)
        """
        config = self._get_current_config()
        
        if section not in config:
            config[section] = {}
        
        config[section][key] = value
        self._config_cache = config
        self._cache_dirty = True
        
        if auto_save:
            return self._save_config(config)
        return True
    
    def set_section(self, section, data, auto_save=False):
        """
        Set an entire preference section.
        
        Args:
            section (str): The preference section name
            data (dict): The section data
            auto_save (bool): Whether to automatically save to disk
            
        Returns:
            bool: True if successful (when auto_save=True)
        """
        config = self._get_current_config()
        config[section] = data.copy()
        
        # Store in cache and mark as dirty
        self._config_cache = config
        self._cache_dirty = True
        
        if auto_save:
            return self._save_config(config)
        return True
    
    def save(self):
        """
        Manually save the current configuration to disk.
        
        Returns:
            bool: True if successful, False otherwise
        """
        config = self._get_current_config()
        result = self._save_config(config)
        if result:
            self._cache_dirty = False  # Mark cache as clean after successful save
        return result
    
    def _save_config(self, config):
        """
        Internal method to save configuration to disk.
        
        Args:
            config (dict): The configuration to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            config_path = get_config_file_path()
            
            # Ensure the directory exists
            config_dir = os.path.dirname(config_path)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            
            with open(config_path, 'w') as file:
                json.dump(config, file, indent=4)
            
            # Update cache after successful save
            self._config_cache = config.copy()
            self._cache_dirty = False
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
                
                # Update cache after successful fallback save
                self._config_cache = config.copy()
                self._cache_dirty = False
                return True
            except Exception as fallback_error:
                QMessageBox.critical(None, "Critical Error", f"Failed to save config: {fallback_error}")
                return False


# Global instance
_preferences_manager = PreferencesManager()


def get_preferences_manager():
    """Get the global preferences manager instance."""
    return _preferences_manager


def set_preference(section, key, value, auto_save=False):
    """
    Helper function to set a preference using the preferences manager.
    
    Args:
        section (str): The preference section (e.g., 'user_preferences', 'STIR_preferences')
        key (str): The preference key
        value: The value to set
        auto_save (bool): Whether to automatically save to disk
        
    Returns:
        bool: True if successful (when auto_save=True)
    """
    return _preferences_manager.set_preference(section, key, value, auto_save)


def get_preference(section, key, default=None):
    """
    Helper function to get a preference using the preferences manager.
    
    Args:
        section (str): The preference section
        key (str): The preference key
        default: The default value if not found
        
    Returns:
        The preference value or default
    """
    return _preferences_manager.get_preference(section, key, default)


def save_preferences():
    """
    Helper function to manually save all preferences to disk.
    
    Returns:
        bool: True if successful, False otherwise
    """
    return _preferences_manager.save()

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
        _preferences_manager._save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
    
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

def open_user_manual(parent=None):
    """Open the user manual in the system's default web browser."""
    return open_html_in_browser(
        html_file_path="user_manual/user_manual.html",
        temp_prefix="pesticides_manual_",
        parent=parent,
        error_title="User Manual Error"
    )

def open_learning_materials(parent=None):
    """Open the learning materials in the system's default web browser."""
    return open_html_in_browser(
        html_file_path="main_page/learning_materials.html",
        temp_prefix="eiq_stir_materials_",
        parent=parent,
        error_title="Learning Materials Error"
    )

def open_html_in_browser(html_file_path, temp_prefix, parent=None, error_title="Error"):
    """
    Generic function to open an HTML file in the system's default web browser.
    
    Args:
        html_file_path (str): Relative path to the HTML file
        temp_prefix (str): Prefix for temporary directory
        parent: Parent widget for error dialogs
        error_title (str): Title for error dialogs
        
    Returns:
        bool: True if successful, False otherwise
    """
    import webbrowser
    import tempfile
    import shutil
    
    try:
        # Get the HTML file path
        file_path = resource_path(html_file_path)
        
        if not os.path.exists(file_path):
            show_generic_error_message(parent, f"{os.path.basename(html_file_path)} file not found.", error_title)
            return False
            
        # Get the directory to copy associated assets
        source_dir = os.path.dirname(file_path)
        
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp(prefix=temp_prefix)
        
        # Copy the entire directory to temp location
        # This ensures CSS, JS, images, and other assets are included
        temp_content_dir = os.path.join(temp_dir, "content")
        shutil.copytree(source_dir, temp_content_dir)
        
        # Path to the copied HTML file
        temp_html_path = os.path.join(temp_content_dir, os.path.basename(html_file_path))
        
        # Open in browser
        webbrowser.open(f"file://{temp_html_path}")
        
        return True
        
    except Exception as e:
        show_generic_error_message(parent, f"Failed to open {os.path.basename(html_file_path)}: {str(e)}", error_title)
        return False

def show_generic_error_message(parent, message, title="Error"):
    """Generic error message dialog."""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec()