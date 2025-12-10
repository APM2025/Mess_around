"""
Tests for table_builder module.
"""

import pytest
from src.layer2_business_logic.table_builder import TableBuilder
from src.layer1_database.models import (
    Vaccine, AgeCohort, GeographicArea, FinancialYear,
    NationalCoverage, LocalAuthorityCoverage, RegionalTimeSeries
)
from src.layer1_database.database import create_test_session


@pytest.fixture
def db_session(tmp_path):
    """Create clean test database session."""
    db_path = tmp_path / "test.db"
    session = create_test_session(db_path)
    yield session
    session.close()


@pytest.fixture
def sample_vaccine(db_session):
    """Create test vaccine."""
    vaccine = Vaccine(
        vaccine_id=1,
        vaccine_code='MMR1',
        vaccine_name='MMR1',
        vaccine_description='Measles, Mumps, Rubella (First Dose)'
    )
    db_session.add(vaccine)
    db_session.commit()
    return vaccine


@pytest.fixture
def sample_cohort_12m(db_session):
    """Create 12 months cohort."""
    cohort = AgeCohort(
        cohort_id=1,
        cohort_name='12 months',
        age_months=12
    )
    db_session.add(cohort)
    db_session.commit()
    return cohort


@pytest.fixture
def sample_cohort_24m(db_session):
    """Create 24 months cohort."""
    cohort = AgeCohort(
        cohort_id=2,
        cohort_name='24 months',
        age_months=24
    )
    db_session.add(cohort)
    db_session.commit()
    return cohort


@pytest.fixture
def sample_country(db_session):
    """Create test country."""
    area = GeographicArea(
        area_code='E92000001',
        area_name='England',
        area_type='country'
    )
    db_session.add(area)
    db_session.commit()
    return area


@pytest.fixture
def sample_utla(db_session):
    """Create test UTLA."""
    area = GeographicArea(
        area_code='E10000019',
        area_name='Lincolnshire',
        area_type='utla',
        ods_code='E10000019'
    )
    db_session.add(area)
    db_session.commit()
    return area


@pytest.fixture
def sample_region(db_session):
    """Create test region."""
    area = GeographicArea(
        area_code='E12000004',
        area_name='East Midlands',
        area_type='region'
    )
    db_session.add(area)
    db_session.commit()
    return area


@pytest.fixture
def sample_year(db_session):
    """Create test year."""
    year = FinancialYear(
        year_id=1,
        year_label='2024-2025',
        year_start=2024,
        year_end=2025
    )
    db_session.add(year)
    db_session.commit()
    return year


@pytest.fixture
def table_builder(db_session):
    """Create table builder instance."""
    return TableBuilder(db_session)


# Phase 1: Basic instantiation
def test_table_builder_can_be_created(db_session):
    """Test that TableBuilder can be instantiated."""
    builder = TableBuilder(db_session)

    assert builder is not None
    assert builder.session == db_session


# Phase 2: get_table1_uk_by_country tests
def test_get_table1_returns_dict(table_builder):
    """Test get_table1_uk_by_country returns dictionary."""
    result = table_builder.get_table1_uk_by_country()

    assert isinstance(result, dict)
    assert 'title' in result
    assert 'notes' in result
    assert 'data' in result


def test_get_table1_with_coverage_data(
    db_session, table_builder, sample_country, sample_vaccine,
    sample_cohort_12m, sample_year
):
    """Test get_table1 returns coverage data."""
    # Add coverage record
    coverage = NationalCoverage(
        year_id=sample_year.year_id,
        area_code=sample_country.area_code,
        vaccine_id=sample_vaccine.vaccine_id,
        cohort_id=sample_cohort_12m.cohort_id,
        eligible_population=1000,
        vaccinated_count=930,
        coverage_percentage=93.0
    )
    db_session.add(coverage)
    db_session.commit()

    result = table_builder.get_table1_uk_by_country(cohort_name='12 months', year=2024)

    assert result['cohort'] == '12 months'
    assert result['year'] == 2024
    assert len(result['data']) > 0


def test_get_table1_row_structure(
    db_session, table_builder, sample_country, sample_vaccine,
    sample_cohort_12m, sample_year
):
    """Test get_table1 row has correct structure."""
    # Add coverage record
    coverage = NationalCoverage(
        year_id=sample_year.year_id,
        area_code=sample_country.area_code,
        vaccine_id=sample_vaccine.vaccine_id,
        cohort_id=sample_cohort_12m.cohort_id,
        eligible_population=1000,
        vaccinated_count=930,
        coverage_percentage=93.0
    )
    db_session.add(coverage)
    db_session.commit()

    result = table_builder.get_table1_uk_by_country(cohort_name='12 months', year=2024)

    row = result['data'][0]
    assert 'code' in row
    assert 'geographic_area' in row
    assert 'note' in row
    assert 'number_aged_12_months' in row
    assert 'coverage_at_12_months_MMR1' in row


# Phase 3: get_utla_table tests
def test_get_utla_table_returns_list(table_builder):
    """Test get_utla_table returns list."""
    result = table_builder.get_utla_table()

    assert isinstance(result, list)


def test_get_utla_table_with_data(
    db_session, table_builder, sample_utla, sample_vaccine,
    sample_cohort_24m, sample_year
):
    """Test get_utla_table returns coverage data."""
    # Add coverage record
    coverage = LocalAuthorityCoverage(
        year_id=sample_year.year_id,
        area_code=sample_utla.area_code,
        vaccine_id=sample_vaccine.vaccine_id,
        cohort_id=sample_cohort_24m.cohort_id,
        eligible_population=1000,
        vaccinated_count=930,
        coverage_percentage=93.0
    )
    db_session.add(coverage)
    db_session.commit()

    result = table_builder.get_utla_table(cohort_name='24 months', year=2024)

    assert len(result) == 1
    row = result[0]
    assert row['code'] == sample_utla.area_code
    assert row['local_authority'] == 'Lincolnshire'
    assert 'coverage_at_24_months_MMR1' in row
    assert row['coverage_at_24_months_MMR1'] == 93.0


def test_get_utla_table_row_structure(
    db_session, table_builder, sample_utla, sample_vaccine,
    sample_cohort_24m, sample_year
):
    """Test UTLA table row has correct structure."""
    # Add coverage record
    coverage = LocalAuthorityCoverage(
        year_id=sample_year.year_id,
        area_code=sample_utla.area_code,
        vaccine_id=sample_vaccine.vaccine_id,
        cohort_id=sample_cohort_24m.cohort_id,
        eligible_population=1000,
        vaccinated_count=930,
        coverage_percentage=93.0
    )
    db_session.add(coverage)
    db_session.commit()

    result = table_builder.get_utla_table(cohort_name='24 months', year=2024)

    row = result[0]
    assert 'code' in row
    assert 'local_authority' in row
    assert 'region_name' in row
    assert 'ods_code' in row
    assert 'note' in row
    assert 'number_aged_24_months' in row
    assert 'vaccinated_at_24_months_MMR1' in row
    assert 'coverage_at_24_months_MMR1' in row


def test_get_utla_table_sorted_by_name(
    db_session, table_builder, sample_vaccine,
    sample_cohort_24m, sample_year
):
    """Test UTLA table is sorted alphabetically by area name."""
    # Create multiple UTLAs
    utla1 = GeographicArea(
        area_code='E001',
        area_name='Zebra County',
        area_type='utla'
    )
    utla2 = GeographicArea(
        area_code='E002',
        area_name='Alpha County',
        area_type='utla'
    )
    utla3 = GeographicArea(
        area_code='E003',
        area_name='Midway County',
        area_type='utla'
    )
    db_session.add_all([utla1, utla2, utla3])
    db_session.commit()

    result = table_builder.get_utla_table(cohort_name='24 months', year=2024)

    # Should be sorted: Alpha, Midway, Zebra
    assert len(result) == 3
    assert result[0]['local_authority'] == 'Alpha County'
    assert result[1]['local_authority'] == 'Midway County'
    assert result[2]['local_authority'] == 'Zebra County'


# Phase 4: get_regional_table tests
def test_get_regional_table_returns_list(table_builder):
    """Test get_regional_table returns list."""
    result = table_builder.get_regional_table()

    assert isinstance(result, list)


def test_get_regional_table_with_data(
    db_session, table_builder, sample_region, sample_vaccine,
    sample_cohort_24m, sample_year
):
    """Test get_regional_table returns time series data."""
    # Add time series record
    ts = RegionalTimeSeries(
        year_id=sample_year.year_id,
        area_code=sample_region.area_code,
        vaccine_id=sample_vaccine.vaccine_id,
        cohort_id=sample_cohort_24m.cohort_id,
        eligible_population=10000,
        coverage_percentage=93.0
    )
    db_session.add(ts)
    db_session.commit()

    result = table_builder.get_regional_table(cohort_name='24 months')

    assert len(result) == 1
    row = result[0]
    assert row['code'] == sample_region.area_code
    assert row['area_name'] == 'East Midlands'
    assert row['coverage_percentage'] == 93.0


def test_get_regional_table_row_structure(
    db_session, table_builder, sample_region, sample_vaccine,
    sample_cohort_24m, sample_year
):
    """Test regional table row has correct structure."""
    # Add time series record
    ts = RegionalTimeSeries(
        year_id=sample_year.year_id,
        area_code=sample_region.area_code,
        vaccine_id=sample_vaccine.vaccine_id,
        cohort_id=sample_cohort_24m.cohort_id,
        eligible_population=10000,
        coverage_percentage=93.0
    )
    db_session.add(ts)
    db_session.commit()

    result = table_builder.get_regional_table(cohort_name='24 months')

    row = result[0]
    assert 'code' in row
    assert 'area_name' in row
    assert 'year' in row
    assert 'vaccine_code' in row
    assert 'vaccine_name' in row
    assert 'coverage_percentage' in row
    assert 'eligible_population' in row


# Phase 5: get_england_summary tests
def test_get_england_summary_returns_dict(table_builder):
    """Test get_england_summary returns dictionary."""
    result = table_builder.get_england_summary()

    assert isinstance(result, dict)


def test_get_england_summary_with_data(
    db_session, table_builder, sample_country, sample_vaccine,
    sample_cohort_24m, sample_year
):
    """Test get_england_summary returns summary data."""
    # Add coverage record
    coverage = LocalAuthorityCoverage(
        year_id=sample_year.year_id,
        area_code=sample_country.area_code,
        vaccine_id=sample_vaccine.vaccine_id,
        cohort_id=sample_cohort_24m.cohort_id,
        eligible_population=600000,
        vaccinated_count=558000,
        coverage_percentage=93.0
    )
    db_session.add(coverage)
    db_session.commit()

    result = table_builder.get_england_summary(cohort_name='24 months', year=2024)

    assert result['cohort'] == '24 months'
    assert result['year'] == 2024
    assert 'vaccines' in result
    assert len(result['vaccines']) == 1
    assert result['vaccines'][0]['vaccine_code'] == 'MMR1'
    assert result['vaccines'][0]['coverage_percentage'] == 93.0


def test_get_england_summary_structure(
    db_session, table_builder, sample_country, sample_vaccine,
    sample_cohort_24m, sample_year
):
    """Test England summary has correct structure."""
    # Add coverage record
    coverage = LocalAuthorityCoverage(
        year_id=sample_year.year_id,
        area_code=sample_country.area_code,
        vaccine_id=sample_vaccine.vaccine_id,
        cohort_id=sample_cohort_24m.cohort_id,
        eligible_population=600000,
        vaccinated_count=558000,
        coverage_percentage=93.0
    )
    db_session.add(coverage)
    db_session.commit()

    result = table_builder.get_england_summary(cohort_name='24 months', year=2024)

    assert 'code' in result
    assert 'area_name' in result
    assert 'cohort' in result
    assert 'year' in result
    assert 'vaccines' in result

    vaccine = result['vaccines'][0]
    assert 'vaccine_code' in vaccine
    assert 'vaccine_name' in vaccine
    assert 'coverage_percentage' in vaccine
    assert 'eligible_population' in vaccine


# Phase 6: Edge cases
def test_get_table1_with_invalid_cohort(table_builder):
    """Test get_table1 with non-existent cohort."""
    result = table_builder.get_table1_uk_by_country(cohort_name='invalid', year=2024)

    assert result['data'] == []


def test_get_table1_with_invalid_year(table_builder, sample_cohort_12m):
    """Test get_table1 with non-existent year."""
    result = table_builder.get_table1_uk_by_country(cohort_name='12 months', year=9999)

    assert result['data'] == []


def test_get_utla_table_with_no_coverage_data(
    db_session, table_builder, sample_utla, sample_cohort_24m, sample_year
):
    """Test UTLA table when area has no coverage data."""
    result = table_builder.get_utla_table(cohort_name='24 months', year=2024)

    # Should still return the area with NULL/0 coverage
    assert len(result) == 1
    assert result[0]['code'] == sample_utla.area_code
