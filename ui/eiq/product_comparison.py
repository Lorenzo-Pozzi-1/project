"""
Product Comparison Calculator for the LORENZO POZZI Pesticide App.

This module provides the ProductComparisonCalculator widget for comparing EIQ
values of multiple pesticide products.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QComboBox, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QDoubleSpinBox
)
from PySide6.QtCore import Qt

from ui.common.styles import (
    get_subtitle_font, get_body_font, PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE,
    EIQ_LOW_COLOR, EIQ_MEDIUM_COLOR, EIQ_HIGH_COLOR
)
from ui.common.widgets import ContentFrame, ColorCodedTableItem

# Import EIQ utilities
from ui.eiq.eiq_utils import (
    get_products_from_csv, get_product_display_names, get_product_info, 
    calculate_field_eiq, get_impact_category
)


class ProductComparisonCalculator(QWidget):
    """Widget for comparing EIQ values of multiple pesticide products."""
    
    def __init__(self, parent=None):
        """Initialize the product comparison calculator widget."""
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Products selection
        selection_frame = ContentFrame()
        selection_layout = QVBoxLayout()
        
        selection_title = QLabel("Select Products to Compare")
        selection_title.setFont(get_subtitle_font(size=16))
        selection_layout.addWidget(selection_title)
        
        # Product selection table
        self.comparison_selection_table = QTableWidget(0, 5)
        self.comparison_selection_table.setHorizontalHeaderLabels([
            "Product", "EIQ Total", "Active Ingredient %", "Application Rate", "Applications"
        ])
        
        # Set up table properties
        self.comparison_selection_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 5):
            self.comparison_selection_table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
        
        # Add a few empty rows for product selection
        for _ in range(1):
            self.add_comparison_row()
        
        selection_layout.addWidget(self.comparison_selection_table)
        
        # Add another product button
        add_product_button = QPushButton("Add Another Product")
        add_product_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        add_product_button.clicked.connect(self.add_comparison_row)
        selection_layout.addWidget(add_product_button, alignment=Qt.AlignRight)
        
        selection_frame.layout.addLayout(selection_layout)
        layout.addWidget(selection_frame)
        
        # Comparison results
        results_frame = ContentFrame()
        results_layout = QVBoxLayout()
        
        results_title = QLabel("EIQ Comparison Results")
        results_title.setFont(get_subtitle_font(size=16))
        results_layout.addWidget(results_title)
        
        # Calculate button
        calculate_button = QPushButton("Calculate and Compare")
        calculate_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        calculate_button.clicked.connect(self.calculate_comparison)
        results_layout.addWidget(calculate_button)
        
        # Results table
        self.comparison_results_table = QTableWidget(0, 2)
        self.comparison_results_table.setHorizontalHeaderLabels([
            "Product", "Field EIQ"
        ])
        
        # Set up table properties
        self.comparison_results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 5):
            self.comparison_results_table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
        
        results_layout.addWidget(self.comparison_results_table)
        
        results_frame.layout.addLayout(results_layout)
        layout.addWidget(results_frame)
        
        # Export button
        export_button = QPushButton("Export Comparison")
        export_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        export_button.clicked.connect(self.export_comparison)
        layout.addWidget(export_button, alignment=Qt.AlignRight)
    
    def add_comparison_row(self):
        """Add a row to the comparison product selection table."""
        row = self.comparison_selection_table.rowCount()
        self.comparison_selection_table.insertRow(row)
        
        # Product selection combo box
        product_combo = QComboBox()
        product_combo.addItem("Select a product...")
        
        # Get product names from CSV or fallback to sample data
        products = get_products_from_csv()
        if products:
            for product in products:
                product_combo.addItem(product.display_name)
        
        self.comparison_selection_table.setCellWidget(row, 0, product_combo)
        
        # Default values for other cells
        self.comparison_selection_table.setItem(row, 1, QTableWidgetItem("--"))  # EIQ Total
        
        # AI percent spin box
        ai_spin = QDoubleSpinBox()
        ai_spin.setRange(0.1, 100.0)
        ai_spin.setValue(0.0)
        ai_spin.setSuffix("%")
        self.comparison_selection_table.setCellWidget(row, 2, ai_spin)
        
        # Rate spin box
        rate_spin = QDoubleSpinBox()
        rate_spin.setRange(0.01, 100.0)
        rate_spin.setValue(0.0)
        self.comparison_selection_table.setCellWidget(row, 3, rate_spin)
        
        # Applications spin box
        apps_spin = QDoubleSpinBox()
        apps_spin.setRange(1, 10)
        apps_spin.setValue(1)
        apps_spin.setDecimals(0)
        self.comparison_selection_table.setCellWidget(row, 4, apps_spin)
        
        # Connect product selection to update EIQ total
        product_combo.currentIndexChanged.connect(
            lambda idx, r=row: self.update_comparison_product(r, idx)
        )
    
    def update_comparison_product(self, row, index):
        """Update product data in the comparison table."""
        combo = self.comparison_selection_table.cellWidget(row, 0)
        if not combo or index == 0:
            self.comparison_selection_table.setItem(row, 1, QTableWidgetItem("--"))
            return
        
        # Get selected product name
        product_name = combo.currentText()
        
        # Get product info from either CSV or sample data
        product_info = get_product_info(product_name)
        
        # Update EIQ Total
        self.comparison_selection_table.setItem(row, 1, QTableWidgetItem(str(product_info["base_eiq"])))
        
        # Update AI percent
        ai_spin = self.comparison_selection_table.cellWidget(row, 2)
        if ai_spin:
            ai_spin.setValue(product_info["ai_percent"])
        
        # Update rate
        rate_spin = self.comparison_selection_table.cellWidget(row, 3)
        if rate_spin:
            rate_spin.setValue(product_info["default_rate"])
    
    def calculate_comparison(self):
        """Calculate and display EIQ comparison results."""
        # Clear the results table
        self.comparison_results_table.setRowCount(0)
        
        # Iterate through the selection table
        for row in range(self.comparison_selection_table.rowCount()):
            # Get the product combo
            product_combo = self.comparison_selection_table.cellWidget(row, 0)
            if not product_combo or product_combo.currentIndex() == 0:
                continue  # Skip empty or "Select a product" rows
            
            product_name = product_combo.currentText()
            product_info = get_product_info(product_name)
            
            try:
                # Get values from the row
                eiq_total_item = self.comparison_selection_table.item(row, 1)
                eiq_total = float(eiq_total_item.text()) if eiq_total_item and eiq_total_item.text() != "--" else 0
                
                ai_spin = self.comparison_selection_table.cellWidget(row, 2)
                ai_percent = ai_spin.value() if ai_spin else 0
                
                rate_spin = self.comparison_selection_table.cellWidget(row, 3)
                rate = rate_spin.value() if rate_spin else 0
                
                apps_spin = self.comparison_selection_table.cellWidget(row, 4)
                applications = apps_spin.value() if apps_spin else 1
                
                # Calculate Field EIQ
                unit = product_info["default_unit"]
                field_eiq = calculate_field_eiq(eiq_total, ai_percent, rate, unit, applications)
                
                # Add to results table
                result_row = self.comparison_results_table.rowCount()
                self.comparison_results_table.insertRow(result_row)
                
                self.comparison_results_table.setItem(result_row, 0, QTableWidgetItem(product_name))
                
                # Field EIQ with color coding
                eiq_item = ColorCodedTableItem(
                    field_eiq, 
                    low_threshold=20, 
                    high_threshold=40,
                    low_color=EIQ_LOW_COLOR,
                    medium_color=EIQ_MEDIUM_COLOR,
                    high_color=EIQ_HIGH_COLOR
                )
                self.comparison_results_table.setItem(result_row, 1, eiq_item)
                
                
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Error calculating comparison for {product_name}: {e}")
                # Add error row
                result_row = self.comparison_results_table.rowCount()
                self.comparison_results_table.insertRow(result_row)
                self.comparison_results_table.setItem(result_row, 0, QTableWidgetItem(product_name))
                self.comparison_results_table.setItem(result_row, 1, QTableWidgetItem("Error"))
                self.comparison_results_table.setItem(result_row, 2, QTableWidgetItem("--"))
                self.comparison_results_table.setItem(result_row, 3, QTableWidgetItem("--"))
                self.comparison_results_table.setItem(result_row, 4, QTableWidgetItem("--"))
    
    def export_comparison(self):
        """Export comparison results to a file."""
        print("Export comparison results")
        # In a real application, this would export to CSV or PDF