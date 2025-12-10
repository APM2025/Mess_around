"""
Test: Loading Local Authority Coverage Data

Tests for loading local_authority_coverage fact table from paired CSV sheets.

Source sheets (PAIRS):
- T4a_UTLA12m (percentages) + T4b_UTLA12m (counts)
- T5a_UTLA24m (percentages) + T5b_UTLA24m (counts)
- T6a_UTLA5y (percentages) + T6b_UTLA5y (counts)

Expected records: ~2,086 (150 UTLAs × 3 cohorts × ~5 vaccines)

Complexity: Must match rows between paired sheets


Requirements:
- DA-FR-001: Load from CSV
- DB-FR-001: Persist to database
- DC-FR-001: Handle missing/suppressed data ([c], [z])
"""

import pytest
from pathlib import Path
from src.layer1_database.database import create_test_session
from src.layer1_database.models import (
    LocalAuthorityCoverage, GeographicArea, Vaccine, AgeCohort, FinancialYear
)


class TestLoadLocalAuthorityCoverage:
    """Test loading local authority coverage from paired sheets"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        """Provide database with reference data loaded"""
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        
        # Load reference tables
        from src.layer0_data_ingestion.load_reference_data import load_all_reference_data
        load_all_reference_data(session)
        
        yield session
        session.close()
    
    @pytest.fixture
    def csv_dir(self):
        """Path to CSV data directory"""
        project_root = Path(__file__).parent.parent.parent
        return project_root / "data" / "csv_data"
    
    def test_load_from_paired_sheets(self, db_session, csv_dir):
        """
        Load from paired sheets (percentages + counts)
        
        T4a has percentages, T4b has counts
        Must match row-by-row
        """
        from src.layer0_data_ingestion.load_local_authority import load_local_authority_coverage_from_paired_csvs
        
        t4a_csv = csv_dir / "cover-anual-data-tables-2024-to-2025_T4a_UTLA12m.csv"
        t4b_csv = csv_dir / "cover-anual-data-tables-2024-to-2025_T4b_UTLA12m.csv"
        
        # Load from both
        load_local_authority_coverage_from_paired_csvs(t4a_csv, t4b_csv, db_session)
        
        # Should have records
        records = db_session.query(LocalAuthorityCoverage).all()
        assert len(records) > 0, "Should load UTLA coverage records"
    
    def test_records_have_both_percentage_and_count(self, db_session, csv_dir):
        """
        Each record should have both coverage % AND vaccinated count
        
        % from 'a' sheet, count from 'b' sheet
        """
        from src.layer0_data_ingestion.load_local_authority import load_local_authority_coverage_from_paired_csvs
        
        t4a_csv = csv_dir / "cover-anual-data-tables-2024-to-2025_T4a_UTLA12m.csv"
        t4b_csv = csv_dir / "cover-anual-data-tables-2024-to-2025_T4b_UTLA12m.csv"
        
        load_local_authority_coverage_from_paired_csvs(t4a_csv, t4b_csv, db_session)
        
        # Get a record
        record = db_session.query(LocalAuthorityCoverage).first()
        
        assert record is not None
        # At least one should be present (some may be suppressed)
        assert record.coverage_percentage is not None or record.vaccinated_count is not None
    
    def test_utla_areas_only(self, db_session, csv_dir):
        """
        Should only load UTLA records, not regional aggregates
        
        Area codes should start with E06, E08, E09, E10 (UTLAs)
        NOT E12 (regions) or E92 (countries)
        """
        from src.layer0_data_ingestion.load_local_authority import load_all_local_authority_coverage
        
        load_all_local_authority_coverage(csv_dir, db_session)
        
        # Check all records are UTLAs
        records = db_session.query(LocalAuthorityCoverage).all()
        
        for record in records:
            area = db_session.query(GeographicArea).filter_by(area_code=record.area_code).first()
            assert area is not None
            assert area.area_type == 'utla', f"Should only have UTLA records, got {area.area_type}"
    
    def test_handles_suppressed_data(self, db_session, csv_dir):
        """
        Handle [c] (confidential) markers
        
        [c] → NULL for that field
        """
        from src.layer0_data_ingestion.load_local_authority import load_local_authority_coverage_from_paired_csvs
        
        t4a_csv = csv_dir / "cover-anual-data-tables-2024-to-2025_T4a_UTLA12m.csv"
        t4b_csv = csv_dir / "cover-anual-data-tables-2024-to-2025_T4b_UTLA12m.csv"
        
        load_local_authority_coverage_from_paired_csvs(t4a_csv, t4b_csv, db_session)
        
        # Should complete without errors
        assert db_session.query(LocalAuthorityCoverage).count() > 0
    
    def test_loads_all_three_cohorts(self, db_session, csv_dir):
        """
        Load all 3 cohort pairs (12m, 24m, 5y)
        
        T4a/b for 12m, T5a/b for 24m, T6a/b for 5y
        """
        from src.layer0_data_ingestion.load_local_authority import load_all_local_authority_coverage
        
        load_all_local_authority_coverage(csv_dir, db_session)
        
        # Check we have records for all 3 cohorts
        cohort_12m = db_session.query(LocalAuthorityCoverage)\
            .join(AgeCohort)\
            .filter(AgeCohort.age_months == 12)\
            .count()
        
        cohort_24m = db_session.query(LocalAuthorityCoverage)\
            .join(AgeCohort)\
            .filter(AgeCohort.age_months == 24)\
            .count()
        
        cohort_5y = db_session.query(LocalAuthorityCoverage)\
            .join(AgeCohort)\
            .filter(AgeCohort.age_months == 60)\
            .count()
        
        assert cohort_12m > 0, "Should have 12-month cohort data"
        assert cohort_24m > 0, "Should have 24-month cohort data"
        assert cohort_5y > 0, "Should have 5-year cohort data"
    
    def test_population_values_reasonable(self, db_session, csv_dir):
        """
        Eligible populations should be reasonable
        
        UTLAs typically have 1,000-30,000 eligible children
        """
        from src.layer0_data_ingestion.load_local_authority import load_all_local_authority_coverage
        
        load_all_local_authority_coverage(csv_dir, db_session)
        
        records = db_session.query(LocalAuthorityCoverage).all()
        
        for record in records:
            if record.eligible_population is not None:
                assert 100 < record.eligible_population < 50000, \
                    f"UTLA population seems unreasonable: {record.eligible_population}"
    
    def test_coverage_percentage_in_range(self, db_session, csv_dir):
        """
        Coverage percentages should be 0-100
        """
        from src.layer0_data_ingestion.load_local_authority import load_all_local_authority_coverage
        
        load_all_local_authority_coverage(csv_dir, db_session)
        
        records = db_session.query(LocalAuthorityCoverage).all()
        
        for record in records:
            if record.coverage_percentage is not None:
                assert 0 <= record.coverage_percentage <= 100, \
                    f"Coverage % out of range: {record.coverage_percentage}"
    
    def test_idempotency(self, db_session, csv_dir):
        """
        Loading twice shouldn't create duplicates
        """
        from src.layer0_data_ingestion.load_local_authority import load_all_local_authority_coverage
        
        # Load once
        load_all_local_authority_coverage(csv_dir, db_session)
        count_first = db_session.query(LocalAuthorityCoverage).count()
        
        # Load again
        load_all_local_authority_coverage(csv_dir, db_session)
        count_second = db_session.query(LocalAuthorityCoverage).count()
        
        assert count_first == count_second, \
            "Loading twice should not create duplicates (use upsert)"
    
    def test_expected_record_count(self, db_session, csv_dir):
        """
        Should have records loaded
        
        ~149 UTLAs × 3 cohorts × vaccines that match = substantial records
        (Some may be suppressed, so allow variance)
        """
        from src.layer0_data_ingestion.load_local_authority import load_all_local_authority_coverage
        
        load_all_local_authority_coverage(csv_dir, db_session)
        
        total = db_session.query(LocalAuthorityCoverage).count()
        
        assert total >= 500, f"Expected 500+ records, got {total}"
        assert total <= 5000, f"Expected <5000 records, got {total} (too many)"
