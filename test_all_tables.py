"""Quick test script to verify all table endpoints work."""

from src.database import get_session
from src.table_builder import TableBuilder

def main():
    session = get_session()
    tb = TableBuilder(session)

    print("=" * 60)
    print("Testing All Table Builder Methods")
    print("=" * 60)

    # Test Table 1 - UK by Country
    print("\n[1] Table 1: UK by Country (12 months)")
    result1 = tb.get_table1_uk_by_country('12 months', 2024)
    print(f"   - Title: {result1['title']}")
    print(f"   - Rows: {len(result1['data'])}")
    if result1['data']:
        print(f"   - Sample row keys: {list(result1['data'][0].keys())[:5]}...")

    # Test Table 4 - UTLA
    print("\n[2] Table 4: UTLA Coverage (12 months)")
    result4 = tb.get_utla_table('12 months', 2024)
    print(f"   - Rows: {len(result4)}")
    if result4:
        print(f"   - Sample row keys: {list(result4[0].keys())[:5]}...")

    # Test Table 7 - HepB
    print("\n[3] Table 7: Neonatal Hepatitis B")
    result7 = tb.get_hepb_table(2024)
    print(f"   - Title: {result7['title']}")
    print(f"   - Rows: {len(result7['data'])}")
    if result7['data']:
        print(f"   - Sample row keys: {list(result7['data'][0].keys())}")
        # Show a sample row with data
        for row in result7['data'][:3]:
            if row.get('coverage_12m') is not None:
                print(f"   - Sample: {row['local_authority']}: 12m={row['coverage_12m']}, 24m={row['coverage_24m']}")
                break

    # Test Table 8 - BCG
    print("\n[4] Table 8: BCG Coverage")
    result8 = tb.get_bcg_table(2024)
    print(f"   - Title: {result8['title']}")
    print(f"   - Rows: {len(result8['data'])}")
    if result8['data']:
        print(f"   - Sample row keys: {list(result8['data'][0].keys())}")
        # Show a sample row with data
        for row in result8['data'][:3]:
            # Check for any cohort data
            if any(k.startswith('coverage_') for k in row.keys()):
                cohort_keys = [k for k in row.keys() if k.startswith('coverage_')]
                print(f"   - Sample: {row['local_authority']}: {cohort_keys}")
                break

    print("\n" + "=" * 60)
    print("All table methods executed successfully!")
    print("=" * 60)

if __name__ == '__main__':
    main()
