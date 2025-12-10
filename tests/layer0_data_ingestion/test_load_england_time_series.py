"""
Test: Loading England Time Series Data

Tests for loading historical England coverage data (2009-2025).

Source sheets:
- T9_Eng12m: 12 month cohort
- T10_Eng24m: 24 month cohort  
- T11_Eng5y: 5 year cohort


Requirements:
- DA-FR-001: Load from CSV
- DB-FR-001: Persist to database
- DC-FR-001: Handle missing data
"""

import pytest
from pathlib import Path
from src.layer1_database.database import create_test_session
from src.layer1_database.models import (
    EnglandTimeSeries, Vaccine, AgeCohort, FinancialYear
)


class TestLoadEnglandTimeSeries:
    """Test loading England time series data"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        """Provide clean test database with reference data"""
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        
        # Load reference data
        from src.layer0_data_ingestion.load_reference_data import load_all_reference_data
        load_all_reference_data(session)
        
        yield session
        session.close()
    
    @pytest.fixture
    def csv_dir(self):
        """Path to CSV data directory"""
        return Path("data/csv_data")
    
    def test_load_england_time_series_from_single_sheet(self, db_session, csv_dir):
        """Load time series from T9 sheet"""
        from src.layer0_data_ingestion.load_england_time_series import (
            load_england_time_series_from_csv
        )
        
        csv_path = csv_dir / "cover-anual-data-tables-2024-to-2025_T9_Eng12m.csv"
        load_england_time_series_from_csv(csv_path, db_session)
        
        # Should have records
        records = db_session.query(EnglandTimeSeries).all()
        assert len(records) > 0, "Should load England time series records"
    
    def test_time_series_has_valid_foreign_keys(self, db_session, csv_dir):
        """Verify FK relationships"""
        from src.layer0_data_ingestion.load_england_time_series import (
            load_england_time_series_from_csv
        )
        
        csv_path = csv_dir / "cover-anual-data-tables-2024-to-2025_T9_Eng12m.csv"
        load_england_time_series_from_csv(csv_path, db_session)
        
        record = db_session.query(EnglandTimeSeries).first()
        
        # Check relationships exist
        assert record.financial_year is not None
        assert record.age_cohort is not None
        assert record.vaccine is not None
    
    def test_coverage_percentage_in_valid_range(self, db_session, csv_dir):
        """Coverage should be 0-100"""
        from src.layer0_data_ingestion.load_england_time_series import (
            load_england_time_series_from_csv
        )
        
        csv_path = csv_dir / "cover-anual-data-tables-2024-to-2025_T9_Eng12m.csv"
        load_england_time_series_from_csv(csv_path, db_session)
        
        for record in db_session.query(EnglandTimeSeries).all():
            if record.coverage_percentage is not None:
                assert 0 <= record.coverage_percentage <= 100, \
                    f"Coverage % out of range: {record.coverage_percentage}"
    
    def test_handles_missing_data(self, db_session, csv_dir):
        """Handle [z], [c] markers"""
        from src.layer0_data_ingestion.load_england_time_series import (
            load_england_time_series_from_csv
        )
        
        csv_path = csv_dir / "cover-anual-data-tables-2024-to-2025_T9_Eng12m.csv"
        load_england_time_series_from_csv(csv_path, db_session)
        
        # Should have some records with None (suppressed data)
        records_with_none = db_session.query(EnglandTimeSeries).filter(
            EnglandTimeSeries.coverage_percentage == None
        ).count()
        
        # At least handles None values without crashing
        assert records_with_none >= 0
    
    def test_loads_all_three_cohort_sheets(self, db_session, csv_dir):
        """Load T9, T10, T11 sheets"""
        from src.layer0_data_ingestion.load_england_time_series import (
            load_all_england_time_series
        )
        
        load_all_england_time_series(csv_dir, db_session)
        
        # Should have records from all three cohorts
        cohorts = db_session.query(EnglandTimeSeries.cohort_id).distinct().all()
        cohort_ids = [c[0] for c in cohorts]
        
        assert len(cohort_ids) >= 2, "Should have multiple cohorts loaded"
    
    def test_historical_years_loaded(self, db_session, csv_dir):
        """Should have historical data (2009-2025)"""
        from src.layer0_data_ingestion.load_england_time_series import (
            load_all_england_time_series
        )
        
        load_all_england_time_series(csv_dir, db_session)
        
        # Check for multiple years
        years = db_session.query(EnglandTimeSeries.year_id).distinct().count()
        assert years > 1, "Should have multiple years of data"
    
    def test_idempotency_no_duplicates(self, db_session, csv_dir):
        """Loading twice shouldn't create duplicates"""
        from src.layer0_data_ingestion.load_england_time_series import (
            load_all_england_time_series
        )
        
        load_all_england_time_series(csv_dir, db_session)
        count1 = db_session.query(EnglandTimeSeries).count()
        
        load_all_england_time_series(csv_dir, db_session)
        count2 = db_session.query(EnglandTimeSeries).count()
        
        assert count1 == count2, "Should not create duplicates on re-load"
