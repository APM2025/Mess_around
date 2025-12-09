"""
England Time Series Data Loader

Loads historical England coverage data (2009-2025) into england_time_series table.

Source sheets:
- T9_Eng12m: 12 month cohort
- T10_Eng24m: 24 month cohort
- T11_Eng5y: 5 year cohort

Expected records: ~205

Requirements:
- DA-FR-001: Load from CSV
- DB-FR-001: Persist to database
- DC-FR-001: Handle missing data
"""

import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from backend_code.database_src.models import (
    EnglandTimeSeries, Vaccine, AgeCohort, FinancialYear
)
from backend_code.database_src.csv_cleaner import (
    load_cleaned_csv, clean_numeric_value
)
from backend_code.database_src.vaccine_reference import match_vaccine_from_header


def load_england_time_series_from_csv(csv_path: Path, session: Session) -> None:
    """
    Load England time series from a single CSV file
    
    Args:
        csv_path: Path to T9/T10/T11 CSV file
        session: SQLAlchemy session
    """
    # Load cleaned CSV - TIME SERIES type (different structure!)
    df = load_cleaned_csv(csv_path, sheet_type='time_series')
    
    if df.empty:
        return
    
    # Determine cohort from filename using utility
    from backend_code.database_src.loader_utils import determine_cohort_from_filename, get_cohort
    
    cohort_months = determine_cohort_from_filename(csv_path)
    cohort = get_cohort(session, cohort_months)
    if not cohort:
        raise ValueError(f"Cohort {cohort_months} months not found")
    
    # Column layout: Financial Year | Vaccine columns...
    METADATA_COLUMNS = 1  # Just the year column
    
    # Identify vaccine columns
    vaccine_columns = []
    for col in df.columns[METADATA_COLUMNS:]:
        vaccine_code = match_vaccine_from_header(col)
        if vaccine_code:
            vaccine_columns.append((col, vaccine_code))
    
    # Process each row (year)
    for idx, row in df.iterrows():
        # Get year label (e.g., "2009 to 2010")
        year_col = df.columns[0]
        year_label = str(row[year_col])
        
        # Skip non-year rows
        if not (' to ' in year_label or '-' in year_label):
            continue
        
        # Normalize year format: "2009 to 2010" → "2009-2010"
        if ' to ' in year_label:
            parts = year_label.split(' to ')
            if len(parts) == 2:
                year_label = f"{parts[0].strip()}-{parts[1].strip()}"
        
        # Find financial year in database
        year = session.query(FinancialYear).filter_by(year_label=year_label).first()
        if not year:
            continue  # Skip years not in reference data
        
        # Process each vaccine
        for col_name, vaccine_code in vaccine_columns:
            # Get vaccine from database
            vaccine = session.query(Vaccine).filter_by(vaccine_code=vaccine_code).first()
            if not vaccine:
                continue
            
            # Get coverage percentage
            coverage_value = row[col_name]
            coverage_pct = clean_numeric_value(coverage_value, decimal_places=2)
            
            # Validate percentage range
            if coverage_pct is not None and not (0 <= coverage_pct <= 100):
                continue  # Skip invalid values
            
            # Check if record exists
            existing = session.query(EnglandTimeSeries).filter_by(
                year_id=year.year_id,
                cohort_id=cohort.cohort_id,
                vaccine_id=vaccine.vaccine_id
            ).first()
            
            if existing:
                # Update
                existing.coverage_percentage = coverage_pct
            else:
                # Create new
                record = EnglandTimeSeries(
                    year_id=year.year_id,
                    cohort_id=cohort.cohort_id,
                    vaccine_id=vaccine.vaccine_id,
                    coverage_percentage=coverage_pct
                )
                session.add(record)
    
    session.commit()


def load_all_england_time_series(csv_dir: Path, session: Session) -> None:
    """
    Load all England time series sheets
    
    Args:
        csv_dir: Directory containing CSV files
        session: SQLAlchemy session
    """
    csv_dir = Path(csv_dir)
    
    sheets = [
        'cover-anual-data-tables-2024-to-2025_T9_Eng12m.csv',
        'cover-anual-data-tables-2024-to-2025_T10_Eng24m.csv',
        'cover-anual-data-tables-2024-to-2025_T11_Eng5y.csv'
    ]
    
    for sheet_name in sheets:
        csv_path = csv_dir / sheet_name
        if csv_path.exists():
            print(f"Loading {sheet_name}...")
            load_england_time_series_from_csv(csv_path, session)
        else:
            print(f"Warning: {sheet_name} not found")
    
    print("England time series data loaded")
