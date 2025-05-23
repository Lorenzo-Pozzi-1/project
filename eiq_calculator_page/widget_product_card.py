"""Product card widget for the LORENZO POZZI Pesticide App."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout
from common import (FRAME_STYLE, PRODUCT_CARD_STYLE, MARGIN_MEDIUM, SPACING_MEDIUM, MEDIUM_TEXT, get_subtitle_font, create_button, ApplicationParamsWidget, ProductSelectionWidget)
from data import ProductRepository


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
        remove_button = create_button(style='remove', callback=lambda: self.remove_requested.emit(self.index))
        remove_button.setFixedSize(24, 24)
        header_layout.addWidget(remove_button)
        
        layout.addLayout(header_layout)
        
        # Product selection widget
        self.product_selection = ProductSelectionWidget(orientation='vertical', style_config={'font_size': MEDIUM_TEXT, 'bold': False})
        self.product_selection.product_selected.connect(self.update_product_info)
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
        
        # Application parameters widget
        self.app_params = ApplicationParamsWidget(orientation='vertical', style_config={'font_size': MEDIUM_TEXT, 'bold': False})
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