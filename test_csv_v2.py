from pathlib import Path
from backend_code.database_src.csv_cleaner_v2 import load_cleaned_csv

# Test T15 (regional time series)
csv_path = Path('data/csv_data/cover-anual-data-tables-2024-to-2025_T15_RegMMR24m.csv')

df, vaccine_columns, csv_type = load_cleaned_csv(csv_path)

print(f"\n=== RESULTS ===")
print(f"CSV Type: {csv_type}")
print(f"Rows loaded: {len(df)}")
print(f"Columns found: {len(vaccine_columns)}")
print(f"\nFirst 5 columns:")
for i, col in enumerate(vaccine_columns[:5]):
    print(f"  {i+1}. {col}")

print(f"\nFirst 3 rows:")
print(df.head(3))
