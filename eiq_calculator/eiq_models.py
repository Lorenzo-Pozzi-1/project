"""
EIQ Calculator Models for the LORENZO POZZI Pesticide App.

This module provides custom Qt model implementations for the EIQ calculator components.
"""

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QBrush, QColor
from data.product_model import Product
from typing import List, Any, Dict, Optional
from eiq_calculator.eiq_calculations import calculate_product_field_eiq
from eiq_calculator.eiq_conversions import convert_concentration_to_percent

class ActiveIngredientsModel(QAbstractTableModel):
    """
    Model for displaying active ingredients of a product in the EIQ calculator.
    """
    
    def __init__(self, parent=None):
        """Initialize the model."""
        super().__init__(parent)
        self._product = None
        self._headers = ["Active Ingredient", "EIQ", "Concentration", "UOM"]
        self._ai_data = []  # List of dictionaries with AI info
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of rows (active ingredients)."""
        return len(self._ai_data)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns."""
        return len(self._headers)
    
    def data(self, index: QModelIndex, role=Qt.DisplayRole) -> Any:
        """Return data for the given index and role."""
        if not index.isValid() or index.row() >= len(self._ai_data):
            return None
            
        row, col = index.row(), index.column()
        ai_info = self._ai_data[row]
        
        if role == Qt.DisplayRole:
            if col == 0:  # Name
                return ai_info.get("name", "")
            elif col == 1:  # EIQ
                eiq = ai_info.get("eiq")
                return str(eiq) if eiq not in (None, "--") else "--"
            elif col == 2:  # Concentration 
                conc = ai_info.get("concentration")
                return str(conc) if conc not in (None, "--") else "--"
            elif col == 3:  # UOM
                return ai_info.get("uom", "")
                
        elif role == Qt.TextAlignmentRole:
            # Center the text in all columns
            return Qt.AlignCenter
            
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole) -> Any:
        """Return header data for the given section and orientation."""
        if role != Qt.DisplayRole:
            return None
            
        if orientation == Qt.Horizontal and section < len(self._headers):
            return self._headers[section]
            
        return None
    
    def setProduct(self, product: Optional[Product]) -> None:
        """Set the product and update the active ingredients."""
        self.beginResetModel()
        self._product = product
        self._ai_data = []
        
        if product:
            # Extract AI data
            if product.ai1:
                concentration = product.ai1_concentration
                uom = product.ai1_concentration_uom
                
                self._ai_data.append({
                    "name": product.ai1,
                    "eiq": product.ai1_eiq if product.ai1_eiq is not None else "--",
                    "concentration": concentration if concentration is not None else "--",
                    "uom": uom if uom is not None else ""
                })
            
            if product.ai2:
                concentration = product.ai2_concentration
                uom = product.ai2_concentration_uom
                
                self._ai_data.append({
                    "name": product.ai2,
                    "eiq": product.ai2_eiq if product.ai2_eiq is not None else "--",
                    "concentration": concentration if concentration is not None else "--",
                    "uom": uom if uom is not None else ""
                })
            
            if product.ai3:
                concentration = product.ai3_concentration
                uom = product.ai3_concentration_uom
                
                self._ai_data.append({
                    "name": product.ai3,
                    "eiq": product.ai3_eiq if product.ai3_eiq is not None else "--",
                    "concentration": concentration if concentration is not None else "--",
                    "uom": uom if uom is not None else ""
                })
            
            if product.ai4:
                concentration = product.ai4_concentration
                uom = product.ai4_concentration_uom
                
                self._ai_data.append({
                    "name": product.ai4,
                    "eiq": product.ai4_eiq if product.ai4_eiq is not None else "--",
                    "concentration": concentration if concentration is not None else "--",
                    "uom": uom if uom is not None else ""
                })
                
        self.endResetModel()
    
    def getActiveIngredients(self) -> List[Dict[str, Any]]:
        """
        Get active ingredients in a format suitable for EIQ calculations.
        
        Returns:
            List of dictionaries with 'name', 'eiq', and 'percent' keys.
        """
        result = []
        
        for ai in self._ai_data:
            # Skip AIs with missing data
            if ai["eiq"] == "--" or ai["concentration"] == "--":
                continue
                
            try:
                eiq_value = float(ai["eiq"])
                
                # Handle concentration based on UOM
                if "%" in str(ai["concentration"]):
                    percent_value = float(str(ai["concentration"]).replace("%", ""))
                else:
                    percent_value = convert_concentration_to_percent(
                        float(ai["concentration"]), 
                        ai["uom"]
                    ) or 0.0
                
                result.append({
                    "name": ai["name"],
                    "eiq": eiq_value,
                    "percent": percent_value
                })
                
            except (ValueError, TypeError):
                # Skip this ingredient if any conversion fails
                continue
                
        return result


class LabelInfoModel(QAbstractTableModel):
    """
    Model for displaying product label information in the EIQ calculator.
    """
    
    def __init__(self, parent=None):
        """Initialize the model."""
        super().__init__(parent)
        self._product = None
        self._headers = [
            "Application Method", "Min Rate", "Max Rate", "Rate UOM", 
            "REI (hours)", "PHI (days)", "Min Days Between Apps"
        ]
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of rows (always 1 for the selected product)."""
        return 1 if self._product else 0
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns."""
        return len(self._headers)
    
    def data(self, index: QModelIndex, role=Qt.DisplayRole) -> Any:
        """Return data for the given index and role."""
        if not index.isValid() or not self._product:
            return None
            
        col = index.column()
        
        if role == Qt.DisplayRole:
            if col == 0:  # Application Method
                return self._product.application_method or "--"
            elif col == 1:  # Min Rate
                if self._product.label_minimum_rate is not None:
                    return f"{self._product.label_minimum_rate:.2f}"
                return "--"
            elif col == 2:  # Max Rate
                if self._product.label_maximum_rate is not None:
                    return f"{self._product.label_maximum_rate:.2f}"
                return "--"
            elif col == 3:  # Rate UOM
                return self._product.rate_uom or "--"
            elif col == 4:  # REI (hours)
                return str(self._product.rei_hours or "--")
            elif col == 5:  # PHI (days)
                return str(self._product.phi_days or "--")
            elif col == 6:  # Min Days Between Apps
                return str(self._product.min_days_between_applications or "--")
                
        elif role == Qt.TextAlignmentRole:
            # Center the text in all columns
            return Qt.AlignCenter
            
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole) -> Any:
        """Return header data for the given section and orientation."""
        if role != Qt.DisplayRole:
            return None
            
        if orientation == Qt.Horizontal and section < len(self._headers):
            return self._headers[section]
            
        return None
    
    def setProduct(self, product: Optional[Product]) -> None:
        """Set the product to display."""
        self.beginResetModel()
        self._product = product
        self.endResetModel()


class ProductComparisonCalculatorModel(QAbstractTableModel):
    """
    Model for the product comparison calculator table in the EIQ calculator.
    """
    
    def __init__(self, parent=None):
        """Initialize the model."""
        super().__init__(parent)
        self._products_data = []  # List of product data dictionaries
        self._headers = [
            "Product Type", "Product Name", "Active Ingredients", 
            "Application Rate", "Unit", "Applications"
        ]
        # Signal to handle data changes in this model
        self.calculation_required = lambda: None  # Default no-op function
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of rows."""
        return len(self._products_data)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns."""
        return len(self._headers)
    
    def data(self, index: QModelIndex, role=Qt.DisplayRole) -> Any:
        """Return data for the given index and role."""
        if not index.isValid() or index.row() >= len(self._products_data):
            return None
            
        row, col = index.row(), index.column()
        product_data = self._products_data[row]
        
        if role == Qt.DisplayRole:
            product = product_data.get("product")
            if not product:
                return ""
                
            if col == 0:  # Product Type
                return product.product_type or ""
            elif col == 1:  # Product Name
                return product.product_name or ""
            elif col == 2:  # Active Ingredients
                return ", ".join(product.active_ingredients) if product.active_ingredients else "None"
            elif col == 3:  # Application Rate
                return str(product_data.get("rate", 0.0))
            elif col == 4:  # Unit
                return product_data.get("unit", "")
            elif col == 5:  # Applications
                return str(product_data.get("applications", 1))
                
        elif role == Qt.TextAlignmentRole:
            if col in [3, 4, 5]:  # Numeric columns
                return Qt.AlignCenter
            return Qt.AlignLeft | Qt.AlignVCenter
            
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole) -> Any:
        """Return header data for the given section and orientation."""
        if role != Qt.DisplayRole:
            return None
            
        if orientation == Qt.Horizontal and section < len(self._headers):
            return self._headers[section]
            
        return None
    
    def setProducts(self, products_data: List[Dict[str, Any]]) -> None:
        """Set the products data."""
        self.beginResetModel()
        self._products_data = products_data
        self.endResetModel()
    
    def addEmptyRow(self) -> int:
        """Add an empty row and return its index."""
        row = len(self._products_data)
        
        self.beginInsertRows(QModelIndex(), row, row)
        self._products_data.append({
            "product": None,
            "active_ingredients": [],
            "rate": 0.0,
            "unit": "lbs/acre",
            "applications": 1
        })
        self.endInsertRows()
        
        return row
    
    def removeRow(self, row: int, parent=QModelIndex()) -> bool:
        """Remove a row from the model."""
        if row < 0 or row >= len(self._products_data):
            return False
            
        self.beginRemoveRows(parent, row, row)
        self._products_data.pop(row)
        self.endRemoveRows()
        
        # Signal calculation update
        self.calculation_required()
        
        return True
    
    def updateProduct(self, row: int, product: Product, 
                    active_ingredients: List[Dict[str, Any]]=None) -> None:
        """Update the product at the given row."""
        if row < 0 or row >= len(self._products_data):
            return
            
        self._products_data[row]["product"] = product
        
        if active_ingredients is not None:
            self._products_data[row]["active_ingredients"] = active_ingredients
            
        # Update default rate if product has one
        if product and product.label_maximum_rate is not None:
            self._products_data[row]["rate"] = product.label_maximum_rate
        elif product and product.label_minimum_rate is not None:
            self._products_data[row]["rate"] = product.label_minimum_rate
            
        # Update default unit if product has one
        if product and product.rate_uom:
            self._products_data[row]["unit"] = product.rate_uom
            
        # Signal that the model data has changed
        top_left = self.index(row, 0)
        bottom_right = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right)
        
        # Signal calculation update
        self.calculation_required()
    
    def updateRate(self, row: int, rate: float) -> None:
        """Update the application rate for the product at the given row."""
        if row < 0 or row >= len(self._products_data):
            return
            
        self._products_data[row]["rate"] = rate
        
        # Signal that the model data has changed
        index = self.index(row, 3)
        self.dataChanged.emit(index, index)
        
        # Signal calculation update
        self.calculation_required()
    
    def updateUnit(self, row: int, unit: str) -> None:
        """Update the unit for the product at the given row."""
        if row < 0 or row >= len(self._products_data):
            return
            
        self._products_data[row]["unit"] = unit
        
        # Signal that the model data has changed
        index = self.index(row, 4)
        self.dataChanged.emit(index, index)
        
        # Signal calculation update
        self.calculation_required()
    
    def updateApplications(self, row: int, applications: int) -> None:
        """Update the number of applications for the product at the given row."""
        if row < 0 or row >= len(self._products_data):
            return
            
        self._products_data[row]["applications"] = applications
        
        # Signal that the model data has changed
        index = self.index(row, 5)
        self.dataChanged.emit(index, index)
        
        # Signal calculation update
        self.calculation_required()
    
    def getProductData(self, row: int) -> Optional[Dict[str, Any]]:
        """Get the product data for the given row."""
        if row < 0 or row >= len(self._products_data):
            return None
            
        return self._products_data[row]
    
    def calculateFieldEIQ(self, row: int) -> float:
        """Calculate the Field EIQ for the product at the given row."""
        if row < 0 or row >= len(self._products_data):
            return 0.0
            
        product_data = self._products_data[row]
        product = product_data.get("product")
        
        if not product:
            return 0.0
            
        active_ingredients = product_data.get("active_ingredients", [])
        
        # If active ingredients not explicitly provided, extract from product
        if not active_ingredients:
            active_ingredients = []
            
            # Check AI1 data
            if product.ai1 and product.ai1_eiq is not None:
                percent_value = convert_concentration_to_percent(
                    product.ai1_concentration, product.ai1_concentration_uom
                ) or 0.0
                
                active_ingredients.append({
                    "name": product.ai1,
                    "eiq": product.ai1_eiq,
                    "percent": percent_value
                })
                
            # Check AI2 data    
            if product.ai2 and product.ai2_eiq is not None:
                percent_value = convert_concentration_to_percent(
                    product.ai2_concentration, product.ai2_concentration_uom
                ) or 0.0
                
                active_ingredients.append({
                    "name": product.ai2,
                    "eiq": product.ai2_eiq,
                    "percent": percent_value
                })
                
            # Check AI3 data
            if product.ai3 and product.ai3_eiq is not None:
                percent_value = convert_concentration_to_percent(
                    product.ai3_concentration, product.ai3_concentration_uom
                ) or 0.0
                
                active_ingredients.append({
                    "name": product.ai3,
                    "eiq": product.ai3_eiq,
                    "percent": percent_value
                })
                
            # Check AI4 data
            if product.ai4 and product.ai4_eiq is not None:
                percent_value = convert_concentration_to_percent(
                    product.ai4_concentration, product.ai4_concentration_uom
                ) or 0.0
                
                active_ingredients.append({
                    "name": product.ai4,
                    "eiq": product.ai4_eiq,
                    "percent": percent_value
                })
        
        rate = product_data.get("rate", 0.0)
        unit = product_data.get("unit", "lbs/acre")
        applications = product_data.get("applications", 1)
        
        return calculate_product_field_eiq(active_ingredients, rate, unit, applications)


class ComparisonResultsModel(QAbstractTableModel):
    """
    Model for the results table in the EIQ comparison calculator.
    """
    
    def __init__(self, parent=None):
        """Initialize the model."""
        super().__init__(parent)
        self._headers = ["Product", "Field EIQ / ha"]
        self._results = []  # List of (product, field_eiq, source_row) tuples
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of rows."""
        return len(self._results)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns."""
        return len(self._headers)
    
    def data(self, index: QModelIndex, role=Qt.DisplayRole) -> Any:
        """Return data for the given index and role."""
        if not index.isValid() or index.row() >= len(self._results):
            return None
            
        row, col = index.row(), index.column()
        product, field_eiq = self._results[row][0:2]  # First two elements
        
        if role == Qt.DisplayRole:
            if col == 0:  # Product
                return product.product_name
            elif col == 1:  # Field EIQ
                return f"{field_eiq:.2f}" if field_eiq > 0 else "--"
                
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
            
        elif role == Qt.BackgroundRole and col == 1:
            # Color-code Field EIQ values
            if field_eiq <= 0:
                return None
                
            if field_eiq < 33.3:
                return QBrush(QColor(200, 255, 200))  # Light green for low
            elif field_eiq < 66.6:
                return QBrush(QColor(255, 255, 200))  # Light yellow for medium
            else:
                return QBrush(QColor(255, 200, 200))  # Light red for high
                
        elif role == Qt.UserRole:
            # Store the row in the source model
            return self._results[row][2] if len(self._results[row]) > 2 else None
            
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole) -> Any:
        """Return header data for the given section and orientation."""
        if role != Qt.DisplayRole:
            return None
            
        if orientation == Qt.Horizontal and section < len(self._headers):
            return self._headers[section]
            
        return None
    
    def updateResult(self, product: Product, field_eiq: float, source_row: int = None) -> None:
        """
        Add or update a result for a product.
        
        Args:
            product: The Product object
            field_eiq: The calculated Field EIQ value
            source_row: Optional reference to the source row in the comparison table
        """
        # Check if the product is already in the results
        for i, result in enumerate(self._results):
            existing_product = result[0]
            if existing_product == product:
                # Update existing entry
                self.beginResetModel()
                self._results[i] = (product, field_eiq, source_row)
                self.endResetModel()
                return
                
        # Add new entry if field_eiq is valid
        if field_eiq > 0:
            row = len(self._results)
            self.beginInsertRows(QModelIndex(), row, row)
            self._results.append((product, field_eiq, source_row))
            self.endInsertRows()
    
    def removeResult(self, source_row: int) -> None:
        """
        Remove a result based on its source row.
        
        Args:
            source_row: The row in the source model to remove
        """
        for i, result in enumerate(self._results):
            if len(result) > 2 and result[2] == source_row:
                self.beginRemoveRows(QModelIndex(), i, i)
                self._results.pop(i)
                self.endRemoveRows()
                return
    
    def clearResults(self) -> None:
        """Clear all results."""
        self.beginResetModel()
        self._results.clear()
        self.endResetModel()