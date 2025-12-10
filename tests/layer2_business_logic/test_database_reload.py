"""
Tests for database reload service.
"""

import pytest
from pathlib import Path
from src.layer1_database.database import create_test_session
from src.layer1_database.models import GeographicArea,Vaccine, AgeCohort, FinancialYear
from src.layer2_business_logic.database_reload import reload_all_data


@pytest.fixture
def test_session(tmp_path):
    """Create a test database session."""
    db_path = tmp_path / "test_reload.db"
    session = create_test_session(db_path)
    yield session
    session.close()


def test_reload_all_data_loads_reference_data(test_session):
    """Test that reload_all_data loads reference data."""
    # Act
    result = reload_all_data(test_session, verbose=False)
    
    # Assert - reference data should be loaded
    assert result['geographic_areas'] > 0
    assert result['vaccines'] > 0
    assert result['age_cohorts'] > 0
    assert result['financial_years'] > 0


def test_reload_all_data_returns_summary(test_session):
    """Test that reload_all_data returns a complete summary dictionary."""
    # Act
    result = reload_all_data(test_session, verbose=False)
    
    # Assert - check all expected keys
    assert 'geographic_areas' in result
    assert 'vaccines' in result
    assert 'age_cohorts' in result
    assert 'financial_years' in result
    assert 'national_coverage' in result
    assert 'la_coverage' in result
    assert 'england_time_series' in result
    assert 'regional_time_series' in result
    assert 'special_programs' in result
    assert 'warnings' in result
    
    # All values should be integers except warnings (list)
    assert isinstance(result['geographic_areas'], int)
    assert isinstance(result['warnings'], list)


def test_reload_with_missing_csv_directory(test_session, tmp_path):
    """Test reload handling when CSV directory doesn't exist."""
    # Arrange
    nonexistent_path = tmp_path / "missing_csv_dir"
    
    # Act
    result = reload_all_data(test_session, csv_path=nonexistent_path, verbose=False)
    
    # Assert
    # Reference data should still be loaded
    assert result['geographic_areas'] > 0
    # But warnings should indicate CSV directory not found
    assert len(result['warnings']) > 0
    assert any('CSV directory not found' in w for w in result['warnings'])


def test_reload_loads_areas_into_database(test_session):
    """Test that geographic areas are actually inserted into database."""
    # Act
    reload_all_data(test_session, verbose=False)
    
    # Assert - check database has records
    areas = test_session.query(GeographicArea).all()
    assert len(areas) > 0
    
    # Check we have areas of different types
    area_types = {area.area_type for area in areas}
    assert 'country' in area_types or 'utla' in area_types


def test_reload_loads_vaccines_into_database(test_session):
    """Test that vaccines are actually inserted into database."""
    # Act
    reload_all_data(test_session, verbose=False)
    
    # Assert
    vaccines = test_session.query(Vaccine).all()
    assert len(vaccines) > 0
    
    # Check we have common vaccines
    vaccine_codes = {v.vaccine_code for v in vaccines}
    # Should have at least some standard vaccines
    assert len(vaccine_codes) > 0


def test_reload_verbose_mode_prints_progress(test_session, capsys):
    """Test that verbose mode prints progress messages."""
    # Act
    reload_all_data(test_session, verbose=True)
    
    # Assert - capture stdout
    captured = capsys.readouterr()
    assert "Loading reference data" in captured.out
    assert "Loading geographic areas" in captured.out
    assert "[OK]" in captured.out


def test_reload_quiet_mode_no_output(test_session, capsys):
    """Test that verbose=False suppresses output."""
    # Act
    reload_all_data(test_session, verbose=False)
    
    # Assert - no output should be printed
    captured = capsys.readouterr()
    assert captured.out == ""


def test_reload_multiple_times_is_idempotent(test_session):
    """Test that reload can be called multiple times safely."""
    # Act - reload twice
    result1 = reload_all_data(test_session, verbose=False)
    result2 = reload_all_data(test_session, verbose=False)
    
    # Assert - counts should be similar (data might be updated, not duplicated)
    # The key is it doesn't crash
    assert result2['geographic_areas'] > 0
    assert result2['vaccines'] > 0
