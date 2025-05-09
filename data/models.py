"""
Custom Qt Models for the LORENZO POZZI Pesticide App.

This module provides custom implementations of Qt's Model classes to
support the application's Model/View architecture.
"""

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PySide6.QtGui import QBrush, QColor
from data.product_model import Product
from typing import List, Any, Optional

class ProductTableModel(QAbstractTableModel):
    """
    Table model for displaying pesticide products.
    
    This model provides a Qt-friendly interface to the product data for
    use with table views. It supports displaying, sorting, and filtering.
    """
    
    def __init__(self, products: List[Product] = None, parent=None):
        """Initialize the model with optional product data."""
        super().__init__(parent)
        self._products = products or []
        self._headers = [
            "", "Product Type", "Product Name", "Producer Name", "Regulator Number",
            "Application Method", "Formulation", "Min Rate", "Max Rate", "Rate UOM",
            "REI (h)", "PHI (d)", "Min Days Between", "Active Ingredients"
        ]  # First header is empty for checkbox column
        
        # Map header names to product attributes or computed values
        self._column_map = {
            "": None,  # No mapping for checkbox column
            "Product Type": "product_type",
            "Product Name": "product_name",
            "Producer Name": "producer_name",
            "Regulator Number": "regulator_number",
            "Application Method": "application_method",
            "Formulation": "formulation",
            "Min Rate": "label_minimum_rate",
            "Max Rate": "label_maximum_rate",
            "Rate UOM": "rate_uom",
            "REI (h)": "rei_hours",
            "PHI (d)": "phi_days", 
            "Min Days Between": "min_days_between_applications",
            "Active Ingredients": lambda product: ", ".join(product.active_ingredients)
        }
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of rows in the model."""
        return len(self._products)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns in the model."""
        return len(self._headers)
    
    def data(self, index: QModelIndex, role=Qt.DisplayRole) -> Any:
        """Return data for the given index and role."""
        if not index.isValid():
            return None
            
        if index.row() >= len(self._products) or index.row() < 0:
            return None
            
        product = self._products[index.row()]
        column = index.column()
        column_name = self._headers[column]
        
        # Display role - what is shown in the cell
        if role == Qt.DisplayRole:
            attr = self._column_map[column_name]
            
            # Handle computed values (functions)
            if callable(attr):
                return str(attr(product) or "")
                
            # Handle direct attributes
            value = getattr(product, attr, None)
            if isinstance(value, (int, float)) and value is not None:
                if attr in ["label_minimum_rate", "label_maximum_rate"]:
                    return f"{value:.2f}" if value else ""
                return str(value)
            return str(value or "")
            
        # Alignment role - how text is aligned in the cell    
        elif role == Qt.TextAlignmentRole:
            # Center numeric values
            attr = self._column_map[column_name]
            if not callable(attr) and attr in [
                "label_minimum_rate", "label_maximum_rate", "rei_hours", 
                "phi_days", "min_days_between_applications"
            ]:
                return Qt.AlignCenter
            return Qt.AlignLeft | Qt.AlignVCenter
        
        # Remove EIQ-specific background and tooltip code
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole) -> Any:
        """Return header data for the given section, orientation and role."""
        if role != Qt.DisplayRole:
            return None
            
        if orientation == Qt.Horizontal and 0 <= section < len(self._headers):
            return self._headers[section]
            
        return None
    
    def setProducts(self, products: List[Product]) -> None:
        """Set the products for this model and refresh the view."""
        self.beginResetModel()
        self._products = products
        self.endResetModel()
    
    def getProduct(self, row: int) -> Optional[Product]:
        """Get the product at the specified row."""
        if 0 <= row < len(self._products):
            return self._products[row]
        return None


class ProductFilterProxyModel(QSortFilterProxyModel):
    """
    Filter proxy model for product data.
    
    This model provides filtering capabilities on top of the ProductTableModel.
    It supports filtering by multiple columns and criteria.
    """
    
    def __init__(self, parent=None):
        """Initialize the proxy model."""
        super().__init__(parent)
        # Dictionary to store filter criteria for each column
        # Format: {column_index: filter_text}
        self._filter_criteria = {}
    
    def setFilterCriteria(self, column: int, filter_text: str) -> None:
        """Set filter criteria for a specific column."""
        if filter_text:
            self._filter_criteria[column] = filter_text.lower()
        elif column in self._filter_criteria:
            del self._filter_criteria[column]
        
        # Apply the filters
        self.invalidateFilter()
    
    def clearFilters(self) -> None:
        """Clear all filters."""
        self._filter_criteria.clear()
        self.invalidateFilter()
    
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Determine if a row should be shown based on filter criteria."""
        # If no filters, accept all rows
        if not self._filter_criteria:
            return True
            
        # Check each filter criteria
        source_model = self.sourceModel()
        
        for column, filter_text in self._filter_criteria.items():
            index = source_model.index(source_row, column, source_parent)
            cell_text = source_model.data(index, Qt.DisplayRole).lower()
            
            # If any filter doesn't match, reject the row
            if filter_text not in cell_text:
                return False
                
        # All filters passed
        return True


class ProductComparisonModel(QAbstractTableModel):
    """
    Table model for comparing product properties side by side.
    
    This model is designed for the product comparison view, where products are columns
    and properties are rows.
    """
    
    def __init__(self, products: List[Product] = None, parent=None):
        """Initialize the model with optional product data."""
        super().__init__(parent)
        self._products = products or []
        
        # Define the properties to show and hide
        self._properties = [
            "product_type", "product_name", "producer_name", "regulator_number",
            "application_method", "formulation", "label_minimum_rate", "label_maximum_rate",
            "rate_uom", "rei_hours", "phi_days", "min_days_between_applications"
        ]
        
        # Human-readable names for properties
        self._property_names = {
            "product_type": "Product Type",
            "product_name": "Product Name",
            "producer_name": "Producer",
            "regulator_number": "Reg. Number",
            "application_method": "Application Method",
            "formulation": "Formulation",
            "label_minimum_rate": "Min Rate",
            "label_maximum_rate": "Max Rate",
            "rate_uom": "Rate UOM",
            "rei_hours": "REI (hours)",
            "phi_days": "PHI (days)",
            "min_days_between_applications": "Min Days Between Apps",
        }
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of rows (properties) in the model."""
        return len(self._properties)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns (products + 1 for property names) in the model."""
        return len(self._products) + 1
    
    def data(self, index: QModelIndex, role=Qt.DisplayRole) -> Any:
        """Return data for the given index and role."""
        if not index.isValid():
            return None
            
        row = index.row()
        col = index.column()
        
        if row >= len(self._properties) or row < 0:
            return None
            
        # First column is property names
        if col == 0:
            if role == Qt.DisplayRole:
                prop = self._properties[row]
                return self._property_names.get(prop, prop)
                
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignRight | Qt.AlignVCenter
                
            return None
            
        # Product data columns
        product_idx = col - 1
        if product_idx >= len(self._products) or product_idx < 0:
            return None
            
        product = self._products[product_idx]
        prop = self._properties[row]
        
        if role == Qt.DisplayRole:
            value = getattr(product, prop, None)
            
            # Format numeric values for better display
            if isinstance(value, (int, float)) and value is not None:
                if prop in ["label_minimum_rate", "label_maximum_rate"]:
                    return f"{value:.2f}" if value else "-"
                return str(value)
                
            return str(value or "-")
            
        elif role == Qt.TextAlignmentRole:
            # Center numeric values
            if prop in ["label_minimum_rate", "label_maximum_rate", "rei_hours", "phi_days", "min_days_between_applications"]:
                return Qt.AlignCenter
                
            return Qt.AlignLeft | Qt.AlignVCenter
            
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole) -> Any:
        """Return header data for the given section, orientation and role."""
        if role != Qt.DisplayRole:
            return None
            
        if orientation == Qt.Horizontal:
            if section == 0:
                return "Property"
            product_idx = section - 1
            if 0 <= product_idx < len(self._products):
                return self._products[product_idx].product_name
                
        return None
    
    def setProducts(self, products: List[Product]) -> None:
        """Set the products for this model and refresh the view."""
        self.beginResetModel()
        self._products = products
        self.endResetModel()