"""
Excel parser for scenario import.

Enhanced parser that validates product names against the application's product repository.
"""

import os
import pandas as pd
from data import Scenario, Application, ProductRepository


class ExcelScenarioParser:
    """Parser for Excel scenario files with product validation."""
    
    def __init__(self):
        """Initialize the parser."""
        # UOM mapping from Excel format to application format
        self.uom_mapping = {
            "GHA": "g/ha",
            "LHA": "l/ha", 
            "KGHA": "kg/ha",
            "MLHA": "ml/ha",
            "LAC": "l/acre"
            # Add more mappings as needed
        }
        
        # Get product repository instance
        self.products_repo = ProductRepository.get_instance()
    
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
            
            # Validate and match products
            product_validation = self._validate_products(applications_df)
            
            # Create scenario from the data
            scenario = self._create_scenario(applications_df, file_path, product_validation)
            
            # Prepare preview info
            preview_info = {
                'total_rows': len(applications_df),
                'headers': list(applications_df.columns),
                'sample_data': self._format_sample_applications(applications_df),
                # Add scenario metadata
                'crop_year': scenario.crop_year if scenario else 'N/A',
                'grower_name': scenario.grower_name if scenario else 'N/A',
                'field_name': scenario.field_name if scenario else 'N/A', 
                'field_area': scenario.field_area if scenario else 'N/A',
                'field_area_uom': scenario.field_area_uom if scenario else '',
                'variety': scenario.variety if scenario else 'N/A',
                # Add product validation info
                'product_validation': product_validation
            }
            
            return scenario, preview_info
            
        except Exception as e:
            return None, None
    
    def _validate_products(self, df):
        """
        Validate product names against the application's product repository.
        
        Args:
            df: DataFrame containing application data
            
        Returns:
            dict: Validation results with matched/unmatched products
        """
        validation_results = {
            'total_products': 0,
            'matched_products': 0,
            'unmatched_products': 0,
            'matched_list': [],
            'unmatched_list': [],
            'product_mapping': {}  # Excel name -> Repository product
        }
        
        # Get all available products from repository (use filtered products)
        available_products = self.products_repo.get_filtered_products()
        available_product_names = {product.product_name.lower(): product for product in available_products}
        
        # Extract unique product names from Excel
        excel_products = df['Control Product'].dropna().unique()
        excel_products = [str(prod).strip() for prod in excel_products if str(prod).strip()]
        
        validation_results['total_products'] = len(excel_products)
        
        for excel_product in excel_products:
            # Try exact match (case-insensitive)
            excel_product_lower = excel_product.lower()
            
            if excel_product_lower in available_product_names:
                # Found exact match
                matched_product = available_product_names[excel_product_lower]
                validation_results['matched_products'] += 1
                validation_results['matched_list'].append(excel_product)
                validation_results['product_mapping'][excel_product] = matched_product
            else:
                # No match found
                validation_results['unmatched_products'] += 1
                validation_results['unmatched_list'].append(excel_product)
                validation_results['product_mapping'][excel_product] = None
        
        return validation_results
    
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
    
    def _format_sample_applications(self, df):
        """Format sample applications for preview display."""
        if len(df) == 0:
            return "No applications found"
        
        sample_lines = []
        for i, (_, row) in enumerate(df.head(3).iterrows()):
            date = row.get('Application Date', 'N/A')
            product = row.get('Control Product', 'N/A')
            rate = row.get('ConvertedRate', 'N/A')
            uom = row.get('ConvertedRateUOM', 'N/A')
            method = row.get('Application Method', 'N/A')
            
            sample_lines.append(f"{i+1}. {date} - {product} @ {rate} {uom} ({method})")
        
        if len(df) > 3:
            sample_lines.append(f"... and {len(df) - 3} more applications")
        
        return "\n".join(sample_lines)

    def _create_scenario(self, df, file_path, product_validation):
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
        
        # Create applications from each row, including unmatched products
        applications = []
        product_mapping = product_validation['product_mapping']
        
        for _, row in df.iterrows():
            excel_product_name = str(row.get('Control Product', '')).strip()
            
            # Skip if no product name
            if not excel_product_name or excel_product_name == 'nan':
                continue
            
            matched_product = product_mapping.get(excel_product_name)
            
            if matched_product is not None:
                # Use matched product data
                app_data = {
                    'application_date': self._format_date_string(row.get('Application Date', '')),
                    'product_name': matched_product.product_name,  # Use the matched product name
                    'product_type': matched_product.product_type,  # Set the product type from matched product
                    'rate': float(row.get('ConvertedRate', 0)) if pd.notna(row.get('ConvertedRate')) else 0.0,
                    'rate_uom': self._map_uom(row.get('ConvertedRateUOM', '')),
                    'application_method': str(row.get('Application Method', 'Broadcast')),
                    'area': float(row.get('Acres', 0)) if pd.notna(row.get('Acres')) else 0.0
                }
            else:
                # Keep unmatched product data as-is from Excel
                app_data = {
                    'application_date': self._format_date_string(row.get('Application Date', '')),
                    'product_name': excel_product_name,  # Keep original Excel name
                    'product_type': '',  # Unknown product type
                    'rate': float(row.get('ConvertedRate', 0)) if pd.notna(row.get('ConvertedRate')) else 0.0,
                    'rate_uom': self._map_uom(row.get('ConvertedRateUOM', '')),
                    'application_method': str(row.get('Application Method', 'Broadcast')),
                    'area': float(row.get('Acres', 0)) if pd.notna(row.get('Acres')) else 0.0
                }
            
            # Add application regardless of match status
            applications.append(Application.from_dict(app_data))
        
        scenario.applications = applications
        
        return scenario
    
    def _map_uom(self, excel_uom):
        """
        Map Excel UOM format to application UOM format.
        
        Args:
            excel_uom (str): UOM string from Excel file
            
        Returns:
            str: Mapped UOM string for application use
        """
        # Strip whitespace and convert to uppercase for consistent lookup
        excel_uom_clean = str(excel_uom).strip().upper()
        
        # Return mapped UOM if exists, otherwise return original (cleaned)
        return self.uom_mapping.get(excel_uom_clean, excel_uom.strip())
    
    def _format_date_string(self, date_value):
        """
        Format date value from Excel to a clean date string in DD/MM/YYYY format.
        
        Args:
            date_value: Date value from Excel (could be string, datetime, etc.)
            
        Returns:
            str: Cleaned date string in DD/MM/YYYY format
        """
        if not date_value or str(date_value).strip() == '' or str(date_value) == 'nan':
            return ''
        
        try:
            # If it's already a datetime object
            if hasattr(date_value, 'strftime'):
                return date_value.strftime('%d/%m/%Y')
            
            date_str = str(date_value).strip()
            
            # If it contains time (space followed by time), remove the time part
            if ' ' in date_str and ':' in date_str:
                date_str = date_str.split(' ')[0]
            
            # Try to parse the date string and format it
            import datetime
            
            # Try common date formats
            date_formats = [
                '%Y-%m-%d',      # 2024-06-04
                '%m/%d/%Y',      # 06/04/2024
                '%d/%m/%Y',      # 04/06/2024
                '%m-%d-%Y',      # 06-04-2024
                '%d-%m-%Y',      # 04-06-2024
                '%Y/%m/%d',      # 2024/06/04
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.datetime.strptime(date_str, fmt)
                    return parsed_date.strftime('%d/%m/%Y')
                except ValueError:
                    continue
            
            # If no format worked, return the original cleaned string
            return date_str
            
        except Exception:
            # If any error occurs, return the original value as string
            return str(date_value).strip()
    
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