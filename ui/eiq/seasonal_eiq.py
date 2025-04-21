"""
Seasonal EIQ Calculator for the LORENZO POZZI Pesticide App.

This module provides the SeasonalEIQCalculator widget for calculating 
total seasonal EIQ for a series of pesticide applications.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QComboBox, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QFormLayout
)
from PySide6.QtCore import Qt

from ui.common.styles import (
    get_subtitle_font, get_body_font, PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE,
    EIQ_LOW_COLOR, EIQ_MEDIUM_COLOR, EIQ_HIGH_COLOR
)
from ui.common.widgets import ContentFrame, ColorCodedTableItem

# Import EIQ utilities
from ui.eiq.eiq_utils_and_components import (
    get_products_from_csv, get_product_display_names, get_product_info, 
    calculate_field_eiq, get_impact_category
)


class SeasonalEIQCalculator(QWidget):
    """Widget for calculating seasonal total EIQ values."""
    
    def __init__(self, parent=None):
        """Initialize the seasonal EIQ calculator widget."""
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Season selection
        season_frame = ContentFrame()
        season_layout = QFormLayout()
        
        # Season/Year selection
        self.season_year_combo = QComboBox()
        self.season_year_combo.addItems(["2025 (Current)", "2024", "2023", "2026 (Planned)"])
        season_layout.addRow("Season:", self.season_year_combo)
        
        # Season description
        self.season_description = QLineEdit()
        self.season_description.setPlaceholderText("Enter a description for this growing season")
        season_layout.addRow("Description:", self.season_description)
        
        season_frame.layout.addLayout(season_layout)
        layout.addWidget(season_frame)
        
        # Product applications table
        applications_frame = ContentFrame()
        applications_layout = QVBoxLayout()
        
        applications_title = QLabel("Product Applications")
        applications_title.setFont(get_subtitle_font(size=16))
        applications_layout.addWidget(applications_title)
        
        # Applications table
        self.season_applications_table = QTableWidget(0, 6)
        self.season_applications_table.setHorizontalHeaderLabels([
            "Application Date", "Product", "EIQ Total", "Active Ingredient %", 
            "Application Rate", "Field EIQ"
        ])
        
        # Set up table properties
        self.season_applications_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.season_applications_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        for col in range(2, 6):
            self.season_applications_table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
        
        # Add initial row
        self.add_season_application()
        
        applications_layout.addWidget(self.season_applications_table)
        
        # Add application button
        add_application_button = QPushButton("Add Application")
        add_application_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        add_application_button.clicked.connect(self.add_season_application)
        applications_layout.addWidget(add_application_button, alignment=Qt.AlignRight)
        
        applications_frame.layout.addLayout(applications_layout)
        layout.addWidget(applications_frame)
        
        # Season results
        results_frame = ContentFrame()
        results_layout = QVBoxLayout()
        
        results_title = QLabel("Seasonal EIQ Results")
        results_title.setFont(get_subtitle_font(size=16))
        results_layout.addWidget(results_title)
        
        # Calculate button
        calculate_season_button = QPushButton("Calculate Seasonal EIQ")
        calculate_season_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        calculate_season_button.clicked.connect(self.calculate_season_eiq)
        results_layout.addWidget(calculate_season_button)
        
        # Results display
        season_results_layout = QFormLayout()
        
        self.total_field_eiq = QLabel("--")
        self.total_field_eiq.setFont(get_body_font(size=14, bold=True))
        season_results_layout.addRow("Total Field EIQ:", self.total_field_eiq)
        
        self.average_field_eiq = QLabel("--")
        self.average_field_eiq.setFont(get_body_font())
        season_results_layout.addRow("Average Field EIQ per Application:", self.average_field_eiq)
        
        self.total_applications = QLabel("--")
        self.total_applications.setFont(get_body_font())
        season_results_layout.addRow("Total Applications:", self.total_applications)
        
        self.season_rating = QLabel("Calculate to see seasonal impact rating")
        self.season_rating.setFont(get_body_font(size=12, bold=True))
        self.season_rating.setAlignment(Qt.AlignCenter)
        self.season_rating.setStyleSheet("padding: 10px; border-radius: 5px; background-color: #F0F0F0;")
        
        results_layout.addLayout(season_results_layout)
        results_layout.addWidget(self.season_rating)
        
        results_frame.layout.addLayout(results_layout)
        layout.addWidget(results_frame)
        
        # Export button
        export_button = QPushButton("Export Seasonal Report")
        export_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        export_button.clicked.connect(self.export_seasonal_report)
        layout.addWidget(export_button, alignment=Qt.AlignRight)
    
    def add_season_application(self):
        """Add a new row to the seasonal applications table."""
        row = self.season_applications_table.rowCount()
        self.season_applications_table.insertRow(row)
        
        # Date selection
        self.season_applications_table.setItem(row, 0, QTableWidgetItem("Click to edit"))
        
        # Product selection combo box
        product_combo = QComboBox()
        product_combo.addItem("Select a product...")
        
        # Get product names from CSV or fallback to sample data
        products = get_products_from_csv()
        if products:
            for product in products:
                product_combo.addItem(product.display_name)
        else:
            # Fallback to sample names
            product_names = get_product_display_names()
            for name in product_names[1:]:  # Skip "Select a product..."
                product_combo.addItem(name)
        
        # Connect product selection to update other fields
        product_combo.currentIndexChanged.connect(
            lambda idx, r=row: self.update_season_product(r, idx)
        )
        
        self.season_applications_table.setCellWidget(row, 1, product_combo)
        
        # Default values for other cells
        self.season_applications_table.setItem(row, 2, QTableWidgetItem("--"))  # EIQ Total
        self.season_applications_table.setItem(row, 3, QTableWidgetItem("--"))  # AI %
        self.season_applications_table.setItem(row, 4, QTableWidgetItem("--"))  # Application Rate
        self.season_applications_table.setItem(row, 5, QTableWidgetItem("--"))  # Field EIQ
    
    def update_season_product(self, row, index):
        """Update product data in the seasonal applications table."""
        combo = self.season_applications_table.cellWidget(row, 1)
        if not combo or index == 0:
            self.season_applications_table.setItem(row, 2, QTableWidgetItem("--"))
            self.season_applications_table.setItem(row, 3, QTableWidgetItem("--"))
            self.season_applications_table.setItem(row, 4, QTableWidgetItem("--"))
            self.season_applications_table.setItem(row, 5, QTableWidgetItem("--"))
            return
        
        # Get selected product name
        product_name = combo.currentText()
        
        # Get product info from either CSV or sample data
        product_info = get_product_info(product_name)
        
        # Update EIQ Total
        self.season_applications_table.setItem(row, 2, QTableWidgetItem(str(product_info["base_eiq"])))
        
        # Update AI %
        self.season_applications_table.setItem(row, 3, QTableWidgetItem(f"{product_info['ai_percent']}%"))
        
        # Update Application Rate
        rate_text = f"{product_info['default_rate']} {product_info['default_unit']}"
        self.season_applications_table.setItem(row, 4, QTableWidgetItem(rate_text))
        
        # Calculate Field EIQ
        base_eiq = product_info["base_eiq"]
        ai_percent = product_info["ai_percent"]
        rate = product_info["default_rate"]
        unit = product_info["default_unit"]
        
        field_eiq = calculate_field_eiq(base_eiq, ai_percent, rate, unit)
        
        # Add color-coded Field EIQ
        eiq_item = ColorCodedTableItem(
            field_eiq, 
            low_threshold=20, 
            high_threshold=40,
            low_color=EIQ_LOW_COLOR,
            medium_color=EIQ_MEDIUM_COLOR,
            high_color=EIQ_HIGH_COLOR
        )
        self.season_applications_table.setItem(row, 5, eiq_item)
    
    def calculate_season_eiq(self):
        """Calculate the total seasonal EIQ."""
        total_eiq = 0.0
        application_count = 0
        
        # Iterate through all applications
        for row in range(self.season_applications_table.rowCount()):
            try:
                eiq_item = self.season_applications_table.item(row, 5)
                if eiq_item and eiq_item.text() != "--" and eiq_item.text() != "0.0":
                    field_eiq = float(eiq_item.text())
                    total_eiq += field_eiq
                    application_count += 1
            except (ValueError, TypeError) as e:
                print(f"Error calculating seasonal EIQ for row {row}: {e}")
        
        # Update results
        self.total_field_eiq.setText(f"{total_eiq:.2f}")
        
        if application_count > 0:
            average_eiq = total_eiq / application_count
            self.average_field_eiq.setText(f"{average_eiq:.2f}")
        else:
            self.average_field_eiq.setText("0.00")
        
        self.total_applications.setText(str(application_count))
        
        # Update season rating
        if total_eiq < 50:
            rating = "Low Total Environmental Impact"
            color = "#E6F5E6"  # Light green
        elif total_eiq < 100:
            rating = "Moderate Total Environmental Impact"
            color = "#FFF5E6"  # Light yellow
        else:
            rating = "High Total Environmental Impact"
            color = "#F5E6E6"  # Light red
        
        self.season_rating.setText(rating)
        self.season_rating.setStyleSheet(f"padding: 10px; border-radius: 5px; background-color: {color};")
    
    def export_seasonal_report(self):
        """Export seasonal EIQ report to a file."""
        print("Export seasonal report")
        # In a real application, this would export to CSV or PDF