"""
Test: Loading Regional Time Series Data

Tests for loading regional coverage data over time (2009-2025).

Source sheets:
- T14_RegDTaP24m: DTaP coverage by region
- T15_RegMMR24m: MMR coverage by region

Structure: Years in rows, regions in columns

"""

import pytest
from pathlib import Path
from src.database import create_test_session
from src.models import (
    RegionalTimeSeries, Vaccine, AgeCohort, FinancialYear, GeographicArea
)


class TestLoadRegionalTimeSeries:
    """Test loading regional time series data"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        """Provide clean test database with reference data"""
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        
        # Load reference data
        from src.load_reference_data import load_all_reference_data
        load_all_reference_data(session)
        
        yield session
        session.close()
    
    @pytest.fixture
    def csv_dir(self):
        """Path to CSV data directory"""
        return Path("data/csv_data")
    
    def test_load_regional_time_series_from_single_sheet(self, db_session, csv_dir):
        """Load regional time series from T14 sheet"""
        from src.load_regional_time_series import (
            load_regional_time_series_from_csv
        )
        
        csv_path = csv_dir / "cover-anual-data-tables-2024-to-2025_T14_RegDTaP24m.csv"
        load_regional_time_series_from_csv(csv_path, db_session)
        
        # Should have records
        records = db_session.query(RegionalTimeSeries).all()
        assert len(records) > 0, "Should load regional time series records"
    
    def test_time_series_has_valid_foreign_keys(self, db_session, csv_dir):
        """Verify FK relationships"""
        from src.load_regional_time_series import (
            load_regional_time_series_from_csv
        )
        
        csv_path = csv_dir / "cover-anual-data-tables-2024-to-2025_T14_RegDTaP24m.csv"
        load_regional_time_series_from_csv(csv_path, db_session)
        
        record = db_session.query(RegionalTimeSeries).first()
        
        # Check relationships exist
        assert record.financial_year is not None
        assert record.geographic_area is not None
        assert record.age_cohort is not None
        assert record.vaccine is not None
    
    def test_coverage_percentage_in_valid_range(self, db_session, csv_dir):
        """Coverage should be 0-100"""
        from src.load_regional_time_series import (
            load_regional_time_series_from_csv
        )
        
        csv_path = csv_dir / "cover-anual-data-tables-2024-to-2025_T14_RegDTaP24m.csv"
        load_regional_time_series_from_csv(csv_path, db_session)
        
        for record in db_session.query(RegionalTimeSeries).all():
            if record.coverage_percentage is not None:
                assert 0 <= record.coverage_percentage <= 100, \
                    f"Coverage % out of range: {record.coverage_percentage}"
    
    def test_multiple_regions_loaded(self, db_session, csv_dir):
        """Should have data for multiple regions"""
        from src.load_regional_time_series import (
            load_regional_time_series_from_csv
        )
        
        csv_path = csv_dir / "cover-anual-data-tables-2024-to-2025_T14_RegDTaP24m.csv"
        load_regional_time_series_from_csv(csv_path, db_session)
        
        # Check for multiple regions
        regions = db_session.query(RegionalTimeSeries.area_code).distinct().all()
        region_codes = [r[0] for r in regions]
        
        assert len(region_codes) >= 2, "Should have multiple regions"
    
    def test_historical_years_loaded(self, db_session, csv_dir):
        """Should have historical data (2009-2025)"""
        from src.load_regional_time_series import (
            load_all_regional_time_series
        )
        
        load_all_regional_time_series(csv_dir, db_session)
        
        # Check for multiple years
        years = db_session.query(RegionalTimeSeries.year_id).distinct().count()
        assert years > 1, "Should have multiple years of data"
    
    def test_loads_both_vaccine_sheets(self, db_session, csv_dir):
        """Load T14 and T15 sheets"""
        from src.load_regional_time_series import (
            load_all_regional_time_series
        )
        
        load_all_regional_time_series(csv_dir, db_session)
        
        # Should have records from multiple vaccines
        vaccines = db_session.query(RegionalTimeSeries.vaccine_id).distinct().all()
        vaccine_ids = [v[0] for v in vaccines]
        
        assert len(vaccine_ids) >= 2, "Should have multiple vaccines loaded"
    
    def test_idempotency_no_duplicates(self, db_session, csv_dir):
        """Loading twice shouldn't create duplicates"""
        from src.load_regional_time_series import (
            load_all_regional_time_series
        )
        
        load_all_regional_time_series(csv_dir, db_session)
        count1 = db_session.query(RegionalTimeSeries).count()
        
        load_all_regional_time_series(csv_dir, db_session)
        count2 = db_session.query(RegionalTimeSeries).count()
        
        assert count1 == count2, "Should not create duplicates on re-load"
