import pandas as pd

df = pd.read_csv('data/csv_data/cover-anual-data-tables-2024-to-2025_T1_UK12m.csv', header=None)

print(f'Total rows: {len(df)}')
print(f'Total cols: {len(df.columns)}')
print('\nFirst 15 rows:\n')

for i in range(min(15, len(df))):
    print(f'Row {i}: {df.iloc[i, 0]}')
