"""
Import Dialog with Interactive Product Mapping

Updated version with simplified interface using ProductSelectionWidget.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QMessageBox, QTextEdit, QDialogButtonBox,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView,
    QTabWidget, QWidget, QFrame
)
from PySide6.QtCore import Qt, Signal
from common.styles import get_medium_font, get_subtitle_font
from common.widgets.product_selection import ProductSearchField
from .excel_parser import ExcelScenarioParser
from data import ProductRepository


class ProductMappingWidget(QWidget):
    """Widget for mapping unmatched products to database products."""
    
    products_mapped = Signal()  # Emitted when mapping changes
    
    def __init__(self, unmatched_products, available_products, parent=None):
        super().__init__(parent)
        self.unmatched_products = unmatched_products
        self.available_products = available_products
        self.product_mappings = {}  # excel_name -> (action, db_product)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the product mapping interface."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Some products from your Excel file don't match our database. "
            "Choose how to handle each unmatched product:"
        )
        instructions.setWordWrap(True)
        instructions.setFont(get_medium_font())
        layout.addWidget(instructions)
        
        # Mapping table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "Excel Product Name", 
            "Action", 
            "Map to Database Product"
        ])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Excel name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Action
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Database product
        
        self.table.setRowCount(len(self.unmatched_products))
        self.populate_table()
        
        layout.addWidget(self.table)
    
    def populate_table(self):
        """Populate the mapping table with unmatched products."""
        # Get available products for the search field
        products_repo = ProductRepository.get_instance()
        all_products = products_repo.get_filtered_products()
        
        for row, excel_product in enumerate(self.unmatched_products):
            # Excel product name (read-only)
            name_item = QTableWidgetItem(excel_product)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, name_item)
            
            # Action selector
            action_combo = QComboBox()
            action_combo.addItems(["Import as-is", "Map to existing", "Skip"])
            action_combo.setCurrentText("Import as-is")  # Default to Import as-is
            action_combo.currentTextChanged.connect(
                lambda text, r=row: self.on_action_changed(r, text)
            )
            self.table.setCellWidget(row, 1, action_combo)
            
            # Database product selector using ProductSearchField
            product_widget = ProductSearchField()
            product_widget.set_products(all_products)  # Set available products
            product_widget.setEnabled(False)  # Disabled until "Map to existing" is selected
            product_widget.product_selected.connect(
                lambda product_name, r=row: self.on_product_selected(r, product_name)
            )
            self.table.setCellWidget(row, 2, product_widget)
            
            # Initialize mapping with default action
            self.product_mappings[excel_product] = ("import_unmatched", None)
    
    def on_action_changed(self, row, action):
        """Handle action selection change."""
        excel_product = self.unmatched_products[row]
        product_widget = self.table.cellWidget(row, 2)
        
        if action == "Map to existing":
            product_widget.setEnabled(True)
            # Try to suggest a similar product
            suggestion = self.find_similar_product(excel_product)
            if suggestion:
                # Find the proper display format for this product
                suggestion_display = f"{suggestion.product_name} - {suggestion.application_method or 'General'}"
                product_widget.text = suggestion_display
        else:
            product_widget.setEnabled(False)
            product_widget.clear()
        
        # Update mapping
        if action == "Skip":
            self.product_mappings[excel_product] = ("skip", None)
        elif action == "Import as-is":
            self.product_mappings[excel_product] = ("import_unmatched", None)
        elif action == "Map to existing":
            display_text = product_widget.text
            if display_text:
                # Get the actual product object from the display text
                db_product = product_widget.completer.get_product_from_display(display_text)
                self.product_mappings[excel_product] = ("map", db_product)
            else:
                self.product_mappings[excel_product] = ("map", None)
        
        self.products_mapped.emit()
    
    def on_product_selected(self, row, product_name):
        """Handle database product selection."""
        if not product_name:
            return
            
        excel_product = self.unmatched_products[row]
        product_widget = self.table.cellWidget(row, 2)
        
        # Get the actual product object from the current display text
        display_text = product_widget.text
        if display_text:
            db_product = product_widget.completer.get_product_from_display(display_text)
            if db_product:
                self.product_mappings[excel_product] = ("map", db_product)
                self.products_mapped.emit()
    
    def find_similar_product(self, excel_name):
        """Find a similar product in the database using fuzzy matching."""
        excel_lower = excel_name.lower()
        
        # First try: exact substring match
        for product in self.available_products:
            db_lower = product.product_name.lower()
            if excel_lower in db_lower or db_lower in excel_lower:
                return product
        
        # Second try: word overlap
        excel_words = set(excel_lower.split())
        best_match = None
        best_score = 0
        
        for product in self.available_products:
            db_words = set(product.product_name.lower().split())
            overlap = len(excel_words.intersection(db_words))
            
            if overlap > best_score and overlap >= 2:  # At least 2 words in common
                best_score = overlap
                best_match = product
        
        return best_match
    
    def get_mapping_summary(self):
        """Get a summary of the current mappings."""
        summary = {
            "skip": [],
            "map": [],
            "import_unmatched": []
        }
        
        for excel_name, (action, db_product) in self.product_mappings.items():
            if action == "skip":
                summary["skip"].append(excel_name)
            elif action == "map" and db_product:
                summary["map"].append((excel_name, db_product.product_name))
            elif action == "import_unmatched":
                summary["import_unmatched"].append(excel_name)
        
        return summary


class ImportScenarioDialog(QDialog):
    """Import dialog with interactive product mapping."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.imported_scenario = None
        self.raw_scenario = None  # Scenario before product filtering
        self.product_validation = None
        self.mapping_widget = None
        
        self.setWindowTitle("Import Scenario from Excel")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI with tabs for file selection and product mapping."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Import Scenario from Excel")
        title_label.setFont(get_subtitle_font())
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Tab widget for different stages
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Tab 1: File Selection and Preview
        self.file_tab = QWidget()
        self.setup_file_tab()
        self.tab_widget.addTab(self.file_tab, "1. Select File")
        
        # Tab 2: Product Mapping (initially hidden)
        self.mapping_tab = QWidget()
        self.tab_widget.addTab(self.mapping_tab, "2. Correct Issues")
        self.tab_widget.setTabEnabled(1, False)  # Disabled until file is loaded
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(False)
        
        layout.addWidget(button_box)
    
    def setup_file_tab(self):
        """Set up the file selection tab."""
        layout = QVBoxLayout(self.file_tab)
        
        # Instructions
        instructions = QLabel(
            "Select an Excel file (.xlsx) containing pesticide application data.\n"
            "The file should have headers followed by application records."
        )
        instructions.setFont(get_medium_font())
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("border: 1px solid gray; padding: 5px;")
        file_layout.addWidget(self.file_label)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_button)
        
        layout.addLayout(file_layout)
        
        # Preview section
        preview_label = QLabel("File Preview:")
        preview_label.setFont(get_medium_font(bold=True))
        layout.addWidget(preview_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlainText("Select a file to see preview...")
        layout.addWidget(self.preview_text)
    
    def browse_file(self):
        """Open file browser to select Excel file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel File",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if file_path:
            self.file_label.setText(os.path.basename(file_path))
            self.parse_file(file_path)
    
    def parse_file(self, file_path):
        """Parse the selected Excel file and handle product validation."""
        try:
            parser = ExcelScenarioParser()
            scenario, preview_info = parser.parse_file(file_path)
            
            if not scenario or not preview_info:
                QMessageBox.warning(
                    self, "Parse Error",
                    "Could not parse the Excel file. Please check the format."
                )
                return
            
            self.raw_scenario = scenario
            self.product_validation = preview_info.get('product_validation', {})
            
            # Show preview
            self.show_preview(preview_info)
            
            # Handle unmatched products
            unmatched_count = self.product_validation.get('unmatched_products', 0)
            
            if unmatched_count > 0:
                # Set up product mapping tab
                self.setup_mapping_tab()
                self.tab_widget.setTabEnabled(1, True)
                
                # Show info about next step
                QMessageBox.information(
                    self, "Product Mapping Required",
                    f"Found {unmatched_count} unmatched products.\n\n"
                    f"Please go to the 'Correct Issues' tab to resolve these before importing."
                )
                self.tab_widget.setCurrentIndex(1)  # Switch to mapping tab
            else:
                # All products matched - ready to import
                self.imported_scenario = scenario
                self.ok_button.setEnabled(True)
                QMessageBox.information(
                    self, "Ready to Import",
                    "All products matched successfully! Ready to import."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self, "Import Error",
                f"Error reading file: {str(e)}"
            )
    
    def setup_mapping_tab(self):
        """Set up the product mapping tab."""
        # Clear existing layout
        if self.mapping_tab.layout():
            QWidget().setLayout(self.mapping_tab.layout())
        
        layout = QVBoxLayout(self.mapping_tab)
        
        # Get unmatched products and available products
        unmatched_products = self.product_validation.get('unmatched_list', [])
        products_repo = ProductRepository.get_instance()
        available_products = products_repo.get_filtered_products()
        
        # Create mapping widget
        self.mapping_widget = ProductMappingWidget(
            unmatched_products, available_products, self
        )
        self.mapping_widget.products_mapped.connect(self.on_products_mapped)
        layout.addWidget(self.mapping_widget)
        
        # Summary section
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        layout.addWidget(separator)
        
        self.mapping_summary_label = QLabel()
        self.mapping_summary_label.setFont(get_medium_font())
        layout.addWidget(self.mapping_summary_label)
        
        # Update initial summary
        self.update_mapping_summary()
        self.update_import_readiness()
    
    def on_products_mapped(self):
        """Handle changes in product mapping."""
        self.update_mapping_summary()
        self.update_import_readiness()
    
    def update_mapping_summary(self):
        """Update the mapping summary display."""
        if not self.mapping_widget:
            return
            
        summary = self.mapping_widget.get_mapping_summary()
        
        text_parts = []
        if summary["map"]:
            text_parts.append(f"✓ {len(summary['map'])} products will be mapped")
        if summary["import_unmatched"]:
            text_parts.append(f"⚠ {len(summary['import_unmatched'])} products will be imported without EIQ data")
        if summary["skip"]:
            text_parts.append(f"✗ {len(summary['skip'])} products will be skipped")
        
        self.mapping_summary_label.setText("\n".join(text_parts))
    
    def update_import_readiness(self):
        """Update whether the import is ready to proceed."""
        if not self.mapping_widget:
            return
            
        summary = self.mapping_widget.get_mapping_summary()
        
        # Import is ready if we have some valid action for each product
        total_actions = len(summary["map"]) + len(summary["import_unmatched"]) + len(summary["skip"])
        total_unmatched = len(self.product_validation.get('unmatched_list', []))
        
        ready = (total_actions == total_unmatched)
        self.ok_button.setEnabled(ready)
        
        if ready:
            # Create the final scenario with mappings applied
            self.apply_product_mappings()
    
    def apply_product_mappings(self):
        """Apply the product mappings to create the final scenario."""
        if not self.raw_scenario or not self.mapping_widget:
            return
            
        # Start with a copy of the raw scenario
        final_scenario = self.raw_scenario.clone()
        final_applications = []
        
        mapping_summary = self.mapping_widget.get_mapping_summary()
        
        for app in self.raw_scenario.applications:
            excel_product_name = app.product_name
            
            # Check if this product needs mapping
            mapping_action = None
            mapped_product = None
            
            for excel_name, db_product_name in mapping_summary["map"]:
                if excel_name == excel_product_name:
                    mapping_action = "map"
                    # Find the actual product object
                    products_repo = ProductRepository.get_instance()
                    available_products = products_repo.get_filtered_products()
                    mapped_product = next((p for p in available_products 
                                         if p.product_name == db_product_name), None)
                    break
            
            if excel_product_name in mapping_summary["skip"]:
                mapping_action = "skip"
            elif excel_product_name in mapping_summary["import_unmatched"]:
                mapping_action = "import_unmatched"
            
            # Apply the mapping
            if mapping_action == "skip":
                # Don't include this application
                continue
            elif mapping_action == "map" and mapped_product:
                # Replace with mapped product data
                app.product_name = mapped_product.product_name
                app.product_type = mapped_product.product_type
                # Keep original rate/uom but let the system recalculate EIQ
                final_applications.append(app)
            elif mapping_action == "import_unmatched":
                # Keep as-is (will show validation errors in UI)
                final_applications.append(app)
            else:
                # Matched product - keep as-is
                final_applications.append(app)
        
        final_scenario.applications = final_applications
        self.imported_scenario = final_scenario
    
    def show_preview(self, preview_info):
        """Show preview of parsed data."""
        matched = self.product_validation.get('matched_products', 0)
        unmatched = self.product_validation.get('unmatched_products', 0)
        
        preview_text = f"""File parsed successfully!

Scenario Metadata:
━━━━━━━━━━━━━━━━━━━━
- Crop Year: {preview_info.get('crop_year', 'N/A')}
- Grower: {preview_info.get('grower_name', 'N/A')}
- Field: {preview_info.get('field_name', 'N/A')}
- Area: {preview_info.get('field_area', 'N/A')} {preview_info.get('field_area_uom', '')}
- Variety: {preview_info.get('variety', 'N/A')}

Applications: {preview_info['total_rows']} records found

Product Validation:
━━━━━━━━━━━━━━━━━━━━
✓ {matched} products matched
✗ {unmatched} products need attention

Sample applications:
━━━━━━━━━━━━━━━━━━━━
{preview_info['sample_data']}
"""
        
        self.preview_text.setPlainText(preview_text)
    
    def get_imported_scenario(self):
        """Get the final imported scenario with mappings applied."""
        return self.imported_scenario