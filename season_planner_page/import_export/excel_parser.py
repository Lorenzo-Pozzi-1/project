"""
Excel parser for scenario import with round-trip support.

Supports both:
1. Original external Excel format
2. Files exported by the application itself (round-trip compatibility)
"""

import os
import pandas as pd
from data import Scenario, Application, ProductRepository


class ExcelScenarioParser:
    """Parser that supports both external and exported Excel formats."""
    
    def __init__(self):
        """Initialize the parser."""
        # UOM mapping from Excel format to application format
        self.uom_mapping = {
            "Fluid Ounce per Hundred Weight": "fl oz/cwt",
            "Ounce per Acre": "oz/acre",
            "Pounds per Hundred Weight": "lb/cwt",
            "Pint per Acre": "pt/acre",
            "Pounds per Acre": "lb/acre",
            "Fluid Ounce per Acre": "fl oz/acre",
            "Milliliters per 100 Kilograms": "ml/100kg",
            "Milliliter per Acre": "ml/acre",
            "Grams per Acre": "g/acre",
            "Kilograms per Acre": "kg/acre",
            "Gallons per Acre": "gal/acre",
            "Liquid Quart per Acre": "qt/acre",
            "Ounce per Hundred Weight": "oz/cwt",
            "Liter per Acre": "l/acre",
            "Milliliters per Hundred Weight": "ml/cwt",
            "Liter per Hectare": "l/acre",
            "Liters per 100 Meter Row": "l/100m",
            "Milliliter per Hectare": "ml/ha",
            "Kilograms per Hectares": "kg/ha",
            "Milliliters per 100 Meter Row": "ml/100m",
            "Imperial Gallons per Acre": "CA gal/acre",
            "Short Ton per Acre": "US ton/acre",
            "Grams per Ton": "g/metric ton",
            "Milliliters per Tonne": "ml/metric ton",
            "Milliliters per Kilograms": "ml/kg"
        }

        # Get product repository instance
        self.products_repo = ProductRepository.get_instance()
    
    def parse_file(self, file_path):
        """
        Parse an Excel file and return a Scenario object.
        Automatically detects format type.
        
        Args:
            file_path (str): Path to the Excel file
            
        Returns:
            tuple: (Scenario object, preview_info dict) or (None, None) if error
        """
        try:
            # Read Excel file with headers=None to get raw data
            df = pd.read_excel(file_path, header=None)
            
            # Detect format type
            format_type = self._detect_format_type(df)
            
            if format_type == "exported":
                return self._parse_exported_format(df, file_path)
            else:
                # For external format, re-read with headers
                df_with_headers = pd.read_excel(file_path)
                return self._parse_external_format(df_with_headers, file_path)
                
        except Exception as e:
            print(f"Error parsing Excel file: {e}")
            return None, None
    
    def _detect_format_type(self, df):
        """
        Detect whether this is an exported file or external format.
        
        Args:
            df: pandas DataFrame (read with header=None)
            
        Returns:
            str: "exported" or "external"
        """
        try:
            # Check for exported format signature
            # Look for "Scenario Name:" in first cell of first row
            if len(df) > 0 and len(df.columns) > 0:
                first_cell = str(df.iloc[0, 0]).strip()
                
                if first_cell.startswith("Scenario Name:"):
                    return "exported"
            
            # Additional check: look for exported format headers in any row
            exported_headers = ["App #", "Date", "Product Type", "Product Name", "Rate", "Rate UOM", "Area", "Method"]
            
            for row_idx in range(min(10, len(df))):  # Check first 10 rows
                row_values = [str(val).strip() for val in df.iloc[row_idx].values if pd.notna(val)]
                
                # Check if this row contains multiple exported headers
                header_matches = sum(1 for header in exported_headers if header in row_values)
                if header_matches >= 4:  # If we find at least 4 exported headers
                    return "exported"
            
            # Check for specific exported format pattern in row 2 (metadata row)
            if len(df) > 1:
                row2_values = [str(val).strip() for val in df.iloc[1].values if pd.notna(val)]
                # Look for metadata pattern: "Crop Year:", "Grower:", "Field:", etc.
                metadata_indicators = ["Crop Year:", "Grower:", "Field:", "Field Area:", "Variety:"]
                metadata_matches = sum(1 for indicator in metadata_indicators if any(indicator in val for val in row2_values))
                
                if metadata_matches >= 2:
                    return "exported"
            
            return "external"
            
        except Exception as e:
            print(f"Error detecting format: {e}")
            return "external"
    
    def _parse_exported_format(self, df, file_path):
        """Parse files exported by the application itself."""
        try:
            # Extract scenario name from row 1
            scenario_name = self._extract_exported_scenario_name(df)
            
            # Extract metadata from row 2
            metadata = self._extract_exported_metadata(df)
            
            # Find the header row
            header_row_index = self._find_exported_header_row(df)
            
            if header_row_index is None:
                raise ValueError("Could not find header row in exported format")
            
            # Extract applications data starting after header row
            applications_df = df.iloc[header_row_index + 1:].copy()
            
            # Clean and process applications
            applications_df = self._clean_exported_applications(applications_df, df.iloc[header_row_index])
            
            # Validate products
            product_validation = self._validate_products_exported(applications_df)
            
            # Create scenario
            scenario = self._create_exported_scenario(applications_df, scenario_name, metadata, product_validation)
            
            # Prepare preview info
            preview_info = {
                'total_rows': len(applications_df),
                'headers': ["App #", "Date", "Product Type", "Product Name", "Rate", "Rate UOM", "Area", "Method", "AI Groups", "Field EIQ"],
                'sample_data': self._format_sample_applications_exported(applications_df),
                'crop_year': scenario.crop_year if scenario else 'N/A',
                'grower_name': scenario.grower_name if scenario else 'N/A',
                'field_name': scenario.field_name if scenario else 'N/A',
                'field_area': scenario.field_area if scenario else 'N/A',
                'field_area_uom': scenario.field_area_uom if scenario else '',
                'variety': scenario.variety if scenario else 'N/A',
                'product_validation': product_validation
            }
            
            return scenario, preview_info
            
        except Exception as e:
            print(f"Error parsing exported format: {e}")
            return None, None
    
    def _parse_external_format(self, df, file_path):
        """Parse external Excel files (original functionality)."""
        try:
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
                'crop_year': scenario.crop_year if scenario else 'N/A',
                'grower_name': scenario.grower_name if scenario else 'N/A',
                'field_name': scenario.field_name if scenario else 'N/A', 
                'field_area': scenario.field_area if scenario else 'N/A',
                'field_area_uom': scenario.field_area_uom if scenario else '',
                'variety': scenario.variety if scenario else 'N/A',
                'product_validation': product_validation
            }
            
            return scenario, preview_info
            
        except Exception as e:
            print(f"Error parsing external format: {e}")
            return None, None
    
    # Exported format parsing methods
    
    def _extract_exported_scenario_name(self, df):
        """Extract scenario name from exported format row 1."""
        try:
            # Look for scenario name in first row
            first_row = df.iloc[0]
            
            # Check if first cell contains "Scenario Name:"
            first_cell = str(first_row.iloc[0]).strip()
            if first_cell.startswith("Scenario Name:"):
                # Name should be in the second column
                if len(first_row) > 1:
                    name = str(first_row.iloc[1]).strip()
                    return name if name != "nan" and name != "" else "Imported Scenario"
                else:
                    # Try to extract from the same cell after the colon
                    name_part = first_cell.replace("Scenario Name:", "").strip()
                    return name_part if name_part else "Imported Scenario"
            
            return "Imported Scenario"
            
        except Exception:
            return "Imported Scenario"
    
    def _extract_exported_metadata(self, df):
        """Extract metadata from exported format row 2."""
        try:
            metadata = {
                'crop_year': 2024,
                'grower_name': '',
                'field_name': '',
                'field_area': 0.0,
                'field_area_uom': 'acre',
                'variety': ''
            }
            
            if len(df) <= 1:
                return metadata
            
            # Row 2 contains metadata in label:value pairs
            row2 = df.iloc[1]
            row2_values = [str(val) for val in row2.values]
            
            # Parse the metadata row looking for patterns like "Label:" followed by value
            for i, val in enumerate(row2_values):
                val_str = str(val).strip()
                
                if val_str.startswith("Crop Year:") and i + 1 < len(row2_values):
                    metadata['crop_year'] = self._parse_crop_year_exported(str(row2_values[i + 1]))
                elif val_str.startswith("Grower:") and i + 1 < len(row2_values):
                    metadata['grower_name'] = str(row2_values[i + 1]).strip()
                elif val_str.startswith("Field:") and i + 1 < len(row2_values):
                    metadata['field_name'] = str(row2_values[i + 1]).strip()
                elif val_str.startswith("Field Area:") and i + 1 < len(row2_values):
                    area_str = str(row2_values[i + 1]).strip()
                    metadata['field_area'], metadata['field_area_uom'] = self._parse_area_exported(area_str)
                elif val_str.startswith("Variety:") and i + 1 < len(row2_values):
                    metadata['variety'] = str(row2_values[i + 1]).strip()
            
            return metadata
            
        except Exception as e:
            print(f"Error extracting exported metadata: {e}")
            return {
                'crop_year': 2024,
                'grower_name': '',
                'field_name': '',
                'field_area': 0.0,
                'field_area_uom': 'acre',
                'variety': ''
            }
    
    def _parse_crop_year_exported(self, year_str):
        """Parse crop year from exported format."""
        try:
            year_str = str(year_str).strip()
            if year_str and year_str != "nan" and year_str != "":
                year = int(float(year_str))
                return year if year > 1900 else 2024
        except Exception:
            pass
        return 2024
    
    def _parse_area_exported(self, area_str):
        """Parse field area and UOM from exported format."""
        try:
            area_str = str(area_str).strip()
            if area_str and area_str != "nan" and area_str != "":
                # Format is like "10.0 acre"
                parts = area_str.split()
                if len(parts) >= 2:
                    area = float(parts[0])
                    uom = " ".join(parts[1:])
                    return area, uom
                elif len(parts) == 1:
                    return float(parts[0]), "acre"
        except Exception:
            pass
        return 0.0, "acre"
    
    def _find_exported_header_row(self, df):
        """Find the header row in exported format."""
        try:
            # Look for row containing "App #" and "Product Name"
            for i in range(len(df)):
                row_values = [str(val).strip() for val in df.iloc[i].values if pd.notna(val)]
                
                if "App #" in row_values and "Product Name" in row_values:
                    return i
            
            return None
            
        except Exception:
            return None
    
    def _clean_exported_applications(self, applications_df, header_row):
        """Clean applications dataframe from exported format."""
        try:
            # Set proper column names from header row
            columns = []
            for col in header_row.values:
                if pd.notna(col) and str(col).strip():
                    columns.append(str(col).strip())
                else:
                    columns.append(f"Unnamed_{len(columns)}")
            
            # Ensure we don't have more columns than data
            num_cols = min(len(columns), len(applications_df.columns))
            applications_df = applications_df.iloc[:, :num_cols].copy()
            applications_df.columns = columns[:num_cols]
            
            # Remove completely empty rows
            applications_df = applications_df.dropna(how='all')
            
            # Filter out rows where App # is not a valid number
            if "App #" in applications_df.columns:
                def is_valid_app_number(val):
                    try:
                        return pd.notna(val) and str(val).strip() != "" and str(val).strip() != "nan" and float(val) > 0
                    except:
                        return False
                
                valid_mask = applications_df["App #"].apply(is_valid_app_number)
                applications_df = applications_df[valid_mask]
            
            # Fill NaN values with appropriate defaults
            for col in applications_df.columns:
                if applications_df[col].dtype == 'object':  # String columns
                    applications_df[col] = applications_df[col].fillna('')
                else:  # Numeric columns
                    applications_df[col] = applications_df[col].fillna(0)
            
            return applications_df
            
        except Exception as e:
            print(f"Error cleaning exported applications: {e}")
            return applications_df
    
    def _validate_products_exported(self, df):
        """Validate products from exported format."""
        return self._validate_products_by_column(df, "Product Name")
    
    def _create_exported_scenario(self, df, scenario_name, metadata, product_validation):
        """Create scenario from exported format data."""
        try:
            # Create new scenario
            scenario = Scenario(scenario_name)
            
            # Set metadata
            scenario.crop_year = metadata.get('crop_year', 2024)
            scenario.grower_name = metadata.get('grower_name', '')
            scenario.field_name = metadata.get('field_name', '')
            scenario.field_area = metadata.get('field_area', 0.0)
            scenario.field_area_uom = metadata.get('field_area_uom', 'acre')
            scenario.variety = metadata.get('variety', '')
            
            # Create applications from each row
            applications = []
            product_mapping = product_validation['product_mapping']
            
            for _, row in df.iterrows():
                product_name = str(row.get('Product Name', '')).strip()
                
                # Skip if no product name
                if not product_name or product_name == 'nan':
                    continue
                
                matched_product = product_mapping.get(product_name)
                
                if matched_product is not None:
                    # Use matched product data
                    app_data = {
                        'application_date': self._format_date_string(row.get('Date', ''), is_exported_format=True),
                        'product_name': matched_product.product_name,
                        'product_type': matched_product.product_type,
                        'rate': float(row.get('Rate', 0)) if pd.notna(row.get('Rate')) else 0.0,
                        'rate_uom': str(row.get('Rate UOM', '')).strip(),
                        'application_method': str(row.get('Method', 'Broadcast')),
                        'area': float(row.get('Area', 0)) if pd.notna(row.get('Area')) else 0.0
                    }
                else:
                    # Keep unmatched product data as-is
                    app_data = {
                        'application_date': self._format_date_string(row.get('Date', ''), is_exported_format=True),
                        'product_name': product_name,
                        'product_type': str(row.get('Product Type', '')).strip(),
                        'rate': float(row.get('Rate', 0)) if pd.notna(row.get('Rate')) else 0.0,
                        'rate_uom': str(row.get('Rate UOM', '')).strip(),
                        'application_method': str(row.get('Method', 'Broadcast')),
                        'area': float(row.get('Area', 0)) if pd.notna(row.get('Area')) else 0.0
                    }
                
                applications.append(Application.from_dict(app_data))
            
            scenario.applications = applications
            return scenario
            
        except Exception as e:
            print(f"Error creating exported scenario: {e}")
            return None
    
    def _format_sample_applications_exported(self, df):
        """Format sample applications for preview from exported format."""
        if len(df) == 0:
            return "No applications found"
        
        sample_lines = []
        for i, (_, row) in enumerate(df.head(3).iterrows()):
            date = row.get('Date', 'N/A')
            product = row.get('Product Name', 'N/A')
            rate = row.get('Rate', 'N/A')
            uom = row.get('Rate UOM', 'N/A')
            method = row.get('Method', 'N/A')
            
            sample_lines.append(f"{i+1}. {date} - {product} @ {rate} {uom} ({method})")
        
        if len(df) > 3:
            sample_lines.append(f"... and {len(df) - 3} more applications")
        
        return "\n".join(sample_lines)
    
    # Original external format methods (unchanged)
    
    def _validate_products(self, df):
        """Original product validation for external format."""
        return self._validate_products_by_column(df, 'Control Product')
    
    def _validate_products_by_column(self, df, product_column):
        """Validate products against the application's product repository."""
        validation_results = {
            'total_products': 0,
            'matched_products': 0,
            'unmatched_products': 0,
            'matched_list': [],
            'unmatched_list': [],
            'product_mapping': {}
        }
        
        # Get all available products from repository
        available_products = self.products_repo.get_filtered_products()
        available_product_names = {product.product_name.lower(): product for product in available_products}
        
        # Extract unique product names from Excel
        if product_column not in df.columns:
            return validation_results
        
        excel_products = df[product_column].dropna().unique()
        excel_products = [str(prod).strip() for prod in excel_products if str(prod).strip() and str(prod).strip() != "nan"]
        
        validation_results['total_products'] = len(excel_products)
        
        for excel_product in excel_products:
            excel_product_lower = excel_product.lower()
            
            if excel_product_lower in available_product_names:
                matched_product = available_product_names[excel_product_lower]
                validation_results['matched_products'] += 1
                validation_results['matched_list'].append(excel_product)
                validation_results['product_mapping'][excel_product] = matched_product
            else:
                validation_results['unmatched_products'] += 1
                validation_results['unmatched_list'].append(excel_product)
                validation_results['product_mapping'][excel_product] = None
        
        return validation_results
    
    def _find_data_end(self, df):
        """Find the index where application data ends (first blank row)."""
        for idx, row in df.iterrows():
            if row.isna().all() or (row == '').all():
                return idx
        return len(df)
    
    def _clean_dataframe(self, df):
        """Clean the dataframe by removing empty rows and standardizing data."""
        df = df.dropna(how='all')
        df = df.dropna(axis=1, how='all')
        
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('')
            else:
                df[col] = df[col].fillna(0)
        
        return df
    
    def _format_sample_applications(self, df):
        """Format sample applications for preview display (external format)."""
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

    def _create_scenario(self, df, file_path, product_validation):
        """Create a Scenario object from the parsed dataframe (external format)."""
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        scenario_name = f"{base_name}"
        
        scenario = Scenario(scenario_name)
        
        if len(df) > 0:
            first_row = df.iloc[0]
            
            scenario.crop_year = self._extract_crop_year(first_row.get('Crop Year', ''))
            scenario.grower_name = str(first_row.get(' Grower Name', '')).strip()
            scenario.field_name = str(first_row.get('GrowerFieldName', ''))
            scenario.field_area = float(first_row.get('Acres', 0)) if pd.notna(first_row.get('Acres')) else 0.0
            scenario.field_area_uom = 'acre'
            scenario.variety = str(first_row.get('Variety', ''))
        
        applications = []
        product_mapping = product_validation['product_mapping']
        
        for _, row in df.iterrows():
            excel_product_name = str(row.get('Control Product', '')).strip()
            
            if not excel_product_name or excel_product_name == 'nan':
                continue
            
            matched_product = product_mapping.get(excel_product_name)
            
            if matched_product is not None:
                app_data = {
                    'application_date': self._format_date_string(row.get('Application Date', ''), is_exported_format=False),
                    'product_name': matched_product.product_name,
                    'product_type': matched_product.product_type,
                    'rate': float(row.get('Rate', 0)) if pd.notna(row.get('Rate')) else 0.0,
                    'rate_uom': self._map_uom(row.get('Rate UOM', '')),
                    'application_method': str(row.get('Application Method', 'Broadcast')),
                    'area': float(row.get('Acres', 0)) if pd.notna(row.get('Acres')) else 0.0
                }
            else:
                app_data = {
                    'application_date': self._format_date_string(row.get('Application Date', ''), is_exported_format=False),
                    'product_name': excel_product_name,
                    'product_type': '',
                    'rate': float(row.get('Rate', 0)) if pd.notna(row.get('Rate')) else 0.0,
                    'rate_uom': self._map_uom(row.get('Rate UOM', '')),
                    'application_method': str(row.get('Application Method', 'Broadcast')),
                    'area': float(row.get('Acres', 0)) if pd.notna(row.get('Acres')) else 0.0
                }
            
            applications.append(Application.from_dict(app_data))
        
        scenario.applications = applications
        return scenario
    
    def _map_uom(self, excel_uom):
        """Map Excel UOM format to application UOM format."""
        excel_uom_clean = str(excel_uom).strip()
        return self.uom_mapping.get(excel_uom_clean, excel_uom.strip())
    
    def _format_date_string(self, date_value, is_exported_format=False):
        """
        Format date value from Excel to a clean date string.
        
        Args:
            date_value: Date value from Excel
            is_exported_format: If True, preserve date as-is (already formatted)
        
        Returns:
            str: Formatted date string
        """
        if not date_value or str(date_value).strip() == '' or str(date_value) == 'nan':
            return ''
        
        try:
            # For exported format (round-trip), preserve the date as-is since it was already formatted
            if is_exported_format:
                date_str = str(date_value).strip()
                # Just return the string as-is, it's already in the correct format
                return date_str
            
            # For external format, perform full date parsing and formatting
            if hasattr(date_value, 'strftime'):
                return date_value.strftime('%d/%m/%Y')
            
            date_str = str(date_value).strip()
            
            if ' ' in date_str and ':' in date_str:
                date_str = date_str.split(' ')[0]
            
            import datetime
            
            date_formats = [
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%m-%d-%Y',
                '%d-%m-%Y',
                '%Y/%m/%d',
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.datetime.strptime(date_str, fmt)
                    return parsed_date.strftime('%d/%m/%Y')
                except ValueError:
                    continue
            
            return date_str
            
        except Exception:
            return str(date_value).strip()
    
    def _extract_crop_year(self, crop_year_str):
        """Extract numeric year from crop year string like 'CY24'."""
        try:
            if isinstance(crop_year_str, str) and crop_year_str.startswith('CY'):
                year_suffix = int(crop_year_str[2:])
                return 2000 + year_suffix if year_suffix > 0 else 2024
            return 2024
        except:
            return 2024