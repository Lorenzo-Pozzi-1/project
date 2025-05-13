"""
Product Comparison Calculator Tab for the LORENZO POZZI Pesticide App.

This module provides the ProductComparisonCalculatorTab widget for comparing EIQ
values of multiple pesticide products with card-based UI and improved UX.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QScrollArea
from PySide6.QtCore import Qt, Signal
from common.styles import REMOVE_BUTTON_STYLE, get_subtitle_font, PRIMARY_BUTTON_STYLE
from common.widgets import ContentFrame
from data.product_repository import ProductRepository
from eiq_calculator_page.widgets import ProductSelectionWidget, ApplicationParamsWidget, EiqComparisonTable
from math_module.eiq_calculations import calculate_product_field_eiq
from common.styles import PRODUCT_CARD_STYLE


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
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header with card title and remove button
        header_layout = QHBoxLayout()
        
        # Card title
        card_title = QLabel(f"Product {self.index + 1}")
        card_title.setFont(get_subtitle_font())
        header_layout.addWidget(card_title)
        
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
        layout.addWidget(self.product_selection)
        
        # Active ingredients label
        ai_layout = QHBoxLayout()
        ai_layout.addWidget(QLabel("Active Ingredients:"))
        
        self.ai_label = QLabel("None")
        self.ai_label.setWordWrap(True)
        ai_layout.addWidget(self.ai_label, 1)  # Give label stretch factor
        
        layout.addLayout(ai_layout)
        
        # Application parameters
        self.app_params = ApplicationParamsWidget()
        self.app_params.params_changed.connect(lambda: self.data_changed.emit(self.index))
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
            
            if not self.product:
                raise ValueError(f"Product '{product_name}' not found")
            
            # Get active ingredients data
            self.active_ingredients = self.product.get_ai_data()
            
            # Update active ingredients display
            ai_display = ", ".join(self.product.active_ingredients) if self.product.active_ingredients else "None"
            self.ai_label.setText(ai_display)
            
            # Update application parameters
            # Set application rate to max rate if available, otherwise min rate
            rate = 0.0
            if self.product.label_maximum_rate is not None:
                rate = self.product.label_maximum_rate
            elif self.product.label_minimum_rate is not None:
                rate = self.product.label_minimum_rate
            
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
        
        # Find the title label in the header layout and update it
        header_layout = self.layout().itemAt(0).layout()
        for i in range(header_layout.count()):
            item = header_layout.itemAt(i)
            if item.widget() and isinstance(item.widget(), QLabel):
                item.widget().setText(f"Product {self.index + 1}")
                break


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
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Products selection section
        selection_frame = ContentFrame()
        selection_layout = QVBoxLayout()
        
        # Title for selection section
        selection_title = QLabel("Select Products to Compare")
        selection_title.setFont(get_subtitle_font())
        selection_layout.addWidget(selection_title)
        
        # Scroll area for product cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        # Change to horizontal scrollbar
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container for product cards
        self.cards_container = QWidget()
        # Change vertical layout to horizontal layout
        self.cards_layout = QHBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch(1)  # Push cards to left
        
        self.scroll_area.setWidget(self.cards_container)
        
        selection_layout.addWidget(self.scroll_area)
        
        # Add another product button
        add_button_layout = QHBoxLayout()
        
        add_product_button = QPushButton("Add Product")
        add_product_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        add_product_button.clicked.connect(self.add_product_card)
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
        if index < 0 or index >= len(self.product_cards):
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
            card.index = i
            card.update_title(i)
        
        # Recalculate all products
        self.refresh_calculations()
    
    def refresh_product_data(self):
        """Refresh product data based on the filtered products."""
        # Clear existing cards
        while self.product_cards:
            card = self.product_cards.pop()
            self.cards_layout.removeWidget(card)
            card.deleteLater()
        
        # Clear comparison table
        self.comparison_table.clear_results()
        
        # Add a new empty card
        self.add_product_card()
    
    def calculate_product(self, index):
        """
        Calculate EIQ for a product and update the comparison table.
        
        Args:
            index (int): Index of the product card to calculate
        """
        if index < 0 or index >= len(self.product_cards):
            return
        
        # Get the card
        card = self.product_cards[index]
        
        # Get product data
        product_data = card.get_product_data()
        
        if not product_data:
            # Remove from comparison table if no valid data
            self.comparison_table.remove_product(product_id=f"card_{index}")
            return
        
        try:
            # Calculate Field EIQ
            field_eiq = calculate_product_field_eiq(
                product_data["active_ingredients"],
                product_data["rate"],
                product_data["unit"],
                product_data["applications"]
            )
            
            # Update comparison table
            if field_eiq > 0:
                self.comparison_table.add_product_result(
                    product_data["product_name"],
                    field_eiq,
                    product_id=f"card_{index}"  # Use a string with index to make it unique
                )
            else:
                # Remove from table if calculation failed
                self.comparison_table.remove_product(product_id=f"card_{index}")
            
        except Exception as e:
            print(f"Error calculating EIQ for product {index}: {e}")
            # Remove from table on error
            self.comparison_table.remove_product(product_id=f"card_{index}")
    
    def refresh_calculations(self):
        """Recalculate EIQ for all products."""
        # Clear comparison table
        self.comparison_table.clear_results()
        
        # Calculate each product
        for i in range(len(self.product_cards)):
            self.calculate_product(i)