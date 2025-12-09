import pandas as pd

df = pd.read_csv('data/cover_anual_data_tables_2024_to_2025.csv')
print("First column name:", df.columns[0])
print("\nUnique values:")
for v in df[df.columns[0]].unique():
    if isinstance(v, str) and len(v) <= 50:
        print(f"  '{v}'")
