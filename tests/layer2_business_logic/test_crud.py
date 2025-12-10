"""
Tests for CRUD operations module.
"""

import pytest
from src.layer1_database.database import create_test_session
from src.layer1_database.models import (
    GeographicArea, Vaccine, AgeCohort, FinancialYear,
    LocalAuthorityCoverage, EnglandTimeSeries
)
from src.layer2_business_logic.crud import VaccinationCRUD


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


# Phase 6: New API-focused methods
def test_get_all_areas_as_dicts(crud_manager, sample_area):
    """Test getting all areas as dictionaries."""
    result = crud_manager.get_all_areas_as_dicts()
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) >= 1
    
    # Check structure of returned dicts
    area_dict = result[0]
    assert 'code' in area_dict
    assert 'name' in area_dict
    assert 'type' in area_dict
    
    # Verify our sample area is in the results
    assert any(a['code'] == sample_area.area_code for a in result)


def test_get_areas_by_type_as_dicts(crud_manager, db_session):
    """Test getting areas filtered by type as dictionaries."""
    # Create areas of different types
    utla1 = GeographicArea(area_code='E12000001', area_name='UTLA 1', area_type='utla')
    utla2 = GeographicArea(area_code='E12000002', area_name='UTLA 2', area_type='utla')
    region = GeographicArea(area_code='E13000001', area_name='Region 1', area_type='region')
    
    db_session.add_all([utla1, utla2, region])
    db_session.commit()
    
    # Get only UTLAs
    result = crud_manager.get_areas_by_type_as_dicts('utla')
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) >= 2
    
    # Check structure
    assert all('code' in a and 'name' in a for a in result)
    
    # Verify only UTLAs are returned
    utla_codes = [a['code'] for a in result]
    assert 'E12000001' in utla_codes
    assert 'E12000002' in utla_codes
    assert 'E13000001' not in utla_codes  # region should not be included


def test_delete_row_by_codes_local_authority(crud_manager, db_session):
    """Test deleting all vaccine records for a local authority area/cohort/year."""
    # Setup test data
    area = GeographicArea(area_code='E10000001', area_name='Test UTLA', area_type='utla')
    cohort = AgeCohort(cohort_name='12 months', age_months=12)
    year = FinancialYear(year_label='2024-2025', year_start=2024, year_end=2025)
    vaccine1 = Vaccine(vaccine_code='VAC1', vaccine_name='Vaccine 1')
    vaccine2 = Vaccine(vaccine_code='VAC2', vaccine_name='Vaccine 2')
    
    db_session.add_all([area, cohort, year, vaccine1, vaccine2])
    db_session.commit()
    
    # Create multiple coverage records for this row
    from src.layer1_database.models import LocalAuthorityCoverage
    
    cov1 = LocalAuthorityCoverage(
        area_code=area.area_code,
        vaccine_id=vaccine1.vaccine_id,
        cohort_id=cohort.cohort_id,
        year_id=year.year_id,
        coverage_percentage=85.0,
        vaccinated_count=850,
        eligible_population=1000
    )
    cov2 = LocalAuthorityCoverage(
        area_code=area.area_code,
        vaccine_id=vaccine2.vaccine_id,
        cohort_id=cohort.cohort_id,
        year_id=year.year_id,
        coverage_percentage=90.0,
        vaccinated_count=900,
        eligible_population=1000
    )
    
    db_session.add_all([cov1, cov2])
    db_session.commit()
    
    # Delete the entire row
    count = crud_manager.delete_row_by_codes(
        area_code='E10000001',
        cohort_name='12 months',
        year=2024
    )
    
    # Verify deletion
    assert count == 2  # Both records should be deleted
    
    # Verify they're actually gone
    remaining = db_session.query(LocalAuthorityCoverage).filter_by(
        area_code='E10000001',
        cohort_id=cohort.cohort_id,
        year_id=year.year_id
    ).all()
    
    assert len(remaining) == 0


def test_delete_row_by_codes_national(crud_manager, db_session):
    """Test deleting all vaccine records for a national area/cohort/year."""
    # Setup test data for a country (national level)
    from src.layer1_database.models import NationalCoverage
    
    area = GeographicArea(area_code='K02000001', area_name='United Kingdom', area_type='country')
    cohort = AgeCohort(cohort_name='24 months', age_months=24)
    year = FinancialYear(year_label='2024-2025', year_start=2024, year_end=2025)
    vaccine = Vaccine(vaccine_code='MMR1', vaccine_name='MMR First Dose')
    
    db_session.add_all([area, cohort, year, vaccine])
    db_session.commit()
    
    # Create national coverage record
    cov = NationalCoverage(
        area_code=area.area_code,
        vaccine_id=vaccine.vaccine_id,
        cohort_id=cohort.cohort_id,
        year_id=year.year_id,
        coverage_percentage=92.5,
        vaccinated_count=92500,
        eligible_population=100000
    )
    
    db_session.add(cov)
    db_session.commit()
    
    # Delete the row
    count = crud_manager.delete_row_by_codes(
        area_code='K02000001',
        cohort_name='24 months',
        year=2024
    )
    
    # Verify deletion
    assert count == 1
    
    # Verify it's gone from the NationalCoverage table
    remaining = db_session.query(NationalCoverage).filter_by(
        area_code='K02000001',
        cohort_id=cohort.cohort_id,
        year_id=year.year_id
    ).all()
    
    assert len(remaining) == 0


def test_delete_row_by_codes_invalid_references(crud_manager):
    """Test that delete_row_by_codes raises ValueError for invalid references."""
    with pytest.raises(ValueError, match="Invalid reference data"):
        crud_manager.delete_row_by_codes(
            area_code='INVALID',
            cohort_name='12 months',
            year=2024
        )
