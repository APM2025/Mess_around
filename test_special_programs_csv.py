from pathlib import Path
from backend_code.database_src.csv_cleaner_v2 import load_cleaned_csv

# Test T7 (HepB)
print("=" * 80)
print("T7 - Hepatitis B")
print("=" * 80)
csv_path = Path('data/csv_data/cover-anual-data-tables-2024-to-2025_T7_UTLAHepB.csv')
df, columns, csv_type = load_cleaned_csv(csv_path)

print(f"\nCSV Type: {csv_type}")
print(f"Rows loaded: {len(df)}")
print(f"Columns found: {len(columns)}")
print(f"\nFirst 3 columns:")
for i, col in enumerate(columns[:3]):
    print(f"  {i+1}. {col}")

print(f"\nFirst 3 rows, first 5 columns:")
print(df.iloc[:3, :5])

print("\n" + "=" * 80)
print("T8 - BCG")
print("=" * 80)
csv_path = Path('data/csv_data/cover-anual-data-tables-2024-to-2025_T8_UTLABCG.csv')
df, columns, csv_type = load_cleaned_csv(csv_path)

print(f"\nCSV Type: {csv_type}")
print(f"Rows loaded: {len(df)}")
print(f"Columns found: {len(columns)}")
print(f"\nFirst 3 columns:")
for i, col in enumerate(columns[:3]):
    print(f"  {i+1}. {col}")

print(f"\nFirst 3 rows, first 5 columns:")
print(df.iloc[:3, :5])
