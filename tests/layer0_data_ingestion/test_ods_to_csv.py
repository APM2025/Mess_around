"""
Tests for ods_to_csv module.
"""

import pytest
import pandas as pd
from pathlib import Path
from src.layer0_data_ingestion.ods_to_csv import (
    convert_ods_to_csv,
    convert_all_data_sheets,
    load_csv_file,
    DATA_SHEETS,
    METADATA_SHEETS
)


@pytest.fixture
def sample_ods_file(tmp_path):
    """Create a sample ODS file for testing."""
    ods_path = tmp_path / "test_data.ods"

    # Create sample DataFrames for different sheets
    sheets = {
        'T1_UK12m': pd.DataFrame({
            'Geographic area': ['England', 'Scotland'],
            'Coverage at 12 months MMR1': [93.5, 91.2]
        }),
        'T4a_UTLA12m': pd.DataFrame({
            'Local Authority': ['Lincolnshire', 'Norfolk'],
            'Coverage at 12 months DTaP/IPV/Hib/HepB': [94.0, 92.5]
        }),
        'Cover': pd.DataFrame({
            'Title': ['COVER Programme Data']
        }),
        'Notes': pd.DataFrame({
            'Note': ['[z] not applicable']
        })
    }

    # Write to ODS file
    with pd.ExcelWriter(ods_path, engine='odf') as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    return ods_path


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing."""
    csv_path = tmp_path / "test_data.csv"

    df = pd.DataFrame({
        'Area': ['England', 'Scotland'],
        'Coverage': [93.5, 91.2]
    })

    df.to_csv(csv_path, index=False)

    return csv_path


# Phase 1: Module constants
def test_data_sheets_constant_exists():
    """Test that DATA_SHEETS constant is defined."""
    assert DATA_SHEETS is not None
    assert isinstance(DATA_SHEETS, dict)


def test_data_sheets_has_all_categories():
    """Test that DATA_SHEETS has all expected categories."""
    expected_categories = [
        'national',
        'local_authority',
        'england_time_series',
        'regional_time_series',
        'special_programs'
    ]

    for category in expected_categories:
        assert category in DATA_SHEETS
        assert isinstance(DATA_SHEETS[category], list)
        assert len(DATA_SHEETS[category]) > 0


def test_metadata_sheets_constant():
    """Test that METADATA_SHEETS is defined."""
    assert METADATA_SHEETS is not None
    assert isinstance(METADATA_SHEETS, list)
    assert 'Cover' in METADATA_SHEETS
    assert 'Notes' in METADATA_SHEETS


# Phase 2: convert_ods_to_csv basic tests
def test_convert_ods_to_csv_file_not_found():
    """Test convert_ods_to_csv raises error for missing file."""
    with pytest.raises(FileNotFoundError):
        convert_ods_to_csv('nonexistent.ods')


def test_convert_ods_to_csv_wrong_extension(tmp_path):
    """Test convert_ods_to_csv raises error for wrong file type."""
    wrong_file = tmp_path / "test.txt"
    wrong_file.touch()

    with pytest.raises(ValueError) as exc_info:
        convert_ods_to_csv(wrong_file)

    assert 'Expected an ODS file' in str(exc_info.value)


def test_convert_ods_to_csv_invalid_sheet(sample_ods_file):
    """Test convert_ods_to_csv with invalid sheet name."""
    with pytest.raises(ValueError) as exc_info:
        convert_ods_to_csv(sample_ods_file, sheet_name='InvalidSheet')

    assert 'not found' in str(exc_info.value)


def test_convert_ods_to_csv_returns_list(sample_ods_file):
    """Test convert_ods_to_csv returns list of paths."""
    result = convert_ods_to_csv(sample_ods_file, sheet_name='T1_UK12m')

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], Path)


def test_convert_ods_to_csv_creates_csv_file(sample_ods_file, tmp_path):
    """Test convert_ods_to_csv creates CSV file."""
    result = convert_ods_to_csv(
        sample_ods_file,
        sheet_name='T1_UK12m',
        output_dir=tmp_path
    )

    csv_file = result[0]
    assert csv_file.exists()
    assert csv_file.suffix == '.csv'


def test_convert_ods_to_csv_correct_content(sample_ods_file, tmp_path):
    """Test convert_ods_to_csv creates CSV with correct content."""
    result = convert_ods_to_csv(
        sample_ods_file,
        sheet_name='T1_UK12m',
        output_dir=tmp_path
    )

    csv_file = result[0]
    df = pd.read_csv(csv_file)

    assert len(df) == 2
    assert 'Geographic area' in df.columns
    assert 'Coverage at 12 months MMR1' in df.columns
    assert df['Geographic area'].tolist() == ['England', 'Scotland']


def test_convert_ods_to_csv_default_output_dir(sample_ods_file):
    """Test convert_ods_to_csv uses default output directory."""
    result = convert_ods_to_csv(sample_ods_file, sheet_name='T1_UK12m')

    csv_file = result[0]
    # Should be in same directory as ODS file
    assert csv_file.parent == sample_ods_file.parent


# Phase 3: convert_all_data_sheets tests
def test_convert_all_data_sheets_returns_dict(sample_ods_file):
    """Test convert_all_data_sheets returns dictionary."""
    result = convert_all_data_sheets(sample_ods_file)

    assert isinstance(result, dict)
    assert 'national' in result
    assert 'local_authority' in result


def test_convert_all_data_sheets_creates_csv_dir(sample_ods_file, tmp_path):
    """Test convert_all_data_sheets creates output directory."""
    output_dir = tmp_path / "csv_output"

    convert_all_data_sheets(sample_ods_file, output_dir=output_dir)

    assert output_dir.exists()
    assert output_dir.is_dir()


def test_convert_all_data_sheets_converts_data_sheets(sample_ods_file, tmp_path):
    """Test convert_all_data_sheets converts available data sheets."""
    result = convert_all_data_sheets(sample_ods_file, output_dir=tmp_path)

    # Should have converted T1_UK12m (national) and T4a_UTLA12m (local_authority)
    assert len(result['national']) > 0
    assert len(result['local_authority']) > 0


def test_convert_all_data_sheets_skips_metadata(sample_ods_file, tmp_path):
    """Test convert_all_data_sheets doesn't convert metadata sheets."""
    convert_all_data_sheets(sample_ods_file, output_dir=tmp_path)

    # Check that metadata sheets were not converted
    csv_files = list(tmp_path.glob('*.csv'))
    filenames = [f.name for f in csv_files]

    for metadata_sheet in METADATA_SHEETS:
        assert not any(metadata_sheet in name for name in filenames)


# Phase 4: load_csv_file tests
def test_load_csv_file_not_found():
    """Test load_csv_file raises error for missing file."""
    with pytest.raises(FileNotFoundError):
        load_csv_file('nonexistent.csv')


def test_load_csv_file_returns_dataframe(sample_csv_file):
    """Test load_csv_file returns pandas DataFrame."""
    result = load_csv_file(sample_csv_file)

    assert isinstance(result, pd.DataFrame)


def test_load_csv_file_correct_content(sample_csv_file):
    """Test load_csv_file loads correct content."""
    df = load_csv_file(sample_csv_file)

    assert len(df) == 2
    assert 'Area' in df.columns
    assert 'Coverage' in df.columns
    assert df['Area'].tolist() == ['England', 'Scotland']
    assert df['Coverage'].tolist() == [93.5, 91.2]


def test_load_csv_file_with_path_object(sample_csv_file):
    """Test load_csv_file works with Path object."""
    path_obj = Path(sample_csv_file)
    df = load_csv_file(path_obj)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2


# Phase 5: Integration tests
def test_full_conversion_workflow(sample_ods_file, tmp_path):
    """Test complete workflow: ODS → CSV → load."""
    # Step 1: Convert ODS to CSV
    csv_paths = convert_ods_to_csv(
        sample_ods_file,
        sheet_name='T1_UK12m',
        output_dir=tmp_path
    )

    # Step 2: Load CSV
    df = load_csv_file(csv_paths[0])

    # Step 3: Verify content
    assert len(df) == 2
    assert 'Geographic area' in df.columns
    assert df['Geographic area'].tolist() == ['England', 'Scotland']


def test_convert_multiple_sheets(sample_ods_file, tmp_path):
    """Test converting multiple sheets sequentially."""
    # Convert national sheet
    result1 = convert_ods_to_csv(
        sample_ods_file,
        sheet_name='T1_UK12m',
        output_dir=tmp_path
    )

    # Convert local authority sheet
    result2 = convert_ods_to_csv(
        sample_ods_file,
        sheet_name='T4a_UTLA12m',
        output_dir=tmp_path
    )

    # Both should succeed
    assert len(result1) == 1
    assert len(result2) == 1
    assert result1[0].exists()
    assert result2[0].exists()
    assert result1[0] != result2[0]  # Different files


# Phase 6: Edge cases
def test_convert_ods_to_csv_with_empty_sheet(tmp_path):
    """Test converting ODS with empty sheet."""
    ods_path = tmp_path / "empty.ods"

    # Create ODS with empty sheet (but with at least one column to avoid pandas error)
    with pd.ExcelWriter(ods_path, engine='odf') as writer:
        pd.DataFrame({'col1': []}).to_excel(writer, sheet_name='T1_UK12m', index=False)

    result = convert_ods_to_csv(ods_path, sheet_name='T1_UK12m', output_dir=tmp_path)

    # Should still create CSV file
    assert len(result) == 1
    assert result[0].exists()

    # Load and verify it's empty (0 rows but has column)
    df = pd.read_csv(result[0])
    assert len(df) == 0
    assert 'col1' in df.columns


def test_convert_ods_to_csv_overwrites_existing(sample_ods_file, tmp_path):
    """Test that converting overwrites existing CSV."""
    # First conversion
    result1 = convert_ods_to_csv(
        sample_ods_file,
        sheet_name='T1_UK12m',
        output_dir=tmp_path
    )
    csv_path = result1[0]
    first_mtime = csv_path.stat().st_mtime

    # Wait a bit (to ensure different timestamp)
    import time
    time.sleep(0.1)

    # Second conversion
    result2 = convert_ods_to_csv(
        sample_ods_file,
        sheet_name='T1_UK12m',
        output_dir=tmp_path
    )

    # Should have overwritten
    assert result2[0] == csv_path
    second_mtime = csv_path.stat().st_mtime
    assert second_mtime >= first_mtime


# Phase 7: File naming tests
def test_csv_filename_format(sample_ods_file, tmp_path):
    """Test CSV filename follows expected format."""
    result = convert_ods_to_csv(
        sample_ods_file,
        sheet_name='T1_UK12m',
        output_dir=tmp_path
    )

    csv_file = result[0]
    filename = csv_file.name

    # Should include original filename and sheet name
    assert 'test_data' in filename
    assert 'T1_UK12m' in filename
    assert filename.endswith('.csv')


def test_load_csv_preserves_dtypes(tmp_path):
    """Test load_csv_file preserves data types."""
    # Create CSV with mixed types
    csv_path = tmp_path / "mixed_types.csv"
    df = pd.DataFrame({
        'text': ['A', 'B'],
        'number': [1, 2],
        'float': [1.5, 2.5]
    })
    df.to_csv(csv_path, index=False)

    # Load and check types
    loaded_df = load_csv_file(csv_path)

    assert loaded_df['text'].dtype == 'object'
    assert loaded_df['number'].dtype == 'int64'
    assert loaded_df['float'].dtype == 'float64'
