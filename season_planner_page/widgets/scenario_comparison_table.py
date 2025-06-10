"""
Scenario Comparison Table Widget

A simple widget that displays a single scenario's data in a table format.
Shows applications grouped by product type and sorted by EIQ values.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from common import (get_medium_font, get_subtitle_font, get_regen_ag_class, EIQ_LOW_THRESHOLD, EIQ_MEDIUM_THRESHOLD, EIQ_HIGH_THRESHOLD, 
                    GENERIC_TABLE_STYLE)
from eiq_calculator_page.widgets_results_display import ColorCodedEiqItem
from collections import defaultdict
from data.repository_AI import AIRepository  # Add this import
from data.repository_product import ProductRepository  # Add this import


class ScenarioComparisonTable(QWidget):
    """
    A widget that displays a single scenario as a table.
    
    Shows scenario name and applications grouped by product type and sorted by EIQ values.
    """
    def __init__(self, scenario, index=None, parent=None):
        """Initialize the scenario comparison table."""
        super().__init__(parent)
        self.scenario = scenario
        self.index = index
        # Initialize repositories
        self.ai_repo = AIRepository.get_instance()
        self.product_repo = ProductRepository.get_instance()
        self.setup_ui()
        self.populate_data()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Scenario title
        self.title_label = QLabel()
        self.title_label.setFont(get_subtitle_font())
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Applications table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Application", "Group", "EIQ"])  # Reordered columns
        
        # Basic table configuration
        self.table.horizontalHeader().setStyleSheet(GENERIC_TABLE_STYLE)
        self.table.horizontalHeader().setStretchLastSection(True)
        # Set all columns to stretch
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Application
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Mode of Action
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # EIQ
        self.table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.table)
        
        # Total EIQ label
        self.total_label = QLabel()
        self.total_label.setFont(get_medium_font(bold=True))
        self.total_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.total_label)

    def _parse_moa_groups(self, moa_string):
        """
        Parse the MoA groups string to extract just the codes.
        
        Args:
            moa_string (str): String like "FRAC: 7, HRAC: A" from get_moa_groups()
            
        Returns:
            str: Parsed codes like "7, A"
        """
        if not moa_string:
            return ""
        
        # Split by comma and extract codes
        parts = moa_string.split(", ")
        codes = []
        
        for part in parts:
            # Split by colon and take the second part (the code)
            if ": " in part:
                code = part.split(": ", 1)[1].strip()
                codes.append(code)
        
        return ", ".join(codes)

    def _get_product_moa_groups(self, product_name):
        """
        Get combined MoA groups for all active ingredients in a product.
        
        Args:
            product_name (str): Name of the product
            
        Returns:
            str: Combined MoA codes for all active ingredients
        """
        # Get the product - try different methods to find the product
        try:
            # Try to get filtered products and find by name
            filtered_products = self.product_repo.get_filtered_products()
            product = None
            for p in filtered_products:
                if p.product_name == product_name:
                    product = p
                    break
            
            if not product:
                return ""
            
            # Get all active ingredients
            active_ingredients = product.active_ingredients
            if not active_ingredients:
                return ""
            
            # Get MoA groups for each active ingredient
            all_moa_codes = []
            for ai_name in active_ingredients:
                moa_string = self.ai_repo.get_moa_groups(ai_name)
                parsed_codes = self._parse_moa_groups(moa_string)
                if parsed_codes:
                    all_moa_codes.append(parsed_codes)
            
            # Combine all codes
            return "; ".join(all_moa_codes) if all_moa_codes else ""
            
        except Exception as e:
            print(f"Error getting MoA groups for {product_name}: {e}")
            return ""

    def _add_section_header(self, row, product_type, count):
        """Add a section header row for a product type."""
        # Product type header with count
        header_text = f"{product_type} ({count} app{'s' if count != 1 else ''})"
        header_item = QTableWidgetItem(header_text)
        
        # Make it bold and non-editable
        font = get_medium_font(bold=True)
        header_item.setFont(font)
        header_item.setFlags(header_item.flags() & ~Qt.ItemIsEditable)
        header_item.setTextAlignment(Qt.AlignCenter)
            
        self.table.setItem(row, 0, header_item)
        
        # Add empty items to other columns (required before merging)
        for col in [1, 2]:
            empty_item = QTableWidgetItem("")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, col, empty_item)
        
        # Merge the cells across all columns
        self.table.setSpan(row, 0, 1, 3)
    
    def _add_application_row(self, row, app):
        """Add a regular application row."""
        # Application name (indented slightly) - Column 0
        app_item = QTableWidgetItem(f"  {app.product_name}")
        app_item.setFlags(app_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 0, app_item)
        
        # Mode of Action groups - Column 1
        moa_codes = self._get_product_moa_groups(app.product_name)
        moa_item = QTableWidgetItem(moa_codes)
        moa_item.setFlags(moa_item.flags() & ~Qt.ItemIsEditable)
        moa_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 1, moa_item)
        
        # EIQ value with color coding - Column 2
        eiq_value = app.field_eiq or 0
        eiq_item = ColorCodedEiqItem(
            eiq_value,
            low_threshold=EIQ_LOW_THRESHOLD,
            medium_threshold=EIQ_MEDIUM_THRESHOLD,
            high_threshold=EIQ_HIGH_THRESHOLD
        )
        eiq_item.setFlags(eiq_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 2, eiq_item)

    def populate_data(self):
        """Populate the widget with scenario data grouped by product type."""
        if not self.scenario:
            return
        
        # Set title
        if self.index is not None:
            self.title_label.setText(f"{self.index}: {self.scenario.name or 'Unnamed Scenario'}")
        else:
            self.title_label.setText(self.scenario.name or "Unnamed Scenario")
        
        # Populate applications table
        applications = self.scenario.applications or []
        
        # Filter valid applications
        valid_applications = [app for app in applications 
                            if app.product_name and (app.field_eiq is not None)]
        
        if valid_applications:
            # Group applications by product type
            grouped_apps = self._group_applications_by_type(valid_applications)
            
            # Calculate total rows needed (applications + section headers)
            total_rows = len(valid_applications) + len(grouped_apps)
            self.table.setRowCount(total_rows)
            
            current_row = 0
            total_eiq = 0
            
            # Sort product types for consistent display order
            sorted_types = sorted(grouped_apps.keys())
            
            for product_type in sorted_types:
                apps_in_type = grouped_apps[product_type]
                
                # Add section header row
                self._add_section_header(current_row, product_type, len(apps_in_type))
                current_row += 1
                
                # Sort applications within this type by EIQ (highest first)
                sorted_apps = sorted(apps_in_type, key=lambda app: app.field_eiq or 0, reverse=True)
                
                # Add applications in this type
                for app in sorted_apps:
                    self._add_application_row(current_row, app)
                    total_eiq += app.field_eiq or 0
                    current_row += 1
            
            # Get regenerative agriculture framework class
            regen_class = get_regen_ag_class(total_eiq)
            
            # Set total EIQ with framework class
            self.total_label.setText(f"Field Use EIQ: {total_eiq:.1f} → {regen_class}")
            
        else:
            # No valid applications
            self.table.setRowCount(1)
            no_apps_item = QTableWidgetItem("No applications")
            no_apps_item.setFlags(no_apps_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(0, 0, no_apps_item)
            
            # Add empty MoA column for no applications case
            moa_item = QTableWidgetItem("")
            moa_item.setFlags(moa_item.flags() & ~Qt.ItemIsEditable)
            moa_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 1, moa_item)
            
            eiq_item = QTableWidgetItem("0.0")
            eiq_item.setFlags(eiq_item.flags() & ~Qt.ItemIsEditable)
            eiq_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 2, eiq_item)
            
            self.total_label.setText("Total Field Use EIQ: 0.0 → Leading")
        
        # Resize rows to content
        self.table.resizeRowsToContents()
    
    def _group_applications_by_type(self, applications):
        """Group applications by their product type (using first 2 words only)."""
        grouped = defaultdict(list)
        
        for app in applications:
            # Get product type from the application
            full_product_type = getattr(app, 'product_type', None) or "Unknown Type"
            
            # Extract first 2 words for grouping
            words = full_product_type.split()
            if len(words) >= 2:
                product_type = f"{words[0]} {words[1]}"
            else:
                product_type = full_product_type
            
            grouped[product_type].append(app)
        
        return dict(grouped)
