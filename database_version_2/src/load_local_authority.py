"""
Local Authority Coverage Data Loader

Loads local_authority_coverage fact table from PAIRED CSV sheets.

Source sheets (PAIRS - must process together):
- T4a_UTLA12m (%) + T4b_UTLA12m (numbers)
- T5a_UTLA24m (%) + T5b_UTLA24m (numbers)
- T6a_UTLA5y (%) + T6b_UTLA5y (numbers)

Expected records: ~2,086 (150 UTLAs × 3 cohorts × ~5 vaccines)

Requirements:
- DA-FR-001: Load from CSV
- DB-FR-001: Persist to database
- DC-FR-001: Handle suppressed data ([c], [z])
"""

import pandas as pd
from pathlib import Path
from typing import Tuple
from database_version_2.src.models import (
    LocalAuthorityCoverage, GeographicArea, Vaccine, AgeCohort, FinancialYear
)
from database_version_2.src.csv_cleaner import (
    load_cleaned_csv, extract_vaccine_name, clean_numeric_value
)


def load_local_authority_coverage_from_paired_csvs(
    percentages_csv: Path, 
    counts_csv: Path, 
    session
):
    """
    Load local authority coverage from paired CSV files
    
    Args:
        percentages_csv: Path to 'a' sheet (percentages)
        counts_csv: Path to 'b' sheet (counts)
        session: SQLAlchemy session
    
    """
    # Load both sheets
    df_pct = load_cleaned_csv(percentages_csv, sheet_type='utla')
    df_cnt = load_cleaned_csv(counts_csv, sheet_type='utla')
    
    if df_pct.empty or df_cnt.empty:
        return
    
    # Determine cohort from filename
    filename = percentages_csv.stem
    if '12m' in filename:
        cohort_months = 12
    elif '24m' in filename:
        cohort_months = 24
    elif '5y' in filename:
        cohort_months = 60
    else:
        raise ValueError(f"Cannot determine cohort from filename: {filename}")
    
    # Get cohort
    cohort = session.query(AgeCohort).filter_by(age_months=cohort_months).first()
    if not cohort:
        raise ValueError(f"Cohort {cohort_months} months not found")
    
    # Get current year
    year = session.query(FinancialYear).filter_by(year_start=2024).first()
    if not year:
        raise ValueError("Financial year 2024-2025 not found")
    
    # Column layout in UTLA sheets: Code | Name | Region | ODS Code | Eligible Pop | Vaccine Data...
    METADATA_COLUMNS = 4  # Skip: code, name, region, ods_code
    
    # Identify vaccine columns (both sheets should have same structure)
    vaccine_columns = []
    for col in df_pct.columns[METADATA_COLUMNS:]:  # Start after metadata
        vaccine_name = extract_vaccine_name(col)
        if vaccine_name and vaccine_name != '':
            vaccine_columns.append((col, vaccine_name))
    
    # Process each row (UTLA)
    for idx in range(min(len(df_pct), len(df_cnt))):
        row_pct = df_pct.iloc[idx]
        row_cnt = df_cnt.iloc[idx]
        
        # Get area code (should be first column or named 'area_code')
        area_code_col = 'area_code' if 'area_code' in df_pct.columns else df_pct.columns[0]
        area_code = row_pct[area_code_col]
        
        if not isinstance(area_code, str):
            continue
        
        # Skip if not a UTLA code (E06, E08, E09, E10)
        if not (area_code.startswith('E06') or area_code.startswith('E08') or 
                area_code.startswith('E09') or area_code.startswith('E10')):
            continue
        
        # Verify area exists in database
        area = session.query(GeographicArea).filter_by(area_code=area_code).first()
        if not area or area.area_type != 'utla':
            continue
        
        # Get eligible population (should be same in both sheets, around column 5)
        eligible_pop = None
        for col_idx in [4, 5]:  # Check columns 4-5
            if col_idx < len(df_pct.columns):
                val = clean_numeric_value(row_pct.iloc[col_idx])
                if val and val > 100:  # Population should be decent size
                    eligible_pop = val
                    break
        
        # Process each vaccine
        for col_name, vaccine_name in vaccine_columns:
            # Match header to canonical vaccine code
            from database_version_2.src.vaccine_matcher import match_vaccine_from_header
            
            vaccine_code = match_vaccine_from_header(col_name)
            if not vaccine_code:
                continue  # Skip if can't match header
            
            # Find vaccine in database using code (exact match)
            vaccine = session.query(Vaccine).filter_by(vaccine_code=vaccine_code).first()
            
            if not vaccine:
                continue
            
            # Get coverage percentage from 'a' sheet
            coverage_pct = None
            if col_name in row_pct.index:
                raw_pct = clean_numeric_value(row_pct[col_name], decimal_places=2)
                # Validate it's actually a percentage (0-100), not a count
                if raw_pct is not None and 0 <= raw_pct <= 100:
                    coverage_pct = raw_pct
            
            # Get vaccinated count from 'b' sheet
            vaccinated_count = None
            if col_name in row_cnt.index:
                vaccinated_count = clean_numeric_value(row_cnt[col_name])
            
            # Skip if both are None (fully suppressed)
            if coverage_pct is None and vaccinated_count is None:
                continue
            
            # Get or create coverage record
            existing = session.query(LocalAuthorityCoverage).filter_by(
                year_id=year.year_id,
                area_code=area_code,
                cohort_id=cohort.cohort_id,
                vaccine_id=vaccine.vaccine_id
            ).first()
            
            if existing:
                # Update
                existing.eligible_population = eligible_pop
                existing.vaccinated_count = vaccinated_count
                existing.coverage_percentage = coverage_pct
            else:
                # Create new
                coverage = LocalAuthorityCoverage(
                    year_id=year.year_id,
                    area_code=area_code,
                    cohort_id=cohort.cohort_id,
                    vaccine_id=vaccine.vaccine_id,
                    eligible_population=eligible_pop,
                    vaccinated_count=vaccinated_count,
                    coverage_percentage=coverage_pct
                )
                session.add(coverage)
    
    session.commit()


def load_all_local_authority_coverage(csv_dir: Path, session):
    """
    Load all local authority coverage sheet pairs
    
    Args:
        csv_dir: Directory containing CSV files
        session: SQLAlchemy session
    """
    csv_dir = Path(csv_dir)
    
    # Define sheet pairs
    sheet_pairs = [
        ('cover-anual-data-tables-2024-to-2025_T4a_UTLA12m.csv',
         'cover-anual-data-tables-2024-to-2025_T4b_UTLA12m.csv'),
        ('cover-anual-data-tables-2024-to-2025_T5a_UTLA24m.csv',
         'cover-anual-data-tables-2024-to-2025_T5b_UTLA24m.csv'),
        ('cover-anual-data-tables-2024-to-2025_T6a_UTLA5y.csv',
         'cover-anual-data-tables-2024-to-2025_T6b_UTLA5y.csv'),
    ]
    
    for pct_sheet, cnt_sheet in sheet_pairs:
        pct_path = csv_dir / pct_sheet
        cnt_path = csv_dir / cnt_sheet
        
        if pct_path.exists() and cnt_path.exists():
            print(f"Loading {pct_sheet} + {cnt_sheet}...")
            load_local_authority_coverage_from_paired_csvs(pct_path, cnt_path, session)
        else:
            print(f"Warning: {pct_sheet} or {cnt_sheet} not found")
    
    print("✓ Local authority coverage data loaded")
