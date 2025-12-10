"""
Test: Database Connection Utilities

Tests for database.py - session management and initialization

Tests:
- Session creation (test and production)
- Database initialization
- Foreign key constraint enforcement
- Transaction handling

Requirements:
- DB-NFR-001: Testable database operations
- DB-NFR-002: Configurable connection
"""

import pytest
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from src.layer1_database.database import (
    create_test_session, create_production_session, get_session
)
from src.layer1_database.models import (
    GeographicArea, Vaccine, init_database, Base
)


class TestSessionCreation:
    """Test database session creation functions"""
    
    def test_create_test_session(self, tmp_path):
        """Test creating a test session with temp database"""
        db_path = tmp_path / "test.db"
        
        session = create_test_session(db_path)
        
        assert session is not None, "Should return a valid session"
        assert session.is_active, "Session should be active"
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(session.bind)
        tables = inspector.get_table_names()
        
        assert 'geographic_areas' in tables, "Tables should be initialized"
        
        session.close()
    
    def test_create_production_session(self, tmp_path):
        """Test creating production session"""
        db_path = tmp_path / "production.db"
        
        session = create_production_session(str(db_path))
        
        assert session is not None
        assert session.is_active
        
        session.close()
    
    def test_get_session_convenience_function(self, tmp_path):
        """Test get_session() convenience wrapper"""
        db_path = tmp_path / "test.db"
        
        session = get_session(str(db_path))
        
        assert session is not None
        assert session.is_active
        
        session.close()


class TestDatabaseInitialization:
    """Test database initialization"""
    
    def test_tables_created_on_init(self, tmp_path):
        """Test that init_database creates all tables"""
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        
        # Tables should already exist from session creation
        from sqlalchemy import inspect
        inspector = inspect(session.bind)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'geographic_areas', 'vaccines', 'age_cohorts', 'financial_years',
            'national_coverage', 'local_authority_coverage'
        ]
        
        for table in expected_tables:
            assert table in tables, f"Table {table} should be created"
        
        session.close()
    
    def test_init_database_is_idempotent(self, tmp_path):
        """Test calling init_database multiple times doesn't error"""
        db_path = tmp_path / "test.db"
        
        # Create once
        session1 = create_test_session(db_path)
        session1.close()
        
        # Create again - should not error
        session2 = create_test_session(db_path)
        session2.close()
        
        # Should succeed without errors


class TestForeignKeyConstraints:
    """Test that foreign key constraints are enforced"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        """Provide clean test database"""
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        yield session
        session.close()
    
    def test_foreign_keys_enabled_in_sqlite(self, db_session):
        """Test that PRAGMA foreign_keys=ON is set"""
        result = db_session.execute(text("PRAGMA foreign_keys")).fetchone()
        
        # Result should be (1,) if enabled, (0,) if disabled
        assert result[0] == 1, "Foreign key constraints should be enabled"
    
    def test_foreign_key_violation_raises_error(self, db_session):
        """Test that violating FK constraint raises IntegrityError"""
        from src.layer1_database.models import NationalCoverage
        
        # Try to create coverage record with invalid FK
        coverage = NationalCoverage(
            year_id=9999,  # Non-existent
            area_code='INVALID',  # Non-existent
            cohort_id=9999,  # Non-existent
            vaccine_id=9999,  # Non-existent
            coverage_percentage=95.5
        )
        
        db_session.add(coverage)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestTransactionHandling:
    """Test transaction commit and rollback"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        """Provide clean test database"""
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        yield session
        session.close()
    
    def test_commit_persists_data(self, db_session):
        """Test that committed data is saved"""
        area = GeographicArea(
            area_code='E92000001',
            area_name='England',
            area_type='country'
        )
        
        db_session.add(area)
        db_session.commit()
        
        # Query in same session
        retrieved = db_session.query(GeographicArea).filter_by(area_code='E92000001').first()
        assert retrieved is not None
        assert retrieved.area_name == 'England'
    
    def test_rollback_undoes_changes(self, db_session):
        """Test that rollback prevents data from being saved"""
        area = GeographicArea(
            area_code='E92000001',
            area_name='England',
            area_type='country'
        )
        
        db_session.add(area)
        db_session.rollback()  # Undo the add
        
        # Should not exist after rollback
        retrieved = db_session.query(GeographicArea).filter_by(area_code='E92000001').first()
        assert retrieved is None, "Data should not persist after rollback"
    
    def test_failed_transaction_can_rollback(self, db_session):
        """Test rollback after failed transaction"""
        # Add valid record
        area1 = GeographicArea(area_code='E92000001', area_name='England', area_type='country')
        db_session.add(area1)
        db_session.commit()
        
        # Try to add duplicate (violates UNIQUE constraint)
        area2 = GeographicArea(area_code='E92000001', area_name='Duplicate', area_type='country')
        db_session.add(area2)
        
        try:
            db_session.commit()
        except IntegrityError:
            db_session.rollback()  # Clean up failed transaction
        
        # Session should still be usable
        count = db_session.query(GeographicArea).count()
        assert count == 1, "Should have only the first record"


class TestDatabasePathHandling:
    """Test database path creation and handling"""
    
    def test_creates_parent_directories(self, tmp_path):
        """Test that parent directories are created if needed"""
        nested_path = tmp_path / "nested" / "dir" / "test.db"
        
        session = create_test_session(nested_path)
        
        assert nested_path.exists(), "Database file should be created"
        assert nested_path.parent.exists(), "Parent directories should be created"
        
        session.close()
    
    def test_handles_string_and_path_objects(self, tmp_path):
        """Test that both string and Path objects work"""
        # Test with Path object
        db_path_obj = tmp_path / "test1.db"
        session1 = create_test_session(db_path_obj)
        assert session1 is not None
        session1.close()
        
        # Test with string
        db_path_str = str(tmp_path / "test2.db")
        session2 = create_production_session(db_path_str)
        assert session2 is not None
        session2.close()
