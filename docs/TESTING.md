# Testing Guide

Comprehensive testing documentation for the UK Vaccination Coverage Dashboard.

## Overview

This project follows **Test-Driven Development (TDD)** principles with a comprehensive test suite covering all layers of the application.

**Test Suite Statistics**:
- **21 test modules** organized by architectural layer
- **100+ individual tests** with comprehensive coverage
- **4 testing layers** mirroring the source code structure

## Running Tests

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with test names
pytest -v --tb=short
```

### Run Tests by Layer

```bash
# Layer 0: Data Ingestion & Cleaning
pytest tests/layer0_data_ingestion/

# Layer 1: Database
pytest tests/layer1_database/

# Layer 2: Business Logic
pytest tests/layer2_business_logic/

# Layer 3: Presentation
pytest tests/layer3_presentation/
```

### Run Specific Test Files

```bash
# Run a specific test file
pytest tests/layer1_database/test_models.py

# Run a specific test class
pytest tests/layer2_business_logic/test_fs_analysis.py::TestVaccinationAnalyzer

# Run a specific test function
pytest tests/layer2_business_logic/test_fs_analysis.py::TestVaccinationAnalyzer::test_filter_by_vaccine
```

### Coverage Reports

```bash
# Run with coverage report
pytest --cov=src

# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View HTML report (opens in browser)
# Open htmlcov/index.html in your browser

# Coverage report with missing lines
pytest --cov=src --cov-report=term-missing
```

## Test Organization

### Directory Structure

```
tests/
├── layer0_data_ingestion/          # Layer 0 Tests
│   ├── __init__.py
│   ├── test_csv_cleaner.py         # CSV cleaning tests
│   ├── test_csv_loader_base.py     # Base loader tests
│   ├── test_load_reference_data.py # Reference data tests
│   ├── test_load_national_coverage.py
│   ├── test_load_local_authority.py
│   ├── test_load_england_timeseries.py
│   ├── test_load_regional_timeseries.py
│   ├── test_load_special_program.py
│   ├── test_ods_to_csv.py          # ODS conversion tests
│   └── test_vaccine_matcher.py     # Vaccine matching tests
│
├── layer1_database/                # Layer 1 Tests
│   ├── __init__.py
│   ├── test_models.py              # ORM model tests
│   └── test_database.py            # Database session tests
│
├── layer2_business_logic/          # Layer 2 Tests
│   ├── __init__.py
│   ├── test_crud.py                # CRUD operation tests
│   ├── test_fs_analysis.py         # Analysis & filtering tests
│   ├── test_export.py              # Export functionality tests
│   ├── test_user_log.py            # Activity logging tests
│   └── test_table_builder.py       # Table reconstruction tests
│
└── layer3_presentation/            # Layer 3 Tests
    ├── __init__.py
    └── test_visualization.py       # Visualization tests
```

## Test Categories

### Layer 0: Data Ingestion Tests

**CSV Cleaner** (`test_csv_cleaner.py`)
- Tests data cleaning functions
- Handles missing values, whitespace, type conversion
- Validates data transformations

**CSV Loader Base** (`test_csv_loader_base.py`)
- Tests template method pattern implementation
- Validates abstract base class behavior
- Tests common loader functionality

**Data Loaders** (`test_load_*.py`)
- Tests each specific loader (6 loaders)
- Validates data extraction from CSV files
- Tests error handling for malformed data

**ODS to CSV** (`test_ods_to_csv.py`)
- Tests ODS file reading
- Validates CSV conversion
- Tests file handling and error cases

**Vaccine Matcher** (`test_vaccine_matcher.py`)
- Tests exact matching
- Tests alias matching
- Tests fuzzy matching
- Validates caching behavior

### Layer 1: Database Tests

**Models** (`test_models.py`)
- Tests all 9 SQLAlchemy models
- Validates relationships between tables
- Tests constraint enforcement
- Validates data types and nullable fields

**Database** (`test_database.py`)
- Tests session factory creation
- Validates connection pooling
- Tests transaction handling

### Layer 2: Business Logic Tests

**CRUD** (`test_crud.py`)
- Tests Create, Read, Update, Delete operations
- Validates data integrity
- Tests error handling
- Validates constraint violations

**Analysis** (`test_fs_analysis.py`)
- Tests data filtering by vaccine, area, cohort
- Tests summary statistics (mean, min, max, count)
- Tests top areas ranking
- Tests trend analysis
- Tests coverage classification (new feature)
- Tests table statistics calculation (new feature)

**Export** (`test_export.py`)
- Tests CSV export functionality
- Validates file creation
- Tests data integrity in exports
- Validates column headers

**User Log** (`test_user_log.py`)
- Tests activity logging
- Validates log formatting
- Tests log retrieval

**Table Builder** (`test_table_builder.py`)
- Tests ODS table reconstruction
- Validates table structure
- Tests data grouping and sorting
- Tests edge cases

### Layer 3: Presentation Tests

**Visualization** (`test_visualization.py`)
- Tests chart generation (4 chart types)
- Validates chart file creation
- Tests chart parameters
- Validates matplotlib integration

## Writing New Tests

### Test File Template

```python
"""
Tests for [module_name].

Test coverage:
- [Feature 1]
- [Feature 2]
- [Feature 3]
"""

import pytest
from pathlib import Path
from src.layer[N]_[layer_name].[module_name] import [ClassName]


class Test[ClassName]:
    """Tests for [ClassName] class."""

    @pytest.fixture
    def setup_data(self):
        """Setup test data."""
        # Create test data
        yield test_data
        # Cleanup (if needed)

    def test_[feature_name](self, setup_data):
        """Test [specific behavior]."""
        # Arrange
        expected = ...

        # Act
        result = ...

        # Assert
        assert result == expected

    def test_[feature_name]_error_case(self):
        """Test [error handling]."""
        with pytest.raises(ValueError):
            # Code that should raise error
            pass
```

### Testing Best Practices

1. **Follow AAA Pattern**: Arrange, Act, Assert
   ```python
   def test_filter_by_vaccine(self):
       # Arrange
       analyzer = VaccinationAnalyzer(session)
       vaccine_code = 'MMR1'

       # Act
       result = analyzer.filter_data(vaccine_code=vaccine_code)

       # Assert
       assert len(result) > 0
       assert all(r['vaccine_code'] == vaccine_code for r in result)
   ```

2. **Use Fixtures for Setup**
   ```python
   @pytest.fixture
   def sample_database(tmp_path):
       """Create temporary test database."""
       db_path = tmp_path / "test.db"
       # Setup database
       yield db_path
       # Cleanup happens automatically
   ```

3. **Test Edge Cases**
   ```python
   def test_empty_data(self):
       """Test behavior with empty dataset."""
       result = analyzer.filter_data(vaccine_code='INVALID')
       assert len(result) == 0

   def test_null_values(self):
       """Test handling of null values."""
       result = analyzer.classify_coverage(None)
       assert result == 'unknown'
   ```

4. **Use Descriptive Test Names**
   ```python
   # Good
   def test_classify_coverage_returns_good_when_above_95_percent(self):
       pass

   # Bad
   def test_classify(self):
       pass
   ```

5. **Test One Thing Per Test**
   ```python
   # Good - each test has single purpose
   def test_filter_by_vaccine(self):
       """Test filtering by vaccine code."""
       pass

   def test_filter_by_area(self):
       """Test filtering by area."""
       pass

   # Bad - testing multiple things
   def test_filter(self):
       """Test all filtering."""
       # Tests vaccine, area, cohort all together
       pass
   ```

## Common Testing Patterns

### Testing Database Operations

```python
import pytest
from src.layer1_database.database import get_session
from src.layer1_database.models import Vaccine

@pytest.fixture
def db_session():
    """Create test database session."""
    session = get_session()
    yield session
    session.rollback()  # Rollback changes after test
    session.close()

def test_create_vaccine(db_session):
    """Test creating a vaccine record."""
    vaccine = Vaccine(
        vaccine_code='TEST1',
        vaccine_name='Test Vaccine',
        vaccine_description='Test Description'
    )
    db_session.add(vaccine)
    db_session.commit()

    # Verify
    result = db_session.query(Vaccine).filter_by(vaccine_code='TEST1').first()
    assert result is not None
    assert result.vaccine_name == 'Test Vaccine'
```

### Testing File Operations

```python
import pytest
from pathlib import Path
from src.layer2_business_logic.export import DataExporter

def test_export_to_csv(tmp_path):
    """Test CSV export functionality."""
    # Use pytest's tmp_path fixture for temporary files
    output_file = tmp_path / "test_export.csv"

    exporter = DataExporter()
    data = [
        {'area': 'Area1', 'coverage': 95.5},
        {'area': 'Area2', 'coverage': 92.3}
    ]

    exporter.export_to_csv(data, output_file)

    # Verify file exists
    assert output_file.exists()

    # Verify content
    import pandas as pd
    df = pd.read_csv(output_file)
    assert len(df) == 2
    assert 'area' in df.columns
```

### Testing Visualizations

```python
import pytest
from pathlib import Path
from src.layer3_presentation.visualization import VaccinationVisualizer

def test_plot_top_areas(tmp_path):
    """Test top areas chart generation."""
    visualizer = VaccinationVisualizer(output_dir=tmp_path)

    data = [
        {'area_name': 'Area1', 'coverage': 98.5},
        {'area_name': 'Area2', 'coverage': 97.2}
    ]

    chart_path = visualizer.plot_top_areas(
        data,
        title="Test Chart",
        filename="test_chart.png"
    )

    # Verify chart was created
    assert chart_path.exists()
    assert chart_path.suffix == '.png'
```

### Testing Error Handling

```python
import pytest
from src.layer2_business_logic.crud import VaccinationCRUD

def test_create_vaccine_duplicate_code(db_session):
    """Test error when creating duplicate vaccine code."""
    crud = VaccinationCRUD(db_session)

    # Create first vaccine
    crud.create_vaccine('TEST1', 'Test Vaccine', 'Description')

    # Attempt to create duplicate should raise error
    with pytest.raises(ValueError, match="Vaccine code TEST1 already exists"):
        crud.create_vaccine('TEST1', 'Another Vaccine', 'Description')
```

## Continuous Integration

### Running Tests in CI/CD

```yaml
# Example GitHub Actions workflow
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting Tests

### Common Issues

**Import Errors**
```bash
# Ensure you're in project root
cd "c:\Users\amyna\OneDrive - University of Warwick\Programming for AI-MSI\New folder\Mess_around"

# Install in development mode
pip install -e .
```

**Database Errors**
```bash
# Recreate test database
python create_database.py

# Or use in-memory SQLite for tests
# In test fixtures, use: engine = create_engine('sqlite:///:memory:')
```

**Test Failures After Refactoring**
```bash
# Run specific failing test with verbose output
pytest tests/layer2_business_logic/test_fs_analysis.py::test_filter_by_vaccine -v

# Check import paths are correct for new layer structure
# Old: from src.fs_analysis import ...
# New: from src.layer2_business_logic.fs_analysis import ...
```

## Test Metrics

### Coverage Targets

- **Overall Coverage**: ≥ 90%
- **Layer 0 (Data Ingestion)**: ≥ 85%
- **Layer 1 (Database)**: ≥ 95%
- **Layer 2 (Business Logic)**: ≥ 95%
- **Layer 3 (Presentation)**: ≥ 80%

### Test Execution Time

Typical test execution times:
- **All tests**: ~10-15 seconds
- **Layer 0**: ~3-5 seconds
- **Layer 1**: ~1-2 seconds
- **Layer 2**: ~4-6 seconds
- **Layer 3**: ~2-3 seconds

If tests take significantly longer, consider:
- Using in-memory databases for faster tests
- Mocking external dependencies
- Parallelizing tests with `pytest-xdist`

## Advanced Testing

### Parameterized Tests

```python
import pytest

@pytest.mark.parametrize("coverage,expected", [
    (98.0, 'good'),
    (95.0, 'good'),
    (90.0, 'warning'),
    (85.0, 'warning'),
    (80.0, 'low'),
    (None, 'unknown')
])
def test_classify_coverage_parametrized(coverage, expected):
    """Test coverage classification with multiple values."""
    from src.layer2_business_logic.fs_analysis import VaccinationAnalyzer
    result = VaccinationAnalyzer.classify_coverage(coverage)
    assert result == expected
```

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test using mocked dependencies."""
    with patch('src.layer2_business_logic.user_log.datetime') as mock_datetime:
        mock_datetime.now.return_value = '2024-01-01 12:00:00'
        # Test code that uses datetime.now()
        pass
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Test-Driven Development Guide](https://testdriven.io/test-driven-development/)

## Contributing Tests

When adding new features:

1. **Write tests first** (TDD approach)
2. **Place tests in correct layer** directory
3. **Follow existing naming conventions**
4. **Document test purpose** in docstrings
5. **Maintain coverage** above 90%
6. **Run full test suite** before committing

```bash
# Before committing
pytest --cov=src --cov-report=term-missing
```

Ensure all tests pass and coverage remains high!
