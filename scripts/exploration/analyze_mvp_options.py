"""
COVER Dataset Analysis & MVP Subset Recommendations

Based on exploration of: cover_anual_data_tables_2024_to_2025.ods
"""

import pandas as pd

print("=" * 80)
print("COVER DATASET STRUCTURE ANALYSIS")
print("=" * 80)

# Load the ODS file
xls = pd.ExcelFile('data/cover_anual_data_tables_2024_to_2025.ods', engine='odf')

print(f"\n📊 Total Sheets: {len(xls.sheet_names)}")
print("\n📋 Sheet Categories:")
print("  - Cover/Contents/Notes: Metadata sheets")
print("  - T1-T3: UK-level data (12m, 24m, 5y age groups)")
print("  - T4-T6: UTLA (local authority) level data")
print("  - T7-T8: Specific vaccines (HepB, BCG)")
print("  - T9-T11: England-level data")
print("  - T12-T15: Specific breakdowns")

print("\n🔍 SAMPLE DATA - Table 1 (UK 12-month immunisations):")
df_t1 = pd.read_excel('data/cover_anual_data_tables_2024_to_2025.ods', 
                      engine='odf', 
                      sheet_name='T1_UK12m',
                      skiprows=5)

print(f"\nShape: {df_t1.shape}")
print(f"Data:\n{df_t1}")

# Check T4a_UTLA12m for local authority data
print("\n\n🔍 SAMPLE DATA - Table 4a (UTLA 12-month data):")
df_t4a = pd.read_excel('data/cover_anual_data_tables_2024_to_2025.ods', 
                       engine='odf', 
                       sheet_name='T4a_UTLA12m',
                       skiprows=5)

print(f"\nShape: {df_t4a.shape}")  
print(f"Columns: {df_t4a.columns.tolist()}")
print(f"First 10 rows:\n{df_t4a.head(10)}")

print("\n" + "=" * 80)
print("MVP SUBSET RECOMMENDATIONS")
print("=" * 80)

print("""
🎯 OPTION 1: Single Age Group, UK-Level (SIMPLEST MVP)
   Sheet: T1_UK12m
   Rows: 4 (England, Northern Ireland, Scotland, Wales)
   Vaccines: DTaP/IPV/Hib, PCV, Rotavirus, MenB
   ✅ Pros: Very small, easy to test all features
   ❌ Cons: Limited data for trends/filtering

🎯 OPTION 2: Single Age Group, UTLA-Level (RECOMMENDED MVP)  
   Sheet: T4a_UTLA12m or T4b_UTLA12m
   Rows: ~150 local authorities
   Vaccines: Multiple vaccines per child cohort
   ✅ Pros: Rich geographic filtering, sufficient data for summaries/trends
   ✅ Pros: Real-world scenario (researchers compare regions)
   ✅ Pros: Can demo grouping (by region, coverage ranges)

🎯 OPTION 3: All UK-Level Tables (MODERATE)
   Sheets: T1_UK12m, T2_UK24m, T3_UK5y
   Rows: 4 × 3 = 12 records
   ✅ Pros: Can compare across age groups (trends over time)
   ✅ Pros: Multiple cohorts for analysis
   ⚠️  Cons: Slightly more complex data loading

🎯 OPTION 4: Full Dataset (POST-MVP)
   All sheets
   ✅ Complete feature set
   ❌ Complex for MVP, harder to test thoroughly

RECOMMENDATION: Start with OPTION 2 (T4a_UTLA12m)
- Provides geographic diversity (~150 local authorities)
- Demonstrates all core features:
  ✓ Filtering (by region, vaccine type, coverage threshold)
  ✓ Summaries (mean coverage, min/max, by region)
  ✓ Visualizations (bar charts by region, coverage distributions)
  ✓ Export (filtered subsets)
- Manageable size for TDD approach
- Can expand to other age groups after MVP proven
""")

print("=" * 80)
