"""
Import Scenario Dialog for the LORENZO POZZI Pesticide App.

Enhanced dialog that shows product validation results and handles unmatched products.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QMessageBox, QTextEdit, QDialogButtonBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from common.styles import get_medium_font, get_subtitle_font
from .excel_parser import ExcelScenarioParser


class ImportScenarioDialog(QDialog):
    """Dialog for importing scenarios from Excel files with product validation."""
    
    def __init__(self, parent=None):
        """Initialize the import dialog."""
        super().__init__(parent)
        self.parent = parent
        self.imported_scenario = None
        self.product_validation = None
        
        self.setWindowTitle("Import Scenario")
        self.setModal(True)
        self.setMinimumSize(700, 500)  # Increased size for validation info
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Import Scenario from Excel")
        title_label.setFont(get_subtitle_font())
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Instructions
        instructions = QLabel(
            "Select an Excel file (.xlsx) containing pesticide application data.\n"
            "The file should have headers in the first row followed by application records.\n"
            "Product names will be validated against the application's product database."
        )
        instructions.setFont(get_medium_font())
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # File selection section
        file_layout = QHBoxLayout()
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("border: 1px solid gray; padding: 5px;")
        file_layout.addWidget(self.file_label)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_button)
        
        layout.addLayout(file_layout)
        
        # Product validation section
        validation_label = QLabel("Product Validation:")
        validation_label.setFont(get_medium_font(bold=True))
        layout.addWidget(validation_label)
        
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        self.validation_text.setMaximumHeight(150)
        self.validation_text.setPlainText("Select a file to see product validation results...")
        layout.addWidget(self.validation_text)
        
        # Preview section
        preview_label = QLabel("File Preview:")
        preview_label.setFont(get_medium_font(bold=True))
        layout.addWidget(preview_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(200)
        layout.addWidget(self.preview_text)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Initially disable OK button
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(False)
        
        layout.addWidget(button_box)
    
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
        """Parse the selected Excel file and show preview."""
        try:
            parser = ExcelScenarioParser()
            scenario, preview_info = parser.parse_file(file_path)
            
            if scenario and preview_info:
                self.imported_scenario = scenario
                self.product_validation = preview_info.get('product_validation', {})
                self.show_validation_results(self.product_validation)
                self.show_preview(preview_info)
                
                # Enable OK button - we always import all applications now
                self.ok_button.setEnabled(True)
                
                # Show info dialog if there are unmatched products
                if self.product_validation.get('unmatched_products', 0) > 0:
                    self.handle_unmatched_products()
            else:
                QMessageBox.warning(
                    self, "Parse Error",
                    "Could not parse the Excel file. Please check the format."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self, "Import Error",
                f"Error reading file: {str(e)}"
            )
    
    def show_validation_results(self, validation):
        """Show product validation results."""
        if not validation:
            self.validation_text.setPlainText("No validation data available.")
            return
        
        total = validation.get('total_products', 0)
        matched = validation.get('matched_products', 0)
        unmatched = validation.get('unmatched_products', 0)
        
        validation_text = f"""Product Validation Results:
━━━━━━━━━━━━━━━━━━━━

Total products found: {total}
✓ Matched products: {matched}
✗ Unmatched products: {unmatched}
"""
        
        if matched > 0:
            validation_text += f"\n✓ MATCHED PRODUCTS ({matched}):\n"
            for product in validation.get('matched_list', []):
                validation_text += f"  • {product}\n"
        
        if unmatched > 0:
            validation_text += f"\n✗ UNMATCHED PRODUCTS ({unmatched}):\n"
            for product in validation.get('unmatched_list', []):
                validation_text += f"  • {product}\n"
            validation_text += "\n⚠ Note: Applications with unmatched products will be imported but will show 0 EIQ."
        
        # Set text color based on validation results
        if unmatched == 0:
            # All products matched - green background
            self.validation_text.setStyleSheet("background-color: #e8f5e8; color: #2d5016;")
        else:
            # Some unmatched products - yellow background
            self.validation_text.setStyleSheet("background-color: #fff3cd; color: #856404;")
        
        self.validation_text.setPlainText(validation_text)
    
    def handle_unmatched_products(self):
        """Handle the case where some products couldn't be matched."""
        unmatched_count = self.product_validation.get('unmatched_products', 0)
        matched_count = self.product_validation.get('matched_products', 0)
        
        # Always enable OK button - we'll import everything
        self.ok_button.setEnabled(True)
        
        if unmatched_count > 0:
            # Show informational message about unmatched products
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Import Information")
            msg_box.setText(
                f"Product Validation Results:\n\n"
                f"✓ {matched_count} products matched successfully\n"
                f"✗ {unmatched_count} products could not be matched\n\n"
                f"All applications will be imported. Unmatched products will show 0 EIQ and "
                f"can be manually corrected after import.\n\n"
                f"Ready to proceed with import?"
            )
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setDefaultButton(QMessageBox.Ok)
            msg_box.exec()
    
    def show_preview(self, preview_info):
        """Show preview of parsed data."""
        preview_text = f"""File parsed successfully!

Scenario Metadata:
━━━━━━━━━━━━━━━━━━━━
- Crop Year: {preview_info.get('crop_year', 'N/A')}
- Grower: {preview_info.get('grower_name', 'N/A')}
- Field: {preview_info.get('field_name', 'N/A')}
- Area: {preview_info.get('field_area', 'N/A')} {preview_info.get('field_area_uom', '')}
- Variety: {preview_info.get('variety', 'N/A')}

Applications found: {preview_info['total_rows']} records

Sample applications:
━━━━━━━━━━━━━━━━━━━━
{preview_info['sample_data']}
"""
        
        # Add import summary
        if self.product_validation:
            matched = self.product_validation.get('matched_products', 0)
            unmatched = self.product_validation.get('unmatched_products', 0)
            total = self.product_validation.get('total_products', 0)
            
            if unmatched > 0:
                preview_text += f"\n\n📋 Import Summary: All {total} applications will be imported ({matched} with EIQ calculations, {unmatched} will show 0 EIQ)."
            else:
                preview_text += f"\n\n✓ Import Summary: All {total} applications will be imported with full EIQ calculations."
        
        self.preview_text.setPlainText(preview_text)
    
    def get_imported_scenario(self):
        """Get the imported scenario."""
        return self.imported_scenario