import pandas as pd
import os

def read_files():
    """
    Read the products and active ingredients CSV files.
    
    Returns:
        tuple: (products_df, cpai_df) - DataFrames for products and active ingredients
    """
    print("=" * 50)
    print("== STEP 1: READING CSV FILES ==")
    print("=" * 50)
    
    # Define file paths
    products_file = r"C:\Users\LORPOZZI\OneDrive - McCain Foods Limited\Desktop\PestIQ app\update_products\csv_products.csv"
    cpai_file = r"C:\Users\LORPOZZI\OneDrive - McCain Foods Limited\Desktop\PestIQ app\update_products\csv_cpai.csv"
    
    try:
        # Read the products CSV file
        print("\n1. Reading products CSV file...")
        products_df = pd.read_csv(products_file)
        print(f"   ✓ Successfully loaded {len(products_df)} product records")
        
        # Read the active ingredients CSV file
        print("\n2. Reading active ingredients CSV file...")
        cpai_df = pd.read_csv(cpai_file)
        print(f"   ✓ Successfully loaded {len(cpai_df)} active ingredient records")
        
        # Display the structure of both files for verification
        print("\n3. Verifying file structure...")
        print(f"   ✓ Products file has {len(products_df.columns)} columns")
        print(f"   ✓ Active ingredients file has {len(cpai_df.columns)} columns")
        print("   ✓ Files loaded successfully!\n")
        
        return products_df, cpai_df
        
    except FileNotFoundError as e:
        print(f"   ✗ ERROR: Could not find file - {e}")
        return None, None
    except Exception as e:
        print(f"   ✗ ERROR: Problem reading files - {e}")
        return None, None

def fill_country_column(products_df):
    """
    Fill the country column based on region values.
    If country is missing:
    - Assign "United States" if region is Idaho, Maine, Washington, or Wisconsin
    - Assign "Canada" if region is Alberta, Manitoba, New Brunswick, Prince Edward Island, Quebec, or Saskatchewan
    - Assign "ERROR" for any other value in the region
    
    Args:
        products_df (pd.DataFrame): Products dataframe
        
    Returns:
        pd.DataFrame: Updated products dataframe with filled country column
    """
    print("=" * 50)
    print("== STEP 2: FILLING MISSING COUNTRY VALUES ==")
    print("=" * 50)
    
    # Define regions
    us_regions = ['Idaho', 'Maine', 'Washington', 'Wisconsin']
    canadian_regions = ['Alberta', 'Manitoba', 'New Brunswick', 'Prince Edward Island', 'Quebec', 'Saskatchewan']
    
    print("\n1. Checking for missing country values...")
    print("\n2. Assigning countries based on regions:")
    print("   • US regions: Idaho, Maine, Washington, Wisconsin")
    print("   • Canadian regions: Alberta, Manitoba, New Brunswick, Prince Edward Island, Quebec, Saskatchewan")
    
    # Track how many records were updated
    updated_count = 0
    
    # Process each row
    for index, row in products_df.iterrows():
        # Check if country is missing (NaN, empty string, or None)
        if pd.isna(row['country']) or row['country'] == '' or row['country'] is None:
            region = row['region']
            
            # Assign country based on region
            if region in us_regions:
                products_df.at[index, 'country'] = 'United States'
                updated_count += 1
            elif region in canadian_regions:
                products_df.at[index, 'country'] = 'Canada'
                updated_count += 1
            else:
                products_df.at[index, 'country'] = 'ERROR'
                updated_count += 1
    
    print(f"\n3. Processing complete:")
    print(f"   ✓ Updated {updated_count} records with missing country values\n")
    return products_df

def add_ai_info(products_df, cpai_df):
    """
    Add active ingredient information columns to the products dataframe.
    Adds 12 new columns: AI1, [AI1], [AI1]UOM, AI2, [AI2], [AI2]UOM, AI3, [AI3], [AI3]UOM, AI4, [AI4], [AI4]UOM
    
    Args:
        products_df (pd.DataFrame): Products dataframe
        cpai_df (pd.DataFrame): Active ingredients dataframe
        
    Returns:
        pd.DataFrame: Updated products dataframe with AI columns
    """
    print("=" * 50)
    print("== STEP 3: ADDING ACTIVE INGREDIENT INFORMATION ==")
    print("=" * 50)
    
    # Initialize the new columns for active ingredients (AI1-AI4)
    ai_columns = []
    for i in range(1, 5):  # AI1 through AI4
        ai_columns.extend([
            f'AI{i}',           # Active ingredient name
            f'[AI{i}]',         # Active ingredient concentration/amount
            f'[AI{i}]UOM'      # Unit of measure
        ])
    
    print("\n1. Adding new columns for active ingredients...")
    # Add the new columns to the products dataframe, initialize with empty strings
    for col in ai_columns:
        products_df[col] = ''
    
    print(f"   ✓ Added 12 new columns: AI1, [AI1], [AI1]UOM, AI2, [AI2], [AI2]UOM, AI3, [AI3], [AI3]UOM, AI4, [AI4], [AI4]UOM")
    
    # Process each row in the products dataframe
    print("\n2. Matching products with their active ingredients...")
    print("   • Each product can have up to 4 active ingredients")
    print("   • Copying ingredient name, concentration, and unit of measure")
    
    total_products = len(products_df)
    processed_count = 0
    
    for index, row in products_df.iterrows():
        cp_id = row['CP ID']
        
        # Find matching active ingredients for this CP ID
        matching_ais = cpai_df[cpai_df['CP ID'] == cp_id]
        
        # Fill in the AI information for up to 4 active ingredients
        for ai_index, (_, ai_row) in enumerate(matching_ais.iterrows()):
            if ai_index >= 4:  # Only process first 4 AIs
                print(f"Skipping additional active ingredients for CP ID {cp_id} as only 4 are allowed.")
                break
                
            ai_num = ai_index + 1
            products_df.at[index, f'AI{ai_num}'] = ai_row['Name'] if pd.notna(ai_row['Name']) else ''
            products_df.at[index, f'[AI{ai_num}]'] = ai_row['Concentration_Amount__c'] if pd.notna(ai_row['Concentration_Amount__c']) else ''
            products_df.at[index, f'[AI{ai_num}]UOM'] = ai_row['UOM Master.Short_Name__c'] if pd.notna(ai_row['UOM Master.Short_Name__c']) else ''
        
        processed_count += 1
        if processed_count % 100 == 0:  # Progress update every 100 rows
            progress = (processed_count / total_products) * 100
            print(f"   • Progress: {processed_count}/{total_products} products processed ({progress:.1f}%)")
    
    print(f"\n3. Active ingredient processing complete:")
    print(f"   ✓ Processed all {total_products} products")
    print(f"   ✓ Active ingredient information added successfully!\n")
    return products_df

def standardize_rate_uom(products_df):
    """
    Standardize rate UOM columns by checking if min and max rate UOM values match.
    If they don't match, replace max rate value with "Check label".
    Then delete max rate UOM column and rename min rate UOM column to "rate UOM".
    
    Args:
        products_df (pd.DataFrame): Products dataframe
        
    Returns:
        pd.DataFrame: Updated products dataframe with standardized rate UOM
    """
    print("=" * 50)
    print("== STEP 4: STANDARDIZING RATE UOM COLUMNS ==")
    print("=" * 50)
    
    print("\n1. Cleaning UOM values...")
    
    # Track how many records were cleaned
    cleaned_count = 0
    
    # Define UOM replacements
    uom_replacements = {
        'FO100G': 'fl oz/100gal',
        'Lb100G': 'lb/100gal',
        'O100G': 'oz/100gal'
    }
    
    # Clean UOM values using the replacement dictionary
    for index, row in products_df.iterrows():
        min_rate_uom = row.get('min rate UOM', '')
        max_rate_uom = row.get('max rate UOM', '')
        
        # Check and replace min rate UOM
        min_uom_clean = str(min_rate_uom).strip()
        if min_uom_clean in uom_replacements:
            products_df.at[index, 'min rate UOM'] = uom_replacements[min_uom_clean]
            cleaned_count += 1
        
        # Check and replace max rate UOM
        max_uom_clean = str(max_rate_uom).strip()
        if max_uom_clean in uom_replacements:
            products_df.at[index, 'max rate UOM'] = uom_replacements[max_uom_clean]
            cleaned_count += 1
    
    print(f"   ✓ Cleaned {cleaned_count} UOM values using replacements: {', '.join([f'{k}→{v}' for k, v in uom_replacements.items()])}")
    
    print("\n2. Checking UOM consistency between min and max rate columns...")
    
    # Track how many records were updated
    updated_count = 0
    total_products = len(products_df)
    
    # Convert max rate column to object dtype to allow string values
    if 'max rate' in products_df.columns:
        products_df['max rate'] = products_df['max rate'].astype('object')
    
    # Second pass: Check consistency and update max rate if needed
    for index, row in products_df.iterrows():
        min_rate_uom = row.get('min rate UOM', '')
        max_rate_uom = row.get('max rate UOM', '')
        
        # Check if UOM values are different (accounting for NaN and empty strings)
        min_uom_clean = str(min_rate_uom).strip() if pd.notna(min_rate_uom) else ''
        max_uom_clean = str(max_rate_uom).strip() if pd.notna(max_rate_uom) else ''
        
        if min_uom_clean != max_uom_clean and min_uom_clean != '' and max_uom_clean != '':
            # UOM values don't match, replace max rate with "Check label"
            products_df.at[index, 'max rate'] = 'Check label'
            updated_count += 1
    
    print(f"   ✓ Found {updated_count} products with mismatched UOM values")
    print(f"   ✓ Updated max rate to 'Check label' for these {updated_count} products")
    
    print("\n3. Cleaning up UOM columns...")
    
    # Delete the max rate UOM column
    if 'max rate UOM' in products_df.columns:
        products_df = products_df.drop('max rate UOM', axis=1)
        print("   ✓ Deleted 'max rate UOM' column")
    
    # Rename min rate UOM column to rate UOM
    if 'min rate UOM' in products_df.columns:
        products_df = products_df.rename(columns={'min rate UOM': 'rate UOM'})
        print("   ✓ Renamed 'min rate UOM' column to 'rate UOM'")
    
    print(f"\n4. Rate UOM standardization complete:")
    print(f"   ✓ Processed all {total_products} products")
    print(f"   ✓ Standardized rate UOM structure successfully!\n")
    
    return products_df

def main():
    """
    Main function to process pesticide product data.
    Orchestrates the reading, country filling, AI information addition, and rate UOM standardization.
    """
    print("\033c", end="")
    print("\n" + "=" * 60)
    print("== PESTICIDE PRODUCT DATA PROCESSING TOOL ==")
    print("=" * 60)
    print("This tool will:")
    print("• Read product and active ingredient data from CSV files")
    print("• Fill missing country information based on regions")
    print("• Add active ingredient details to each product")
    print("• Standardize rate UOM columns and clean up structure")
    print("• Save the final processed data to a new CSV file")
    print("=" * 60 + "\n")
    
    # Step 1: Read files
    products_df, cpai_df = read_files()
    if products_df is None or cpai_df is None:
        print("=" * 50)
        print("== PROCESSING FAILED ==")
        print("=" * 50)
        print("✗ Could not read input files. Please check file paths and try again.")
        return None
    
    # Step 2: Fill country column
    products_df = fill_country_column(products_df)
    
    # Step 3: Add AI information
    products_df = add_ai_info(products_df, cpai_df)
    
    # Step 4: Standardize rate UOM columns
    products_df = standardize_rate_uom(products_df)
    
    # Final summary
    print("=" * 50)
    print("== PROCESSING COMPLETE ==")
    print("=" * 50)
    print(f"✓ Final dataset contains {products_df.shape[0]} products with {products_df.shape[1]} columns")
    
    if products_df is not None:
        output_file = r"C:\Users\LORPOZZI\OneDrive - McCain Foods Limited\Desktop\PestIQ app\data\csv_products.csv"
        products_df.to_csv(output_file, index=False)
        print(f"✓ Data successfully saved to: {output_file}")
        print("\nYou can now open the processed_products.csv file to view the results!")
    
    print("=" * 50)

if __name__ == "__main__":
    main()