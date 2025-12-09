"""
Load Reference Data

Functions to load dimension/reference tables for the vaccination database.

Reference tables:
- geographic_areas (163): Countries, regions, UTLAs
- vaccines (11): From canonical list
- age_cohorts (4): 12m, 24m, 5y, 3m
- financial_years (17): 2009-2025
"""

from database_version_2.src.models import (
    GeographicArea, Vaccine, AgeCohort, FinancialYear
)


# =============================================================================
# GEOGRAPHIC AREAS (163 total: 4 countries + 9 regions + 150 UTLAs)
# =============================================================================

def load_geographic_areas(session):
    """
    Load all 163 geographic areas (countries, regions, UTLAs)
    
    UTLAs are extracted from real CSV data.
    
    Args:
        session: SQLAlchemy session
    """
    # Countries (4)
    countries = [
        {'area_code': 'E92000001', 'area_name': 'England', 'area_type': 'country', 'parent_region_code': None},
        {'area_code': 'S92000003', 'area_name': 'Scotland', 'area_type': 'country', 'parent_region_code': None},
        {'area_code': 'W92000004', 'area_name': 'Wales', 'area_type': 'country', 'parent_region_code': None},
        {'area_code': 'N92000002', 'area_name': 'Northern Ireland', 'area_type': 'country', 'parent_region_code': None},
    ]
    
    # Regions (9) - NHS England regions
    regions = [
        {'area_code': 'E12000001', 'area_name': 'North East', 'area_type': 'region', 'parent_region_code': 'E92000001'},
        {'area_code': 'E12000002', 'area_name': 'North West', 'area_type': 'region', 'parent_region_code': 'E92000001'},
        {'area_code': 'E12000003', 'area_name': 'Yorkshire and The Humber', 'area_type': 'region', 'parent_region_code': 'E92000001'},
        {'area_code': 'E12000004', 'area_name': 'East Midlands', 'area_type': 'region', 'parent_region_code': 'E92000001'},
        {'area_code': 'E12000005', 'area_name': 'West Midlands', 'area_type': 'region', 'parent_region_code': 'E92000001'},
        {'area_code': 'E12000006', 'area_name': 'East of England', 'area_type': 'region', 'parent_region_code': 'E92000001'},
        {'area_code': 'E12000007', 'area_name': 'London', 'area_type': 'region', 'parent_region_code': 'E92000001'},
        {'area_code': 'E12000008', 'area_name': 'South East', 'area_type': 'region', 'parent_region_code': 'E92000001'},
        {'area_code': 'E12000009', 'area_name': 'South West', 'area_type': 'region', 'parent_region_code': 'E92000001'},
    ]
    
    # UTLAs (150) - Extract from T4a CSV
    utlas = []
    
    from pathlib import Path
    import pandas as pd
    from database_version_2.src.csv_cleaner import load_cleaned_csv
    
    csv_path = Path("data/csv_data/cover-anual-data-tables-2024-to-2025_T4a_UTLA12m.csv")
    
    if csv_path.exists():
        try:
            df = load_cleaned_csv(csv_path, sheet_type='utla')
            
            for idx, row in df.iterrows():
                area_code_col = 'area_code' if 'area_code' in df.columns else df.columns[0]
                area_code = row[area_code_col]
                
                if not isinstance(area_code, str):
                    continue
                
                if (area_code.startswith('E06') or area_code.startswith('E08') or
                    area_code.startswith('E09') or area_code.startswith('E10')):
                    
                    area_name = row.iloc[1] if len(row) > 1 else f'UTLA_{area_code}'
                    region_name = row.iloc[2] if len(row) > 2 else None
                    
                    region_map = {
                        'North East': 'E12000001',
                        'North West': 'E12000002',
                        'Yorkshire and The Humber': 'E12000003',
                        'East Midlands': 'E12000004',
                        'West Midlands': 'E12000005',
                        'East of England': 'E12000006',
                        'London': 'E12000007',
                        'South East': 'E12000008',
                        'South West': 'E12000009'
                    }
                    parent_region_code = region_map.get(str(region_name))
                    
                    utlas.append({
                        'area_code': area_code,
                        'area_name': str(area_name),
                        'area_type': 'utla',
                        'parent_region_code': parent_region_code
                    })
        except Exception as e:
            print(f"Warning: Could not load UTLAs from CSV: {e}")
    
    if len(utlas) == 0:
        for i in range(1, 151):
            utlas.append({
                'area_code': f'E{10000000 + i:08d}',
                'area_name': f'UTLA_{i:03d}',
                'area_type': 'utla',
                'parent_region_code': regions[i % 9]['area_code']
            })
    
    all_areas = countries + regions + utlas
    
    for area_dict in all_areas:
        existing = session.query(GeographicArea).filter_by(area_code=area_dict['area_code']).first()
        
        if not existing:
            area = GeographicArea(**area_dict)
            session.add(area)
    
    session.commit()


def load_vaccines(session):
    """
    Load all vaccines from canonical reference list
    
    Args:
        session: SQLAlchemy session
    """
    from database_version_2.src.vaccine_matcher import CANONICAL_VACCINES
    
    for vaccine_data in CANONICAL_VACCINES:
        existing = session.query(Vaccine).filter_by(vaccine_code=vaccine_data['vaccine_code']).first()
        
        if not existing:
            vaccine = Vaccine(
                vaccine_code=vaccine_data['vaccine_code'],
                vaccine_name=vaccine_data['vaccine_name'],
                vaccine_description=vaccine_data['description']
            )
            session.add(vaccine)
    
    session.commit()


def load_age_cohorts(session):
    """Load all 4 age cohorts"""
    cohorts = [
        {'cohort_name': '12 months', 'age_months': 12, 'birth_year_start': 2023, 'birth_year_end': 2024, 'description': 'Children born Apr 2023 - Mar 2024'},
        {'cohort_name': '24 months', 'age_months': 24, 'birth_year_start': 2022, 'birth_year_end': 2023, 'description': 'Children born Apr 2022 - Mar 2023'},
        {'cohort_name': '5 years', 'age_months': 60, 'birth_year_start': 2019, 'birth_year_end': 2020, 'description': 'Children born Apr 2019 - Mar 2020'},
        {'cohort_name': '3 months', 'age_months': 3, 'birth_year_start': 2024, 'birth_year_end': 2025, 'description': 'Children 3 months old (for BCG)'},
    ]
    
    for cohort_dict in cohorts:
        existing = session.query(AgeCohort).filter_by(cohort_name=cohort_dict['cohort_name']).first()
        
        if not existing:
            cohort = AgeCohort(**cohort_dict)
            session.add(cohort)
    
    session.commit()


def load_financial_years(session):
    """Load all 17 financial years (2009-2025)"""
    years = []
    
    for start_year in range(2009, 2026):
        end_year = start_year + 1
        years.append({
            'year_label': f'{start_year}-{end_year}',
            'year_start': start_year,
            'year_end': end_year,
            'evaluation_start_date': f'{start_year}-04-01',
            'evaluation_end_date': f'{end_year}-03-31'
        })
    
    for year_dict in years:
        existing = session.query(FinancialYear).filter_by(year_label=year_dict['year_label']).first()
        
        if not existing:
            year = FinancialYear(**year_dict)
            session.add(year)
    
    session.commit()


def load_all_reference_data(session):
    """
    Load all reference data tables
    
    Args:
        session: SQLAlchemy session
    """
    print("Loading reference data...")
    
    # Load vaccines INLINE from canonical list
    print("  - Vaccines...")
    from database_version_2.src.vaccine_matcher import CANONICAL_VACCINES
    
    session.query(Vaccine).delete()
    session.commit()
    
    for vaccine_data in CANONICAL_VACCINES:
        vaccine = Vaccine(
            vaccine_code=vaccine_data['vaccine_code'],
            vaccine_name=vaccine_data['vaccine_name'],
            vaccine_description=vaccine_data['description']
        )
        session.add(vaccine)
    session.commit()
    
    vaccine_count = session.query(Vaccine).count()
    print(f"    Loaded {vaccine_count} vaccines from canonical list")
    
    print("  - Geographic areas...")
    load_geographic_areas(session)
    
    print("  - Age cohorts...")
    load_age_cohorts(session)
    
    print("  - Financial years...")
    load_financial_years(session)
    
    print("  Reference data loaded successfully!")
