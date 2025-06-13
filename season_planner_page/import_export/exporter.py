"""
Excel exporter for scenario export.

Exports scenarios to Excel format with each scenario as a separate worksheet.
"""

import pandas as pd
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
            
            # Create Excel writer
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                
                for scenario in scenarios:
                    # Create worksheet name (Excel limits to 31 chars)
                    sheet_name = self._sanitize_sheet_name(scenario.name)
                    
                    # Convert scenario applications to DataFrame
                    df = self._scenario_to_dataframe(scenario)
                    
                    # Write to Excel sheet WITHOUT headers (header=False prevents pandas from adding column names)
                    df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                    
                    # Get the worksheet to apply formatting
                    worksheet = writer.sheets[sheet_name]
                    self._format_worksheet(worksheet, df)
        
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
    
    def _scenario_to_dataframe(self, scenario):
        """
        Convert scenario applications to pandas DataFrame.
        
        Args:
            scenario: Scenario object
            
        Returns:
            pd.DataFrame: DataFrame with application data
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
        
        # Start with metadata rows
        all_rows = []
        
        # Add scenario info metadata
        all_rows.append({
            "App #": "Scenario Name:",
            "Date": scenario.name or "Unnamed Scenario",
            "Product Type": "",
            "Product Name": "",
            "Rate": "",
            "Rate UOM": "",
            "Area": "",
            "Method": "",
            "AI Groups": "",
            "Field EIQ": ""
        })
        
        all_rows.append({
            "App #": "Crop Year:",
            "Date": str(getattr(scenario, 'crop_year', '') or ''),
            "Product Type": "Grower:",
            "Product Name": str(getattr(scenario, 'grower_name', '') or ''),
            "Rate": "Field:",
            "Rate UOM": str(getattr(scenario, 'field_name', '') or ''),
            "Area": "Field Area:",
            "Method": f"{getattr(scenario, 'field_area', 0) or 0} {getattr(scenario, 'field_area_uom', 'acre') or 'acre'}",
            "AI Groups": "Variety:",
            "Field EIQ": str(getattr(scenario, 'variety', '') or '')
        })
        
        # Add empty row separator
        all_rows.append({col: "" for col in columns})
        
        # Add column headers row
        header_row = {col: col for col in columns}
        all_rows.append(header_row)
        
        # Add application data rows
        for i, app in enumerate(applications):
            row = {
                "App #": i + 1,
                "Date": getattr(app, 'application_date', '') or '',
                "Product Type": getattr(app, 'product_type', '') or '',
                "Product Name": getattr(app, 'product_name', '') or '',
                "Rate": getattr(app, 'rate', 0) or 0,
                "Rate UOM": getattr(app, 'rate_uom', '') or '',
                "Area": getattr(app, 'area', 0) or 0,
                "Method": getattr(app, 'application_method', '') or '',
                "AI Groups": ', '.join(getattr(app, 'ai_groups', []) or []),
                "Field EIQ": f"{getattr(app, 'field_eiq', 0) or 0:.2f}"
            }
            all_rows.append(row)
        
        # Create DataFrame without headers (header=None to avoid default column headers)
        df = pd.DataFrame(all_rows, columns=columns)
        
        return df
    
    def _format_worksheet(self, worksheet, df):
        """
        Apply formatting to the Excel worksheet.
        
        Args:
            worksheet: openpyxl worksheet object
            df: pandas DataFrame with the data
        """
        try:
            from openpyxl.styles import Font, PatternFill, Alignment
            
            # Header formatting
            header_font = Font(bold=True)
            header_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
            
            # The header row is now at row 4 (metadata row 1, metadata row 2, empty row, then headers)
            header_row_num = 4
            
            # Format the header row (grey background)
            for col in range(1, len(df.columns) + 1):
                cell = worksheet.cell(row=header_row_num, column=col)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center')
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # Set column width with some padding
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 for very long content
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Format metadata rows (make labels bold)
            metadata_font = Font(bold=True)
            for row in range(1, 3):  # First two metadata rows
                for col in range(1, len(df.columns) + 1):
                    cell = worksheet.cell(row=row, column=col)
                    if col in [1, 3, 5, 7, 9]:  # Label columns
                        cell.font = metadata_font
        
        except ImportError:
            # If openpyxl styling is not available, skip formatting
            print("Warning: Could not apply Excel formatting - openpyxl styling not available")
        except Exception as e:
            print(f"Warning: Could not apply Excel formatting: {e}")