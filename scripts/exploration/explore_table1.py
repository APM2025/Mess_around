import pandas as pd

# Load T1_UK12m sheet
df_raw = pd.read_excel('data/cover_anual_data_tables_2024_to_2025.ods', 
                       engine='odf', 
                       sheet_name='T1_UK12m',
                       header=None)

print("RAW DATA (first 20 rows):")
print(df_raw.head(20))

print("\n\n" + "="*80)
print("Trying to parse with skiprows...")

# Try skipping metadata rows
df = pd.read_excel('data/cover_anual_data_tables_2024_to_2025.ods', 
                   engine='odf', 
                   sheet_name='T1_UK12m',
                   skiprows=5)  # Skip first 5 rows

print(f"\nShape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nData:")
print(df)
