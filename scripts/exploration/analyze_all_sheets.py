"""
Comprehensive ODS Sheet Analysis

Analyzes ALL sheets in the COVER ODS file to understand:
- Sheet structure (rows, columns)
- Metadata rows vs data rows
- Geographic levels (UK, UTLA, Region)
- Vaccine types per sheet
- Age cohorts per sheet

This will help us design the proper data loading strategy.
"""

import pandas as pd
from pathlib import Path

# Load ODS file
ods_path = Path("data/cover_anual_data_tables_2024_to_2025.ods")
xls = pd.ExcelFile(ods_path, engine='odf')

print("=" * 100)
print("COMPREHENSIVE COVER DATASET SHEET ANALYSIS")
print("=" * 100)
print(f"\nTotal sheets: {len(xls.sheet_names)}\n")

# Categorize sheets
metadata_sheets = ['Cover', 'Contents', 'Notes', 'Revision_History']
uk_level_sheets = ['T1_UK12m', 'T2_UK24m', 'T3_UK5y']
utla_sheets = ['T4a_UTLA12m', 'T4b_UTLA12m', 'T5a_UTLA24m', 'T5b_UTLA24m', 
               'T6a_UTLA5y', 'T6b_UTLA5y', 'T7_UTLAHepB', 'T8_UTLABCG']
england_sheets = ['T9_Eng12m', 'T10_Eng24m', 'T11_Eng5y', 'T12_EngDip5y', 'T13_EngMMR24m']
regional_sheets = ['T14_RegDTaP24m', 'T15_RegMMR24m']

sheet_categories = {
    'Metadata': metadata_sheets,
    'UK National': uk_level_sheets,
    'UTLA (Local Authority)': utla_sheets,
    'England Level': england_sheets,
    'Regional': regional_sheets
}

# Analyze each category
for category, sheets in sheet_categories.items():
    print(f"\n{'='*100}")
    print(f"CATEGORY: {category}")
    print(f"{'='*100}\n")
    
    for sheet_name in sheets:
        if sheet_name not in xls.sheet_names:
            print(f"⚠️  {sheet_name} - NOT FOUND")
            continue
        
        print(f"\n📊 Sheet: {sheet_name}")
        print("-" * 80)
        
        # Load without header to see raw structure
        df_raw = pd.read_excel(ods_path, sheet_name=sheet_name, engine='odf', header=None)
        
        print(f"   Dimensions: {df_raw.shape[0]} rows × {df_raw.shape[1]} columns")
        
        # Show first 10 rows to identify metadata
        print(f"\n   First 10 rows (raw):")
        for i in range(min(10, len(df_raw))):
            row_preview = str(df_raw.iloc[i, 0])[:60]
            print(f"      Row {i}: {row_preview}")
        
        # Try to identify where actual data starts
        if category not in ['Metadata']:
            # Look for a row that might be the header
            for i in range(min(15, len(df_raw))):
                first_cell = str(df_raw.iloc[i, 0])
                if any(keyword in first_cell for keyword in ['Country', 'UTLA', 'Code', 'Area', 'Region']):
                    print(f"\n   ✓ Possible header row at index {i}: {first_cell}")
                    
                    # Try loading with this as header
                    try:
                        df_data = pd.read_excel(ods_path, sheet_name=sheet_name, 
                                               engine='odf', skiprows=i)
                        print(f"   ✓ Data shape after skipping {i} rows: {df_data.shape}")
                        print(f"   ✓ Columns: {list(df_data.columns[:5])}...")
                        
                        # Check first data column
                        geo_col = df_data.columns[0]
                        unique_geos = df_data[geo_col].dropna().unique()[:5]
                        print(f"   ✓ Sample {geo_col} values: {list(unique_geos)}")
                        
                    except Exception as e:
                        print(f"   ✗ Error loading with header at row {i}: {e}")
                    
                    break

print("\n" + "=" * 100)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 100)

print("""
Based on this analysis, we need:

1. **Sheet Type Detection**: Identify if sheet is UK/UTLA/Regional
2. **Metadata Row Detection**: Skip rows until we find the header
3. **Column Mapping**: Different sheets have different column names
4. **Geographic Extraction**: 
   - UK sheets: England, Scotland, Wales, NI
   - UTLA sheets: ~150 local authorities
   - Regional sheets: 9 NHS regions

Next steps:
- Create a sheet configuration mapping
- Update data loaders to handle different sheet types
- Write specific parsers for each category
""")

print("=" * 100)
