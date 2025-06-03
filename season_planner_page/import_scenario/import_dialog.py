"""
Import Scenario Dialog for the LORENZO POZZI Pesticide App.

Handles file selection and import workflow.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QMessageBox, QTextEdit, QDialogButtonBox
)
from PySide6.QtCore import Qt
from common.styles import get_medium_font, get_subtitle_font
from .excel_parser import ExcelScenarioParser


class ImportScenarioDialog(QDialog):
    """Dialog for importing scenarios from Excel files."""
    
    def __init__(self, parent=None):
        """Initialize the import dialog."""
        super().__init__(parent)
        self.parent = parent
        self.imported_scenario = None
        
        self.setWindowTitle("Import Scenario")
        self.setModal(True)
        self.setMinimumSize(600, 400)
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
            "The file should have headers in the first row followed by application records."
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
            
            if scenario:
                self.imported_scenario = scenario
                self.show_preview(preview_info)
                self.ok_button.setEnabled(True)
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
    
    def show_preview(self, preview_info):
        """Show preview of parsed data."""
        preview_text = f"""File parsed successfully!

Scenario Metadata:
- Crop Year: {preview_info.get('crop_year', 'N/A')}
- Grower: {preview_info.get('grower_name', 'N/A')}
- Field: {preview_info.get('field_name', 'N/A')}
- Area: {preview_info.get('field_area', 'N/A')} {preview_info.get('field_area_uom', '')}
- Variety: {preview_info.get('variety', 'N/A')}

Applications found: {preview_info['total_rows']} records

Sample applications:
{preview_info['sample_data']}

CSV debug file saved to: {preview_info['csv_path']}
"""
        self.preview_text.setPlainText(preview_text)
    
    def get_imported_scenario(self):
        """Get the imported scenario."""
        return self.imported_scenario