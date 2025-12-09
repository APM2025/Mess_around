"""
Test: Database Models (ORM Schema)

Tests for SQLAlchemy ORM models in models.py

Tests:
- Table creation
- Relationships (Foreign Keys, parent/child)
- Constraints (UNIQUE, CHECK, NOT NULL)
- Cascade/Restrict behavior
- Model representations

TDD Phase: Tests verify the models work correctly

Requirements:
- DB-FR-005: Structured data model
- DB-FR-004: Data integrity constraints
"""

import pytest
from sqlalchemy.exc import IntegrityError
from src.database import create_test_session
from src.models import (
    GeographicArea, Vaccine, AgeCohort, FinancialYear,
    NationalCoverage, LocalAuthorityCoverage, EnglandTimeSeries,
    RegionalTimeSeries, SpecialProgram, init_database, create_database_engine
)


class TestTableCreation:
    """Test that all tables are created correctly"""
    
    def test_all_tables_created(self, tmp_path):
        """Verify all 9 tables are created"""
        db_path = tmp_path / "test.db"
        engine = create_database_engine(f"sqlite:///{db_path}")
        
        init_database(engine)
        
        # Check tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = {
            'geographic_areas', 'vaccines', 'age_cohorts', 'financial_years',
            'national_coverage', 'local_authority_coverage', 'england_time_series',
            'regional_time_series', 'special_programs'
        }
        
        assert expected_tables.issubset(set(tables)), f"Missing tables: {expected_tables - set(tables)}"


class TestGeographicAreaModel:
    """Test GeographicArea model and constraints"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        """Provide clean test database"""
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        yield session
        session.close()
    
    def test_create_geographic_area(self, db_session):
        """Test creating a geographic area"""
        area = GeographicArea(
            area_code='E92000001',
            area_name='England',
            area_type='country'
        )
        
        db_session.add(area)
        db_session.commit()
        
        retrieved = db_session.query(GeographicArea).filter_by(area_code='E92000001').first()
        assert retrieved is not None
        assert retrieved.area_name == 'England'
    
    def test_area_code_must_be_unique(self, db_session):
        """Test UNIQUE constraint on area_code"""
        area1 = GeographicArea(area_code='E92000001', area_name='England', area_type='country')
        area2 = GeographicArea(area_code='E92000001', area_name='Duplicate', area_type='country')
        
        db_session.add(area1)
        db_session.commit()
        
        db_session.add(area2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_area_type_must_be_valid(self, db_session):
        """Test CHECK constraint on area_type"""
        area = GeographicArea(area_code='TEST001', area_name='Test', area_type='invalid_type')
        
        db_session.add(area)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_parent_child_relationship(self, db_session):
        """Test self-referential parent/child relationship"""
        # Create parent (country)
        england = GeographicArea(area_code='E92000001', area_name='England', area_type='country')
        db_session.add(england)
        db_session.commit()
        
        # Create child (region)
        london = GeographicArea(
            area_code='E12000007',
            area_name='London',
            area_type='region',
            parent_region_code='E92000001'
        )
        db_session.add(london)
        db_session.commit()
        
        # Verify relationship
        retrieved_london = db_session.query(GeographicArea).filter_by(area_code='E12000007').first()
        assert retrieved_london.parent_region is not None
        assert retrieved_london.parent_region.area_name == 'England'


class TestVaccineModel:
    """Test Vaccine model"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        yield session
        session.close()
    
    def test_create_vaccine(self, db_session):
        """Test creating a vaccine"""
        vaccine = Vaccine(
            vaccine_code='MMR1',
            vaccine_name='Measles, Mumps, Rubella - First dose'
        )
        
        db_session.add(vaccine)
        db_session.commit()
        
        retrieved = db_session.query(Vaccine).filter_by(vaccine_code='MMR1').first()
        assert retrieved is not None
        assert 'Measles' in retrieved.vaccine_name
    
    def test_vaccine_code_unique(self, db_session):
        """Test vaccine_code UNIQUE constraint"""
        v1 = Vaccine(vaccine_code='MMR1', vaccine_name='First')
        v2 = Vaccine(vaccine_code='MMR1', vaccine_name='Duplicate')
        
        db_session.add(v1)
        db_session.commit()
        
        db_session.add(v2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestAgeCohortModel:
    """Test AgeCohort model"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        yield session
        session.close()
    
    def test_create_cohort(self, db_session):
        """Test creating age cohort"""
        cohort = AgeCohort(
            cohort_name='12 months',
            age_months=12,
            birth_year_start=2023,
            birth_year_end=2024
        )
        
        db_session.add(cohort)
        db_session.commit()
        
        retrieved = db_session.query(AgeCohort).filter_by(age_months=12).first()
        assert retrieved is not None
        assert retrieved.cohort_name == '12 months'


class TestFinancialYearModel:
    """Test FinancialYear model"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        yield session
        session.close()
    
    def test_create_financial_year(self, db_session):
        """Test creating financial year"""
        year = FinancialYear(
            year_label='2024-2025',
            year_start=2024,
            year_end=2025
        )
        
        db_session.add(year)
        db_session.commit()
        
        retrieved = db_session.query(FinancialYear).filter_by(year_label='2024-2025').first()
        assert retrieved is not None
        assert retrieved.year_start == 2024
    
    def test_year_label_unique(self, db_session):
        """Test UNIQUE constraint on (year, quarter)"""
        y1 = FinancialYear(year_label='2024-2025', year_start=2024, year_end=2025)
        y2 = FinancialYear(year_label='2024-2025', year_start=2024, year_end=2025)
        
        db_session.add(y1)
        db_session.commit()
        
        db_session.add(y2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestNationalCoverageModel:
    """Test NationalCoverage fact table"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        """Create session with reference data"""
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        
        # Add required reference data
        area = GeographicArea(area_code='E92000001', area_name='England', area_type='country')
        vaccine = Vaccine(vaccine_code='MMR1', vaccine_name='MMR First Dose')
        cohort = AgeCohort(cohort_name='12 months', age_months=12)
        year = FinancialYear(year_label='2024-2025', year_start=2024, year_end=2025)
        
        session.add_all([area, vaccine, cohort, year])
        session.commit()
        
        yield session
        session.close()
    
    def test_create_national_coverage(self, db_session):
        """Test creating coverage record with FKs"""
        area = db_session.query(GeographicArea).first()
        vaccine = db_session.query(Vaccine).first()
        cohort = db_session.query(AgeCohort).first()
        year = db_session.query(FinancialYear).first()
        
        coverage = NationalCoverage(
            year_id=year.year_id,
            area_code=area.area_code,
            cohort_id=cohort.cohort_id,
            vaccine_id=vaccine.vaccine_id,
            coverage_percentage=95.5,
            eligible_population=100000,
            vaccinated_count=95500
        )
        
        db_session.add(coverage)
        db_session.commit()
        
        retrieved = db_session.query(NationalCoverage).first()
        assert retrieved is not None
        assert retrieved.coverage_percentage == 95.5
    
    def test_unique_constraint_on_coverage(self, db_session):
        """Test UNIQUE constraint on (year, area, cohort, vaccine)"""
        area = db_session.query(GeographicArea).first()
        vaccine = db_session.query(Vaccine).first()
        cohort = db_session.query(AgeCohort).first()
        year = db_session.query(FinancialYear).first()
        
        c1 = NationalCoverage(
            year_id=year.year_id, area_code=area.area_code,
            cohort_id=cohort.cohort_id, vaccine_id=vaccine.vaccine_id,
            coverage_percentage=95.5
        )
        
        c2 = NationalCoverage(
            year_id=year.year_id, area_code=area.area_code,
            cohort_id=cohort.cohort_id, vaccine_id=vaccine.vaccine_id,
            coverage_percentage=96.0  # Different value, same keys
        )
        
        db_session.add(c1)
        db_session.commit()
        
        db_session.add(c2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_foreign_key_relationships(self, db_session):
        """Test FK relationships work"""
        area = db_session.query(GeographicArea).first()
        vaccine = db_session.query(Vaccine).first()
        cohort = db_session.query(AgeCohort).first()
        year = db_session.query(FinancialYear).first()
        
        coverage = NationalCoverage(
            year_id=year.year_id, area_code=area.area_code,
            cohort_id=cohort.cohort_id, vaccine_id=vaccine.vaccine_id,
            coverage_percentage=95.5
        )
        
        db_session.add(coverage)
        db_session.commit()
        
        # Access via relationships
        retrieved = db_session.query(NationalCoverage).first()
        assert retrieved.geographic_area.area_name == 'England'
        assert retrieved.vaccine.vaccine_code == 'MMR1'
        assert retrieved.age_cohort.age_months == 12
        assert retrieved.financial_year.year_start == 2024
