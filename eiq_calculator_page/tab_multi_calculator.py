"""
Product Comparison Calculator Tab for the LORENZO POZZI Pesticide App.

This module provides the ProductComparisonCalculatorTab widget for comparing EIQ
values of multiple pesticide products with card-based UI.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget
from common import MARGIN_MEDIUM, SPACING_LARGE, get_subtitle_font, ContentFrame, create_button, get_config
from common.calculations import eiq_calculator
from eiq_calculator_page.widgets_results_display import EiqComparisonTable
from eiq_calculator_page.widget_product_card import ProductCard


class ProductComparisonCalculatorTab(QWidget):
    """Widget for comparing EIQ values of multiple pesticide products."""
    
    def __init__(self, parent=None):
        """Initialize the product comparison calculator tab."""
        super().__init__(parent)
        self.parent = parent
        self.product_cards = []  # List of ProductCard widgets
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MARGIN_MEDIUM, MARGIN_MEDIUM, MARGIN_MEDIUM, MARGIN_MEDIUM)
        main_layout.setSpacing(SPACING_LARGE)
        
        # Products selection section
        selection_frame = ContentFrame()
        selection_layout = QVBoxLayout()
        
        # Title for selection section
        selection_title = QLabel("Select Products to Compare")
        selection_title.setFont(get_subtitle_font())
        selection_layout.addWidget(selection_title)
        
        # Wrap scroll area in ContentFrame
        cards_frame = ContentFrame()
        cards_frame_layout = QVBoxLayout()
        
        # Scroll area for product cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container for product cards
        self.cards_container = QWidget()
        self.cards_layout = QHBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch(1)  # Push cards to left
        
        self.scroll_area.setWidget(self.cards_container)
        cards_frame_layout.addWidget(self.scroll_area)
        
        cards_frame.layout.addLayout(cards_frame_layout)
        selection_layout.addWidget(cards_frame)
        
        # Add another product button
        add_button_layout = QHBoxLayout()
        add_product_button = create_button(text="Add Product", style="yellow", callback=self.add_product_card, parent=self)
        add_button_layout.addWidget(add_product_button)
        add_button_layout.addStretch(1)  # Push button to left
        selection_layout.addLayout(add_button_layout)
        selection_frame.layout.addLayout(selection_layout)
        main_layout.addWidget(selection_frame)
        
        # Comparison results section
        results_frame = ContentFrame()
        results_layout = QVBoxLayout()
        
        # Title for results section
        results_title = QLabel("EIQ Comparison Results")
        results_title.setFont(get_subtitle_font())
        results_layout.addWidget(results_title)
        
        # Comparison table
        self.comparison_table = EiqComparisonTable()
        results_layout.addWidget(self.comparison_table)
        
        results_frame.layout.addLayout(results_layout)
        main_layout.addWidget(results_frame)
        
        # Add initial product card
        self.add_product_card()
    
    def add_product_card(self):
        """Add a new product card to the calculator."""
        # Create new card with current index
        index = len(self.product_cards)
        card = ProductCard(index, self)
        
        # Connect signals
        card.data_changed.connect(self.on_product_data_changed)
        card.remove_requested.connect(self.remove_product_card)
        
        # Add to layout just before the stretch
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        
        # Add to list of cards
        self.product_cards.append(card)
    
    def remove_product_card(self, index):
        """
        Remove a product card from the calculator.
        
        Args:
            index (int): Index of the card to remove
        """
        if not (0 <= index < len(self.product_cards)):
            return
        
        # Get the card
        card = self.product_cards[index]
        
        # Remove from comparison table first
        product_id = f"card_{index}"
        self.comparison_table.remove_product(product_id=product_id)
        
        # Remove from layout
        self.cards_layout.removeWidget(card)
        
        # Delete the widget
        card.deleteLater()
        
        # Remove from list
        self.product_cards.pop(index)
        
        # Update indices and titles of remaining cards
        for i, card in enumerate(self.product_cards):
            card.update_title(i)
        
        # Update the entire comparison table with new indices
        self.update_comparison_table()
    
    def clear_all_cards(self):
        """Clear all product cards."""
        while self.product_cards:
            card = self.product_cards.pop()
            self.cards_layout.removeWidget(card)
            card.deleteLater()
        
        # Clear comparison table
        self.comparison_table.clear_results()
    
    def refresh_product_data(self):
        """Refresh product data based on the filtered products."""
        # Clear existing cards
        self.clear_all_cards()
        
        # Add a new empty card
        self.add_product_card()
    
    def calculate_eiq_for_card(self, card_index):
        """Calculate EIQ for a specific product card."""
        if not (0 <= card_index < len(self.product_cards)):
            return None, 0.0
        
        card = self.product_cards[card_index]
        product_data = card.get_product_data()
        
        if not product_data:
            return None, 0.0
        
        try:
            # Get user preferences for UOM conversions
            user_preferences = get_config("user_preferences", {})
            
            # Calculate field use EIQ for the product
            field_eiq = eiq_calculator.calculate_product_field_eiq(
                active_ingredients=product_data["active_ingredients"],
                application_rate=product_data["rate"],
                application_rate_uom=product_data["unit"],
                applications=product_data["applications"],
                user_preferences=user_preferences
            )
            
            return product_data, field_eiq
            
        except Exception as e:
            print(f"Error calculating EIQ for product {card_index}: {e}")
            return product_data, 0.0
    
    def update_comparison_table(self):
        """Update the comparison table with current EIQ calculations for all cards."""
        # Clear the table first
        self.comparison_table.clear_results()
        
        # Calculate and add each product
        for i in range(len(self.product_cards)):
            product_data, field_eiq = self.calculate_eiq_for_card(i)
            
            if product_data and field_eiq > 0:
                product_id = f"card_{i}"
                self.comparison_table.add_product_result(
                    product_data["product_name"],
                    field_eiq,
                    product_id=product_id
                )
    
    def on_product_data_changed(self, card_index):
        """
        Handle changes to product data in any card.
        
        Args:
            card_index (int): Index of the card that changed
        """
        # Calculate EIQ for the changed card
        product_data, field_eiq = self.calculate_eiq_for_card(card_index)
        product_id = f"card_{card_index}"
        
        # Update comparison table based on result
        if product_data and field_eiq > 0:
            self.comparison_table.add_product_result(
                product_data["product_name"],
                field_eiq,
                product_id=product_id
            )
        else:
            self.comparison_table.add_product_result("0")