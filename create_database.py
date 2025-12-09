"""
Database Creation and Population Script

This script:
1. Creates the database schema
2. Loads all reference data
3. Loads fact data from CSV files
4. Verifies the data was loaded correctly
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database_version_2.src.database import get_session
from database_version_2.src.models import (
    GeographicArea, Vaccine, AgeCohort, FinancialYear,
    LocalAuthorityCoverage, EnglandTimeSeries
)

# Import loaders
from database_version_2.src.load_reference_data import (
    load_geographic_areas,
    load_vaccines,
    load_age_cohorts,
    load_financial_years
)


def main():
    """Create and populate the database."""
    print("=" * 70)
    print("DATABASE CREATION AND POPULATION")
    print("=" * 70)

    # Step 1: Create session (this creates the database if it doesn't exist)
    print("\n[1/5] Creating database schema...")
    session = get_session()
    print("    [OK] Database created at: data/vaccination_coverage.db")

    # Step 2: Load reference data
    print("\n[2/5] Loading reference data...")

    print("    - Loading geographic areas (countries, regions, UTLAs)...")
    load_geographic_areas(session)
    area_count = session.query(GeographicArea).count()
    print(f"      [OK] Loaded {area_count} geographic areas")

    print("    - Loading vaccines...")
    load_vaccines(session)
    vaccine_count = session.query(Vaccine).count()
    print(f"      [OK] Loaded {vaccine_count} vaccines")

    print("    - Loading age cohorts...")
    load_age_cohorts(session)
    cohort_count = session.query(AgeCohort).count()
    print(f"      [OK] Loaded {cohort_count} age cohorts")

    print("    - Loading financial years...")
    load_financial_years(session)
    year_count = session.query(FinancialYear).count()
    print(f"      [OK] Loaded {year_count} financial years")

    # Step 3: Check for CSV data loaders
    print("\n[3/5] Checking for CSV data files...")
    csv_path = Path("data/csv_data")
    if csv_path.exists():
        print(f"    [OK] CSV directory found: {csv_path}")
        csv_files = list(csv_path.glob("*.csv"))
        print(f"    Found {len(csv_files)} CSV files")

        # Try to load CSV data
        try:
            from database_version_2.src.load_local_authority import load_all_local_authority_coverage
            from database_version_2.src.load_england_time_series import load_all_england_time_series

            print("\n[4/5] Loading fact data from CSV files...")

            # Load local authority data
            try:
                print("    - Loading local authority coverage data...")
                load_all_local_authority_coverage(csv_path, session)
                la_count = session.query(LocalAuthorityCoverage).count()
                print(f"      [OK] Loaded {la_count} local authority records")
            except Exception as e:
                print(f"      [WARN] Local authority data not loaded: {str(e)[:100]}")

            # Load England time series
            try:
                print("    - Loading England time series data...")
                load_all_england_time_series(csv_path, session)
                ts_count = session.query(EnglandTimeSeries).count()
                print(f"      [OK] Loaded {ts_count} time series records")
            except Exception as e:
                print(f"      [WARN] England time series not loaded: {str(e)[:100]}")

        except ImportError as e:
            print(f"    [WARN] CSV loaders not fully configured: {str(e)[:100]}")
            print("    Reference data loaded successfully, but CSV fact data skipped")
    else:
        print(f"    [WARN] CSV directory not found: {csv_path}")
        print("    Reference data loaded, but CSV fact data skipped")

    # Step 5: Summary
    print("\n[5/5] Database Summary:")
    print("-" * 70)
    print(f"    Geographic Areas:     {session.query(GeographicArea).count()}")
    print(f"    Vaccines:             {session.query(Vaccine).count()}")
    print(f"    Age Cohorts:          {session.query(AgeCohort).count()}")
    print(f"    Financial Years:      {session.query(FinancialYear).count()}")
    print(f"    LA Coverage Records:  {session.query(LocalAuthorityCoverage).count()}")
    print(f"    England Time Series:  {session.query(EnglandTimeSeries).count()}")

    session.close()

    print("\n" + "=" * 70)
    print("DATABASE CREATION COMPLETE!")
    print("=" * 70)
    print("\nYou can now run: python scripts/test_analysis.py")
    print()


if __name__ == "__main__":
    main()
