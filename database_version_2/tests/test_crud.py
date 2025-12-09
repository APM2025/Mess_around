"""
Tests for CRUD operations module.
"""

import pytest
from database_version_2.src.database import create_test_session
from database_version_2.src.models import (
    GeographicArea, Vaccine, AgeCohort, FinancialYear,
    LocalAuthorityCoverage, EnglandTimeSeries
)
from database_version_2.src.crud import VaccinationCRUD


@pytest.fixture
def db_session(tmp_path):
    """Create a test database session."""
    db_path = tmp_path / "test_crud.db"
    session = create_test_session(db_path)
    yield session
    session.close()


@pytest.fixture
def crud_manager(db_session):
    """Create CRUD manager instance."""
    return VaccinationCRUD(db_session)


@pytest.fixture
def sample_area(db_session):
    """Create a sample geographic area."""
    area = GeographicArea(
        area_code='E12345678',
        area_name='Test Area',
        area_type='utla'
    )
    db_session.add(area)
    db_session.commit()
    return area


@pytest.fixture
def sample_vaccine(db_session):
    """Create a sample vaccine."""
    vaccine = Vaccine(
        vaccine_code='TEST1',
        vaccine_name='Test Vaccine 1'
    )
    db_session.add(vaccine)
    db_session.commit()
    return vaccine


@pytest.fixture
def sample_cohort(db_session):
    """Create a sample age cohort."""
    cohort = AgeCohort(
        cohort_name='12 months',
        age_months=12
    )
    db_session.add(cohort)
    db_session.commit()
    return cohort


@pytest.fixture
def sample_year(db_session):
    """Create a sample financial year."""
    year = FinancialYear(
        year_label='2023-2024',
        year_start=2023,
        year_end=2024
    )
    db_session.add(year)
    db_session.commit()
    return year


# Phase 1: Basic instantiation
def test_crud_manager_can_be_created(crud_manager):
    """Test that VaccinationCRUD can be instantiated."""
    assert crud_manager is not None
    assert hasattr(crud_manager, 'session')


# Phase 2: CREATE operations
def test_create_geographic_area(crud_manager):
    """Test creating a new geographic area."""
    area_data = {
        'area_code': 'E00000001',
        'area_name': 'New Test Area',
        'area_type': 'utla'
    }

    result = crud_manager.create_geographic_area(**area_data)

    assert result is not None
    assert result.area_code == 'E00000001'
    assert result.area_name == 'New Test Area'
    assert result.area_type == 'utla'


def test_create_vaccine(crud_manager):
    """Test creating a new vaccine."""
    vaccine_data = {
        'vaccine_code': 'TEST2',
        'vaccine_name': 'Test Vaccine 2'
    }

    result = crud_manager.create_vaccine(**vaccine_data)

    assert result is not None
    assert result.vaccine_code == 'TEST2'
    assert result.vaccine_name == 'Test Vaccine 2'


def test_create_coverage_record(crud_manager, sample_area, sample_vaccine, sample_cohort, sample_year):
    """Test creating a coverage record."""
    coverage_data = {
        'area_code': sample_area.area_code,
        'vaccine_id': sample_vaccine.vaccine_id,
        'cohort_id': sample_cohort.cohort_id,
        'year_id': sample_year.year_id,
        'coverage_percentage': 85.5,
        'vaccinated_count': 855,
        'eligible_population': 1000
    }

    result = crud_manager.create_coverage_record(**coverage_data)

    assert result is not None
    assert result.coverage_percentage == 85.5
    assert result.vaccinated_count == 855
    assert result.eligible_population == 1000


# Phase 3: READ operations
def test_get_geographic_area_by_code(crud_manager, sample_area):
    """Test retrieving a geographic area by code."""
    result = crud_manager.get_geographic_area(sample_area.area_code)

    assert result is not None
    assert result.area_code == sample_area.area_code
    assert result.area_name == sample_area.area_name


def test_get_vaccine_by_code(crud_manager, sample_vaccine):
    """Test retrieving a vaccine by code."""
    result = crud_manager.get_vaccine(sample_vaccine.vaccine_code)

    assert result is not None
    assert result.vaccine_code == sample_vaccine.vaccine_code
    assert result.vaccine_name == sample_vaccine.vaccine_name


def test_get_all_vaccines(crud_manager, sample_vaccine):
    """Test retrieving all vaccines."""
    result = crud_manager.get_all_vaccines()

    assert result is not None
    assert len(result) >= 1
    assert any(v.vaccine_code == sample_vaccine.vaccine_code for v in result)


def test_get_coverage_records(crud_manager, sample_area, sample_vaccine, sample_cohort, sample_year):
    """Test retrieving coverage records with filters."""
    # First create a coverage record
    crud_manager.create_coverage_record(
        area_code=sample_area.area_code,
        vaccine_id=sample_vaccine.vaccine_id,
        cohort_id=sample_cohort.cohort_id,
        year_id=sample_year.year_id,
        coverage_percentage=90.0,
        vaccinated_count=900,
        eligible_population=1000
    )

    # Retrieve it
    result = crud_manager.get_coverage_records(
        vaccine_code=sample_vaccine.vaccine_code,
        area_code=sample_area.area_code
    )

    assert result is not None
    assert len(result) >= 1
    assert result[0].coverage_percentage == 90.0


# Phase 4: UPDATE operations
def test_update_geographic_area(crud_manager, sample_area):
    """Test updating a geographic area."""
    updated = crud_manager.update_geographic_area(
        sample_area.area_code,
        area_name='Updated Area Name'
    )

    assert updated is not None
    assert updated.area_name == 'Updated Area Name'
    assert updated.area_code == sample_area.area_code


def test_update_vaccine(crud_manager, sample_vaccine):
    """Test updating a vaccine."""
    updated = crud_manager.update_vaccine(
        sample_vaccine.vaccine_code,
        vaccine_name='Updated Vaccine Name'
    )

    assert updated is not None
    assert updated.vaccine_name == 'Updated Vaccine Name'
    assert updated.vaccine_code == sample_vaccine.vaccine_code


def test_update_coverage_record(crud_manager, sample_area, sample_vaccine, sample_cohort, sample_year):
    """Test updating a coverage record."""
    # Create a record first
    record = crud_manager.create_coverage_record(
        area_code=sample_area.area_code,
        vaccine_id=sample_vaccine.vaccine_id,
        cohort_id=sample_cohort.cohort_id,
        year_id=sample_year.year_id,
        coverage_percentage=80.0,
        vaccinated_count=800,
        eligible_population=1000
    )

    # Update it
    updated = crud_manager.update_coverage_record(
        record.coverage_id,
        coverage_percentage=95.0,
        vaccinated_count=950
    )

    assert updated is not None
    assert updated.coverage_percentage == 95.0
    assert updated.vaccinated_count == 950
    assert updated.eligible_population == 1000  # Unchanged


# Phase 5: DELETE operations
def test_delete_geographic_area(crud_manager, db_session):
    """Test deleting a geographic area."""
    # Create area to delete
    area = GeographicArea(
        area_code='E99999999',
        area_name='To Delete',
        area_type='utla'
    )
    db_session.add(area)
    db_session.commit()

    # Delete it
    result = crud_manager.delete_geographic_area('E99999999')

    assert result is True
    # Verify it's gone
    deleted = crud_manager.get_geographic_area('E99999999')
    assert deleted is None


def test_delete_vaccine(crud_manager, db_session):
    """Test deleting a vaccine."""
    # Create vaccine to delete
    vaccine = Vaccine(
        vaccine_code='DEL1',
        vaccine_name='Delete Me'
    )
    db_session.add(vaccine)
    db_session.commit()

    # Delete it
    result = crud_manager.delete_vaccine('DEL1')

    assert result is True
    # Verify it's gone
    deleted = crud_manager.get_vaccine('DEL1')
    assert deleted is None


def test_delete_coverage_record(crud_manager, sample_area, sample_vaccine, sample_cohort, sample_year):
    """Test deleting a coverage record."""
    # Create record to delete
    record = crud_manager.create_coverage_record(
        area_code=sample_area.area_code,
        vaccine_id=sample_vaccine.vaccine_id,
        cohort_id=sample_cohort.cohort_id,
        year_id=sample_year.year_id,
        coverage_percentage=75.0,
        vaccinated_count=750,
        eligible_population=1000
    )

    # Delete it
    result = crud_manager.delete_coverage_record(record.coverage_id)

    assert result is True
