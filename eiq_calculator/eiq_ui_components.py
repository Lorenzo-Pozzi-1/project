"""
EIQ UI Components for the LORENZO POZZI Pesticide App.

This module provides UI components for EIQ calculations and display.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QFrame, QScrollArea, QTableWidgetItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush

from common.styles import get_title_font, get_subtitle_font, get_body_font, EIQ_LOW_COLOR, EIQ_MEDIUM_COLOR, EIQ_HIGH_COLOR
from common.widgets import ToxicityBar
from data.products_data import load_products, get_product_by_name
from eiq_calculator.eiq_conversions import convert_concentration_to_percent
from eiq_calculator.eiq_calculations import format_eiq_result, get_impact_category

#------------------------
# Data Handling Functions
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
        
        # Add focus events to show/hide suggestions
        self.search_field.focusInEvent = self.on_focus_in
        self.search_field.focusOutEvent = self.on_focus_out
        
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
    
    def on_focus_in(self, event):
        """Show all suggestions when the field gets focus."""
        # Call the original focusInEvent
        QLineEdit.focusInEvent(self.search_field, event)
        
        # Show all items if there's no search text
        if not self.search_field.text():
            self.filtered_items = self.all_items.copy()
            self.suggestions_list.clear()
            self.suggestions_list.addItems(self.filtered_items)
            
            # Only show if we have items
            has_suggestions = len(self.filtered_items) > 0
            self.suggestions_container.setVisible(has_suggestions)
            
            # Set fixed height based on number of items
            if has_suggestions:
                item_height = self.suggestions_list.sizeHintForRow(0)
                num_visible_items = min(8, len(self.filtered_items))
                list_height = item_height * num_visible_items + 4
                self.suggestions_list.setFixedHeight(list_height)
    
    def on_focus_out(self, event):
        """Hide suggestions when the field loses focus."""
        # Call the original focusOutEvent
        QLineEdit.focusOutEvent(self.search_field, event)
        
        # Hide suggestions immediately
        # This is fine since the click event on an item will be processed
        # before the focus out event
        self.suggestions_container.setVisible(False)
    
    def update_suggestions(self, text):
        """Update suggestions based on input text."""
        # Clear selection when search text changes
        self.suggestions_list.clearSelection()
        
        if not text:
            # Show all items when text is cleared
            self.filtered_items = self.all_items.copy()
        else:
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
        self.field_eiq_result = QLabel("-- /ha")
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
            self.field_eiq_result.setText("-- /ha")
            self.toxicity_bar.set_value(0, "No calculation")
            return
            
        # Format result with per-ha values only
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