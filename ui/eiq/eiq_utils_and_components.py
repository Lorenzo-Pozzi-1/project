"""
EIQ Utilities and Shared Components for the LORENZO POZZI Pesticide App.

This module provides common utilities and UI components for EIQ calculations 
across different EIQ calculator components.
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

# Unit conversion factors for EIQ calculations
UNIT_CONVERSION = {
    "quarts/acre": 2.0,    # Assumption: 1 quart = 2 pounds
    "pints/acre": 1.0,     # Assumption: 1 pint = 1 pound
    "fl oz/acre": 1/16.0,  # 16 fl oz = 1 pound
    "oz/acre": 1/16.0,     # 16 oz = 1 pound
    "lbs/acre": 1.0,
    "kg/ha": 0.892         # 1 kg/ha = 0.892 lbs/acre
}

#------------------------
# Utility Functions
#------------------------

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
            # If the concentration UOM is already in percent, use it directly
            if product.ai1_concentration_uom == '%':
                ai_percent = product.ai1_concentration
            # Otherwise, handle other UOMs (this would need expansion based on your data)
            elif product.ai1_concentration_uom == 'g/l':
                # Example conversion: g/l to percent (this may need to be updated)
                ai_percent = product.ai1_concentration / 10.0
            else:
                # Default assumption that concentration is in percent
                ai_percent = product.ai1_concentration
        
        if product.label_suggested_rate is not None:
            rate = product.label_suggested_rate
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
        # Convert to decimal
        ai_decimal = ai_percent / 100.0
        
        # Convert rate to pounds/acre based on unit
        if unit in UNIT_CONVERSION:
            rate_in_pounds = rate * UNIT_CONVERSION[unit]
        else:
            # Default if unit not recognized
            rate_in_pounds = rate
        
        # Calculate Field EIQ
        field_eiq = ai_eiq * ai_decimal * rate_in_pounds * applications
        return field_eiq
    
    except (ValueError, ZeroDivisionError, TypeError) as e:
        print(f"Error calculating Field EIQ: {e}")
        return 0.0

def calculate_product_field_eiq(active_ingredients, rate, unit, applications=1):
    """
    Calculate total Field EIQ for a product with multiple active ingredients.
    
    Args:
        active_ingredients (list): List of dictionaries with 'eiq' and 'percent' keys
        rate (float): Application rate
        unit (str): Unit of measure for rate
        applications (int): Number of applications
        
    Returns:
        float: Total Field EIQ value for the product
    """
    total_field_eiq = 0.0
    
    for ai in active_ingredients:
        # Skip AIs with missing data
        if not ai or 'eiq' not in ai or 'percent' not in ai:
            continue
            
        # Handle case where eiq or percent might be stored as strings or have "--" placeholder
        if ai['eiq'] == "--" or ai['percent'] == "--":
            continue
            
        try:
            # Convert to float if stored as string
            ai_eiq = float(ai['eiq']) if isinstance(ai['eiq'], str) else ai['eiq']
            
            # Handle percent that might be stored with "%" suffix
            percent_str = str(ai['percent'])
            ai_percent = float(percent_str.replace('%', '')) if '%' in percent_str else float(ai['percent'])
            
            # Calculate and add Field EIQ for this active ingredient
            ai_field_eiq = calculate_field_eiq(ai_eiq, ai_percent, rate, unit, applications)
            total_field_eiq += ai_field_eiq
            
        except (ValueError, TypeError) as e:
            print(f"Error calculating EIQ for active ingredient {ai.get('name', 'unknown')}: {e}")
            # Skip this ingredient but continue with others
            continue
    
    return total_field_eiq

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

def convert_concentration_to_percent(concentration, uom):
    """
    Convert concentration to percentage based on unit of measure.
    
    Args:
        concentration (float): Concentration value
        uom (str): Unit of measure for concentration
        
    Returns:
        float or None: Concentration as percentage
    """
    if concentration is None:
        return None
        
    try:
        # Handle different UOMs
        if uom == '%':
            # Already in percent
            return float(concentration)
        elif uom == 'g/l':
            # Conversion from g/l to % (approximation)
            # This assumes that g/l * 0.1 = % (verify with domain experts)
            return float(concentration) * 0.1
        elif uom == 'g/kg':
            # g/kg is equivalent to 0.1%
            return float(concentration) * 0.1
        elif uom == 'ppm':
            # ppm to % (1 ppm = 0.0001%)
            return float(concentration) * 0.0001
        elif uom == 'w/w':
            # w/w is typically expressed as decimal, so multiply by 100
            return float(concentration) * 100
        elif uom == 'w/v':
            # w/v is typically expressed as decimal, so multiply by 100
            return float(concentration) * 100
        else:
            # Default: assume value is already in percent
            return float(concentration)
    except (ValueError, TypeError):
        return None

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