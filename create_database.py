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

from src.layer1_database.database import get_session
from src.layer1_database.models import (
    GeographicArea, Vaccine, AgeCohort, FinancialYear,
    LocalAuthorityCoverage, EnglandTimeSeries, NationalCoverage,
    RegionalTimeSeries, SpecialProgram
)

# Import loaders
from src.layer0_data_ingestion.load_reference_data import (
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
            from src.load_national_coverage import load_all_national_coverage
            from src.load_local_authority import load_all_local_authority_coverage
            from src.load_england_time_series import load_all_england_time_series
            from src.load_regional_time_series import load_all_regional_time_series
            from src.load_special_programs import load_all_special_programs

            print("\n[4/5] Loading fact data from CSV files...")

            # Load national coverage (UK + 4 countries)
            try:
                print("    - Loading national coverage data (UK + countries)...")
                load_all_national_coverage(csv_path, session)
                nc_count = session.query(NationalCoverage).count()
                print(f"      [OK] Loaded {nc_count} national coverage records")
            except Exception as e:
                print(f"      [WARN] National coverage not loaded: {str(e)[:100]}")

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

            # Load regional time series
            try:
                print("    - Loading regional time series data...")
                load_all_regional_time_series(csv_path, session)
                rt_count = session.query(RegionalTimeSeries).count()
                print(f"      [OK] Loaded {rt_count} regional time series records")
            except Exception as e:
                print(f"      [WARN] Regional time series not loaded: {str(e)[:100]}")

            # Load special programs (HepB and BCG)
            try:
                print("    - Loading special programs (HepB, BCG)...")
                load_all_special_programs(csv_path, session)
                sp_count = session.query(SpecialProgram).count()
                print(f"      [OK] Loaded {sp_count} special program records")
            except Exception as e:
                print(f"      [WARN] Special programs not loaded: {str(e)[:100]}")

        except ImportError as e:
            print(f"    [WARN] CSV loaders not fully configured: {str(e)[:100]}")
            print("    Reference data loaded successfully, but CSV fact data skipped")
    else:
        print(f"    [WARN] CSV directory not found: {csv_path}")
        print("    Reference data loaded, but CSV fact data skipped")

    # Step 5: Summary
    print("\n[5/5] Database Summary:")
    print("-" * 70)
    print(f"    Geographic Areas:       {session.query(GeographicArea).count()}")
    print(f"    Vaccines:               {session.query(Vaccine).count()}")
    print(f"    Age Cohorts:            {session.query(AgeCohort).count()}")
    print(f"    Financial Years:        {session.query(FinancialYear).count()}")
    print(f"    National Coverage:      {session.query(NationalCoverage).count()}")
    print(f"    LA Coverage Records:    {session.query(LocalAuthorityCoverage).count()}")
    print(f"    England Time Series:    {session.query(EnglandTimeSeries).count()}")
    print(f"    Regional Time Series:   {session.query(RegionalTimeSeries).count()}")
    print(f"    Special Programs:       {session.query(SpecialProgram).count()}")

    session.close()

    print("\n" + "=" * 70)
    print("DATABASE CREATION COMPLETE!")
    print("=" * 70)
    print("\nYou can now run: python scripts/test_analysis.py")
    print()


if __name__ == "__main__":
    main()
