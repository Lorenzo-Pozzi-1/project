"""
Excel parser for scenario import.

Simple parser that reads Excel files and extracts application data.
"""

import os
import pandas as pd
from data import Scenario, Application


class ExcelScenarioParser:
    """Parser for Excel scenario files."""
    
    def __init__(self):
        """Initialize the parser."""
        self.debug_mode = True  # For development - saves CSV files
    
    def parse_file(self, file_path):
        """
        Parse an Excel file and return a Scenario object.
        
        Args:
            file_path (str): Path to the Excel file
            
        Returns:
            tuple: (Scenario object, preview_info dict) or (None, None) if error
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Find where data ends (first completely empty row)
            data_end_idx = self._find_data_end(df)
            
            # Extract just the application data
            applications_df = df.iloc[:data_end_idx].copy()
            
            # Clean the dataframe
            applications_df = self._clean_dataframe(applications_df)
            
            # Save CSV for development/debugging
            csv_path = None
            if self.debug_mode:
                csv_path = self._save_debug_csv(applications_df, file_path)
            
            # Create scenario from the data
            scenario = self._create_scenario(applications_df, file_path)
            
            # Prepare preview info
            preview_info = {
                'total_rows': len(applications_df),
                'headers': list(applications_df.columns),
                'sample_data': self._format_sample_applications(applications_df),
                'csv_path': csv_path,
                # Add scenario metadata
                'crop_year': scenario.crop_year if scenario else 'N/A',
                'grower_name': scenario.grower_name if scenario else 'N/A',
                'field_name': scenario.field_name if scenario else 'N/A', 
                'field_area': scenario.field_area if scenario else 'N/A',
                'field_area_uom': scenario.field_area_uom if scenario else '',
                'variety': scenario.variety if scenario else 'N/A'
            }
            
            return scenario, preview_info
            
        except Exception as e:
            print(f"Error parsing Excel file: {e}")
            return None, None
    
    def _find_data_end(self, df):
        """Find the index where application data ends (first blank row)."""
        for idx, row in df.iterrows():
            # Check if row is completely empty (all NaN or empty strings)
            if row.isna().all() or (row == '').all():
                return idx
        
        # If no blank row found, return all data
        return len(df)
    
    def _clean_dataframe(self, df):
        """Clean the dataframe by removing empty rows and standardizing data."""
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Remove completely empty columns
        df = df.dropna(axis=1, how='all')
        
        # Fill NaN values with appropriate defaults
        for col in df.columns:
            if df[col].dtype == 'object':  # String columns
                df[col] = df[col].fillna('')
            else:  # Numeric columns
                df[col] = df[col].fillna(0)
        
        return df
    
    def _save_debug_csv(self, df, original_file_path):
        """Save dataframe as CSV for debugging purposes."""
        try:
            # Create debug filename
            base_name = os.path.splitext(os.path.basename(original_file_path))[0]
            csv_filename = f"{base_name}_imported_debug.csv"
            
            # Save in same directory as original file
            csv_path = os.path.join(os.path.dirname(original_file_path), csv_filename)
            
            # Save CSV
            df.to_csv(csv_path, index=False)
            
            print(f"Debug CSV saved to: {csv_path}")
            return csv_path
            
        except Exception as e:
            print(f"Could not save debug CSV: {e}")
            return None
    
    def _format_sample_applications(self, df):
        """Format sample applications for preview display."""
        if len(df) == 0:
            return "No applications found"
        
        sample_lines = []
        for i, (_, row) in enumerate(df.head(3).iterrows()):
            date = row.get('Application Date', 'N/A')
            product = row.get('Control Product', 'N/A')
            rate = row.get('Rate', 'N/A')
            uom = row.get('Rate UOM', 'N/A')
            method = row.get('Application Method', 'N/A')
            
            sample_lines.append(f"{i+1}. {date} - {product} @ {rate} {uom} ({method})")
        
        if len(df) > 3:
            sample_lines.append(f"... and {len(df) - 3} more applications")
        
        return "\n".join(sample_lines)

    def _create_scenario(self, df, file_path):
        """Create a Scenario object from the parsed dataframe."""
        # Extract base filename for scenario name
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        scenario_name = f"Imported: {base_name}"
        
        # Create new scenario
        scenario = Scenario(scenario_name)
        
        # Extract metadata from first row (all rows should have same metadata)
        if len(df) > 0:
            first_row = df.iloc[0]
            
            # Set scenario metadata
            scenario.crop_year = self._extract_crop_year(first_row.get('Crop Year', ''))
            scenario.grower_name = str(first_row.get(' Grower Name', '')).strip()
            scenario.field_name = str(first_row.get('GrowerFieldName', ''))
            scenario.field_area = float(first_row.get('Acres', 0)) if pd.notna(first_row.get('Acres')) else 0.0
            scenario.field_area_uom = 'acre'  # Data shows acres
            scenario.variety = str(first_row.get('Variety', ''))
        
        # Create applications from each row
        applications = []
        
        for _, row in df.iterrows():
            app_data = {
                'application_date': str(row.get('Application Date', '')),
                'product_name': str(row.get('Control Product', '')),
                'rate': float(row.get('Rate', 0)) if pd.notna(row.get('Rate')) else 0.0,
                'rate_uom': str(row.get('Rate UOM', '')),
                'application_method': str(row.get('Application Method', 'Broadcast')),
                'area': float(row.get('Acres', 0)) if pd.notna(row.get('Acres')) else 0.0,
                'product_type': ''  # Will be determined by product matching later
            }
            
            # Only add if we have at least a product name and valid rate
            if app_data['product_name'] and app_data['product_name'] != 'nan':
                applications.append(Application.from_dict(app_data))
        
        scenario.applications = applications
        
        return scenario
    
    def _extract_crop_year(self, crop_year_str):
        """Extract numeric year from crop year string like 'CY24'."""
        try:
            if isinstance(crop_year_str, str) and crop_year_str.startswith('CY'):
                year_suffix = int(crop_year_str[2:])
                # Convert 2-digit year to 4-digit (assuming 21st century)
                return 2000 + year_suffix if year_suffix > 0 else 2024
            return 2024  # Default
        except:
            return 2024