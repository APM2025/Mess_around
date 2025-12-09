"""
Quick data exploration script to understand the COVER dataset structure
"""
import pandas as pd
from pathlib import Path

# Load the CSV
csv_path = Path("data/cover_anual_data_tables_2024_to_2025.csv")
df = pd.read_csv(csv_path)

print("=" * 80)
print("COVER DATASET EXPLORATION")
print("=" * 80)

print(f"\n📊 DATASET SHAPE: {df.shape[0]} rows × {df.shape[1]} columns")

print("\n📋 COLUMN NAMES:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2d}. {col}")

print("\n🔍 DATA TYPES:")
print(df.dtypes)

print("\n📝 FIRST 5 ROWS:")
print(df.head())

print("\n🔢 UNIQUE VALUES PER COLUMN:")
for col in df.columns:
    unique_count = df[col].nunique()
    print(f"  {col:40s}: {unique_count:6d} unique values")

print("\n🎯 SAMPLE VALUES FROM KEY COLUMNS:")
# Show sample unique values from likely grouping columns
for col in df.columns[:5]:  # First 5 columns likely have categorical data
    print(f"\n  {col}:")
    print(f"    {df[col].unique()[:10].tolist()}")

print("\n📊 MISSING DATA:")
missing = df.isnull().sum()
if missing.sum() > 0:
    print(missing[missing > 0])
else:
    print("  No missing values found!")

print("\n" + "=" * 80)
