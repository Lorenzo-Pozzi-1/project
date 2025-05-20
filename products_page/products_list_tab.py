"""
Products list tab for the LORENZO POZZI Pesticide App with improved component architecture.

This module defines the ProductsListTab class that provides product listing
and filtering functionality using a table-based view.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QScrollArea
from PySide6.QtCore import Qt
from common import SECONDARY_BUTTON_STYLE, get_subtitle_font, ContentFrame, create_button
from data import ProductRepository
from products_page.widgets.filter_row import FilterRow
from products_page.widgets.products_table import ProductTable


class ProductsListTab(QWidget):
    """
    Products list tab for displaying and filtering products.
    
    This tab provides a searchable table of products with filtering capabilities,
    allowing the user to select products for comparison.
    """
    
    def __init__(self, parent=None):
        """Initialize the products list tab."""
        super().__init__(parent)
        self.parent = parent
        self.filter_rows = []
        self.all_products = []
        self.visible_columns = []
        self.field_to_column_map = {}
        self.setup_ui()
        self.load_product_data()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # Filter section
        filter_frame = ContentFrame()
        filter_layout = QVBoxLayout()
        
        # Filter title
        selection_title = QLabel("Filter Products")
        selection_title.setFont(get_subtitle_font())
        filter_layout.addWidget(selection_title)
        
        # Filter rows area
        self.filter_rows_container = QWidget()
        self.filter_rows_layout = QHBoxLayout(self.filter_rows_container)
        self.filter_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_rows_layout.setAlignment(Qt.AlignLeft)
        
        filter_scroll = QScrollArea()
        filter_scroll.setWidgetResizable(True)
        filter_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        filter_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        filter_scroll.setFrameShape(QFrame.NoFrame)
        filter_scroll.setWidget(self.filter_rows_container)
        filter_scroll.setMaximumHeight(60)
        filter_layout.addWidget(filter_scroll)
        
        # Add filter button
        add_filter_button = QPushButton("Add Another Filter")
        add_filter_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        add_filter_button.clicked.connect(self.add_filter_row)
        filter_layout.addWidget(add_filter_button, alignment=Qt.AlignLeft)
        
        # Add layout to the frame
        filter_frame.layout.addLayout(filter_layout)
        main_layout.addWidget(filter_frame)
        
        # Products table
        table_frame = ContentFrame()
        table_layout = QVBoxLayout()
        
        self.products_table = ProductTable()
        self.products_table.selection_changed.connect(self.on_selection_changed)
        table_layout.addWidget(self.products_table)
        
        table_frame.layout.addLayout(table_layout)
        main_layout.addWidget(table_frame, 1)  # Give stretch factor
        
        # Compare button
        button_frame = ContentFrame()
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)  # Align to right
        compare_button = create_button(text="View facts sheet / Compare Selected Products", style="primary", callback=self.compare_selected_products, parent=self)
        button_layout.addWidget(compare_button)
        button_frame.layout.addLayout(button_layout)
        main_layout.addWidget(button_frame)
    
    def load_product_data(self):
        """Load product data from repository."""
        # Get products
        products_repo = ProductRepository.get_instance()
        products = products_repo.get_filtered_products()
        if not products:
            return
                
        self.all_products = products
        
        # Get columns from first product
        first_product = products[0].to_dict()
        column_keys = list(first_product.keys())
        
        # Set products in the table
        self.products_table.set_products(products, column_keys)
        
        # Configure table columns
        self.setup_field_mapping()
        
        # Add initial filter row if not already added
        if not self.filter_rows and self.visible_columns:
            self.add_filter_row()
    
    def setup_field_mapping(self):
        """Setup field to column mapping for filters."""
        self.visible_columns = []
        self.field_to_column_map = {}
        
        # Skip if table not setup yet
        if self.products_table.columnCount() == 0:
            return
        
        # Find AI column first
        ai1_col = -1
        for i, key in enumerate(self.products_table.column_keys):
            if key.lower() == "ai1":
                ai1_col = i
                break
        
        # Calculate groups column position
        groups_col = ai1_col + 2 if ai1_col >= 0 else -1  # +1 for checkbox, +1 for position after AI1
        
        # Hide columns and manage visibility
        hide_columns = ["country", "region", "min days between applications", "[ai1]", "[ai1]uom", "ai1 eiq", 
                      "[ai2]", "[ai2]uom", "ai2 eiq", "[ai3]", "[ai3]uom", "ai3 eiq",
                      "[ai4]", "[ai4]uom", "ai4 eiq", "ai2", "ai3", "ai4"]
        
        # Setup column properties
        for col, key in enumerate(self.products_table.column_keys, start=1):
            # Calculate the actual table column index
            table_col = col
            if groups_col > 0 and col >= groups_col:
                table_col = col + 1  # Adjust for inserted Groups column
            
            # Rename AI column
            if key.lower() == "ai1":
                # Add to visible columns for filtering
                self.visible_columns.append("AIs")
                self.field_to_column_map["AIs"] = table_col
            
            # Hide specified columns
            elif any(key.lower() == hide_key.lower() for hide_key in hide_columns):
                pass  # Skip hidden columns
            
            # Add visible columns to filter options
            else:
                self.visible_columns.append(key)
                self.field_to_column_map[key] = table_col
        
        # Add Groups column to visible columns
        if groups_col > 0:
            self.visible_columns.append("Groups")
            self.field_to_column_map["Groups"] = groups_col
    
    def add_filter_row(self):
        """Add a new filter row."""
        if not self.visible_columns:
            return
            
        filter_row = FilterRow(self.visible_columns, self.field_to_column_map, self)
        filter_row.filter_changed.connect(self.apply_filters)
        filter_row.remove_requested.connect(self.remove_filter_row)
        
        self.filter_rows_layout.addWidget(filter_row)
        self.filter_rows.append(filter_row)
        
        # Show/hide remove buttons based on number of rows
        for row in self.filter_rows:
            row.remove_button.setVisible(len(self.filter_rows) > 1)
    
    def remove_filter_row(self, filter_row):
        """Remove a filter row."""
        if filter_row in self.filter_rows:
            self.filter_rows_layout.removeWidget(filter_row)
            self.filter_rows.remove(filter_row)
            filter_row.deleteLater()
            
            # Update remove button visibility
            for row in self.filter_rows:
                row.remove_button.setVisible(len(self.filter_rows) > 1)
            
            self.apply_filters()
    
    def apply_filters(self):
        """Apply all active filters."""
        # Get valid filter criteria
        filters = []
        for filter_row in self.filter_rows:
            criteria = filter_row.get_filter_criteria()
            if criteria and criteria[1]:  # Only if column and non-empty text
                filters.append(criteria)
        
        # Apply filters to the table
        self.products_table.apply_filters(filters)

    def reset_filters(self):
        """Reset all filter rows and show all products."""
        # Clear existing filter rows
        while self.filter_rows:
            row = self.filter_rows.pop()
            self.filter_rows_layout.removeWidget(row)
            row.deleteLater()
        
        # Add a single empty filter row
        if self.visible_columns:
            self.add_filter_row()
        
        # Show all rows in the table
        for row in range(self.products_table.rowCount()):
            self.products_table.showRow(row)
    
    def on_selection_changed(self, selected_products):
        """Handle selection changes from the table."""
        self.parent.selected_products = selected_products

    def compare_selected_products(self):
        """Handle the compare button click."""
        selected_products = self.parent.selected_products
        if not selected_products:
            return
        
        # Load selected products into the comparison tab
        self.parent.comparison_tab.update_comparison_view(selected_products)

        # Navigate to the comparison tab
        self.parent.tabs.setCurrentIndex(1)
        
        