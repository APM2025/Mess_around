"""
Tests for data export module.
"""

import pytest
import csv
from pathlib import Path
from src.layer2_business_logic.export import DataExporter


@pytest.fixture
def exporter():
    """Create exporter instance."""
    return DataExporter()


@pytest.fixture
def sample_data():
    """Sample data for export."""
    return [
        {'area_name': 'Area1', 'coverage': 90.5, 'vaccine_code': 'MMR1'},
        {'area_name': 'Area2', 'coverage': 85.3, 'vaccine_code': 'MMR1'},
        {'area_name': 'Area3', 'coverage': 92.1, 'vaccine_code': 'MMR1'},
    ]


# Phase 1: Basic instantiation
def test_exporter_can_be_created(exporter):
    """Test that DataExporter can be instantiated."""
    assert exporter is not None


# Phase 2: CSV export
def test_export_to_csv_returns_path(exporter, sample_data, tmp_path):
    """Test export_to_csv returns file path."""
    output_file = tmp_path / "test_export.csv"
    result = exporter.export_to_csv(sample_data, output_file)

    assert result is not None
    assert isinstance(result, Path)


def test_export_to_csv_creates_file(exporter, sample_data, tmp_path):
    """Test export_to_csv creates actual file."""
    output_file = tmp_path / "test_export.csv"
    result = exporter.export_to_csv(sample_data, output_file)

    assert result.exists()
    assert result.suffix == '.csv'


def test_export_to_csv_has_correct_headers(exporter, sample_data, tmp_path):
    """Test CSV has correct headers."""
    output_file = tmp_path / "test_export.csv"
    exporter.export_to_csv(sample_data, output_file)

    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

    assert 'area_name' in headers
    assert 'coverage' in headers
    assert 'vaccine_code' in headers


def test_export_to_csv_has_correct_row_count(exporter, sample_data, tmp_path):
    """Test CSV has correct number of rows."""
    output_file = tmp_path / "test_export.csv"
    exporter.export_to_csv(sample_data, output_file)

    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 3


def test_export_to_csv_has_correct_data(exporter, sample_data, tmp_path):
    """Test CSV contains correct data."""
    output_file = tmp_path / "test_export.csv"
    exporter.export_to_csv(sample_data, output_file)

    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert rows[0]['area_name'] == 'Area1'
    assert rows[0]['coverage'] == '90.5'
    assert rows[1]['area_name'] == 'Area2'


def test_export_empty_data(exporter, tmp_path):
    """Test exporting empty data list."""
    output_file = tmp_path / "empty_export.csv"
    result = exporter.export_to_csv([], output_file)

    assert result.exists()
    # Empty file or just headers
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    assert len(content) < 10  # Should be very small


def test_export_with_different_columns(exporter, tmp_path):
    """Test export with different column structure."""
    data = [
        {'col1': 'value1', 'col2': 100, 'col3': 'test'},
        {'col1': 'value2', 'col2': 200, 'col3': 'test2'},
    ]

    output_file = tmp_path / "custom_export.csv"
    exporter.export_to_csv(data, output_file)

    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)

    assert 'col1' in headers
    assert 'col2' in headers
    assert 'col3' in headers
    assert len(rows) == 2
