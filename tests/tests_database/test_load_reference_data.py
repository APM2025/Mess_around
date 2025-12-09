"""
Tests for loading reference data (dimension tables).

Covers:
- Geographic areas (countries, regions, UTLAs)
- Vaccines from canonical list
- Age cohorts (12m, 24m, 5y, 3m)
- Financial years (2009-2025)

Requirements:
- DB-FR-001: CREATE operations
- DA-FR-001: Load from CSV
"""

import pytest
from pathlib import Path
from backend_code.database_src.database import create_test_session
from backend_code.database_src.models import (
    GeographicArea, Vaccine, AgeCohort, FinancialYear
)


class TestLoadGeographicAreas:
    """Test loading 163 geographic areas"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        """Provide clean test database"""
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        yield session
        session.close()
    
    def test_load_all_geographic_areas(self, db_session):
        """Load all geographic areas from CSV and verify count."""
        from backend_code.database_src.load_reference_data import load_geographic_areas
        
        load_geographic_areas(db_session)
        
        total = db_session.query(GeographicArea).count()
        assert total >= 162, f"Expected 162+ areas, got {total}"
    
    def test_countries_loaded(self, db_session):
        """Verify all 4 UK countries are loaded correctly."""
        from backend_code.database_src.load_reference_data import load_geographic_areas
        
        load_geographic_areas(db_session)
        
        countries = db_session.query(GeographicArea)\
            .filter_by(area_type='country')\
            .count()
        
        assert countries == 4, f"Expected 4 countries, got {countries}"
        
        # Check England exists
        england = db_session.query(GeographicArea)\
            .filter_by(area_name='England')\
            .first()
        
        assert england is not None, "England should exist"
        assert england.area_type == 'country', "England should be a country"
    
    def test_regions_loaded(self, db_session):
        """Verify all 9 NHS England regions are loaded."""
        from backend_code.database_src.load_reference_data import load_geographic_areas
        
        load_geographic_areas(db_session)
        
        regions = db_session.query(GeographicArea)\
            .filter_by(area_type='region')\
            .count()
        
        assert regions == 9, f"Expected 9 regions, got {regions}"
    
    def test_utlas_loaded(self, db_session):
        """Verify UTLAs are loaded from T4a CSV."""
        from backend_code.database_src.load_reference_data import load_geographic_areas
        
        load_geographic_areas(db_session)
        
        utlas = db_session.query(GeographicArea)\
            .filter_by(area_type='utla')\
            .count()
        
        assert utlas >= 149, f"Expected 149+ UTLAs, got {utlas}"


class TestLoadVaccines:
    """Test loading 16 vaccines"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        """Provide clean test database"""
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        yield session
        session.close()
    
    def test_load_all_vaccines(self, db_session):
        """Load vaccines from canonical reference list."""
        from backend_code.database_src.load_reference_data import load_vaccines
        
        load_vaccines(db_session)
        
        count = db_session.query(Vaccine).count()
        assert count == 13, f"Expected 13 vaccines (from canonical list), got {count}"
    
    def test_vaccine_has_required_fields(self, db_session):
        """Verify vaccine records have all required fields populated."""
        from backend_code.database_src.load_reference_data import load_vaccines
        
        load_vaccines(db_session)
        
        vaccine = db_session.query(Vaccine).first()
        
        assert vaccine is not None, "Should have at least one vaccine"
        assert vaccine.vaccine_name is not None, "Vaccine should have name"
        assert len(vaccine.vaccine_name) > 0, "Vaccine name should not be empty"


class TestLoadAgeCohorts:
    """Test loading 4 age cohorts"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        """Provide clean test database"""
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        yield session
        session.close()
    
    def test_load_all_cohorts(self, db_session):
        """Load all 4 age cohorts and verify count."""
        from backend_code.database_src.load_reference_data import load_age_cohorts
        
        load_age_cohorts(db_session)
        
        count = db_session.query(AgeCohort).count()
        assert count == 4, f"Expected 4 cohorts, got {count}"
    
    def test_cohort_has_age_info(self, db_session):
        """Verify cohort records contain age information."""
        from backend_code.database_src.load_reference_data import load_age_cohorts
        
        load_age_cohorts(db_session)
        
        cohort_12m = db_session.query(AgeCohort)\
            .filter_by(age_months=12)\
            .first()
        
        assert cohort_12m is not None, "12-month cohort should exist"
        assert cohort_12m.cohort_name is not None, "Cohort should have name"


class TestLoadFinancialYears:
    """Test loading 17 financial years"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        """Provide clean test database"""
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        yield session
        session.close()
    
    def test_load_all_years(self, db_session):
        """Load all 17 financial years (2009-2025)."""
        from backend_code.database_src.load_reference_data import load_financial_years
        
        load_financial_years(db_session)
        
        count = db_session.query(FinancialYear).count()
        assert count == 17, f"Expected 17 years, got {count}"
    
    def test_current_year_exists(self, db_session):
        """Verify current financial year (2024-2025) is present."""
        from backend_code.database_src.load_reference_data import load_financial_years
        
        load_financial_years(db_session)
        
        year_2024 = db_session.query(FinancialYear)\
            .filter_by(year_start=2024)\
            .first()
        
        assert year_2024 is not None, "2024-2025 should exist"
        assert year_2024.year_label == "2024-2025", "Year label should be formatted correctly"


class TestLoadAllReferenceData:
    """Integration test: Load all reference data together"""
    
    def test_load_complete_reference_data(self, tmp_path):
        """Integration test for loading all reference tables together."""
        from backend_code.database_src.load_reference_data import load_all_reference_data
        
        db_path = tmp_path / "test_complete.db"
        session = create_test_session(db_path)
        
        load_all_reference_data(session)
        
        # Verify all tables populated
        assert session.query(GeographicArea).count() >= 162  # 4 countries + 9 regions + 149 UTLAs
        assert session.query(Vaccine).count() == 13  # From canonical list (11 + HepB + BCG)
        assert session.query(AgeCohort).count() == 4
        assert session.query(FinancialYear).count() == 17
        
        session.close()
