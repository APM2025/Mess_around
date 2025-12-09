"""
Manual test script to verify analyzer works with real data.

NOTE: This script requires a populated database at data/vaccination_coverage.db
Run the database loaders first to populate data before running this script.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database_version_2.src.database import get_session
from database_version_2.src.fs_analysis import VaccinationAnalyzer

try:
    session = get_session()
    analyzer = VaccinationAnalyzer(session)

    print("=" * 60)
    print("MANUAL TEST: Filtering & Analysis Module")
    print("=" * 60)

    # Test 1: Filter data
    print("\n1. Filter MMR1 data for UTLAs:")
    data = analyzer.filter_data(vaccine_code='MMR1', cohort_name='24 months')
    print(f"   Found {len(data)} records")
    if data:
        print(f"   Sample: {data[0]}")
    else:
        print("   WARNING: No data found. Database may be empty.")

    # Test 2: Summary stats
    if data:
        print("\n2. Summary statistics:")
        stats = analyzer.get_summary(data)
        print(f"   Count: {stats['count']}")
        print(f"   Mean: {stats['mean']}%")
        print(f"   Min: {stats['min']}%")
        print(f"   Max: {stats['max']}%")

        # Test 3: Top areas
        print("\n3. Top 5 performing areas:")
        top_5 = analyzer.get_top_areas('MMR1', n=5, cohort_name='24 months')
        for i, area in enumerate(top_5, 1):
            print(f"   {i}. {area['area_name']}: {area['coverage']}%")

        # Test 4: Trend
        print("\n4. England trend (last 5 years):")
        trend = analyzer.get_trend('MMR1', cohort_name='24 months')
        if trend:
            for point in trend[-5:]:
                print(f"   {point['year']}: {point['coverage']}%")
        else:
            print("   No trend data available")

    print("\n" + "=" * 60)
    print("All manual tests complete")
    print("=" * 60)

except FileNotFoundError:
    print("ERROR: Database file not found.")
    print("Please populate the database first using the data loaders.")
except Exception as e:
    print(f"ERROR: {e}")
    print("Ensure database is properly initialized with data.")
