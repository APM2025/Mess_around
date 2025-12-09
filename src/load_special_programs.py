"""
Special Programs Data Loader

Loads special vaccination program data (HepB, BCG) into special_programs table.

Source sheets:
- T7_UTLAHepB: Hepatitis B vaccination for eligible children
- T8_UTLABCG: BCG vaccination for eligible children

Structure: UTLA-level coverage data for specific eligible populations

Expected records: ~300 per program

Requirements:
- DA-FR-001: Load from CSV
- DB-FR-001: Persist to database
- DC-FR-001: Handle missing data
"""

import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from src.models import (
    SpecialProgram, Vaccine, AgeCohort, FinancialYear, GeographicArea
)
from src.csv_cleaner import clean_numeric_value
from src.vaccine_matcher import match_vaccine_from_header


def load_special_programs_from_csv(csv_path: Path, session: Session) -> None:
    """
    Load special programs from a single CSV file
    
    Args:
        csv_path: Path to T7/T8 CSV file
        session: SQLAlchemy session
    """
    # Determine program type and header row from filename
    filename = csv_path.stem
    
    if 'HepB' in filename or 'T7' in filename:
        program_type = 'HepB'
        vaccine_code = 'HepB'
        header_row = 10  # T7 header at row 10
    elif 'BCG' in filename or 'T8' in filename:
        program_type = 'BCG'
        vaccine_code = 'BCG'
        header_row = 8  # T8 header at row 8
    else:
        raise ValueError(f"Cannot determine program type from filename: {filename}")
    
    print(f"\n[Special Program: {program_type}] {csv_path.name}")
    print(f"  Header row: {header_row}")
    
    # Read CSV with correct header
    df = pd.read_csv(csv_path, header=header_row)
    
    if df.empty:
        print(f"  No data rows found")
        return
    
    # Filter to data rows (area codes only)
    import re
    df_filtered = df[df.iloc[:, 0].apply(
        lambda x: bool(re.match(r'^[ESWN]\d{8}', str(x).strip())) if pd.notna(x) else False
    )].copy()
    
    print(f"  Rows: {len(df)} -> {len(df_filtered)} (filtered)")
    
    # Get vaccine
    vaccine = session.query(Vaccine).filter_by(vaccine_code=vaccine_code).first()
    if not vaccine:
        print(f"  ERROR: Vaccine {vaccine_code} not found")
        return
    
    print(f"  Vaccine: {vaccine.vaccine_code} (ID: {vaccine.vaccine_id})")
    
    # Get year (2024-2025)
    year = session.query(FinancialYear).filter_by(year_label='2024-2025').first()
    if not year:
        raise ValueError("Year 2024-2025 not found")
    
    # Find vaccine columns - HepB/BCG have 12m and 24m cohorts
    vaccine_columns = []
    for col_idx, col_name in enumerate(df.columns):
        col_str = str(col_name)
        
        # Look for "Coverage at X months" pattern
        if 'Coverage at' in col_str and '(%)' in col_str:
            # Extract cohort
            if '12 months' in col_str:
                cohort_months = 12
            elif '24 months' in col_str:
                cohort_months = 24
            else:
                continue
            
            # Get eligible and vaccinated column indices
            # Pattern: "Number aged X months eligible", "Number aged X months vaccinated", "Coverage at X months (%)"
            eligible_col = None
            vaccinated_col = None
            
            # Search backwards for eligible/vaccinated columns
            for i in range(col_idx - 1, max(0, col_idx - 3), -1):
                if 'eligible' in str(df.columns[i]).lower():
                    eligible_col = i
                if 'vaccinated' in str(df.columns[i]).lower():
                    vaccinated_col = i
            
            vaccine_columns.append({
                'cohort_months': cohort_months,
                'coverage_col': col_idx,
                'eligible_col': eligible_col,
                'vaccinated_col': vaccinated_col
            })
    
    print(f"  Found {len(vaccine_columns)} cohort columns")
    
    records_created = 0
    records_updated = 0
    
    # Process each row
    for idx, row in df_filtered.iterrows():
        area_code = str(row.iloc[0]).strip()
        
        # Lookup area
        area = session.query(GeographicArea).filter_by(area_code=area_code).first()
        if not area:
            continue
        
        # Process each cohort
        for vac_col in vaccine_columns:
            cohort_months = vac_col['cohort_months']
            
            # Get cohort
            cohort = session.query(AgeCohort).filter_by(age_months=cohort_months).first()
            if not cohort:
                continue
            
            # Get values
            eligible_pop = None if vac_col['eligible_col'] is None else clean_numeric_value(row.iloc[vac_col['eligible_col']])
            vaccinated = None if vac_col['vaccinated_col'] is None else clean_numeric_value(row.iloc[vac_col['vaccinated_col']])
            coverage_pct = clean_numeric_value(row.iloc[vac_col['coverage_col']], decimal_places=2)
            
            # Validate coverage percentage
            if coverage_pct is not None and not (0 <= coverage_pct <= 100):
                continue
            
            # Check if record exists
            existing = session.query(SpecialProgram).filter_by(
                year_id=year.year_id,
                area_code=area.area_code,
                cohort_id=cohort.cohort_id,
                program_type=program_type
            ).first()
            
            if existing:
                # Update
                existing.eligible_population = eligible_pop
                existing.vaccinated_count = vaccinated
                existing.coverage_percentage = coverage_pct
                records_updated += 1
            else:
                # Create new
                record = SpecialProgram(
                    year_id=year.year_id,
                    area_code=area.area_code,
                    cohort_id=cohort.cohort_id,
                    program_type=program_type,
                    eligible_population=eligible_pop,
                    vaccinated_count=vaccinated,
                    coverage_percentage=coverage_pct
                )
                session.add(record)
                records_created += 1
    
    print(f"  Created: {records_created} | Updated: {records_updated}")
    session.commit()


def load_all_special_programs(csv_dir: Path, session: Session) -> None:
    """
    Load all special programs sheets
    
    Args:
        csv_dir: Directory containing CSV files
        session: SQLAlchemy session
    """
    csv_dir = Path(csv_dir)
    
    sheets = [
        'cover-anual-data-tables-2024-to-2025_T7_UTLAHepB.csv',
        'cover-anual-data-tables-2024-to-2025_T8_UTLABCG.csv'
    ]
    
    for sheet_name in sheets:
        csv_path = csv_dir / sheet_name
        if csv_path.exists():
            load_special_programs_from_csv(csv_path, session)
        else:
            print(f"Warning: {sheet_name} not found")
    
    print("\n[COMPLETE] Special programs data loaded")

