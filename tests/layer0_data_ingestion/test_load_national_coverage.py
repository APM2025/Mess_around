"""
Test: Loading National Coverage Data

Tests for loading national_coverage fact table from CSV sheets.

Source sheets: T1_UK12m, T2_UK24m, T3_UK5y
Expected records: ~70 (4 countries × 3 cohorts × ~6 vaccines)


Requirements:
- DA-FR-001: Load from CSV
- DB-FR-001: Persist to database
- DC-FR-001: Handle missing data
"""

import pytest
from pathlib import Path
from src.layer1_database.database import create_test_session
from src.layer1_database.models import (
    NationalCoverage, GeographicArea, Vaccine, AgeCohort, FinancialYear
)


class TestLoadNationalCoverage:
    """Test loading national coverage data from CSV sheets"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        """Provide database with reference data already loaded"""
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        
        # Load reference tables first (required for FKs)
        from src.layer0_data_ingestion.load_reference_data import load_all_reference_data
        load_all_reference_data(session)
        
        yield session
        session.close()
    
    @pytest.fixture
    def csv_dir(self):
        """Path to CSV data directory"""
        project_root = Path(__file__).parent.parent.parent
        return project_root / "data" / "csv_data"
    
    def test_load_national_coverage_from_t1_sheet(self, db_session, csv_dir):
        """
        Load national coverage from T1_UK12m sheet
        
        T1 = UK level, 12 month cohort
        Should extract: Countries, vaccines, coverage percentages
        """
        from src.layer0_data_ingestion.load_national_coverage import load_national_coverage_from_csv
        
        t1_csv = csv_dir / "cover-anual-data-tables-2024-to-2025_T1_UK12m.csv"
        
        # Load data
        load_national_coverage_from_csv(t1_csv, db_session)
        
        # Verify records created
        records = db_session.query(NationalCoverage).all()
        assert len(records) > 0, "Should load national coverage records"
    
    def test_coverage_has_valid_foreign_keys(self, db_session, csv_dir):
        """
        Verify all FKs reference valid records
        
        Every coverage record must link to:
        - Valid geographic area
        - Valid vaccine
        - Valid age cohort
        - Valid financial year
        """
        from src.layer0_data_ingestion.load_national_coverage import load_national_coverage_from_csv
        
        t1_csv = csv_dir / "cover-anual-data-tables-2024-to-2025_T1_UK12m.csv"
        load_national_coverage_from_csv(t1_csv, db_session)
        
        # Check one record's relationships work
        record = db_session.query(NationalCoverage).first()
        
        assert record.geographic_area is not None, "Should link to geographic area"
        assert record.vaccine is not None, "Should link to vaccine"
        assert record.age_cohort is not None, "Should link to age cohort"
        assert record.financial_year is not None, "Should link to financial year"
    
    def test_coverage_percentage_in_valid_range(self, db_session, csv_dir):
        """
        Verify coverage percentages are between 0-100
        
        Requirement: DC-FR-001 (Data validation)
        """
        from src.layer0_data_ingestion.load_national_coverage import load_national_coverage_from_csv
        
        t1_csv = csv_dir / "cover-anual-data-tables-2024-to-2025_T1_UK12m.csv"
        load_national_coverage_from_csv(t1_csv, db_session)
        
        records = db_session.query(NationalCoverage).all()
        
        for record in records:
            if record.coverage_percentage is not None:
                assert 0 <= record.coverage_percentage <= 100, \
                    f"Coverage % must be 0-100, got {record.coverage_percentage}"
    
    def test_handles_missing_data(self, db_session, csv_dir):
        """
        Test handling of missing/suppressed data
        
        Some cells may be:
        - Empty (NULL)
        - [z] (not applicable)
        - [c] (confidential)
        
        Requirement: DC-FR-001 (Handle missing data)
        """
        from src.layer0_data_ingestion.load_national_coverage import load_national_coverage_from_csv
        
        t1_csv = csv_dir / "cover-anual-data-tables-2024-to-2025_T1_UK12m.csv"
        load_national_coverage_from_csv(t1_csv, db_session)
        
        # Should complete without errors even with missing data
        records = db_session.query(NationalCoverage).all()
        assert len(records) > 0, "Should load records despite missing data"
    
    def test_loads_all_three_cohort_sheets(self, db_session, csv_dir):
        """
        Load all 3 national sheets (12m, 24m, 5y)
        
        T1_UK12m, T2_UK24m, T3_UK5y
        """
        from src.layer0_data_ingestion.load_national_coverage import load_all_national_coverage
        
        # Load all three sheets
        load_all_national_coverage(csv_dir, db_session)
        
        # Should have records for all 3 cohorts
        cohort_12m = db_session.query(NationalCoverage)\
            .join(AgeCohort)\
            .filter(AgeCohort.age_months == 12)\
            .count()
        
        cohort_24m = db_session.query(NationalCoverage)\
            .join(AgeCohort)\
            .filter(AgeCohort.age_months == 24)\
            .count()
        
        cohort_5y = db_session.query(NationalCoverage)\
            .join(AgeCohort)\
            .filter(AgeCohort.age_months == 60)\
            .count()
        
        assert cohort_12m > 0, "Should have 12-month cohort data"
        assert cohort_24m > 0, "Should have 24-month cohort data"
        assert cohort_5y > 0, "Should have 5-year cohort data"
    
    def test_england_data_loaded(self, db_session, csv_dir):
        """
        Verify England coverage data is loaded
        """
        from src.layer0_data_ingestion.load_national_coverage import load_all_national_coverage
        
        load_all_national_coverage(csv_dir, db_session)
        
        # Check England records exist
        england_records = db_session.query(NationalCoverage)\
            .join(GeographicArea)\
            .filter(GeographicArea.area_name == 'England')\
            .count()
        
        assert england_records > 0, "Should have coverage data for England"
    
    def test_idempotency_no_duplicates(self, db_session, csv_dir):
        """
        Loading twice shouldn't create duplicates
        
        Requirement: DB-FR-005 (Data integrity)
        """
        from src.layer0_data_ingestion.load_national_coverage import load_all_national_coverage
        
        # Load once
        load_all_national_coverage(csv_dir, db_session)
        count_first = db_session.query(NationalCoverage).count()
        
        # Load again
        load_all_national_coverage(csv_dir, db_session)
        count_second = db_session.query(NationalCoverage).count()
        
        assert count_first == count_second, \
            "Loading twice should not create duplicates (should use upsert)"
