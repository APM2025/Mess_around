"""Detailed test of Table 1 generation."""

from src.database import get_session
from src.table_builder import TableBuilder
import json

session = get_session()
tb = TableBuilder(session)

for cohort_name in ['12 months', '24 months', '5 years']:
    print(f"\n{'='*60}")
    print(f"Testing Table 1 for: {cohort_name}")
    print('='*60)

    result = tb.get_table1_uk_by_country(cohort_name, 2024)

    print(f"Title: {result['title']}")
    print(f"Number of rows: {len(result['data'])}")

    if result['data']:
        first_row = result['data'][0]
        print(f"\nColumns in first row ({len(first_row)} total):")
        for col_name in first_row.keys():
            value = first_row[col_name]
            print(f"  - {col_name}: {value}")

        print(f"\nAll column names:")
        print(list(first_row.keys()))

session.close()
