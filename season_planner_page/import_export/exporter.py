"""
Excel exporter for scenario export.

Exports scenarios to Excel format with each scenario as a separate worksheet.
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from PySide6.QtWidgets import QMessageBox, QFileDialog


class ExcelScenarioExporter:
    """Exporter for scenario data to Excel format."""
    
    def __init__(self):
        """Initialize the exporter."""
        pass
    
    def export_scenarios(self, scenarios, parent_widget=None):
        """
        Export scenarios to Excel file with user-selected location and filename.
        
        Args:
            scenarios (list): List of scenario objects to export
            parent_widget: Parent widget for message boxes and dialogs
            
        Returns:
            str: Path to created file or None if failed
        """
        try:
            # Open file dialog to select save location and filename
            file_path, _ = QFileDialog.getSaveFileName(
                parent_widget,
                "Save Excel Export",
                "*.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )
            
            # If user cancelled the dialog
            if not file_path:
                return None
            
            # Ensure .xlsx extension
            if not file_path.lower().endswith('.xlsx'):
                file_path = file_path + '.xlsx'
            
            # Create workbook
            workbook = Workbook()
            
            # Remove default sheet
            if workbook.worksheets:
                workbook.remove(workbook.active)
            
            for scenario in scenarios:
                # Create worksheet name (Excel limits to 31 chars)
                sheet_name = self._sanitize_sheet_name(scenario.name)
                
                # Create worksheet
                worksheet = workbook.create_sheet(title=sheet_name)
                
                # Write scenario data to worksheet
                self._write_scenario_to_worksheet(worksheet, scenario)
                
                # Apply formatting
                self._format_worksheet(worksheet)
            
            # Save workbook
            workbook.save(file_path)
            
            # Show success message
            if parent_widget:
                QMessageBox.information(
                    parent_widget, 
                    "Export Successful",
                    f"Scenarios exported successfully!\n\nFile saved to:\n{file_path}"
                )
            
            return file_path
            
        except Exception as e:
            error_msg = f"Failed to export scenarios: {str(e)}"
            print(f"Export error: {error_msg}")
            
            if parent_widget:
                QMessageBox.critical(
                    parent_widget,
                    "Export Failed", 
                    error_msg
                )
            
            return None
    
    def _sanitize_sheet_name(self, name):
        """
        Sanitize scenario name for use as Excel worksheet name.
        
        Args:
            name (str): Original scenario name
            
        Returns:
            str: Sanitized name suitable for Excel worksheet
        """
        # Remove invalid characters for Excel sheet names
        invalid_chars = ['\\', '/', '*', '[', ']', ':', '?']
        sanitized = name
        
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Limit to 31 characters (Excel limit)
        if len(sanitized) > 31:
            sanitized = sanitized[:31]
        
        # Ensure it's not empty
        if not sanitized.strip():
            sanitized = "Scenario"
        
        return sanitized
    
    def _write_scenario_to_worksheet(self, worksheet, scenario):
        """
        Write scenario data to worksheet.
        
        Args:
            worksheet: openpyxl worksheet object
            scenario: Scenario object
        """
        applications = scenario.applications or []
        
        # Define column structure matching the applications table
        columns = [
            "App #",
            "Date", 
            "Product Type",
            "Product Name",
            "Rate",
            "Rate UOM",
            "Area",
            "Method",
            "AI Groups",
            "Field EIQ"
        ]
        
        current_row = 1
        
        # Add scenario info metadata
        worksheet.cell(row=current_row, column=1, value="Scenario Name:")
        worksheet.cell(row=current_row, column=2, value=scenario.name or "Unnamed Scenario")
        current_row += 1
        
        # Add metadata row
        worksheet.cell(row=current_row, column=1, value="Crop Year:")
        worksheet.cell(row=current_row, column=2, value=str(getattr(scenario, 'crop_year', '') or ''))
        worksheet.cell(row=current_row, column=3, value="Grower:")
        worksheet.cell(row=current_row, column=4, value=str(getattr(scenario, 'grower_name', '') or ''))
        worksheet.cell(row=current_row, column=5, value="Field:")
        worksheet.cell(row=current_row, column=6, value=str(getattr(scenario, 'field_name', '') or ''))
        worksheet.cell(row=current_row, column=7, value="Field Area:")
        worksheet.cell(row=current_row, column=8, value=f"{getattr(scenario, 'field_area', 0) or 0} {getattr(scenario, 'field_area_uom', 'acre') or 'acre'}")
        worksheet.cell(row=current_row, column=9, value="Variety:")
        worksheet.cell(row=current_row, column=10, value=str(getattr(scenario, 'variety', '') or ''))
        current_row += 1
        
        # Add empty row separator
        current_row += 1
        
        # Add column headers row
        for col_idx, header in enumerate(columns, 1):
            worksheet.cell(row=current_row, column=col_idx, value=header)
        
        self.header_row_num = current_row  # Store for formatting
        current_row += 1
        
        # Add application data rows
        for i, app in enumerate(applications):
            worksheet.cell(row=current_row, column=1, value=i + 1)  # App #
            worksheet.cell(row=current_row, column=2, value=getattr(app, 'application_date', '') or '')  # Date
            worksheet.cell(row=current_row, column=3, value=getattr(app, 'product_type', '') or '')  # Product Type
            worksheet.cell(row=current_row, column=4, value=getattr(app, 'product_name', '') or '')  # Product Name
            worksheet.cell(row=current_row, column=5, value=getattr(app, 'rate', 0) or 0)  # Rate
            worksheet.cell(row=current_row, column=6, value=getattr(app, 'rate_uom', '') or '')  # Rate UOM
            worksheet.cell(row=current_row, column=7, value=getattr(app, 'area', 0) or 0)  # Area
            worksheet.cell(row=current_row, column=8, value=getattr(app, 'application_method', '') or '')  # Method
            worksheet.cell(row=current_row, column=9, value=', '.join(getattr(app, 'ai_groups', []) or []))  # AI Groups
            worksheet.cell(row=current_row, column=10, value=f"{getattr(app, 'field_eiq', 0) or 0:.2f}")  # Field EIQ
            current_row += 1
    
    def _format_worksheet(self, worksheet):
        """
        Apply formatting to the Excel worksheet.
        
        Args:
            worksheet: openpyxl worksheet object
        """
        try:
            # Header formatting
            header_font = Font(bold=True)
            header_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
            
            # Format the header row (grey background)
            header_row_num = self.header_row_num
            
            for col in range(1, 11):  # 10 columns
                cell = worksheet.cell(row=header_row_num, column=col)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center')
            
            # Auto-adjust column widths
            for column_cells in worksheet.columns:
                max_length = 0
                column_letter = column_cells[0].column_letter
                
                for cell in column_cells:
                    try:
                        cell_value = str(cell.value) if cell.value is not None else ""
                        if len(cell_value) > max_length:
                            max_length = len(cell_value)
                    except:
                        pass
                
                # Set column width with some padding
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 for very long content
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Format metadata rows (make labels bold)
            metadata_font = Font(bold=True)
            for row in range(1, 3):  # First two metadata rows
                for col in range(1, 11):
                    cell = worksheet.cell(row=row, column=col)
                    if col in [1, 3, 5, 7, 9]:  # Label columns
                        cell.font = metadata_font
        
        except Exception as e:
            print(f"Warning: Could not apply Excel formatting: {e}")