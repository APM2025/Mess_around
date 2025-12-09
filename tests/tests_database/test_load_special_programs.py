"""
Test: Loading Special Programs Data

Tests for loading special vaccination programs (HepB, BCG).

Source sheets:
- T7_UTLAHepB: Hepatitis B for eligible children
- T8_UTLABCG: BCG for eligible children

Structure: Similar to LOCAL_AUTHORITY with UTLA coverage data

"""

import pytest
from pathlib import Path
from backend_code.database_src.database import create_test_session
from backend_code.database_src.models import (
    SpecialProgram, Vaccine, AgeCohort, FinancialYear, GeographicArea
)


class TestLoadSpecialProgram:
    """Test loading special programs data"""
    
    @pytest.fixture
    def db_session(self, tmp_path):
        """Provide clean test database with reference data"""
        db_path = tmp_path / "test.db"
        session = create_test_session(db_path)
        
        # Load reference data
        from backend_code.database_src.load_reference_data import load_all_reference_data
        load_all_reference_data(session)
        
        yield session
        session.close()
    
    @pytest.fixture
    def csv_dir(self):
        """Path to CSV data directory"""
        return Path("data/csv_data")
    
    def test_load_special_program_from_single_sheet(self, db_session, csv_dir):
        """Load special programs from T7 sheet"""
        from backend_code.database_src.load_special_programs import (
            load_special_programs_from_csv
        )
        
        csv_path = csv_dir / "cover-anual-data-tables-2024-to-2025_T7_UTLAHepB.csv"
        load_special_programs_from_csv(csv_path, db_session)
        
        # Should have records
        records = db_session.query(SpecialProgram).all()
        assert len(records) > 0, "Should load special programs records"
    
    def test_special_programs_has_valid_foreign_keys(self, db_session, csv_dir):
        """Verify FK relationships"""
        from backend_code.database_src.load_special_programs import (
            load_special_programs_from_csv
        )
        
        csv_path = csv_dir / "cover-anual-data-tables-2024-to-2025_T7_UTLAHepB.csv"
        load_special_programs_from_csv(csv_path, db_session)
        
        record = db_session.query(SpecialProgram).first()
        
        # Check relationships exist (SpecialProgram doesn't have vaccine FK)
        assert record.financial_year is not None
        assert record.geographic_area is not None
        assert record.age_cohort is not None
    
    def test_coverage_percentage_in_valid_range(self, db_session, csv_dir):
        """Coverage should be 0-100"""
        from backend_code.database_src.load_special_programs import (
            load_special_programs_from_csv
        )
        
        csv_path = csv_dir / "cover-anual-data-tables-2024-to-2025_T7_UTLAHepB.csv"
        load_special_programs_from_csv(csv_path, db_session)
        
        for record in db_session.query(SpecialProgram).all():
            if record.coverage_percentage is not None:
                assert 0 <= record.coverage_percentage <= 100, \
                    f"Coverage % out of range: {record.coverage_percentage}"
    
    def test_program_type_is_set(self, db_session, csv_dir):
        """Program type should be HepB or BCG"""
        from backend_code.database_src.load_special_programs import (
            load_all_special_programs
        )
        
        load_all_special_programs(csv_dir, db_session)
        
        # Check program types
        program_types = db_session.query(SpecialProgram.program_type).distinct().all()
        types = [t[0] for t in program_types]
        
        assert 'HepB' in types or 'BCG' in types, "Should have HepB or BCG program type"
    
    def test_loads_both_programs(self, db_session, csv_dir):
        """Load both T7 (HepB) and T8 (BCG)"""
        from backend_code.database_src.load_special_programs import (
            load_all_special_programs
        )
        
        load_all_special_programs(csv_dir, db_session)
        
        # Should have records from both programs
        program_types = db_session.query(SpecialProgram.program_type).distinct().all()
        types = [t[0] for t in program_types]
        
        assert len(types) >= 2, "Should have multiple program types loaded"
    
    def test_idempotency_no_duplicates(self, db_session, csv_dir):
        """Loading twice shouldn't create duplicates"""
        from backend_code.database_src.load_special_programs import (
            load_all_special_programs
        )
        
        load_all_special_programs(csv_dir, db_session)
        count1 = db_session.query(SpecialProgram).count()
        
        load_all_special_programs(csv_dir, db_session)
        count2 = db_session.query(SpecialProgram).count()
        
        assert count1 == count2, "Should not create duplicates on re-load"
    
    def test_eligible_population_present(self, db_session, csv_dir):
        """Eligible population should be present"""
        from backend_code.database_src.load_special_programs import (
            load_special_programs_from_csv
        )
        
        csv_path = csv_dir / "cover-anual-data-tables-2024-to-2025_T7_UTLAHepB.csv"
        load_special_programs_from_csv(csv_path, db_session)
        
        records_with_pop = db_session.query(SpecialProgram).filter(
            SpecialProgram.eligible_population.isnot(None)
        ).count()
        
        assert records_with_pop > 0, "Should have records with eligible population"

