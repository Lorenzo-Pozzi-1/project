"""
Product table widget for the LORENZO POZZI Pesticide App.

This module defines the ProductTable widget which provides a table
view of products with selection, filtering, and sorting capabilities.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from common import GENERIC_TABLE_STYLE, get_medium_font


class NumericTableWidgetItem(QTableWidgetItem):
    """A table widget item that sorts numerically instead of alphabetically."""
    
    def __lt__(self, other):
        """Override less than comparison for proper numeric sorting."""
        try:
            # Try to convert both values to float for comparison
            self_value = float(self.text()) if self.text() and self.text() != "--" else 0
            other_value = float(other.text()) if other.text() and other.text() != "--" else 0
            return self_value < other_value
        except (ValueError, TypeError):
            # Fall back to string comparison if conversion fails
            return super().__lt__(other)


class ProductTable(QTableWidget):
    """A table widget for displaying product information."""
    
    selection_changed = Signal(list)  # Signal emitted when selection changes
    
    # Define the exact columns we want in the exact order
    COLUMNS = [
        {"key": "checkbox", "header": "", "width": 25, "resize": "fixed"},
        {"key": "type", "header": "Type", "width": 150, "resize": "fixed"},
        {"key": "name", "header": "Name", "width": None, "resize": "stretch"},
        {"key": "use", "header": "Use", "width": 200, "resize": "fixed"},
        {"key": "registrant", "header": "Registrant", "width": None, "resize": "stretch"},
        {"key": "formulation", "header": "Formulation", "width": 120, "resize": "fixed"},
        {"key": "REI (h)", "header": "REI (h)", "width": 80, "resize": "fixed"},
        {"key": "PHI (d)", "header": "PHI (d)", "width": 80, "resize": "fixed"},
        {"key": "AIs", "header": "AIs", "width": 200, "resize": "fixed"},
        {"key": "Groups", "header": "Groups", "width": 200, "resize": "fixed"},
    ]
    
    def __init__(self, parent=None):
        """Initialize the product table."""
        super().__init__(parent)
        self.all_products = []
        self.selected_products = []
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
        
        # Set up columns
        self.setColumnCount(len(self.COLUMNS))
        
        # Set headers and column properties
        headers = []
        for col_index, col_config in enumerate(self.COLUMNS):
            headers.append(col_config["header"])
            
            # Set column width and resize mode
            if col_config["resize"] == "fixed":
                self.horizontalHeader().setSectionResizeMode(col_index, QHeaderView.Fixed)
                if col_config["width"]:
                    self.setColumnWidth(col_index, col_config["width"])
            elif col_config["resize"] == "stretch":
                self.horizontalHeader().setSectionResizeMode(col_index, QHeaderView.Stretch)
        
        self.setHorizontalHeaderLabels(headers)
        
        # Configure header for sorting
        header = self.horizontalHeader()
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self.on_header_clicked)
    
    def set_products(self, products, column_keys=None, column_config=None):
        """Set the products to display in the table.
        
        Args:
            products: List of product objects
            column_keys: Ignored - kept for backward compatibility
            column_config: Ignored - kept for backward compatibility
        """
        # Clear existing table data (but preserve headers)
        self.setRowCount(0)
        self.clearContents()  # Only clear cell contents, not headers
        
        # Store products
        self.all_products = products
        self.selected_products = []
        
        if not products:
            return
        
        # Set row count
        self.setRowCount(len(products))
        
        # Restore headers (in case they were cleared)
        headers = [col_config["header"] for col_config in self.COLUMNS]
        self.setHorizontalHeaderLabels(headers)
        
        # Fill table with data
        self._populate_table(products)
    
    def _populate_table(self, products):
        """Populate table with product data."""
        for row, product in enumerate(products):
            for col_index, col_config in enumerate(self.COLUMNS):
                col_key = col_config["key"]
                
                if col_key == "checkbox":
                    # Add checkbox
                    checkbox = QCheckBox()
                    checkbox.stateChanged.connect(lambda state, r=row: self.product_selected(r, state))
                    checkbox_cell = QWidget()
                    checkbox_layout = QHBoxLayout(checkbox_cell)
                    checkbox_layout.addWidget(checkbox)
                    checkbox_layout.setAlignment(Qt.AlignCenter)
                    checkbox_layout.setContentsMargins(0, 0, 0, 0)
                    self.setCellWidget(row, col_index, checkbox_cell)
                
                elif col_key == "AIs":
                    # Show all active ingredients
                    ais_text = ", ".join(product.active_ingredients) if product.active_ingredients else ""
                    self.setItem(row, col_index, QTableWidgetItem(ais_text))
                
                elif col_key == "Groups":
                    # Show mode of action groups
                    ai_groups = product.get_ai_groups()
                    groups_text = self._format_groups(ai_groups)
                    self.setItem(row, col_index, QTableWidgetItem(groups_text))
                
                elif col_key in ["REI (h)", "PHI (d)"]:
                    # Numeric columns - use NumericTableWidgetItem for proper sorting
                    product_dict = product.to_dict()
                    value = product_dict.get(col_key, "")
                    if value is not None and value != "":
                        self.setItem(row, col_index, NumericTableWidgetItem(str(value)))
                    else:
                        self.setItem(row, col_index, NumericTableWidgetItem("--"))
                
                else:
                    # Standard product field - map to product dictionary
                    product_dict = product.to_dict()
                    value = product_dict.get(col_key, "")
                    if value is not None:
                        self.setItem(row, col_index, QTableWidgetItem(str(value)))
                    else:
                        self.setItem(row, col_index, QTableWidgetItem(""))
    
    def _format_groups(self, ai_groups):
        """Format mode of action groups for display."""
        if not ai_groups:
            return ""
        
        # Consolidate groups by organization
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
        
        return "; ".join(groups_formatted)
    
    def get_visible_columns(self):
        """Get visible columns and their mapping for filtering."""
        visible_columns = []
        field_to_column_map = {}
        
        for col_index, col_config in enumerate(self.COLUMNS):
            if col_config["key"] != "checkbox":  # Skip checkbox column
                visible_columns.append(col_config["header"])
                field_to_column_map[col_config["header"]] = col_index
        
        return visible_columns, field_to_column_map
    
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
            checkbox_widget = self.cellWidget(row, 0)  # Checkbox is always column 0
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
        """Apply multiple filters to the table.
        
        Args:
            filters: List of (column_index, filter_text) tuples
        """
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