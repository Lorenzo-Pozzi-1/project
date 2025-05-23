"""
Result display widgets for the LORENZO POZZI Pesticide App.

This module provides widgets for displaying EIQ calculation results.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidgetItem, QTableWidget, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush
from common import GENERIC_TABLE_STYLE, get_subtitle_font, ContentFrame, ScoreBar, get_eiq_color, get_eiq_rating, EIQ_LOW_THRESHOLD as LOW_THRESHOLD, EIQ_MEDIUM_THRESHOLD as MEDIUM_THRESHOLD, EIQ_HIGH_THRESHOLD as HIGH_THRESHOLD
from common import format_eiq_result


class ColorCodedEiqItem(QTableWidgetItem):
    """
    A table item specifically for EIQ values with automatic color coding.
    
    This item displays EIQ values with color coding based on impact thresholds.
    """
    
    def __init__(self, eiq_value, low_threshold=LOW_THRESHOLD, 
                medium_threshold=MEDIUM_THRESHOLD, high_threshold=HIGH_THRESHOLD):
        """
        Initialize with EIQ value and thresholds.
        
        Args:
            eiq_value (float): The EIQ value to display
            low_threshold (float): Threshold between low and medium impact
            medium_threshold (float): Threshold between medium and high impact
            high_threshold (float): Threshold between high and extreme impact
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
            color = get_eiq_color(value_float, low_threshold, medium_threshold, high_threshold)
            self.setBackground(QBrush(color))
        except (ValueError, TypeError):
            # If value can't be converted to float, don't apply color
            pass


class EiqResultDisplay(QWidget):
    """
    A widget for displaying EIQ results with score bar and rating.
    
    This widget provides a visual representation of EIQ calculation results.
    """
    
    def __init__(self, parent=None):
        """Initialize the EIQ result display widget."""
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # CHANGE: Wrap content in ContentFrame
        content_frame = ContentFrame()
        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignCenter)
        
        # Results title
        results_title = QLabel("EIQ Results")
        results_title.setFont(get_subtitle_font())
        content_layout.addWidget(results_title)
        
        # Field EIQ result layout
        field_eiq_layout = QHBoxLayout()
        field_eiq_label = QLabel("Field EIQ:")
        field_eiq_label.setFont(get_subtitle_font(bold=True))

        # Label for ha value
        self.field_eiq_result_ha = QLabel("--")
        self.field_eiq_result_ha.setFont(get_subtitle_font(bold=True))
        
        field_eiq_layout.addWidget(field_eiq_label)
        field_eiq_layout.addWidget(self.field_eiq_result_ha)
        field_eiq_layout.addStretch(1)
        
        content_layout.addLayout(field_eiq_layout)
        
        # Create score bar with default thresholds and labels
        self.score_bar = ScoreBar(
            thresholds=[LOW_THRESHOLD, MEDIUM_THRESHOLD, HIGH_THRESHOLD],
            min_value=0,
            max_value=HIGH_THRESHOLD,
            labels=["Low", "Medium", "High", "EXTREME"],
            title_text="Field EIQ score:"
        )
        content_layout.addWidget(self.score_bar)
        
        content_frame.layout.addLayout(content_layout)
        layout.addWidget(content_frame)
    
    def update_result(self, field_eiq):
        """
        Update the EIQ result display with the calculated value.
        
        Args:
            field_eiq (float): The calculated Field EIQ value
        """
        self.set_field_eiq_text(field_eiq)
        
        # Update score bar
        rating = get_eiq_rating(field_eiq)
        self.score_bar.set_value(field_eiq, rating)

    def set_field_eiq_text(self, field_eiq):
        """
        Set the field EIQ text.
        
        Args:
            field_eiq (float): The Field EIQ value to display
        """
        if field_eiq <= 0:
            self.field_eiq_result_ha.setText("--")
            self.score_bar.set_value(0, "No calculation")
            return
        
        ha_text = format_eiq_result(field_eiq)
        self.field_eiq_result_ha.setText(ha_text)


class EiqComparisonTable(QTableWidget):
    """
    A table for displaying and comparing EIQ values of multiple products.
    
    This table shows products and their Field EIQ values with color coding.
    """
    
    def __init__(self, parent=None):
        """Initialize the EIQ comparison table."""
        super().__init__(0, 2, parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""

        self.setStyleSheet(GENERIC_TABLE_STYLE)
        # Set header labels
        self.setHorizontalHeaderLabels(["Product", "Field EIQ"])
        
        # Set up table properties
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        # Set up visual style
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.verticalHeader().setVisible(False)
    
    def add_product_result(self, product_name, field_eiq, product_id=None,
                         low_threshold=LOW_THRESHOLD, medium_threshold=MEDIUM_THRESHOLD, high_threshold=HIGH_THRESHOLD):
        """
        Add or update a product's EIQ result in the table.
        
        Args:
            product_name (str): Name of the product
            field_eiq (float): Calculated Field EIQ value
            product_id (any, optional): Identifier for the product, used for updates
            low_threshold (float): Threshold for low impact
            medium_threshold (float): Threshold for medium impact
            high_threshold (float): Threshold for high impact
            
        Returns:
            int: Row index of the added/updated product
        """
        if field_eiq is None or field_eiq <= 0:
            # If invalid EIQ, remove the product if it exists
            self.remove_product(product_name, product_id)
            return -1
        
        # Check if product already exists in table
        row = self.find_product_row(product_name, product_id)
        
        # If not found, add a new row
        if row == -1:
            row = self.rowCount()
            self.insertRow(row)
        
        # Product name item
        name_item = QTableWidgetItem(product_name)
        if product_id is not None:
            name_item.setData(Qt.UserRole, product_id)
        self.setItem(row, 0, name_item)
        
        # Field EIQ item with color coding
        eiq_item = ColorCodedEiqItem(
            field_eiq, 
            low_threshold=low_threshold, 
            medium_threshold=medium_threshold,
            high_threshold=high_threshold
        )
        self.setItem(row, 1, eiq_item)
        
        return row
    
    def remove_product(self, product_name=None, product_id=None):
        """
        Remove a product from the table.
        
        Args:
            product_name (str, optional): Name of the product to remove
            product_id (any, optional): ID of the product to remove
            
        Returns:
            bool: True if product was found and removed, False otherwise
        """
        row = self.find_product_row(product_name, product_id)
        
        if row != -1:
            self.removeRow(row)
            return True
            
        return False
    
    def find_product_row(self, product_name=None, product_id=None):
        """
        Find the row index of a product in the table.
        
        Args:
            product_name (str, optional): Name of the product to find
            product_id (any, optional): ID of the product to find
            
        Returns:
            int: Row index if found, -1 otherwise
        """
        # Search by ID if provided
        if product_id is not None:
            for row in range(self.rowCount()):
                item = self.item(row, 0)
                if item and item.data(Qt.UserRole) == product_id:
                    return row
        
        # Search by name if provided
        if product_name is not None:
            for row in range(self.rowCount()):
                item = self.item(row, 0)
                if item and item.text() == product_name:
                    return row
        
        return -1
    
    def clear_results(self):
        """Clear all results from the table."""
        self.setRowCount(0)