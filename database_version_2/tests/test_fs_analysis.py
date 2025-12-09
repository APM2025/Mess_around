"""
Tests for filtering and analysis module.
"""

import pytest
from database_version_2.src.fs_analysis import VaccinationAnalyzer
from database_version_2.src.models import (
    Vaccine, AgeCohort, GeographicArea, FinancialYear,
    LocalAuthorityCoverage, EnglandTimeSeries
)
from database_version_2.src.database import create_test_session


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
        vaccine_name='MMR (First Dose)',
        vaccine_description='Test vaccine'
    )
    db_session.add(vaccine)
    db_session.commit()
    return vaccine


@pytest.fixture
def sample_cohort(db_session):
    """Create test cohort."""
    cohort = AgeCohort(
        cohort_id=1,
        cohort_name='24_months',
        age_months=24
    )
    db_session.add(cohort)
    db_session.commit()
    return cohort


@pytest.fixture
def sample_area(db_session):
    """Create test area."""
    area = GeographicArea(
        area_code='E10000019',
        area_name='Lincolnshire',
        area_type='utla'
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
def sample_coverage(db_session, sample_vaccine, sample_cohort, sample_area, sample_year):
    """Create test coverage record."""
    coverage = LocalAuthorityCoverage(
        year_id=sample_year.year_id,
        area_code=sample_area.area_code,
        vaccine_id=sample_vaccine.vaccine_id,
        cohort_id=sample_cohort.cohort_id,
        eligible_population=1000,
        vaccinated_count=930,
        coverage_percentage=93.0
    )
    db_session.add(coverage)
    db_session.commit()
    return coverage


@pytest.fixture
def analyzer(db_session):
    """Create analyzer instance."""
    return VaccinationAnalyzer(db_session)


# Phase 1: Basic instantiation
def test_analyzer_can_be_created(db_session):
    """Test that VaccinationAnalyzer can be instantiated."""
    analyzer = VaccinationAnalyzer(db_session)

    assert analyzer is not None
    assert analyzer.session == db_session


# Phase 2: filter_data tests
def test_filter_data_returns_list(analyzer, sample_coverage):
    """Test filter_data returns a list."""
    result = analyzer.filter_data()

    assert isinstance(result, list)


def test_filter_data_returns_coverage_records(analyzer, sample_coverage):
    """Test filter_data returns coverage data with correct fields."""
    result = analyzer.filter_data()

    assert len(result) == 1
    record = result[0]

    # Check required fields exist
    assert 'area_name' in record
    assert 'coverage' in record
    assert 'vaccine_code' in record


def test_filter_data_by_vaccine_code(analyzer, sample_coverage):
    """Test filtering by vaccine code."""
    result = analyzer.filter_data(vaccine_code='MMR1')

    assert len(result) == 1
    assert result[0]['vaccine_code'] == 'MMR1'
    assert result[0]['coverage'] == 93.0


# Phase 3: get_summary tests
def test_get_summary_returns_dict(analyzer, sample_coverage):
    """Test get_summary returns dict with stats."""
    data = analyzer.filter_data()
    stats = analyzer.get_summary(data)

    assert isinstance(stats, dict)
    assert 'mean' in stats
    assert 'min' in stats
    assert 'max' in stats
    assert 'count' in stats


def test_get_summary_calculates_correctly(analyzer, sample_coverage):
    """Test get_summary calculates correct values."""
    data = analyzer.filter_data()
    stats = analyzer.get_summary(data)

    assert stats['count'] == 1
    assert stats['mean'] == 93.0
    assert stats['min'] == 93.0
    assert stats['max'] == 93.0


def test_get_summary_with_multiple_records(db_session, analyzer, sample_vaccine, sample_cohort, sample_year):
    """Test summary with multiple records."""
    # Create multiple areas with different coverage
    area1 = GeographicArea(area_code='E001', area_name='Area1', area_type='utla')
    area2 = GeographicArea(area_code='E002', area_name='Area2', area_type='utla')
    area3 = GeographicArea(area_code='E003', area_name='Area3', area_type='utla')
    db_session.add_all([area1, area2, area3])
    db_session.commit()

    cov1 = LocalAuthorityCoverage(
        year_id=sample_year.year_id, area_code='E001',
        vaccine_id=sample_vaccine.vaccine_id, cohort_id=sample_cohort.cohort_id,
        coverage_percentage=90.0, eligible_population=1000
    )
    cov2 = LocalAuthorityCoverage(
        year_id=sample_year.year_id, area_code='E002',
        vaccine_id=sample_vaccine.vaccine_id, cohort_id=sample_cohort.cohort_id,
        coverage_percentage=85.0, eligible_population=1000
    )
    cov3 = LocalAuthorityCoverage(
        year_id=sample_year.year_id, area_code='E003',
        vaccine_id=sample_vaccine.vaccine_id, cohort_id=sample_cohort.cohort_id,
        coverage_percentage=95.0, eligible_population=1000
    )
    db_session.add_all([cov1, cov2, cov3])
    db_session.commit()

    data = analyzer.filter_data()
    stats = analyzer.get_summary(data)

    assert stats['count'] == 3
    assert stats['mean'] == 90.0  # (90 + 85 + 95) / 3
    assert stats['min'] == 85.0
    assert stats['max'] == 95.0


def test_get_summary_with_empty_data(analyzer):
    """Test summary with no data."""
    stats = analyzer.get_summary([])

    assert stats['count'] == 0
    assert stats['mean'] is None
    assert stats['min'] is None
    assert stats['max'] is None


# Phase 4: get_top_areas tests
def test_get_top_areas_returns_list(db_session, analyzer, sample_vaccine, sample_cohort, sample_year):
    """Test get_top_areas returns list."""
    # Create 5 areas
    for i in range(5):
        area = GeographicArea(
            area_code=f'E00{i}',
            area_name=f'Area{i}',
            area_type='utla'
        )
        db_session.add(area)

        cov = LocalAuthorityCoverage(
            year_id=sample_year.year_id,
            area_code=f'E00{i}',
            vaccine_id=sample_vaccine.vaccine_id,
            cohort_id=sample_cohort.cohort_id,
            coverage_percentage=90.0 - i,  # 90, 89, 88, 87, 86
            eligible_population=1000
        )
        db_session.add(cov)

    db_session.commit()

    result = analyzer.get_top_areas('MMR1', n=3)

    assert isinstance(result, list)
    assert len(result) == 3


def test_get_top_areas_sorted_descending(db_session, analyzer, sample_vaccine, sample_cohort, sample_year):
    """Test get_top_areas returns sorted results."""
    # Create areas with coverage: 95, 85, 90, 80, 88
    coverages = [95.0, 85.0, 90.0, 80.0, 88.0]

    for i, cov_pct in enumerate(coverages):
        area = GeographicArea(
            area_code=f'E00{i}',
            area_name=f'Area{i}',
            area_type='utla'
        )
        db_session.add(area)

        cov = LocalAuthorityCoverage(
            year_id=sample_year.year_id,
            area_code=f'E00{i}',
            vaccine_id=sample_vaccine.vaccine_id,
            cohort_id=sample_cohort.cohort_id,
            coverage_percentage=cov_pct,
            eligible_population=1000
        )
        db_session.add(cov)

    db_session.commit()

    top_3 = analyzer.get_top_areas('MMR1', n=3)

    # Should be: 95, 90, 88
    assert top_3[0]['coverage'] == 95.0
    assert top_3[1]['coverage'] == 90.0
    assert top_3[2]['coverage'] == 88.0


# Phase 5: get_trend tests
def test_get_trend_returns_list(db_session, analyzer, sample_vaccine, sample_cohort):
    """Test get_trend returns list."""
    # Create time series data for 3 years
    for year_num in range(2022, 2025):
        year = FinancialYear(
            year_id=year_num - 2021,
            year_label=f'{year_num}-{year_num+1}',
            year_start=year_num,
            year_end=year_num + 1
        )
        db_session.add(year)
        db_session.commit()

        ts = EnglandTimeSeries(
            year_id=year.year_id,
            vaccine_id=sample_vaccine.vaccine_id,
            cohort_id=sample_cohort.cohort_id,
            coverage_percentage=85.0 + (year_num - 2022),  # 85, 86, 87
            eligible_population=600000
        )
        db_session.add(ts)

    db_session.commit()

    result = analyzer.get_trend('MMR1')

    assert isinstance(result, list)
    assert len(result) == 3


def test_get_trend_ordered_by_year(db_session, analyzer, sample_vaccine, sample_cohort):
    """Test get_trend returns chronologically ordered results."""
    # Create time series in random order
    years_data = [
        (2024, 87.0),
        (2022, 85.0),
        (2023, 86.0)
    ]

    for year_num, coverage in years_data:
        year = FinancialYear(
            year_id=year_num - 2021,
            year_label=f'{year_num}-{year_num+1}',
            year_start=year_num,
            year_end=year_num + 1
        )
        db_session.add(year)
        db_session.commit()

        ts = EnglandTimeSeries(
            year_id=year.year_id,
            vaccine_id=sample_vaccine.vaccine_id,
            cohort_id=sample_cohort.cohort_id,
            coverage_percentage=coverage,
            eligible_population=600000
        )
        db_session.add(ts)

    db_session.commit()

    trend = analyzer.get_trend('MMR1')

    # Check chronological order
    assert trend[0]['coverage'] == 85.0  # 2022
    assert trend[1]['coverage'] == 86.0  # 2023
    assert trend[2]['coverage'] == 87.0  # 2024


def test_get_trend_has_required_fields(db_session, analyzer, sample_vaccine, sample_cohort):
    """Test trend records have year and coverage fields."""
    year = FinancialYear(
        year_id=1,
        year_label='2024-2025',
        year_start=2024,
        year_end=2025
    )
    db_session.add(year)
    db_session.commit()

    ts = EnglandTimeSeries(
        year_id=year.year_id,
        vaccine_id=sample_vaccine.vaccine_id,
        cohort_id=sample_cohort.cohort_id,
        coverage_percentage=90.0,
        eligible_population=600000
    )
    db_session.add(ts)
    db_session.commit()

    trend = analyzer.get_trend('MMR1')

    assert len(trend) == 1
    record = trend[0]
    assert 'year' in record
    assert 'coverage' in record
    assert record['year'] == '2024-2025'
    assert record['coverage'] == 90.0
