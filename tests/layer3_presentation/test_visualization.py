"""
Tests for visualization module.
"""

import pytest
from pathlib import Path
from src.layer3_presentation.visualization import VaccinationVisualizer


@pytest.fixture
def sample_filter_data():
    """Sample data from filter_data()."""
    return [
        {'area_name': 'Area1', 'coverage': 90.0, 'vaccine_code': 'MMR1', 'vaccine_name': 'MMR1'},
        {'area_name': 'Area2', 'coverage': 85.0, 'vaccine_code': 'MMR1', 'vaccine_name': 'MMR1'},
        {'area_name': 'Area3', 'coverage': 95.0, 'vaccine_code': 'MMR1', 'vaccine_name': 'MMR1'},
    ]


@pytest.fixture
def sample_summary():
    """Sample summary statistics."""
    return {
        'count': 149,
        'mean': 88.8,
        'min': 65.3,
        'max': 96.3
    }


@pytest.fixture
def sample_top_areas():
    """Sample top areas data."""
    return [
        {'area_name': 'North Tyneside', 'coverage': 96.3, 'vaccine_code': 'MMR1', 'vaccine_name': 'MMR1'},
        {'area_name': 'Sunderland', 'coverage': 96.2, 'vaccine_code': 'MMR1', 'vaccine_name': 'MMR1'},
        {'area_name': 'Cumbria', 'coverage': 95.9, 'vaccine_code': 'MMR1', 'vaccine_name': 'MMR1'},
        {'area_name': 'South Tyneside', 'coverage': 95.7, 'vaccine_code': 'MMR1', 'vaccine_name': 'MMR1'},
        {'area_name': 'Derbyshire', 'coverage': 95.5, 'vaccine_code': 'MMR1', 'vaccine_name': 'MMR1'},
    ]


@pytest.fixture
def sample_trend():
    """Sample trend data."""
    return [
        {'year': '2020-2021', 'coverage': 90.3},
        {'year': '2021-2022', 'coverage': 89.18},
        {'year': '2022-2023', 'coverage': 89.35},
        {'year': '2023-2024', 'coverage': 88.94},
        {'year': '2024-2025', 'coverage': 88.9},
    ]


@pytest.fixture
def visualizer(tmp_path):
    """Create visualizer instance with temp output directory."""
    return VaccinationVisualizer(output_dir=tmp_path)


# Phase 1: Basic instantiation
def test_visualizer_can_be_created(tmp_path):
    """Test that VaccinationVisualizer can be instantiated."""
    visualizer = VaccinationVisualizer(output_dir=tmp_path)

    assert visualizer is not None
    assert visualizer.output_dir == tmp_path


# Phase 2: Top areas horizontal bar chart
def test_plot_top_areas_returns_path(visualizer, sample_top_areas):
    """Test plot_top_areas returns a file path."""
    result = visualizer.plot_top_areas(sample_top_areas, title="Test Top Areas")

    assert result is not None
    assert isinstance(result, Path)


def test_plot_top_areas_creates_file(visualizer, sample_top_areas):
    """Test plot_top_areas creates an actual file."""
    filepath = visualizer.plot_top_areas(sample_top_areas, title="Test Top Areas")

    assert filepath.exists()
    assert filepath.suffix == '.png'


def test_plot_top_areas_with_custom_filename(visualizer, sample_top_areas):
    """Test plot_top_areas with custom filename."""
    filepath = visualizer.plot_top_areas(
        sample_top_areas,
        title="Test Top Areas",
        filename="custom_chart.png"
    )

    assert filepath.name == "custom_chart.png"
    assert filepath.exists()


# Phase 3: Trend line chart
def test_plot_trend_returns_path(visualizer, sample_trend):
    """Test plot_trend returns a file path."""
    result = visualizer.plot_trend(sample_trend, title="Test Trend")

    assert result is not None
    assert isinstance(result, Path)


def test_plot_trend_creates_file(visualizer, sample_trend):
    """Test plot_trend creates an actual file."""
    filepath = visualizer.plot_trend(sample_trend, title="Test Trend")

    assert filepath.exists()
    assert filepath.suffix == '.png'


# Phase 4: Summary bar chart
def test_plot_summary_returns_path(visualizer, sample_summary):
    """Test plot_summary returns a file path."""
    result = visualizer.plot_summary(sample_summary, title="Test Summary")

    assert result is not None
    assert isinstance(result, Path)


def test_plot_summary_creates_file(visualizer, sample_summary):
    """Test plot_summary creates an actual file."""
    filepath = visualizer.plot_summary(sample_summary, title="Test Summary")

    assert filepath.exists()
    assert filepath.suffix == '.png'


# Phase 5: Distribution histogram
def test_plot_distribution_returns_path(visualizer, sample_filter_data):
    """Test plot_distribution returns a file path."""
    result = visualizer.plot_distribution(sample_filter_data, title="Test Distribution")

    assert result is not None
    assert isinstance(result, Path)


def test_plot_distribution_creates_file(visualizer, sample_filter_data):
    """Test plot_distribution creates an actual file."""
    filepath = visualizer.plot_distribution(sample_filter_data, title="Test Distribution")

    assert filepath.exists()
    assert filepath.suffix == '.png'
