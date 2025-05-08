"""
Products list tab for the Lorenzo Pozzi Pesticide App

This module defines the ProductsListTab class which handles the product listing
and filtering functionality with an improved filtering system and optimized layout.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, 
                                QHeaderView, QCheckBox, QComboBox, QLineEdit, QFrame, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from common.styles import get_body_font, PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
from data.product_repository import ProductRepository

class FilterRow(QWidget):
    """
    A filter row widget containing field selection and filter input.
    
    This widget provides a single filter criteria consisting of a field
    dropdown and a text input for the filter value.
    """
    
    filter_changed = Signal()  # Signal emitted when the filter changes
    remove_requested = Signal(object)  # Signal emitted when remove button is clicked
    
    def __init__(self, fields, field_to_column_map, parent=None):
        """
        Initialize a filter row with the given field options.
        
        Args:
            fields: List of field names to display in dropdown
            field_to_column_map: Dictionary mapping field names to actual column indices
        """
        super().__init__(parent)
        self.fields = fields
        self.field_to_column_map = field_to_column_map
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components with simplified structure."""
        # Single horizontal layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Field selection dropdown
        self.field_combo = QComboBox()
        self.field_combo.addItem("Select field...")
        self.field_combo.addItems(self.fields)
        self.field_combo.setMinimumWidth(150)
        self.field_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(self.field_combo)
        
        # Contains label
        contains_label = QLabel("contains:")
        layout.addWidget(contains_label)
        
        # Filter value input
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Type to filter...")
        self.value_input.textChanged.connect(self.on_filter_changed)
        layout.addWidget(self.value_input)
        
        # Remove button
        self.remove_button = QPushButton("×")  # Using × character for close icon
        self.remove_button.setFixedSize(24, 24)
        self.remove_button.setToolTip("Remove this filter")
        self.remove_button.setStyleSheet("QPushButton { color: red; font-weight: bold; }")
        self.remove_button.clicked.connect(self.request_remove)
        layout.addWidget(self.remove_button)
    
    def on_filter_changed(self):
        """Handle changes to the filter criteria."""
        self.filter_changed.emit()
    
    def request_remove(self):
        """Request removal of this filter row."""
        self.remove_requested.emit(self)
    
    def get_filter_criteria(self):
        """
        Get the current filter criteria as a tuple.
        
        Returns:
            tuple: (column_index, filter_text) or None if no valid field selected
        """
        field_index = self.field_combo.currentIndex()
        selected_field = self.field_combo.currentText()
        filter_text = self.value_input.text().strip().lower()
        
        # Ignore if "Select field..." is chosen (index 0)
        if field_index > 0:
            # Look up the actual column index from the field name
            column_index = self.field_to_column_map.get(selected_field)
            if column_index is not None:
                return (column_index, filter_text)
        
        return None


class ProductsListTab(QWidget):
    """
    Products list tab for displaying and filtering the products.
    
    This tab displays a table of products with advanced filtering capabilities.
    """
    def __init__(self, parent=None):
        """Initialize the products list tab."""
        super().__init__(parent)
        self.parent = parent
        self.column_keys = []  # Store CSV column keys
        self.country_column_index = -1  # Will store index of the country column
        self.filter_rows = []  # Track filter row widgets
        self.original_header_texts = {}  # Store original header texts
        self.all_products = []  # Store all loaded products
        self.setup_ui()
        self.load_product_data()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # Simplified filter section
        self.setup_filter_section(main_layout)
        
        # Create table for products
        self.products_table = QTableWidget()
        self.products_table.setAlternatingRowColors(True)
        self.products_table.verticalHeader().setVisible(False)  # Hide row numbers
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Set size policy for table to expand and fill available space
        self.products_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Add table to main layout with stretch factor 1 (gets all remaining space)
        main_layout.addWidget(self.products_table, 1)
        
        # "Compare Selected" button
        compare_button = QPushButton("View Fact Sheet / Compare Selected Products")
        compare_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        compare_button.clicked.connect(self.parent.compare_selected_products)
        compare_button.setMinimumWidth(300)
        compare_button.setFont(get_body_font())
        
        main_layout.addWidget(compare_button, alignment=Qt.AlignRight)
    
    def setup_filter_section(self, main_layout):
        """Set up the filter section with simplified layout."""
        # Filter container
        filter_container = QWidget()
        filter_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        filter_layout = QVBoxLayout(filter_container)
        filter_layout.setContentsMargins(10, 10, 10, 10)
        filter_layout.setSpacing(10)
        
        # Filter title
        filter_title = QLabel("Filter Products")
        filter_title.setFont(get_body_font(bold=True))
        filter_layout.addWidget(filter_title)
        
        # Horizontal scrollable area for filter rows
        self.filter_rows_container = QWidget()
        self.filter_rows_layout = QHBoxLayout(self.filter_rows_container)
        self.filter_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_rows_layout.setSpacing(10)
        self.filter_rows_layout.setAlignment(Qt.AlignLeft)
        
        # Add the scrollable area
        filter_scroll = QScrollArea()
        filter_scroll.setWidgetResizable(True)
        filter_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        filter_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        filter_scroll.setFrameShape(QFrame.NoFrame)
        filter_scroll.setWidget(self.filter_rows_container)
        filter_scroll.setMaximumHeight(60)  # Reduced height for horizontal filters
        filter_layout.addWidget(filter_scroll)
        
        # Add Filter button
        add_filter_button = QPushButton("Add Another Filter")
        add_filter_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        add_filter_button.clicked.connect(self.add_filter_row)
        filter_layout.addWidget(add_filter_button, alignment=Qt.AlignLeft)
        
        # Add to main layout
        main_layout.addWidget(filter_container, 0)
    
    def load_product_data(self):
        """Load product data from the repository."""
        self.products_table.setRowCount(0)
        
        # Load products from repository
        repo = ProductRepository.get_instance()
        products = repo.get_filtered_products()
        
        if not products:
            return
            
        self.all_products = products  # Store filtered list of Product objects
        
        # Get the first product to determine column structure
        if products:
            first_product = products[0].to_dict()
            
            # Get all keys from the product dictionary
            self.column_keys = list(first_product.keys())
            
            # Set column count to all fields plus one for checkbox
            self.products_table.setColumnCount(len(self.column_keys) + 1)
            
            # Set column headers
            headers = ["Select"] + self.column_keys
            self.products_table.setHorizontalHeaderLabels(headers)

            # Store original header texts
            self.original_header_texts = {}
            for i, header_text in enumerate(headers):
                self.original_header_texts[i] = header_text

            # Replace specific header texts with shortened versions
            header_replacements = {
                "regulator number": "Reg. #",
                "min days between applications": "DBA"
            }

            for col, key in enumerate(self.column_keys, start=1):
                for original, replacement in header_replacements.items():
                    if key.lower() == original.lower():
                        self.products_table.horizontalHeader().model().setHeaderData(
                            col, Qt.Horizontal, replacement)

            # Set column resize modes
            self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Checkbox column

            # Columns that should resize to content
            content_resize_columns = [
                "regulator number", "formulation", "min rate", "max rate", 
                "rate UOM", "REI (h)", "PHI (d)", "min days between applications", "application method"
            ]

            # Apply resize modes
            for col, key in enumerate(self.column_keys, start=1):
                if any(resize_col.lower() == key.lower() for resize_col in content_resize_columns):
                    self.products_table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
                else:
                    self.products_table.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)
            
            # Columns to hide (case-insensitive matching to handle potential variations)
            columns_to_hide = [
                "country", "region", 
                "[ai1]", "[ai1]UOM", "ai1 eiq",
                "[ai2]", "[ai2]UOM", "ai2 eiq",
                "[ai3]", "[ai3]UOM", "ai3 eiq",
                "[ai4]", "[ai4]UOM", "ai4 eiq"
            ]
            
            # Hidden column indices
            self.hidden_column_indices = []
            
            # Hide specified columns
            for col, key in enumerate(self.column_keys, start=1):
                # Check if the key matches any of the hide keys in a case-insensitive manner
                if any(hide_key.lower() == key.lower() for hide_key in columns_to_hide):
                    self.products_table.setColumnHidden(col, True)
                    self.hidden_column_indices.append(col)
            
            # Create visible column list and mapping for filter dropdowns
            self.visible_columns = []
            self.field_to_column_map = {}
            
            for col, key in enumerate(self.column_keys, start=1):
                if col not in self.hidden_column_indices:
                    self.visible_columns.append(key)
                    # Map the field name to its actual column index in the table
                    self.field_to_column_map[key] = col
            
            # Initialize filters now that we have columns
            # Clear existing filter rows
            self.clear_filter_rows()
            
            # Add initial filter row
            self.add_filter_row()

        # Set row count for products
        self.products_table.setRowCount(len(products))
        
        # Populate the table with product data
        for row, product in enumerate(products):
            product_dict = product.to_dict()

            # Add checkbox for product selection
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, r=row: self.product_selected(r, state))
            checkbox_cell = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_cell)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.products_table.setCellWidget(row, 0, checkbox_cell)

            # Add all product fields
            for col, key in enumerate(self.column_keys, start=1):
                value = product_dict.get(key, "")
                self.products_table.setItem(row, col, QTableWidgetItem(str(value) if value is not None else ""))
    
    def add_filter_row(self):
        """Add a new filter row to the filter section."""
        # Only add filter rows if we have columns
        if not self.visible_columns:
            return
            
        # Create a new filter row with field-to-column mapping
        filter_row = FilterRow(self.visible_columns, self.field_to_column_map, self)
        filter_row.filter_changed.connect(self.apply_filters)
        filter_row.remove_requested.connect(self.remove_filter_row)
        
        # Add to layout
        self.filter_rows_layout.addWidget(filter_row)
        
        # Add to tracking list
        self.filter_rows.append(filter_row)
        
        # Hide remove button on first row if it's the only one
        if len(self.filter_rows) == 1:
            filter_row.remove_button.setVisible(False)
        else:
            # Make sure all remove buttons are visible if we have multiple rows
            for row in self.filter_rows:
                row.remove_button.setVisible(True)
    
    def remove_filter_row(self, filter_row):
        """Remove a filter row from the filter section."""
        if filter_row in self.filter_rows:
            # Remove from layout
            self.filter_rows_layout.removeWidget(filter_row)
            
            # Remove from tracking list
            self.filter_rows.remove(filter_row)
            
            # Delete the widget
            filter_row.deleteLater()
            
            # Hide remove button on first row if it's the only one
            if len(self.filter_rows) == 1:
                self.filter_rows[0].remove_button.setVisible(False)
            
            # Apply filters after removing a row
            self.apply_filters()
    
    def clear_filter_rows(self):
        """Clear all filter rows."""
        # Remove all filter rows
        for filter_row in self.filter_rows:
            self.filter_rows_layout.removeWidget(filter_row)
            filter_row.deleteLater()
        
        # Clear tracking list
        self.filter_rows = []
    
    def apply_filters(self):
        """Apply all active filters to the products table."""
        # Show all rows initially
        for row in range(self.products_table.rowCount()):
            self.products_table.showRow(row)
        
        # Collect all valid filter criteria
        filter_criteria = []
        for filter_row in self.filter_rows:
            criteria = filter_row.get_filter_criteria()
            if criteria:
                column_index, filter_text = criteria
                
                # Only add non-empty filters
                if filter_text:
                    filter_criteria.append(criteria)
        
        # No filters active, return early
        if not filter_criteria:
            return
        
        # Check each row against all active filters
        for row in range(self.products_table.rowCount()):
            show_row = True
            
            # Check each active filter
            for column_index, filter_text in filter_criteria:
                # Get cell text
                item = self.products_table.item(row, column_index)
                cell_text = item.text().lower() if item else ""
                
                # If cell text doesn't contain filter text, hide the row
                if filter_text not in cell_text:
                    show_row = False
                    break
            
            # Show or hide the row based on filter results
            if show_row:
                self.products_table.showRow(row)
            else:
                self.products_table.hideRow(row)
    
    def product_selected(self, row, state):
        """Handle product selection for comparison."""
        product = self.all_products[row]
        if state:
            if product not in self.parent.selected_products:
                self.parent.selected_products.append(product)
        else:
            if product in self.parent.selected_products:
                self.parent.selected_products.remove(product)