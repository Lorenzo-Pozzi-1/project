"""
EIQ styling constants and utility functions for the LORENZO POZZI Pesticide App.

This module provides styling constants and helper functions for EIQ calculations.
"""

from PySide6.QtGui import QColor

# EIQ threshold constants
LOW_THRESHOLD = 33.3
MEDIUM_THRESHOLD = 66.6
HIGH_THRESHOLD = 100.0

# EIQ color constants
EIQ_LOW_COLOR = QColor(50, 205, 50)      # Green
EIQ_MEDIUM_COLOR = QColor(255, 165, 0)   # Orange
EIQ_HIGH_COLOR = QColor(255, 0, 0)       # Red
EIQ_EXTREME_COLOR = QColor(139, 0, 0)    # Dark Red

def get_eiq_color(eiq_value, low_threshold=LOW_THRESHOLD, 
                  medium_threshold=MEDIUM_THRESHOLD, high_threshold=HIGH_THRESHOLD):
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

def get_eiq_rating(eiq_value, low_threshold=LOW_THRESHOLD, 
                  medium_threshold=MEDIUM_THRESHOLD, high_threshold=HIGH_THRESHOLD):
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