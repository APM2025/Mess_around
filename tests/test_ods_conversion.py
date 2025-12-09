"""
Test: ODS to CSV Conversion

Tests for converting ODS spreadsheet files to CSV format.
Updated to support multi-sheet conversion.

Requirements:
- DA-FR-002: Support multiple file formats (ODS → CSV)
"""

import pytest
from pathlib import Path


class TestODSConversion:
    """Test ODS-to-CSV conversion functionality"""
    
    @pytest.fixture
    def data_dir(self):
        """Fixture to provide the data directory path."""
        project_root = Path(__file__).parent.parent.parent
        return project_root / "data"
    
    @pytest.fixture
    def ods_filepath(self, data_dir):
        """Fixture to provide the ODS file path."""
        return data_dir / "ods_data" / "cover-anual-data-tables-2024-to-2025.ods"
    
    @pytest.fixture
    def csv_output_dir(self, data_dir):
        """Fixture to provide CSV output directory"""
        return data_dir / "csv_data"
    
    def test_ods_file_exists(self, ods_filepath):
        """
        Prerequisite: Verify the ODS file exists before conversion.
        """
        assert ods_filepath.exists(), f"ODS file not found at {ods_filepath}"
        assert ods_filepath.suffix == ".ods", "File should have .ods extension"
    
    def test_convert_single_sheet_to_csv(self, ods_filepath, tmp_path):
        """
        Test converting a single ODS sheet to CSV
        
        Requirement: DA-FR-001 - Load data from external file
        """
        from src.ods_to_csv import convert_ods_to_csv
        
        # Convert specific sheet (T1_UK12m)
        result_paths = convert_ods_to_csv(ods_filepath, sheet_name='T1_UK12m', output_dir=tmp_path)
        
        assert len(result_paths) == 1, "Should return one CSV file"
        assert result_paths[0].exists(), "CSV file should be created"
        assert result_paths[0].suffix == ".csv", "Output should be CSV"
    
    def test_convert_all_data_sheets(self, ods_filepath, tmp_path):
        """
        Test converting all data sheets from ODS
        
        Requirement: DA-FR-002 - Support multiple formats
        """
        from src.ods_to_csv import convert_all_data_sheets
        
        # Convert all sheets
        converted_files = convert_all_data_sheets(ods_filepath, tmp_path)
        
        # Should have converted sheets in each category
        assert len(converted_files['national']) > 0, "Should convert national sheets"
        assert len(converted_files['local_authority']) > 0, "Should convert UTLA sheets"
        
        # Verify files exist
        for category, files in converted_files.items():
            for file_path in files:
                assert file_path.exists(), f"CSV file should exist: {file_path}"
    
    def test_converted_csv_is_readable(self, ods_filepath, tmp_path):
        """
        Test that generated CSV can be read back
        
        Requirement: DA-FR-002 - Structured data accessible
        """
        import pandas as pd
        from src.ods_to_csv import convert_ods_to_csv
        
        # Convert a sheet
        csv_paths = convert_ods_to_csv(ods_filepath, sheet_name='T1_UK12m', output_dir=tmp_path)
        
        # Load it back
        df = pd.read_csv(csv_paths[0])
        
        assert df is not None, "CSV should load successfully"
        assert len(df) > 0, "CSV should contain data rows"
        assert len(df.columns) > 0, "CSV should contain columns"
    
    def test_convert_nonexistent_ods_shows_error(self):
        """
        Test error handling for missing ODS file
        
        Requirement: DA-NFR-001 - Clear error messages
        """
        from src.ods_to_csv import convert_ods_to_csv
        
        nonexistent_file = Path("data/this_file_does_not_exist.ods")
        
        with pytest.raises(FileNotFoundError) as exc_info:
            convert_ods_to_csv(nonexistent_file)
        
        error_message = str(exc_info.value)
        assert "not found" in error_message.lower(), "Error should indicate file not found"
    
    def test_converted_csv_has_utf8_encoding(self, ods_filepath, tmp_path):
        """
        Test CSV has proper UTF-8 encoding
        
        Requirement: DA-FR-002 - Structured data format
        """
        from src.ods_to_csv import convert_ods_to_csv
        
        csv_paths = convert_ods_to_csv(ods_filepath, sheet_name='T1_UK12m', output_dir=tmp_path)
        
        # Try reading with UTF-8
        try:
            with open(csv_paths[0], 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0, "CSV should have content"
        except UnicodeDecodeError:
            pytest.fail("CSV is not properly UTF-8 encoded")
    
    def test_conversion_creates_correct_filenames(self, ods_filepath, tmp_path):
        """
        Test that CSV files have correct naming convention
        
        Should be: {ods_name}_{sheet_name}.csv
        """
        from src.ods_to_csv import convert_ods_to_csv
        
        csv_paths = convert_ods_to_csv(ods_filepath, sheet_name='T1_UK12m', output_dir=tmp_path)
        
        filename = csv_paths[0].name
        assert 'T1_UK12m' in filename, "Filename should include sheet name"
        assert filename.endswith('.csv'), "Should have .csv extension"
