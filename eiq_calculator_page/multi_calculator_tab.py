"""
Product Comparison Calculator Tab for the LORENZO POZZI Pesticide App.

This module provides the ProductComparisonCalculatorTab widget for comparing EIQ
values of multiple pesticide products with card-based UI and improved UX.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget
from common.styles import FRAME_STYLE, MARGIN_MEDIUM, PRODUCT_CARD_STYLE, REMOVE_BUTTON_STYLE, SPACING_LARGE, SPACING_MEDIUM, get_subtitle_font, create_button
from common.widgets.widgets import ContentFrame
from data.product_repository import ProductRepository
from eiq_calculator_page.widgets import ApplicationParamsWidget, EiqComparisonTable, ProductSelectionWidget
from math_module.eiq_calculations import calculate_product_field_eiq


class ProductCard(QFrame):
    """
    A card-like widget for a single product in the comparison calculator.
    
    This widget encapsulates all inputs for a single product in the comparison.
    """
    
    # Signal emitted when product data changes
    data_changed = Signal(int)  # Parameter is the card index
    # Signal emitted when card should be removed
    remove_requested = Signal(int)  # Parameter is the card index
    
    def __init__(self, index, parent=None):
        """
        Initialize the product card.
        
        Args:
            index (int): The index of this card
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.index = index
        self.product = None
        self.active_ingredients = []
        
        # Apply card styling
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet(PRODUCT_CARD_STYLE)
        
        # Set fixed width for horizontal layout
        self.setFixedWidth(300)
        # Add minimum height to ensure visibility of all content
        self.setMinimumHeight(250)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(MARGIN_MEDIUM, MARGIN_MEDIUM, MARGIN_MEDIUM, MARGIN_MEDIUM)
        layout.setSpacing(SPACING_MEDIUM)
        
        # Set minimum sizes, allowing for resizing
        self.setMinimumWidth(400)
        self.setMinimumHeight(250)
        
        # Header with card title and remove button
        header_layout = QHBoxLayout()
        
        # Card title - store reference
        self.card_title = QLabel(f"Product {self.index + 1}")
        self.card_title.setFont(get_subtitle_font())
        self.card_title.setStyleSheet(FRAME_STYLE)
        header_layout.addWidget(self.card_title)
        
        # Push remove button to right
        header_layout.addStretch(1)
        
        # Remove button
        remove_button = QPushButton("✕")  # Unicode ✕ character for X
        remove_button.setFixedSize(24, 24)
        remove_button.setStyleSheet(REMOVE_BUTTON_STYLE)
        remove_button.clicked.connect(lambda: self.remove_requested.emit(self.index))
        header_layout.addWidget(remove_button)
        
        layout.addLayout(header_layout)
        
        # Product selection widget
        self.product_selection = ProductSelectionWidget()
        self.product_selection.product_selected.connect(self.update_product_info)
        self.product_selection.setStyleSheet(FRAME_STYLE)
        layout.addWidget(self.product_selection)
        
        # Active ingredients section
        ai_frame = QFrame()
        ai_frame.setStyleSheet(FRAME_STYLE)
        ai_frame_layout = QVBoxLayout(ai_frame)
        
        ai_layout = QHBoxLayout()
        ai_layout.addWidget(QLabel("Active Ingredients:"))
        
        self.ai_label = QLabel("None")
        self.ai_label.setWordWrap(True)
        ai_layout.addWidget(self.ai_label, 1)  # Give label stretch factor
        
        ai_frame_layout.addLayout(ai_layout)
        layout.addWidget(ai_frame)
        
        # Application parameters
        self.app_params = ApplicationParamsWidget()
        self.app_params.params_changed.connect(lambda: self.data_changed.emit(self.index))
        self.app_params.setStyleSheet(FRAME_STYLE)
        layout.addWidget(self.app_params)
    
    def refresh_product_types(self):
        """Refresh the product types in the selection widget."""
        self.product_selection.refresh_data()
    
    def update_product_info(self, product_name):
        """
        Update product information when a product is selected.
        
        Args:
            product_name (str): The selected product name
        """
        if not product_name:
            self.clear_product()
            return
        
        try:
            # Get product from repository
            products_repo = ProductRepository.get_instance()
            self.product = products_repo.get_product_by_name(product_name)
            
            # If product doesn't exist, clear and return
            if not self.product:
                self.clear_product()
                return
            
            # Get active ingredients data
            self.active_ingredients = self.product.get_ai_data()
            
            # Update active ingredients display
            ai_display = ", ".join(self.product.active_ingredients) if self.product.active_ingredients else "None"
            self.ai_label.setText(ai_display)
            
            # Update application parameters - simplified rate selection
            rate = self.product.label_maximum_rate or self.product.label_minimum_rate or 0.0
            
            # Set unit to product's UOM if available
            unit = self.product.rate_uom
            
            # Default to 1 application
            applications = 1
            
            # Update application parameters widget
            self.app_params.set_params(rate, unit, applications)
            
            # Emit signal that data has changed
            self.data_changed.emit(self.index)
            
        except Exception as e:
            print(f"Error loading product info for '{product_name}': {e}")
            self.clear_product()
    
    def clear_product(self):
        """Clear the current product selection and related data."""
        self.product = None
        self.active_ingredients = []
        self.ai_label.setText("None")
        self.app_params.set_params(0.0, None, 1)
        
        # Emit signal that data has changed
        self.data_changed.emit(self.index)
    
    def get_product_data(self):
        """
        Get the current product data for calculation.
        
        Returns:
            dict: Dictionary with product data or None if no product selected
        """
        if not self.product or not self.active_ingredients:
            return None
        
        # Get application parameters
        params = self.app_params.get_params()
        
        return {
            "product": self.product,
            "product_name": self.product.product_name,
            "active_ingredients": self.active_ingredients,
            "rate": params["rate"],
            "unit": params["unit"],
            "applications": params["applications"]
        }
    
    def update_title(self, index):
        """
        Update the card title based on new index.
        
        Args:
            index (int): The new index for this card
        """
        self.index = index
        self.card_title.setText(f"Product {self.index + 1}")


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
        add_product_button = create_button(text="Add Product", style="primary", callback=self.add_product_card, parent=self)
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
        card.data_changed.connect(self.calculate_product)
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
        
        # Remove from layout
        self.cards_layout.removeWidget(card)
        
        # Delete the widget
        card.deleteLater()
        
        # Remove from list
        self.product_cards.pop(index)
        
        # Update indices and titles of remaining cards
        for i, card in enumerate(self.product_cards):
            card.update_title(i)
        
        # Recalculate all products
        self.refresh_calculations()
    
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
    
    def calculate_product(self, index):
        """
        Calculate EIQ for a product and update the comparison table.
        
        Args:
            index (int): Index of the product card to calculate
        """
        # Validate index
        if not (0 <= index < len(self.product_cards)):
            return
        
        # Get the card and product data
        card = self.product_cards[index]
        product_data = card.get_product_data()
        product_id = f"card_{index}"
        
        # Remove product if no valid data
        if not product_data:
            self.comparison_table.remove_product(product_id=product_id)
            return
        
        try:
            # Calculate Field EIQ
            field_eiq = calculate_product_field_eiq(
                product_data["active_ingredients"],
                product_data["rate"],
                product_data["unit"],
                product_data["applications"]
            )
            
            # Update or remove from comparison table based on result
            if field_eiq > 0:
                self.comparison_table.add_product_result(
                    product_data["product_name"],
                    field_eiq,
                    product_id=product_id
                )
            else:
                self.comparison_table.remove_product(product_id=product_id)
            
        except Exception as e:
            print(f"Error calculating EIQ for product {index}: {e}")
            self.comparison_table.remove_product(product_id=product_id)
    
    def refresh_calculations(self):
        """Recalculate EIQ for all products."""
        # Clear comparison table
        self.comparison_table.clear_results()
        
        # Calculate each product
        for i in range(len(self.product_cards)):
            self.calculate_product(i)