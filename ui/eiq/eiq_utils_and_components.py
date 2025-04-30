"""
EIQ Utilities and Shared Components for the LORENZO POZZI Pesticide App.

This module provides common utilities and UI components for EIQ calculations 
across different EIQ calculator components, with enhanced unit of measure (UOM) management.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QFrame, QScrollArea, QTableWidgetItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush

from ui.common.styles import (
    get_title_font, get_subtitle_font, get_body_font,
    EIQ_LOW_COLOR, EIQ_MEDIUM_COLOR, EIQ_HIGH_COLOR
)
from ui.common.widgets import ToxicityBar

from data.products_data import load_products, get_product_by_name

#------------------------
# UOM Conversion Functions
#------------------------

# Application rate conversion factors to lb/acre (standard for EIQ calculation)
APPLICATION_RATE_CONVERSION = {
    # Imperial units to lb/acre
    "lbs/acre": 1.0,      # Base unit
    "oz/acre": 1/16.0,    # 16 oz = 1 pound
    "fl oz/acre": 1/16.0, # Assuming density of 1.0 for liquids
    "pints/acre": 1.0,    # Assumption: 1 pint = 1 pound
    "quarts/acre": 2.0,   # Assumption: 1 quart = 2 pounds
    "gal/acre": 8.0,      # Assumption: 1 gallon = 8 pounds
    
    # Metric units to lb/acre
    "kg/ha": 0.892,       # 1 kg/ha = 0.892 lbs/acre
    "g/ha": 0.000892,     # 1 g/ha = 0.000892 lbs/acre
    "l/ha": 0.892,        # Assumption: 1 L/ha = 0.892 lbs/acre (density of 1.0)
    "ml/ha": 0.000892,    # 1 ml/ha = 0.000892 lbs/acre (density of 1.0)
}

# AI concentration conversion factors to decimal (for percentage calculations)
CONCENTRATION_CONVERSION = {
    "%": 0.01,            # Direct percentage (e.g., 50% = 0.5)
    "g/l": 0.001,         # Approximate conversion (e.g., 500 g/L ≈ 0.5 or 50%)
    "g/kg": 0.001,        # Direct conversion (e.g., 500 g/kg = 0.5 or 50%)
    "ppm": 0.000001,      # Parts per million (e.g., 1000 ppm = 0.001 or 0.1%)
    "w/w": 1.0,           # Already in decimal form (e.g., 0.5 w/w = 0.5 or 50%)
    "w/v": 1.0,           # Already in decimal form (e.g., 0.5 w/v = 0.5 or 50%)
}

def convert_application_rate(rate, from_unit, to_unit="lbs/acre"):
    """
    Convert application rate from one unit to another.
    
    Args:
        rate (float): Application rate value
        from_unit (str): Source unit of measure
        to_unit (str): Target unit of measure (default: lbs/acre for EIQ calculation)
    
    Returns:
        float: Converted application rate
    """
    if rate is None:
        return None
        
    if from_unit == to_unit:
        return rate
        
    try:
        # Convert to standard unit (lbs/acre)
        if from_unit in APPLICATION_RATE_CONVERSION:
            standard_rate = rate * APPLICATION_RATE_CONVERSION[from_unit]
            
            # If target is not the standard unit, convert to target
            if to_unit != "lbs/acre" and to_unit in APPLICATION_RATE_CONVERSION:
                return standard_rate / APPLICATION_RATE_CONVERSION[to_unit]
            
            return standard_rate
    except (ValueError, TypeError, ZeroDivisionError) as e:
        print(f"Error converting application rate: {e}")
        
    # Default return if conversion fails
    return rate

def convert_concentration_to_decimal(concentration, uom):
    """
    Convert concentration to decimal value (0-1) based on unit of measure.
    
    Args:
        concentration (float): Concentration value
        uom (str): Unit of measure for concentration
        
    Returns:
        float or None: Concentration as decimal (0-1)
    """
    if concentration is None:
        return None
        
    try:
        # Handle different UOMs using the conversion factors
        if uom in CONCENTRATION_CONVERSION:
            return float(concentration) * CONCENTRATION_CONVERSION[uom]
        else:
            # Default: assume value is already in percent
            return float(concentration) * 0.01
    except (ValueError, TypeError):
        return None

def convert_eiq_units(eiq_value, application_rate, rate_uom, ai_concentration, concentration_uom, applications=1):
    """
    Prepare all units for EIQ calculation to ensure mathematical correctness.
    
    Args:
        eiq_value (float): Base EIQ value for active ingredient [EIQ/lb of AI]
        application_rate (float): Application rate in original units
        rate_uom (str): Unit of measure for application rate
        ai_concentration (float): Active ingredient concentration in original units
        concentration_uom (str): Unit of measure for AI concentration
        applications (int): Number of applications
        
    Returns:
        tuple: (standardized_eiq, standardized_rate, standardized_concentration)
            All values standardized for calculation in the base formula
    """
    # Convert application rate to standard unit (lbs/acre)
    std_rate = convert_application_rate(application_rate, rate_uom)
    
    # Convert AI concentration to decimal (0-1)
    std_concentration = convert_concentration_to_decimal(ai_concentration, concentration_uom)
    
    # EIQ value remains unchanged (already in EIQ/lb)
    std_eiq = eiq_value
    
    return (std_eiq, std_rate, std_concentration)

#------------------------
# EIQ Calculation Functions
#------------------------

def calculate_field_eiq(ai_eiq, ai_percent, rate, unit, applications=1):
    """
    Calculate Field EIQ based on product data and application parameters.
    
    Args:
        ai_eiq (float): Active ingredient EIQ value
        ai_percent (float): Active ingredient percentage (0-100)
        rate (float): Application rate
        unit (str): Unit of measure for rate
        applications (int): Number of applications
        
    Returns:
        float: Field EIQ value
    """
    try:
        # Use the new conversion function to standardize units
        std_eiq, std_rate, _ = convert_eiq_units(
            ai_eiq, rate, unit, ai_percent, "%", applications)
        
        # Convert percentage to decimal (0-1)
        ai_decimal = ai_percent / 100.0
        
        # Calculate Field EIQ with standardized units
        field_eiq = std_eiq * ai_decimal * std_rate * applications
        return field_eiq
    
    except (ValueError, ZeroDivisionError, TypeError) as e:
        print(f"Error calculating Field EIQ: {e}")
        return 0.0

def calculate_product_field_eiq(active_ingredients, rate, unit, applications=1):
    """
    Calculate total Field EIQ for a product with multiple active ingredients.
    
    Args:
        active_ingredients (list): List of dictionaries with 'eiq', 'percent', and 'name' keys
        rate (float): Application rate
        unit (str): Unit of measure for rate
        applications (int): Number of applications
        
    Returns:
        float: Total Field EIQ value for the product
    """
    if not active_ingredients:
        return 0.0
        
    # Convert application rate to standard unit (lbs/acre)
    std_rate = convert_application_rate(rate, unit)
    
    # Sum contributions from all active ingredients
    total_field_eiq = 0.0
    
    for ai in active_ingredients:
        # Skip AIs with missing data
        if not ai or 'eiq' not in ai or 'percent' not in ai:
            continue
            
        # Handle case where eiq or percent might be stored as strings or have "--" placeholder
        if ai['eiq'] == "--" or ai['percent'] == "--":
            continue
            
        try:
            # Convert values to float if stored as string
            ai_eiq = float(ai['eiq']) if isinstance(ai['eiq'], str) else ai['eiq']
            
            # Handle percent that might be stored with "%" suffix
            percent_str = str(ai['percent'])
            percent_value = float(percent_str.replace('%', '')) if '%' in percent_str else float(ai['percent'])
            
            # Convert percentage to decimal (0-1)
            ai_decimal = percent_value / 100.0
            
            # Calculate and add Field EIQ for this active ingredient using standardized rate
            ai_field_eiq = ai_eiq * ai_decimal * std_rate
            total_field_eiq += ai_field_eiq
            
        except (ValueError, TypeError) as e:
            print(f"Error calculating EIQ for active ingredient {ai.get('name', 'unknown')}: {e}")
            # Skip this ingredient but continue with others
            continue
    
    # Multiply by number of applications
    return total_field_eiq * applications

def convert_concentration_to_percent(concentration, uom):
    """
    Convert concentration to percentage based on unit of measure.
    
    Args:
        concentration (float): Concentration value
        uom (str): Unit of measure for concentration
        
    Returns:
        float or None: Concentration as percentage (0-100)
    """
    # Get decimal value and convert to percentage
    decimal_value = convert_concentration_to_decimal(concentration, uom)
    if decimal_value is not None:
        return decimal_value * 100
    return None

def get_products_from_csv():
    """
    Load products from CSV data.
    If CSV data is not available, return an empty list.
    """
    try:
        products = load_products()
        return products
    except Exception as e:
        print(f"Error loading products from CSV: {e}")
        return []

def get_product_display_names():
    """
    Get a list of product display names from CSV data.
    """
    products = get_products_from_csv()
    if products:
        # Use display_name property if available
        return ["Select a product..."] + [p.display_name for p in products]
    return ["Select a product..."]

def get_product_info(product_name):
    """
    Get product information from CSV
    
    Args:
        product_name (str): Name of the product
        
    Returns:
        dict: Product data containing ai1_eiq, ai_percent, etc.
    """
    # First try to get product from CSV
    product = get_product_by_name(product_name.split(" (")[0])
    
    if product:
        # Now using AI1 EIQ instead of base EIQ
        ai1_eiq = product.ai1_eiq if product.ai1_eiq is not None else 0.0
        
        # Get concentration and convert to percent based on UOM
        ai_percent = 0.0
        if product.ai1_concentration is not None:
            ai_percent = convert_concentration_to_percent(
                product.ai1_concentration, 
                product.ai1_concentration_uom
            ) or 0.0
        
        # Use maximum rate if available, otherwise minimum rate
        if product.label_maximum_rate is not None:
            rate = product.label_maximum_rate
        elif product.label_minimum_rate is not None:
            rate = product.label_minimum_rate
        else:
            rate = 0.0
            
        unit = product.rate_uom or "lbs/acre"
        
        return {
            "ai1_eiq": ai1_eiq,
            "ai_percent": ai_percent,
            "default_rate": rate,
            "default_unit": unit
        }
    
    # Default values if product not found
    return {
        "ai1_eiq": 0.0,
        "ai_percent": 0.0,
        "default_rate": 0.0,
        "default_unit": "lbs/acre"
    }

def get_impact_category(field_eiq):
    """
    Get the impact category and color based on Field EIQ value.
    
    Args:
        field_eiq (float): Field EIQ value
        
    Returns:
        tuple: (rating, color) where rating is a string and color is a hex code
    """
    if field_eiq < 33.3:
        return "Low Environmental Impact", "#E6F5E6"  # Light green
    elif field_eiq < 66.6:
        return "Moderate Environmental Impact", "#FFF5E6"  # Light yellow
    else:
        return "High Environmental Impact", "#F5E6E6"  # Light red

def format_eiq_result(field_eiq):
    """Format EIQ results for display, including per-acre and per-ha values."""
    field_eiq_per_ha = field_eiq * 2.47
    return f"{field_eiq:.2f} /acre = {field_eiq_per_ha:.2f} /ha"

def get_eiq_color(eiq_value, low_threshold=33.3, high_threshold=66.6):
    """Get color for EIQ value based on thresholds."""
    if eiq_value < low_threshold:
        return EIQ_LOW_COLOR
    elif eiq_value < high_threshold:
        return EIQ_MEDIUM_COLOR
    else:
        return EIQ_HIGH_COLOR

#------------------------
# UI Components
#------------------------

class ProductSearchField(QWidget):
    """A custom search field with suggestions displayed underneath."""
    
    # Signal emitted when a product is selected
    product_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_items = []  # All available products
        self.filtered_items = []  # Filtered products based on search
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Search field
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Type to search products...")
        self.search_field.setFont(get_body_font())
        self.search_field.textChanged.connect(self.update_suggestions)
        layout.addWidget(self.search_field)
        
        # Suggestions container
        self.suggestions_container = QFrame()
        self.suggestions_container.setFrameStyle(QFrame.StyledPanel)
        self.suggestions_container.setStyleSheet("""
            QFrame {
                border: 1px solid #CCCCCC;
                border-top: none;
                background-color: white;
            }
        """)
        
        # Scroll area for suggestions to handle large lists
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Suggestions list
        self.suggestions_list = QListWidget()
        self.suggestions_list.setFrameStyle(QFrame.NoFrame)
        self.suggestions_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.suggestions_list.setStyleSheet("""
            QListWidget {
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #F5F5F5;
            }
            QListWidget::item:selected {
                background-color: #E0E0E0;
            }
        """)
        self.suggestions_list.itemClicked.connect(self.select_suggestion)
        scroll_area.setWidget(self.suggestions_list)
        
        # Add scroll area to suggestions container
        suggestions_layout = QVBoxLayout(self.suggestions_container)
        suggestions_layout.setContentsMargins(0, 0, 0, 0)
        suggestions_layout.addWidget(scroll_area)
        
        # Add suggestions container to main layout
        layout.addWidget(self.suggestions_container)
        
        # Initially hide suggestions
        self.suggestions_container.setVisible(False)
    
    def update_suggestions(self, text):
        """Update suggestions based on input text."""
        # Clear selection when search text changes
        self.suggestions_list.clearSelection()
        
        if not text:
            # Hide suggestions when search field is empty
            self.suggestions_container.setVisible(False)
            return
        
        # Filter items based on search text
        self.filtered_items = [
            item for item in self.all_items 
            if text.lower() in item.lower()
        ]
        
        # Update suggestions list
        self.suggestions_list.clear()
        self.suggestions_list.addItems(self.filtered_items)
        
        # Show suggestions if there are any matches
        has_suggestions = len(self.filtered_items) > 0
        self.suggestions_container.setVisible(has_suggestions)
        
        # Set fixed height based on number of items
        if has_suggestions:
            item_height = self.suggestions_list.sizeHintForRow(0)
            num_visible_items = min(8, len(self.filtered_items))
            list_height = item_height * num_visible_items + 4
            self.suggestions_list.setFixedHeight(list_height)
    
    def select_suggestion(self, item):
        """Handle selection of a suggestion."""
        selected_text = item.text()
        self.search_field.setText(selected_text)
        self.suggestions_container.setVisible(False)
        self.product_selected.emit(selected_text)
    
    def set_items(self, items):
        """Set the full list of available items."""
        self.all_items = items
        self.update_suggestions(self.search_field.text())
    
    def clear(self):
        """Clear the search field and hide suggestions."""
        self.search_field.clear()
        self.suggestions_container.setVisible(False)

class EiqResultDisplay(QWidget):
    """A widget for displaying EIQ results with toxicity bar and rating."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignCenter)
        
        # Results title
        results_title = QLabel("EIQ Results")
        results_title.setFont(get_subtitle_font(size=16))
        layout.addWidget(results_title)
        
        # Field EIQ result layout
        field_eiq_layout = QHBoxLayout()
        field_eiq_label = QLabel("Field EIQ:")
        field_eiq_label.setFont(get_body_font(size=14, bold=True))
        
        # Single label for the entire result with consistent formatting
        self.field_eiq_result = QLabel("-- acre = -- ha")
        self.field_eiq_result.setFont(get_body_font(size=16, bold=True))
        
        field_eiq_layout.addWidget(field_eiq_label)
        field_eiq_layout.addWidget(self.field_eiq_result)
        field_eiq_layout.addStretch(1)
        
        layout.addLayout(field_eiq_layout)
        
        # Toxicity bar (replacing the gauge)
        self.toxicity_bar = ToxicityBar(
            low_threshold=33.3,  # Adjust based on your EIQ thresholds
            high_threshold=66.6  # Adjust based on your EIQ thresholds
        )
        layout.addWidget(self.toxicity_bar)
    
    def update_result(self, field_eiq):
        """Update the EIQ result display with the calculated value."""
        if field_eiq <= 0:
            self.field_eiq_result.setText("-- acre = -- ha")
            self.toxicity_bar.set_value(0, "No calculation")
            return
            
        # Format result with per-acre and per-ha values
        self.field_eiq_result.setText(format_eiq_result(field_eiq))
        
        # Update toxicity bar
        rating, _ = get_impact_category(field_eiq)
        self.toxicity_bar.set_value(field_eiq, rating)

class ColorCodedEiqItem(QTableWidgetItem):
    """A table item specifically for EIQ values with automatic color coding."""
    
    def __init__(self, eiq_value, low_threshold=33.3, high_threshold=66.6):
        """
        Initialize with EIQ value and thresholds.
        
        Args:
            eiq_value (float): The EIQ value to display
            low_threshold (float): Values below this are considered "low impact"
            high_threshold (float): Values above this are considered "high impact"
        """
        if isinstance(eiq_value, (int, float)):
            display_value = f"{eiq_value:.1f}"
        else:
            display_value = str(eiq_value)
            
        super().__init__(display_value)
        
        self.setTextAlignment(Qt.AlignCenter)
        
        # Apply color coding based on thresholds
        try:
            value_float = float(eiq_value)
            self.setBackground(QBrush(get_eiq_color(value_float, low_threshold, high_threshold)))
        except (ValueError, TypeError):
            # If value can't be converted to float, don't apply color
            pass