"""
Product table widget for the LORENZO POZZI Pesticide App.

This module defines the ProductTable widget which provides a table
view of products with selection, filtering, and sorting capabilities.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from common import GENERIC_TABLE_STYLE, get_medium_font


class ProductTable(QTableWidget):
    """A table widget for displaying product information."""
    
    selection_changed = Signal(list)  # Signal emitted when selection changes
    
    def __init__(self, parent=None):
        """Initialize the product table."""
        super().__init__(parent)
        self.all_products = []
        self.selected_products = []
        self.column_keys = []
        self.visible_columns = []
        self.field_to_column_map = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Configure table appearance
        self.setStyleSheet(GENERIC_TABLE_STYLE)
        self.setFont(get_medium_font())
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Configure header
        header = self.horizontalHeader()
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self.on_header_clicked)
    
    def set_products(self, products, column_keys=None, column_config=None):
        """Set the products to display in the table with configuration.
        
        Args:
            products: List of product objects
            column_keys: Optional list of column keys to display
            column_config: Optional configuration for columns 
                {
                   "hide_columns": [...],
                   "rename_columns": {"original": "new"},
                   "special_columns": {"groups": {"after": "ai1"}}
                }
        """
        # Default configuration if not provided
        if column_config is None:
            column_config = self.get_default_column_config()
        
        # Clear existing table
        self.clear()
        self.setRowCount(0)
        self.visible_columns = []
        self.field_to_column_map = {}
        
        # Store products
        self.all_products = products
        self.selected_products = []
        
        if not products:
            return
        
        # Determine columns to display
        if column_keys is None:
            # Get columns from first product
            first_product = products[0].to_dict()
            self.column_keys = list(first_product.keys())
        else:
            self.column_keys = column_keys
        
        # Configure table columns using the configuration
        self._setup_table_columns(column_config)
        
        # Set row count
        self.setRowCount(len(products))
        
        # Fill table with data
        self._populate_table(products, column_config)
        
        # Update visible columns and mapping for filtering
        self._update_visible_columns_map(column_config)
    
    def get_default_column_config(self):
        """Get the default column configuration."""
        return {
            "hide_columns": [
                "country", "region", "min days between applications",
                "min rate", "max rate", "rate UOM",
                "[ai1]", "[ai1]uom", "ai1 eiq",
                "[ai2]", "[ai2]uom", "ai2 eiq", "ai2",
                "[ai3]", "[ai3]uom", "ai3 eiq", "ai3",
                "[ai4]", "[ai4]uom", "ai4 eiq", "ai4"
            ],
            "rename_columns": {
                "ai1": "AIs"
            },
            "special_columns": {
                "groups": {"after": "ai1"}
            }
        }
    
    def _setup_table_columns(self, config):
        """Configure table columns based on provided configuration.
        
        Args:
            config: Column configuration dictionary
        """
        hide_columns = config.get("hide_columns", [])
        rename_columns = config.get("rename_columns", {})
        special_columns = config.get("special_columns", {})
        
        # Find special column positions
        special_col_positions = {}
        
        # Find AI1 column position (used for Groups column)
        ai1_col = -1
        for i, key in enumerate(self.column_keys):
            if key.lower() == "ai1":
                ai1_col = i
                break
        
        # Calculate positions for special columns
        for special_key, special_config in special_columns.items():
            if special_config.get("after") == "ai1" and ai1_col >= 0:
                special_col_positions[special_key] = ai1_col + 2  # +1 for checkbox, +1 for position after AI1
        
        # Calculate total number of columns needed
        additional_cols = 1  # +1 for checkbox
        for special_key in special_col_positions:
            if special_key not in self.column_keys:  # Only count if not already in column_keys
                additional_cols += 1
                
        col_count = len(self.column_keys) + additional_cols
        self.setColumnCount(col_count)
        
        # Set header labels
        headers = [""] + self.column_keys  # [""] for checkbox column
        
        # Insert special column headers
        for special_key, position in special_col_positions.items():
            if position > 0 and special_key not in self.column_keys:
                headers.insert(position, special_key.capitalize())
        
        self.setHorizontalHeaderLabels(headers)
        
        # Apply rename operations
        for col, key in enumerate(self.column_keys, start=1):
            # Calculate the actual table column index
            table_col = col
            for special_key, position in special_col_positions.items():
                if position > 0 and col >= position and special_key not in self.column_keys:
                    table_col = col + 1  # Adjust for inserted special column
            
            # Apply column renaming
            if key.lower() in [k.lower() for k in rename_columns.keys()]:
                for orig_key, new_name in rename_columns.items():
                    if key.lower() == orig_key.lower():
                        self.horizontalHeader().model().setHeaderData(
                            table_col, Qt.Horizontal, new_name
                        )
            
            # Hide specified columns
            if any(key.lower() == hide_key.lower() for hide_key in hide_columns):
                self.setColumnHidden(table_col, True)
        
        # Set column sizing
        for col in range(col_count):
            # Set checkbox column to fixed width
            if col == 0:
                self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)
                self.setColumnWidth(col, 25)
            # Set name column to stretch
            elif self.horizontalHeaderItem(col) and self.horizontalHeaderItem(col).text().lower() == "name":
                self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)
            # Set AIs column to fixed width
            elif self.horizontalHeaderItem(col) and self.horizontalHeaderItem(col).text().lower() == "ais":
                self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)
                self.setColumnWidth(col, 200)
            # Set Groups column to fixed width
            elif self.horizontalHeaderItem(col) and self.horizontalHeaderItem(col).text().lower() == "groups":
                self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)
                self.setColumnWidth(col, 200)
            # Set registrant column to stretch
            elif self.horizontalHeaderItem(col) and self.horizontalHeaderItem(col).text().lower() == "registrant":
                self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)
            # Set type column to fixed width
            elif self.horizontalHeaderItem(col) and self.horizontalHeaderItem(col).text().lower() == "type":
                self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)
                self.setColumnWidth(col, 150)
            # Set all other columns to fixed width
            elif not self.isColumnHidden(col):
                self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)
                self.setColumnWidth(col, 100)
    
    def _populate_table(self, products, config):
        """Populate table with product data.
        
        Args:
            products: List of product objects
            config: Column configuration dictionary
        """
        special_columns = config.get("special_columns", {})
        
        # Find AI1 column position (for Groups column)
        ai1_col = -1
        for i, key in enumerate(self.column_keys):
            if key.lower() == "ai1":
                ai1_col = i
                break
        
        # Calculate groups column position
        groups_col = -1
        if "groups" in special_columns and special_columns["groups"].get("after") == "ai1" and ai1_col >= 0:
            groups_col = ai1_col + 2  # +1 for checkbox, +1 for position after AI1
        
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
            self.setCellWidget(row, 0, checkbox_cell)
            
            # Process groups data if needed
            if groups_col > 0:
                ai_groups = product.get_ai_groups()
                # Process groups to consolidate by organization code
                org_groups = {}
                for group_text in ai_groups:
                    if not group_text:
                        continue
                    for part in group_text.split(', '):
                        if ':' in part:
                            org, code = part.split(':', 1)
                            org = org.strip()
                            code = code.strip()
                            if org not in org_groups:
                                org_groups[org] = []
                            if code not in org_groups[org]:
                                org_groups[org].append(code)
                
                # Format the consolidated groups
                groups_formatted = []
                for org, codes in org_groups.items():
                    groups_formatted.append(f"{org}: {', '.join(codes)}")
                
                groups_text = "; ".join(groups_formatted)
                self.setItem(row, groups_col, QTableWidgetItem(groups_text))
            
            # Fill all other data cells
            for col, key in enumerate(self.column_keys, start=1):
                # Calculate the actual table column index
                table_col = col
                if groups_col > 0 and col >= groups_col:
                    table_col = col + 1  # Adjust for inserted Groups column
                
                value = product_dict.get(key, "")
                if value is not None:
                    self.setItem(row, table_col, QTableWidgetItem(str(value)))
                else:
                    self.setItem(row, table_col, QTableWidgetItem(""))
    
    def _update_visible_columns_map(self, config):
        """Update the list of visible columns and their mapping."""
        hide_columns = config.get("hide_columns", [])
        rename_columns = config.get("rename_columns", {})
        special_columns = config.get("special_columns", {})
        
        self.visible_columns = []
        self.field_to_column_map = {}
        
        # Find AI column first
        ai1_col = -1
        for i, key in enumerate(self.column_keys):
            if key.lower() == "ai1":
                ai1_col = i
                break
        
        # Calculate groups column position
        groups_col = -1
        if "groups" in special_columns and special_columns["groups"].get("after") == "ai1" and ai1_col >= 0:
            groups_col = ai1_col + 2  # +1 for checkbox, +1 for position after AI1
        
        # Setup column properties
        for col, key in enumerate(self.column_keys, start=1):
            # Calculate the actual table column index
            table_col = col
            if groups_col > 0 and col >= groups_col:
                table_col = col + 1  # Adjust for inserted Groups column
            
            # Rename AI column
            if key.lower() == "ai1":
                # Add to visible columns for filtering with new name
                display_name = rename_columns.get(key, key)
                self.visible_columns.append(display_name)
                self.field_to_column_map[display_name] = table_col
            
            # Skip hidden columns
            elif any(key.lower() == hide_key.lower() for hide_key in hide_columns):
                pass
            
            # Add visible columns to filter options
            else:
                self.visible_columns.append(key)
                self.field_to_column_map[key] = table_col
        
        # Add Groups column to visible columns if present
        if groups_col > 0:
            self.visible_columns.append("Groups")
            self.field_to_column_map["Groups"] = groups_col
    
    def get_visible_columns(self):
        """Get visible columns and their mapping."""
        return self.visible_columns, self.field_to_column_map
    
    def product_selected(self, row, state):
        """Handle product selection from checkbox."""
        product = self.all_products[row]
        if state:
            if product not in self.selected_products:
                self.selected_products.append(product)
        else:
            if product in self.selected_products:
                self.selected_products.remove(product)
        
        self.selection_changed.emit(self.selected_products)
    
    def get_selected_products(self):
        """Get the currently selected products."""
        return self.selected_products
    
    def clear_selection(self):
        """Clear all product selections."""
        self.selected_products = []
        
        # Uncheck all checkboxes
        for row in range(self.rowCount()):
            checkbox_widget = self.cellWidget(row, 0)
            if checkbox_widget:
                layout = checkbox_widget.layout()
                if layout and layout.count() > 0:
                    checkbox = layout.itemAt(0).widget()
                    if isinstance(checkbox, QCheckBox):
                        checkbox.setChecked(False)
        
        self.selection_changed.emit(self.selected_products)
    
    def on_header_clicked(self, column):
        """Handle column header click for sorting."""
        # Skip checkbox column
        if column == 0:
            return
            
        # Sort the table by the selected column
        self.sortByColumn(column, Qt.AscendingOrder)
    
    def apply_filter(self, column, filter_text):
        """Apply a text filter to a specific column."""
        filter_text = filter_text.lower()
        
        for row in range(self.rowCount()):
            # Get item in the column
            item = self.item(row, column)
            show_row = True
            
            if item:
                # Check if item text contains filter text
                item_text = item.text().lower()
                show_row = filter_text in item_text
            
            # Show or hide the row
            self.setRowHidden(row, not show_row)
    
    def apply_filters(self, filters):
        """Apply multiple filters to the table."""
        # Show all rows initially
        for row in range(self.rowCount()):
            self.showRow(row)
        
        # Apply each filter in sequence
        for column_index, filter_text in filters:
            if filter_text:  # Only apply if filter text is not empty
                for row in range(self.rowCount()):
                    if not self.isRowHidden(row):  # Only check visible rows
                        item = self.item(row, column_index)
                        cell_text = item.text().lower() if item else ""
                        if filter_text not in cell_text:
                            self.setRowHidden(row, True)