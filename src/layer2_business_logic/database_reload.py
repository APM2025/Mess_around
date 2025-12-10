"""
Database Reload Service

Business logic for reloading all database data from CSV files.
Extracted from create_database.py for better testability and architecture.
"""

from pathlib import Path
from typing import Dict, Any

from src.layer1_database.models import (
    GeographicArea, Vaccine, AgeCohort, FinancialYear,
    LocalAuthorityCoverage, EnglandTimeSeries, NationalCoverage,
    RegionalTimeSeries, SpecialProgram
)

from src.layer0_data_ingestion.load_reference_data import (
    load_geographic_areas,
    load_vaccines,
    load_age_cohorts,
    load_financial_years
)


def reload_all_data(session, csv_path: Path = None, verbose: bool = True) -> Dict[str, Any]:
    """
    Reload all database data from CSV files.
    
    This function:
    1. Loads reference data (areas, vaccines, cohorts, years)
    2. Loads fact data from CSV files
    3. Returns summary statistics
    
    Args:
        session: SQLAlchemy database session
        csv_path: Path to CSV data directory (defaults to data/csv_data)
        verbose: Whether to print progress messages
        
    Returns:
        Dictionary with summary statistics:
        {
            'geographic_areas': int,
            'vaccines': int,
            'age_cohorts': int,
            'financial_years': int,
            'national_coverage': int,
            'la_coverage': int,
            'england_time_series': int,
            'regional_time_series': int,
            'special_programs': int,
            'warnings': list of str
        }
    """
    if csv_path is None:
        csv_path = Path("data/csv_data")
        
    warnings = []
    
    def log(message: str):
        """Print message if verbose mode is on."""
        if verbose:
            print(message)
    
    # Load reference data
    log("Loading reference data...")
    
    log("  - Loading geographic areas...")
    load_geographic_areas(session)
    area_count = session.query(GeographicArea).count()
    log(f"    [OK] Loaded {area_count} geographic areas")
    
    log("  - Loading vaccines...")
    load_vaccines(session)
    vaccine_count = session.query(Vaccine).count()
    log(f"    [OK] Loaded {vaccine_count} vaccines")
    
    log("  - Loading age cohorts...")
    load_age_cohorts(session)
    cohort_count = session.query(AgeCohort).count()
    log(f"    [OK] Loaded {cohort_count} age cohorts")
    
    log("  - Loading financial years...")
    load_financial_years(session)
    year_count = session.query(FinancialYear).count()
    log(f"    [OK] Loaded {year_count} financial years")
    
    # Initialize fact data counts
    nc_count = 0
    la_count = 0
    ts_count = 0
    rt_count = 0
    sp_count = 0
    
    # Load fact data from CSV files
    if csv_path.exists():
        log(f"CSV directory found: {csv_path}")
        csv_files = list(csv_path.glob("*.csv"))
        log(f"Found {len(csv_files)} CSV files")
        
        try:
            from src.load_national_coverage import load_all_national_coverage
            from src.load_local_authority import load_all_local_authority_coverage
            from src.load_england_time_series import load_all_england_time_series
            from src.load_regional_time_series import load_all_regional_time_series
            from src.load_special_programs import load_all_special_programs
            
            log("Loading fact data from CSV files...")
            
            # National coverage
            try:
                log("  - Loading national coverage data...")
                load_all_national_coverage(csv_path, session)
                nc_count = session.query(NationalCoverage).count()
                log(f"    [OK] Loaded {nc_count} national coverage records")
            except Exception as e:
                warning = f"National coverage not loaded: {str(e)[:100]}"
                warnings.append(warning)
                log(f"    [WARN] {warning}")
            
            # Local authority
            try:
                log("  - Loading local authority coverage data...")
                load_all_local_authority_coverage(csv_path, session)
                la_count = session.query(LocalAuthorityCoverage).count()
                log(f"    [OK] Loaded {la_count} local authority records")
            except Exception as e:
                warning = f"Local authority data not loaded: {str(e)[:100]}"
                warnings.append(warning)
                log(f"    [WARN] {warning}")
            
            # England time series
            try:
                log("  - Loading England time series data...")
                load_all_england_time_series(csv_path, session)
                ts_count = session.query(EnglandTimeSeries).count()
                log(f"    [OK] Loaded {ts_count} time series records")
            except Exception as e:
                warning = f"England time series not loaded: {str(e)[:100]}"
                warnings.append(warning)
                log(f"    [WARN] {warning}")
            
            # Regional time series
            try:
                log("  - Loading regional time series data...")
                load_all_regional_time_series(csv_path, session)
                rt_count = session.query(RegionalTimeSeries).count()
                log(f"    [OK] Loaded {rt_count} regional time series records")
            except Exception as e:
                warning = f"Regional time series not loaded: {str(e)[:100]}"
                warnings.append(warning)
                log(f"    [WARN] {warning}")
            
            # Special programs
            try:
                log("  - Loading special programs (HepB, BCG)...")
                load_all_special_programs(csv_path, session)
                sp_count = session.query(SpecialProgram).count()
                log(f"    [OK] Loaded {sp_count} special program records")
            except Exception as e:
                warning = f"Special programs not loaded: {str(e)[:100]}"
                warnings.append(warning)
                log(f"    [WARN] {warning}")
                
        except ImportError as e:
            warning = f"CSV loaders not fully configured: {str(e)[:100]}"
            warnings.append(warning)
            log(f"  [WARN] {warning}")
    else:
        warning = f"CSV directory not found: {csv_path}"
        warnings.append(warning)
        log(f"  [WARN] {warning}")
    
    # Return summary
    return {
        'geographic_areas': area_count,
        'vaccines': vaccine_count,
        'age_cohorts': cohort_count,
        'financial_years': year_count,
        'national_coverage': nc_count,
        'la_coverage': la_count,
        'england_time_series': ts_count,
        'regional_time_series': rt_count,
        'special_programs': sp_count,
        'warnings': warnings
    }
