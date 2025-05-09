"""
Products list tab for the Lorenzo Pozzi Pesticide App with simplified implementation.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, 
                              QHeaderView, QCheckBox, QFrame, QScrollArea)
from PySide6.QtCore import Qt
from common.styles import PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
from data.product_repository import ProductRepository
from products.filter_row import FilterRow


class ProductsListTab(QWidget):
    """Products list tab for displaying and filtering products."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.column_keys = []
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
        filter_container = QWidget()
        filter_layout = QVBoxLayout(filter_container)
        filter_layout.setContentsMargins(10, 10, 10, 10)
        
        # Filter title
        filter_layout.addWidget(QLabel("Filter Products"))
        
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
        
        main_layout.addWidget(filter_container)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setAlternatingRowColors(True)
        self.products_table.verticalHeader().setVisible(False)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.products_table, 1)
        
        # Compare button
        compare_button = QPushButton("View Fact Sheet / Compare Selected Products")
        compare_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        compare_button.clicked.connect(self.parent.compare_selected_products)
        compare_button.setMinimumWidth(300)
        main_layout.addWidget(compare_button, alignment=Qt.AlignRight)
    
    def load_product_data(self):
        """Load product data from repository."""
        self.products_table.setRowCount(0)
        
        # Get products
        products_repo = ProductRepository.get_instance()
        products = products_repo.get_filtered_products()
        if not products:
            return
                
        self.all_products = products
        
        # Get columns from first product
        first_product = products[0].to_dict()
        self.column_keys = list(first_product.keys())
        
        # Configure table columns
        self.setup_table_columns()
        
        # Set row count
        self.products_table.setRowCount(len(products))
        
        # Fill table with data
        self.populate_table(products)
        
        # Add initial filter row only if we have visible columns and no filter rows yet
        if self.visible_columns and not self.filter_rows:
            self.add_filter_row()
    
    def setup_table_columns(self):
        """Configure table columns with simplified approach."""
        # Find AI1 column first
        ai1_col = -1
        for i, key in enumerate(self.column_keys):
            if key.lower() == "ai1":
                ai1_col = i
                break
        
        # Basic setup - all columns plus checkbox and groups column
        col_count = len(self.column_keys) + 2  # +1 for checkbox, +1 for groups
        self.products_table.setColumnCount(col_count)
        
        # Set header labels
        headers = ["Select"] + self.column_keys
        # Insert Groups header after AI1
        if ai1_col >= 0:
            groups_col = ai1_col + 2  # +1 for checkbox, +1 for position after AI1
            headers.insert(groups_col, "Groups")
        else:
            groups_col = -1
        
        self.products_table.setHorizontalHeaderLabels(headers)
        
        # Track columns and setup filtering
        self.visible_columns = []
        self.field_to_column_map = {}
        
        # Hide columns and manage visibility
        hide_columns = ["country", "region", "[ai1]", "[ai1]uom", "ai1 eiq", 
                        "[ai2]", "[ai2]uom", "ai2 eiq", "[ai3]", "[ai3]uom", "ai3 eiq",
                        "[ai4]", "[ai4]uom", "ai4 eiq", "ai2", "ai3", "ai4"]
        
        # Setup column properties
        for col, key in enumerate(self.column_keys, start=1):
            # Calculate the actual table column index
            table_col = col
            if groups_col > 0 and col >= groups_col:
                table_col = col + 1  # Adjust for inserted Groups column
            
            # Rename AI column
            if key.lower() == "ai1":
                self.products_table.horizontalHeader().model().setHeaderData(table_col, Qt.Horizontal, "AIs")
                # Add to visible columns for filtering
                self.visible_columns.append("AIs")
                self.field_to_column_map["AIs"] = table_col
            
            # Hide specified columns
            elif any(key.lower() == hide_key.lower() for hide_key in hide_columns):
                self.products_table.setColumnHidden(table_col, True)
            
            # Add visible columns to filter options
            else:
                self.visible_columns.append(key)
                self.field_to_column_map[key] = table_col
        
        # Add Groups column to visible columns
        if groups_col > 0:
            self.visible_columns.append("Groups")
            self.field_to_column_map["Groups"] = groups_col
        
        # Set column sizing
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for col in range(1, col_count):
            if not self.products_table.isColumnHidden(col):
                self.products_table.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)

    def populate_table(self, products):
        """Populate table with product data."""
        # Find AI column
        ai1_col = -1
        for i, key in enumerate(self.column_keys):
            if key.lower() == "ai1":
                ai1_col = i
                break
        
        # Calculate groups column position
        groups_col = ai1_col + 2 if ai1_col >= 0 else -1  # +1 for checkbox, +1 for position after AI1
        
        # Fill table rows
        for row, product in enumerate(products):
            product_dict = product.to_dict()
            
            # Add checkbox
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, r=row: self.product_selected(r, state))
            checkbox_cell = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_cell)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.products_table.setCellWidget(row, 0, checkbox_cell)
            
            # Fill data cells
            for col, key in enumerate(self.column_keys, start=1):
                # Calculate the actual table column index
                table_col = col
                if groups_col > 0 and col >= groups_col:
                    table_col = col + 1  # Adjust for inserted Groups column
                
                # Handle active ingredients
                if col == ai1_col + 1:  # +1 for checkbox
                    ai_text = ", ".join(product.active_ingredients)
                    self.products_table.setItem(row, table_col, QTableWidgetItem(ai_text))
                    
                    # Add MoA groups data
                    if groups_col > 0:
                        ai_groups = product.get_ai_groups()
                        groups_text = ", ".join(filter(None, ai_groups))  # Filter out empty strings
                        self.products_table.setItem(row, groups_col, QTableWidgetItem(groups_text))
                else:
                    # Normal column
                    value = product_dict.get(key, "")
                    if value is not None:
                        self.products_table.setItem(row, table_col, QTableWidgetItem(str(value)))
                    else:
                        self.products_table.setItem(row, table_col, QTableWidgetItem(""))
    
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
        # Show all rows initially
        for row in range(self.products_table.rowCount()):
            self.products_table.showRow(row)
        
        # Get valid filter criteria
        filters = []
        for filter_row in self.filter_rows:
            criteria = filter_row.get_filter_criteria()
            if criteria and criteria[1]:  # Only if column and non-empty text
                filters.append(criteria)
        
        if not filters:
            return
        
        # Apply filters
        for row in range(self.products_table.rowCount()):
            show_row = True
            for column_index, filter_text in filters:
                item = self.products_table.item(row, column_index)
                cell_text = item.text().lower() if item else ""
                if filter_text not in cell_text:
                    show_row = False
                    break
            
            self.products_table.setRowHidden(row, not show_row)
    
    def product_selected(self, row, state):
        """Handle product selection for comparison."""
        product = self.all_products[row]
        if state:
            if product not in self.parent.selected_products:
                self.parent.selected_products.append(product)
        else:
            if product in self.parent.selected_products:
                self.parent.selected_products.remove(product)