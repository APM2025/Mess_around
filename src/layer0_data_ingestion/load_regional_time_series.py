"""
Regional Time Series Data Loader

Loads regional coverage data over time (2009-2025) into regional_time_series table.

Source sheets:
- T14_RegDTaP24m: DTaP coverage by region
- T15_RegMMR24m: MMR coverage by region

Structure: Years in rows, regions in columns (different from other CSVs!)

Expected records: ~150

Requirements:
- DA-FR-001: Load from CSV
- DB-FR-001: Persist to database
- DC-FR-001: Handle missing data
"""

import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from src.layer1_database.models import (
    RegionalTimeSeries, Vaccine, AgeCohort, FinancialYear, GeographicArea
)
from src.layer0_data_ingestion.csv_cleaner import clean_numeric_value
from src.layer0_data_ingestion.vaccine_matcher import match_vaccine_from_header


def load_regional_time_series_from_csv(csv_path: Path, session: Session) -> None:
    """
    Load regional time series from a single CSV file
    
    Args:
        csv_path: Path to T14/T15 CSV file
        session: SQLAlchemy session
        
    Note: These CSVs have a unique structure:
        - Years in ROWS (first column)
        - Regions in COLUMNS (England, North East, North West, etc.)
        - Each file is for ONE vaccine
    """
    # Use type-aware CSV cleaner
    from src.layer0_data_ingestion.csv_cleaner import load_cleaned_csv_typed
    
    df, region_columns, csv_type = load_cleaned_csv_typed(csv_path)
    
    if df.empty:
        print(f"  No data rows found")
        return
    
    # Determine vaccine from filename
    filename = csv_path.stem
    if 'DTaP' in filename or 'T14' in filename:
        vaccine = session.query(Vaccine).filter_by(vaccine_code='DTaP_IPV_Hib_HepB').first()
    elif 'MMR' in filename or 'T15' in filename:
        vaccine = session.query(Vaccine).filter_by(vaccine_code='MMR1').first()
    else:
        raise ValueError(f"Cannot determine vaccine from filename: {filename}")
    
    if not vaccine:
        print(f"  ERROR: Vaccine not found for {filename}")
        return
    
    print(f"  Vaccine: {vaccine.vaccine_code} (ID: {vaccine.vaccine_id})")
    
    # Determine cohort from filename
    if '24m' in filename:
        cohort_months = 24
    elif '12m' in filename:
        cohort_months = 12
    elif '5y' in filename:
        cohort_months = 60
    else:
        raise ValueError(f"Cannot determine cohort from filename: {filename}")
    
    # Get cohort
    cohort = session.query(AgeCohort).filter_by(age_months=cohort_months).first()
    if not cohort:
        raise ValueError(f"Cohort {cohort_months} months not found")
    
    # Column layout: Financial year | Notes | Region columns...
    year_col = df.columns[0]  # "Financial year"
    
    records_created = 0
    records_updated = 0
    
    for idx, row in df.iterrows():
        # Get year label
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
        
        # Process each region column from the cleaner
        for region_col in region_columns:
            region_name = region_col['region_name']
            col_idx = region_col['col_idx']
            
            # Find geographic area by name
            area = session.query(GeographicArea).filter_by(
                area_name=region_name,
                area_type='region'
            ).first()
            
            # Also check for "England" (country, not region)
            if not area and region_name == 'England':
                area = session.query(GeographicArea).filter_by(
                    area_name='England',
                    area_type='country'
                ).first()
            
            if not area:
                continue  # Skip unknown regions
            
            # Get coverage percentage from the correct column
            coverage_value = row.iloc[col_idx]
            coverage_pct = clean_numeric_value(coverage_value, decimal_places=2)
            
            # Validate percentage range
            if coverage_pct is not None and not (0 <= coverage_pct <= 100):
                continue
            
            # Check if record exists
            existing = session.query(RegionalTimeSeries).filter_by(
                year_id=year.year_id,
                area_code=area.area_code,
                cohort_id=cohort.cohort_id,
                vaccine_id=vaccine.vaccine_id
            ).first()
            
            if existing:
                # Update
                existing.coverage_percentage = coverage_pct
                records_updated += 1
            else:
                # Create new
                record = RegionalTimeSeries(
                    year_id=year.year_id,
                    area_code=area.area_code,
                    cohort_id=cohort.cohort_id,
                    vaccine_id=vaccine.vaccine_id,
                    coverage_percentage=coverage_pct
                )
                session.add(record)
                records_created += 1
    
    print(f"  Created: {records_created} | Updated: {records_updated}")
    session.commit()


def load_all_regional_time_series(csv_dir: Path, session: Session) -> None:
    """
    Load all regional time series sheets
    
    Args:
        csv_dir: Directory containing CSV files
        session: SQLAlchemy session
    """
    csv_dir = Path(csv_dir)
    
    sheets = [
        'cover-anual-data-tables-2024-to-2025_T14_RegDTaP24m.csv',
        'cover-anual-data-tables-2024-to-2025_T15_RegMMR24m.csv'
    ]
    
    for sheet_name in sheets:
        csv_path = csv_dir / sheet_name
        if csv_path.exists():
            load_regional_time_series_from_csv(csv_path, session)
            
            # Commit after each file
            session.commit()
            
            # Check what was loaded
            total = session.query(RegionalTimeSeries).count()
            vaccines = session.query(RegionalTimeSeries.vaccine_id).distinct().count()
            print(f"   After {sheet_name}: {total} records, {vaccines} vaccine(s)")
        else:
            print(f"Warning: {sheet_name} not found")
    
    print("\n[COMPLETE] Regional time series data loaded")
