"""
National Coverage Data Loader

Loads national_coverage fact table from T1, T2, T3 CSV sheets.

Source sheets:
- T1_UK12m: UK countries, 12 month cohort
- T2_UK24m: UK countries, 24 month cohort  
- T3_UK5y: UK countries, 5 year cohort

Expected records: ~70 (4 countries × 3 cohorts × ~6 vaccines)

Requirements:
- DA-FR-001: Load from CSV
- DB-FR-001: Persist to database
- DC-FR-001: Handle missing data
"""

import pandas as pd
from pathlib import Path
from typing import List
from database_version_2.src.models import (
    NationalCoverage, GeographicArea, Vaccine, AgeCohort, FinancialYear
)
from database_version_2.src.csv_cleaner import (
    load_cleaned_csv, extract_vaccine_name, clean_numeric_value, parse_note_reference
)


def load_national_coverage_from_csv(csv_path: Path, session):
    """
    Load national coverage data from a single CSV file (T1, T2, or T3)
    
    Args:
        csv_path: Path to CSV file
        session: SQLAlchemy session
    
    """
    # Load cleaned CSV
    df = load_cleaned_csv(csv_path, sheet_type='national')
    
    if df.empty:
        return
    
    # Determine cohort from filename
    # T1_UK12m → 12 months, T2_UK24m → 24 months, T3_UK5y → 60 months
    filename = csv_path.stem
    if '12m' in filename:
        cohort_months = 12
    elif '24m' in filename:
        cohort_months = 24
    elif '5y' in filename:
        cohort_months = 60
    else:
        raise ValueError(f"Cannot determine cohort from filename: {filename}")
    
    # Get cohort from database
    cohort = session.query(AgeCohort).filter_by(age_months=cohort_months).first()
    if not cohort:
        raise ValueError(f"Cohort {cohort_months} months not found in database")
    
    # Get current year (2024-2025)
    year = session.query(FinancialYear).filter_by(year_start=2024).first()
    if not year:
        raise ValueError("Financial year 2024-2025 not found in database")
    
    # Column layout in national sheets: Area Name | Notes | Eligible Pop | Vaccine Data...
    METADATA_COLUMNS = 3  # Skip: area, notes, population
    
    # Identify vaccine columns (skip first few meta columns)
    vaccine_columns = []
    for col in df.columns[METADATA_COLUMNS:]:  # Start after metadata
        vaccine_name = extract_vaccine_name(col)
        if vaccine_name and vaccine_name != '':
            vaccine_columns.append((col, vaccine_name))
    
    # Get country name to area_code mapping
    country_map = {
        'United Kingdom': 'K02000001',
        'England': 'E92000001',
        'Scotland': 'S92000003',
        'Wales': 'W92000004',
        'Northern Ireland': 'N92000002'
    }
    
    # Process each row (country)
    for idx, row in df.iterrows():
        # Get area
        area_name_col = 'area_name' if 'area_name' in df.columns else df.columns[0]
        area_name = row[area_name_col]
        
        if not isinstance(area_name, str):
            continue
        
        area_code = country_map.get(area_name)
        if not area_code:
            continue  # Skip non-country rows
        
        # Verify area exists in database
        area = session.query(GeographicArea).filter_by(area_code=area_code).first()
        if not area:
            continue  # Skip if area not in reference data
        
        # Get eligible population (usually column 2 or 3)
        eligible_pop = None
        for col in df.columns[2:5]:  # Check first few columns
            val = clean_numeric_value(row[col])
            if val and val > 1000:  # Population should be large
                eligible_pop = val
                break
        
        # Process each vaccine column
        for col_name, vaccine_name in vaccine_columns:
            # Match header to canonical vaccine code
            from database_version_2.src.vaccine_matcher import match_vaccine_from_header
            
            vaccine_code = match_vaccine_from_header(col_name)
            if not vaccine_code:
                continue  # Skip if can't match header
            
            # Find vaccine in database using code (exact match)
            vaccine = session.query(Vaccine).filter_by(vaccine_code=vaccine_code).first()
            
            if not vaccine:
                continue  # Skip if vaccine not in reference data
            
            # Get coverage percentage
            coverage_value = row[col_name]
            coverage_pct = clean_numeric_value(coverage_value, decimal_places=2)
            
            # Get or create coverage record
            existing = session.query(NationalCoverage).filter_by(
                year_id=year.year_id,
                area_code=area_code,
                cohort_id=cohort.cohort_id,
                vaccine_id=vaccine.vaccine_id
            ).first()
            
            if existing:
                # Update
                existing.eligible_population = eligible_pop
                existing.coverage_percentage = coverage_pct
            else:
                # Create new
                coverage = NationalCoverage(
                    year_id=year.year_id,
                    area_code=area_code,
                    cohort_id=cohort.cohort_id,
                    vaccine_id=vaccine.vaccine_id,
                    eligible_population=eligible_pop,
                    coverage_percentage=coverage_pct
                )
                session.add(coverage)
    
    session.commit()


def load_all_national_coverage(csv_dir: Path, session):
    """
    Load all national coverage sheets (T1, T2, T3)
    
    Args:
        csv_dir: Directory containing CSV files
        session: SQLAlchemy session
    """
    csv_dir = Path(csv_dir)
    
    # Find T1, T2, T3 sheets
    sheets = [
        'cover-anual-data-tables-2024-to-2025_T1_UK12m.csv',
        'cover-anual-data-tables-2024-to-2025_T2_UK24m.csv',
        'cover-anual-data-tables-2024-to-2025_T3_UK5y.csv'
    ]
    
    for sheet_name in sheets:
        csv_path = csv_dir / sheet_name
        if csv_path.exists():
            print(f"Loading {sheet_name}...")
            load_national_coverage_from_csv(csv_path, session)
        else:
            print(f"Warning: {sheet_name} not found")
    
    print("✓ National coverage data loaded")
