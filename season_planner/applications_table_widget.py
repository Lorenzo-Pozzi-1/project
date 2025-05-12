"""
Applications Table Widget for the LORENZO POZZI Pesticide App.

This module defines a custom table widget for managing pesticide applications
within a season plan.
"""

from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView, 
                             QComboBox, QDoubleSpinBox, QLineEdit, QWidget, 
                             QHBoxLayout, QPushButton)
from PySide6.QtCore import Qt, Signal
from data.product_repository import ProductRepository
from eiq_calculator.eiq_calculations import calculate_field_eiq


class ApplicationsTableWidget(QTableWidget):
    """
    Custom table widget for managing pesticide applications in a season plan.
    
    Each row represents a single application with fields for date, product,
    rate, area, method, etc. Field EIQ is calculated automatically.
    """
    
    # Signal emitted when any application data changes
    applications_changed = Signal()
    
    def __init__(self, parent=None):
        """Initialize the applications table widget."""
        super().__init__(parent)
        self.parent = parent
        self.field_area = 10.0  # Default field area
        self.field_area_uom = "ha"  # Default unit of measure
        self.setup_table()
    
    def setup_table(self):
        """Set up the table structure and appearance."""
        # Define columns
        columns = ["Date", "Product", "Rate", "UOM", "Area", "Method", "AI Groups", "Field EIQ"]
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        
        # Configure table appearance
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Set column widths - adjust percentages as needed
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Date
        header.setSectionResizeMode(1, QHeaderView.Stretch)      # Product
        header.setSectionResizeMode(2, QHeaderView.Interactive)  # Rate
        header.setSectionResizeMode(3, QHeaderView.Interactive)  # UOM
        header.setSectionResizeMode(4, QHeaderView.Interactive)  # Area
        header.setSectionResizeMode(5, QHeaderView.Interactive)  # Method
        header.setSectionResizeMode(6, QHeaderView.Stretch)      # AI Groups
        header.setSectionResizeMode(7, QHeaderView.Interactive)  # Field EIQ
        
        # Set initial column widths
        self.setColumnWidth(0, 120)  # Date
        self.setColumnWidth(2, 70)   # Rate
        self.setColumnWidth(3, 70)   # UOM
        self.setColumnWidth(4, 70)   # Area
        self.setColumnWidth(5, 120)  # Method
        self.setColumnWidth(7, 90)   # Field EIQ
    
    def set_field_area(self, area, uom):
        """
        Set the default field area for new applications.
        
        Args:
            area (float): Area value
            uom (str): Unit of measure
        """
        self.field_area = area
        self.field_area_uom = uom
    
    def add_application_row(self):
        """Add a new empty application row to the table."""
        # Get current row count
        row = self.rowCount()
        
        # Insert new row
        self.insertRow(row)
        
        # Date field (text input)
        date_edit = QLineEdit()
        date_edit.setPlaceholderText("Enter date or description")
        date_edit.textChanged.connect(lambda: self.on_cell_changed(row))
        self.setCellWidget(row, 0, date_edit)
        
        # Product selection
        product_combo = QComboBox()
        product_combo.addItem("Select a product...")
        
        # Load products from repository
        products_repo = ProductRepository.get_instance()
        products = products_repo.get_filtered_products()
        
        for product in products:
            product_combo.addItem(product.product_name)
        
        product_combo.currentIndexChanged.connect(lambda: self.update_product_info(row))
        self.setCellWidget(row, 1, product_combo)
        
        # Application rate
        rate_spin = QDoubleSpinBox()
        rate_spin.setRange(0.0, 9999.99)
        rate_spin.setDecimals(2)
        rate_spin.setValue(0.0)
        rate_spin.valueChanged.connect(lambda: self.calculate_row_eiq(row))
        self.setCellWidget(row, 2, rate_spin)
        
        # Rate UOM
        uom_combo = QComboBox()
        common_uoms = ["kg/ha", "l/ha", "g/ha", "ml/ha", "lbs/acre", "fl oz/acre", "oz/acre"]
        uom_combo.addItems(common_uoms)
        uom_combo.currentIndexChanged.connect(lambda: self.calculate_row_eiq(row))
        self.setCellWidget(row, 3, uom_combo)
        
        # Area treated
        area_spin = QDoubleSpinBox()
        area_spin.setRange(0.0, 9999.99)
        area_spin.setDecimals(1)
        area_spin.setValue(self.field_area)  # Default to field area
        area_spin.valueChanged.connect(lambda: self.calculate_row_eiq(row))
        self.setCellWidget(row, 4, area_spin)
        
        # Application method
        method_combo = QComboBox()
        method_options = ["Broadcast", "Band", "Foliar spray", "Soil incorporation",
                        "Seed treatment", "Spot treatment", "Chemigation"]
        method_combo.addItems(method_options)
        method_combo.currentIndexChanged.connect(lambda: self.on_cell_changed(row))
        self.setCellWidget(row, 5, method_combo)
        
        # AI Groups (read-only)
        self.setItem(row, 6, QTableWidgetItem(""))
        
        # Field EIQ (read-only)
        self.setItem(row, 7, QTableWidgetItem(""))
        
        # Emit signal for the new row
        self.applications_changed.emit()
        
        # Return the row index
        return row
    
    def remove_application_row(self, row=None):
        """
        Remove an application row from the table.
        
        Args:
            row (int): Row to remove, if None removes the currently selected row
        
        Returns:
            bool: True if a row was removed, False otherwise
        """
        # If no row specified, use selected row
        if row is None:
            selected_rows = self.selectionModel().selectedRows()
            if not selected_rows:
                return False
            
            row = selected_rows[0].row()
        
        # Check if row is valid
        if 0 <= row < self.rowCount():
            self.removeRow(row)
            self.applications_changed.emit()
            return True
        
        return False
    
    def update_product_info(self, row):
        """
        Update product-related information when a product is selected.
        
        Args:
            row (int): Row index to update
        """
        product_combo = self.cellWidget(row, 1)
        
        if not product_combo or product_combo.currentIndex() == 0:
            # Clear product-related fields if "Select a product..." is chosen
            return
        
        product_name = product_combo.currentText()
        
        # Find product in repository
        products_repo = ProductRepository.get_instance()
        products = products_repo.get_filtered_products()
        product = None
        
        for p in products:
            if p.product_name == product_name:
                product = p
                break
        
        if not product:
            return
        
        # Update UOM based on product rate UOM
        if product.rate_uom:
            uom_combo = self.cellWidget(row, 3)
            if uom_combo:
                index = uom_combo.findText(product.rate_uom)
                if index >= 0:
                    uom_combo.setCurrentIndex(index)
        
        # Update AI Groups
        ai_groups = product.get_ai_groups()
        groups_text = ", ".join(filter(None, ai_groups))
        self.item(row, 6).setText(groups_text)
        
        # Update application rate with max rate or min rate from product
        rate_spin = self.cellWidget(row, 2)
        if rate_spin:
            if product.label_maximum_rate is not None:
                rate_spin.setValue(product.label_maximum_rate)
            elif product.label_minimum_rate is not None:
                rate_spin.setValue(product.label_minimum_rate)
        
        # Recalculate EIQ
        self.calculate_row_eiq(row)
    
    def calculate_row_eiq(self, row):
        """
        Calculate and update the Field EIQ for a specific row.
        
        Args:
            row (int): Row index to calculate
        """
        try:
            # Get widgets for all needed cells
            product_combo = self.cellWidget(row, 1)
            rate_spin = self.cellWidget(row, 2)
            uom_combo = self.cellWidget(row, 3)
            area_spin = self.cellWidget(row, 4)
            
            # Check if all necessary widgets exist and have valid values
            if (not product_combo or product_combo.currentIndex() == 0 or
                not rate_spin or not uom_combo or not area_spin):
                # Clear EIQ if any required data is missing
                self.item(row, 7).setText("")
                return
            
            product_name = product_combo.currentText()
            application_rate = rate_spin.value()
            rate_uom = uom_combo.currentText()
            
            # Get product from repository
            products_repo = ProductRepository.get_instance()
            products = products_repo.get_filtered_products()
            product = None
            
            for p in products:
                if p.product_name == product_name:
                    product = p
                    break
            
            if not product:
                self.item(row, 7).setText("")
                return
            
            # Prepare active ingredients data for calculation
            active_ingredients = []
            
            # AI1
            if product.ai1 and product.ai1_eiq is not None and product.ai1_concentration is not None:
                from eiq_calculator.eiq_conversions import convert_concentration_to_percent
                percent = convert_concentration_to_percent(
                    product.ai1_concentration, 
                    product.ai1_concentration_uom
                )
                active_ingredients.append({
                    'name': product.ai1,
                    'eiq': product.ai1_eiq,
                    'percent': percent
                })
            
            # AI2
            if product.ai2 and product.ai2_eiq is not None and product.ai2_concentration is not None:
                from eiq_calculator.eiq_conversions import convert_concentration_to_percent
                percent = convert_concentration_to_percent(
                    product.ai2_concentration, 
                    product.ai2_concentration_uom
                )
                active_ingredients.append({
                    'name': product.ai2,
                    'eiq': product.ai2_eiq,
                    'percent': percent
                })
            
            # AI3
            if product.ai3 and product.ai3_eiq is not None and product.ai3_concentration is not None:
                from eiq_calculator.eiq_conversions import convert_concentration_to_percent
                percent = convert_concentration_to_percent(
                    product.ai3_concentration, 
                    product.ai3_concentration_uom
                )
                active_ingredients.append({
                    'name': product.ai3,
                    'eiq': product.ai3_eiq,
                    'percent': percent
                })
            
            # AI4
            if product.ai4 and product.ai4_eiq is not None and product.ai4_concentration is not None:
                from eiq_calculator.eiq_conversions import convert_concentration_to_percent
                percent = convert_concentration_to_percent(
                    product.ai4_concentration, 
                    product.ai4_concentration_uom
                )
                active_ingredients.append({
                    'name': product.ai4,
                    'eiq': product.ai4_eiq,
                    'percent': percent
                })
            
            # Calculate Field EIQ using the eiq_calculator function
            from eiq_calculator.eiq_calculations import calculate_product_field_eiq
            field_eiq = calculate_product_field_eiq(
                active_ingredients, application_rate, rate_uom, applications=1
            )
            
            # Update the Field EIQ cell
            self.item(row, 7).setText(f"{field_eiq:.2f}")
            
            # Emit signal for the EIQ update
            self.applications_changed.emit()
            
        except Exception as e:
            print(f"Error calculating Field EIQ: {e}")
            self.item(row, 7).setText("Error")
    
    def on_cell_changed(self, row):
        """
        Handle changes to any cell in the specified row.
        
        Args:
            row (int): Row index where the change occurred
        """
        # Emit signal for data change
        self.applications_changed.emit()
    
    def get_applications(self):
        """
        Get all applications from the table as a list of dictionaries.
        
        Returns:
            list: List of application dictionaries
        """
        applications = []
        
        for row in range(self.rowCount()):
            # Skip rows with no product selected
            product_combo = self.cellWidget(row, 1)
            if not product_combo or product_combo.currentIndex() == 0:
                continue
            
            # Get values from each cell
            date_edit = self.cellWidget(row, 0)
            rate_spin = self.cellWidget(row, 2)
            uom_combo = self.cellWidget(row, 3)
            area_spin = self.cellWidget(row, 4)
            method_combo = self.cellWidget(row, 5)
            
            ai_groups_item = self.item(row, 6)
            field_eiq_item = self.item(row, 7)
            
            # Check if all required widgets exist
            if (not date_edit or not product_combo or not rate_spin or 
                not uom_combo or not area_spin or not method_combo or
                not ai_groups_item or not field_eiq_item):
                continue
            
            # Get values from widgets
            application_date = date_edit.text()
            product_name = product_combo.currentText()
            rate = rate_spin.value()
            rate_uom = uom_combo.currentText()
            area = area_spin.value()
            application_method = method_combo.currentText()
            ai_groups = ai_groups_item.text().split(", ") if ai_groups_item.text() else []
            
            # Field EIQ might be empty or 'Error'
            field_eiq = 0.0
            try:
                if field_eiq_item.text():
                    field_eiq = float(field_eiq_item.text())
            except ValueError:
                field_eiq = 0.0
            
            # Create application dictionary
            application = {
                "application_date": application_date,
                "product_name": product_name,
                "rate": rate,
                "rate_uom": rate_uom,
                "area": area,
                "application_method": application_method,
                "ai_groups": ai_groups,
                "field_eiq": field_eiq
            }
            
            applications.append(application)
        
        return applications
    
    def set_applications(self, applications):
        """
        Set the table contents from a list of application dictionaries.
        
        Args:
            applications (list): List of application dictionaries
        """
        # Clear table
        self.setRowCount(0)
        
        # Add each application
        for app in applications:
            row = self.add_application_row()
            
            # Set values in each cell
            date_edit = self.cellWidget(row, 0)
            if date_edit and "application_date" in app:
                date_edit.setText(app["application_date"])
            
            product_combo = self.cellWidget(row, 1)
            if product_combo and "product_name" in app:
                index = product_combo.findText(app["product_name"])
                if index >= 0:
                    product_combo.setCurrentIndex(index)
            
            rate_spin = self.cellWidget(row, 2)
            if rate_spin and "rate" in app:
                rate_spin.setValue(app["rate"])
            
            uom_combo = self.cellWidget(row, 3)
            if uom_combo and "rate_uom" in app:
                index = uom_combo.findText(app["rate_uom"])
                if index >= 0:
                    uom_combo.setCurrentIndex(index)
            
            area_spin = self.cellWidget(row, 4)
            if area_spin and "area" in app:
                area_spin.setValue(app["area"])
            
            method_combo = self.cellWidget(row, 5)
            if method_combo and "application_method" in app:
                index = method_combo.findText(app["application_method"])
                if index >= 0:
                    method_combo.setCurrentIndex(index)
            
            # AI Groups and Field EIQ are calculated/updated automatically
            # by the update_product_info and calculate_row_eiq functions
        
        # Emit signal for the data update
        self.applications_changed.emit()
    
    def clear_table(self):
        """Clear all rows from the table."""
        self.setRowCount(0)
        self.applications_changed.emit()
    
    def get_total_field_eiq(self):
        """
        Calculate the total Field EIQ for all applications.
        
        Returns:
            float: Total Field EIQ
        """
        total_eiq = 0.0
        
        for row in range(self.rowCount()):
            field_eiq_item = self.item(row, 7)
            if field_eiq_item and field_eiq_item.text():
                try:
                    eiq = float(field_eiq_item.text())
                    total_eiq += eiq
                except ValueError:
                    pass
        
        return total_eiq