"""
Tests for CSV cleaning functions.

Covers:
- Finding header rows in messy CSVs
- Extracting vaccine names from headers
- Cleaning numeric values (commas, markers, ranges)
- Parsing note references
- Identifying data vs metadata rows

Requirements:
- DC-FR-001: Handle missing/inconsistent data
- DC-FR-002: Convert to correct types
"""

import pytest
import pandas as pd
from pathlib import Path


class TestFindHeaderRow:
    """Test finding the data header row in messy CSV"""
    
    @pytest.fixture
    def t1_csv_path(self):
        """Path to T1_UK12m CSV"""
        return Path("data/csv_data/cover-anual-data-tables-2024-to-2025_T1_UK12m.csv")
    
    def test_find_header_row_in_t1(self, t1_csv_path):
        """Find header row in T1 CSV structure."""
        from database_version_2.src.csv_cleaner import find_header_row
        
        header_row_index = find_header_row(t1_csv_path, indicator="Geographic")
        
        assert header_row_index is not None, "Should find header row"
        assert header_row_index >= 0, "Header row index should be valid"
        assert header_row_index < 10, "Header should be in first 10 rows"
    
    def test_find_header_row_returns_dataframe_index(self, t1_csv_path):
        """Verify returned index works with pandas DataFrame."""
        from database_version_2.src.csv_cleaner import find_header_row
        
        df = pd.read_csv(t1_csv_path, header=None)
        header_idx = find_header_row(t1_csv_path, indicator="Geographic")
        
        # Should be able to use this index
        header_row = df.iloc[header_idx]
        assert header_row is not None


class TestExtractVaccineNames:
    """Test extracting vaccine names from column headers"""
    
    def test_extract_vaccine_from_header(self):
        """Extract vaccine name from column header text."""
        from database_version_2.src.csv_cleaner import extract_vaccine_name
        
        header = "Coverage at 12 months DTaP/IPV/Hib/HepB (%)"
        vaccine_name = extract_vaccine_name(header)
        
        assert vaccine_name == "DTaP/IPV/Hib/HepB"
    
    def test_handle_booster_suffix(self):
        """Preserve 'booster' suffix in vaccine names."""
        from database_version_2.src.csv_cleaner import extract_vaccine_name
        
        header = "Coverage at 24 months PCV booster (%)"
        vaccine_name = extract_vaccine_name(header)
        
        assert "booster" in vaccine_name.lower()
    
    def test_remove_prim_suffix(self):
        """Remove 'Prim' suffix from vaccine names."""
        from database_version_2.src.csv_cleaner import extract_vaccine_name
        
        header = "DTaP/IPV/Hib/HepB Prim"
        vaccine_name = extract_vaccine_name(header)
        
        assert "Prim" not in vaccine_name
        assert vaccine_name == "DTaP/IPV/Hib/HepB"


class TestCleanNumericValues:
    """Test cleaning numeric values from CSV"""
    
    def test_remove_commas_from_number(self):
        """Remove commas from numeric values."""
        from database_version_2.src.csv_cleaner import clean_numeric_value
        
        result = clean_numeric_value('668,160')
        
        assert result == 668160
        assert isinstance(result, int)
    
    def test_handle_z_marker(self):
        """Convert [z] marker to None."""
        from database_version_2.src.csv_cleaner import clean_numeric_value
        
        result = clean_numeric_value('[z]')
        
        assert result is None
    
    def test_handle_c_marker(self):
        """Convert [c] (confidential) marker to None."""
        from database_version_2.src.csv_cleaner import clean_numeric_value
        
        result = clean_numeric_value('[c]')
        
        assert result is None
    
    def test_handle_percentage_range(self):
        """Handle percentage range format."""
        from database_version_2.src.csv_cleaner import clean_numeric_value
        
        result = clean_numeric_value("35% to 69%", return_range=True)
        
        assert result == (None, "35% to 69%")
    
    def test_round_long_decimals(self):
        """Round long decimals to 2 places."""
        from database_version_2.src.csv_cleaner import clean_numeric_value
        
        result = clean_numeric_value(94.03672966891358, decimal_places=2)
        
        assert result == 94.04
    
    def test_handle_plain_numbers(self):
        """Verify plain numbers pass through unchanged."""
        from database_version_2.src.csv_cleaner import clean_numeric_value
        
        assert clean_numeric_value(95.5) == 95.5
        assert clean_numeric_value(1000) == 1000


class TestParseNoteReferences:
    """Test parsing note references like [note 23]"""
    
    def test_extract_note_number(self):
        """Extract note number from reference marker."""
        from database_version_2.src.csv_cleaner import parse_note_reference
        
        note_num = parse_note_reference('[note 23]')
        
        assert note_num == 23
    
    def test_return_none_for_non_notes(self):
        """Return None for non-note values."""
        from database_version_2.src.csv_cleaner import parse_note_reference
        
        assert parse_note_reference('England') is None
        assert parse_note_reference('95.5') is None


class TestIdentifyRowType:
    """Test identifying data vs metadata rows"""
    
    def test_identify_data_row(self):
        """Identify rows with valid area codes as data rows."""
        from database_version_2.src.csv_cleaner import is_data_row
        
        # Row starting with area code
        assert is_data_row(['E92000001', 'England', '668,160', '91.7']) == True
    
    def test_identify_empty_row(self):
        """Identify empty rows as non-data."""
        from database_version_2.src.csv_cleaner import is_data_row
        
        assert is_data_row([]) == False
        assert is_data_row([None, None, None]) == False
        assert is_data_row(['', '', '']) == False
    
    def test_identify_header_row(self):
        """Identify header rows as non-data."""
        from database_version_2.src.csv_cleaner import is_data_row
        
        header = ['Geographic area', 'Notes', 'Number aged 12 months']
        assert is_data_row(header) == False


class TestLoadCleanedCSV:
    """Integration test: Load and clean entire CSV"""
    
    @pytest.fixture
    def t1_csv_path(self):
        return Path("data/csv_data/cover-anual-data-tables-2024-to-2025_T1_UK12m.csv")
    
    def test_load_cleaned_t1_csv(self, t1_csv_path):
        """Load and clean complete CSV file."""
        from database_version_2.src.csv_cleaner import load_cleaned_csv
        
        df = load_cleaned_csv(t1_csv_path, sheet_type='national')
        
        assert df is not None
        assert len(df) > 0, "Should have data rows"
        assert 'area_name' in df.columns or df.columns[0] != '', "Should have column names"
        
        # Should have UK countries
        if 'area_name' in df.columns:
            assert 'England' in df['area_name'].values
