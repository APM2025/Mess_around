import pandas as pd

# Check sheets in ODS file
xls = pd.ExcelFile('data/cover_anual_data_tables_2024_to_2025.ods', engine='odf')

print("Available sheets:")
for i, sheet in enumerate(xls.sheet_names, 1):
    print(f"  {i}. {sheet}")

# Load first data sheet (skip title sheet)
if len(xls.sheet_names) > 1:
    print(f"\nLoading sheet: {xls.sheet_names[1]}")
    df = pd.read_excel('data/cover_anual_data_tables_2024_to_2025.ods', 
                       engine='odf', 
                       sheet_name=1)
    
    print(f"\nShape: {df.shape}")
    print(f"\nColumns:")
    print(df.columns.tolist())
    print(f"\nFirst 10 rows:")
    print(df.head(10))
