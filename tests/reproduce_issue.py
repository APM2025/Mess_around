
from sqlalchemy.orm import Session
from src.models import (
    Base, GeographicArea, Vaccine, AgeCohort, FinancialYear,
    LocalAuthorityCoverage
)
from src.table_builder import TableBuilder
from sqlalchemy import create_engine
import pytest

def test_utla_table_shows_region_name():
    # Setup in-memory DB
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    session = Session(engine)

    # 1. Create Reference Data
    year = FinancialYear(
        year_label='2023-2024',
        year_start=2023,
        year_end=2024
    )
    cohort = AgeCohort(
        cohort_name='24 months',
        age_months=24
    )
    region = GeographicArea(
        area_code='REG01',
        area_name='Test Region',
        area_type='region'
    )
    utla = GeographicArea(
        area_code='UTLA01',
        area_name='Test UTLA',
        area_type='utla',
        parent_region_code='REG01'
    )
    vaccine = Vaccine(
        vaccine_code='MMR',
        vaccine_name='Measles Mumps Rubella'
    )

    session.add_all([year, cohort, region, utla, vaccine])
    session.commit()

    # 2. Create Coverage Data
    coverage = LocalAuthorityCoverage(
        year_id=year.year_id,
        area_code=utla.area_code,
        cohort_id=cohort.cohort_id,
        vaccine_id=vaccine.vaccine_id,
        eligible_population=100,
        vaccinated_count=90,
        coverage_percentage=90.0
    )
    session.add(coverage)
    session.commit()

    # 3. Build Table
    builder = TableBuilder(session)
    results = builder.get_utla_table(cohort_name='24 months', year=2023)

    # 4. Verify
    assert len(results) == 1
    row = results[0]
    print(f"Region Name in Table: {row.get('region_name')}")
    assert row['region_name'] == 'Test Region', f"Expected 'Test Region', got '{row['region_name']}'"
