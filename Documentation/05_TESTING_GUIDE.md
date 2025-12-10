# Testing Guide

## Overview

This document provides comprehensive guidance on the testing strategy, test structure, and how to run and extend the test suite for the UK Childhood Immunisation Coverage Data Insights Tool.

---

## Test Statistics

**Overall Test Coverage:**
- **Total Tests:** 324
- **Passing Tests:** 324 (100%)
- **Code Coverage:** 76%
- **Test Execution Time:** ~7 minutes

**Test Distribution by Layer:**
- Layer 0 (Data Ingestion): 93 tests
- Layer 1 (Database): 25 tests
- Layer 2 (Business Logic): 156 tests
- Layer 3 (Presentation): 50 tests

---

## Testing Philosophy

### Test-Driven Development (TDD)

This project follows TDD principles:

1. **RED:** Write a failing test first
2. **GREEN:** Write minimal code to make the test pass
3. **REFACTOR:** Improve code while keeping tests green

### Testing Pyramid

```
        /\
       /  \
      / E2E\ (10%)
     /______\
    /        \
   /Integration\ (30%)
  /____________\
 /              \
/__Unit Tests___\ (60%)
```

- **Unit Tests (60%):** Test individual functions/methods
- **Integration Tests (30%):** Test layer interactions
- **End-to-End Tests (10%):** Test complete user workflows

---

## Test Structure

### Directory Layout

```
tests/
├── layer0_data_ingestion/
│   ├── test_csv_cleaner.py (17 tests)
│   ├── test_load_england_time_series.py (7 tests)
│   ├── test_load_local_authority.py (10 tests)
│   ├── test_load_national_coverage.py (7 tests)
│   ├── test_load_reference_data.py (11 tests)
│   ├── test_load_regional_time_series.py (7 tests)
│   ├── test_load_special_programs.py (7 tests)
│   ├── test_ods_to_csv.py (24 tests)
│   └── test_vaccine_matcher.py (33 tests)
├── layer1_database/
│   ├── test_database.py (12 tests)
│   └── test_models.py (13 tests)
├── layer2_business_logic/
│   ├── test_crud.py (44 tests)
│   ├── test_database_reload.py (8 tests)
│   ├── test_export.py (8 tests)
│   ├── test_fs_analysis.py (22 tests)
│   ├── test_ods_conversion.py (7 tests)
│   ├── test_table_builder.py (17 tests)
│   └── test_user_log.py (14 tests)
└── layer3_presentation/
    ├── test_flask_app.py (46 tests)
    └── test_visualization.py (10 tests)
```

### Test Naming Convention

```python
def test_<function_name>_<scenario>_<expected_outcome>():
    """Test that <function_name> <expected_outcome> when <scenario>."""
    # Arrange
    # Act
    # Assert
```

**Examples:**
```python
def test_create_vaccine_with_valid_data_succeeds():
    """Test that create_vaccine succeeds with valid data."""

def test_get_nonexistent_vaccine_returns_none():
    """Test that getting a non-existent vaccine returns None."""

def test_sql_injection_in_vaccine_code_is_prevented():
    """Test that SQL injection attempts in vaccine codes are blocked."""
```

---

## Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/layer2_business_logic/test_crud.py
```

### Run Specific Test Class

```bash
pytest tests/layer3_presentation/test_flask_app.py::TestSecurityXSS
```

### Run Specific Test Function

```bash
pytest tests/layer2_business_logic/test_crud.py::test_create_vaccine
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run with Coverage Report

```bash
# Terminal output
pytest tests/ --cov=src --cov-report=term-missing

# HTML report (opens in browser)
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Run Tests in Parallel

```bash
# Install pytest-xdist first: pip install pytest-xdist
pytest tests/ -n auto
```

### Run Only Failed Tests

```bash
# Run all tests first
pytest tests/

# Then run only failures
pytest --lf
```

---

## Test Categories

### 1. Unit Tests

Test individual functions in isolation.

**Example:**
```python
def test_clean_numeric_value_removes_commas():
    """Test that clean_numeric_value removes commas from numbers."""
    result = clean_numeric_value("1,234.56")
    assert result == 1234.56
```

### 2. Integration Tests

Test interactions between layers.

**Example:**
```python
def test_crud_create_and_retrieve_vaccine(crud_manager):
    """Test creating and retrieving a vaccine through CRUD layer."""
    # Create via CRUD
    vaccine = crud_manager.create_vaccine(
        vaccine_code='TEST',
        vaccine_name='Test Vaccine'
    )

    # Retrieve via CRUD
    retrieved = crud_manager.get_vaccine('TEST')

    assert retrieved.vaccine_code == vaccine.vaccine_code
```

### 3. Security Tests

Test protection against common vulnerabilities.

**Example:**
```python
def test_sql_injection_in_vaccine_code(crud_manager):
    """Test that SQL injection attempts are prevented."""
    malicious_code = "TEST'; DROP TABLE vaccines; --"
    result = crud_manager.get_vaccine(malicious_code)
    assert result is None  # Should not find anything or execute SQL
```

### 4. End-to-End Tests

Test complete user workflows through the Flask app.

**Example:**
```python
def test_complete_vaccine_crud_workflow(client):
    """Test complete CRUD workflow for vaccines."""
    # CREATE
    create_response = client.post('/api/crud/vaccines',
        json={'vaccine_code': 'E2E_TEST', 'vaccine_name': 'E2E Vaccine'})
    assert create_response.status_code == 201

    # READ
    read_response = client.get('/api/crud/vaccines')
    assert any(v['vaccine_code'] == 'E2E_TEST' for v in read_response.json)

    # UPDATE
    update_response = client.put('/api/crud/vaccines',
        json={'vaccine_code': 'E2E_TEST', 'vaccine_name': 'Updated'})
    assert update_response.status_code == 200

    # DELETE
    delete_response = client.delete('/api/crud/vaccines',
        json={'vaccine_code': 'E2E_TEST'})
    assert delete_response.status_code == 200
```

---

## Test Fixtures

### Database Fixtures

```python
@pytest.fixture
def db_session(tmp_path):
    """Create a temporary test database session."""
    db_path = tmp_path / "test.db"
    session = create_test_session(db_path)
    yield session
    session.close()

@pytest.fixture
def sample_vaccine(db_session):
    """Create a sample vaccine for testing."""
    vaccine = Vaccine(vaccine_code='TEST1', vaccine_name='Test Vaccine')
    db_session.add(vaccine)
    db_session.commit()
    return vaccine
```

### Flask App Fixtures

```python
@pytest.fixture
def client():
    """Create a Flask test client."""
    flask_app.config['TESTING'] = True
    from src.layer3_presentation.flask_app import session

    with flask_app.test_client() as client:
        yield client

        # Cleanup: rollback session after each test
        try:
            session.rollback()
        except:
            pass
```

---

## Code Coverage Analysis

### Current Coverage by Module

```
High Coverage (>90%):
✓ src/layer1_database/models.py               99%
✓ src/layer1_database/database.py             96%
✓ src/layer2_business_logic/crud.py           96%
✓ src/layer0_data_ingestion/load_reference_data.py  94%
✓ src/layer2_business_logic/user_log.py       90%

Good Coverage (80-90%):
✓ src/layer0_data_ingestion/load_local_authority.py  88%
✓ src/layer0_data_ingestion/load_national_coverage.py  86%
✓ src/layer0_data_ingestion/csv_loader_base.py  82%

Areas Needing Improvement (<70%):
⚠ src/layer3_presentation/flask_app.py        58%
⚠ src/layer3_presentation/visualization.py    42%
⚠ src/layer2_business_logic/database_reload.py  48%
⚠ src/layer2_business_logic/table_builder.py  70%
⚠ src/layer0_data_ingestion/csv_cleaner.py    74%
```

### Viewing Coverage Reports

1. **Generate HTML report:**
```bash
pytest tests/ --cov=src --cov-report=html
```

2. **Open in browser:**
```bash
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

3. **View missing lines:**
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Writing New Tests

### Template for New Tests

```python
import pytest
from src.module_name import function_to_test

class TestFunctionName:
    """Tests for function_name."""

    def test_function_name_with_valid_input_returns_expected_result(self):
        """Test that function_name returns expected result with valid input."""
        # Arrange
        input_data = "test_input"
        expected_output = "expected_result"

        # Act
        result = function_to_test(input_data)

        # Assert
        assert result == expected_output

    def test_function_name_with_invalid_input_raises_error(self):
        """Test that function_name raises error with invalid input."""
        # Arrange
        invalid_input = None

        # Act & Assert
        with pytest.raises(ValueError, match="expected error message"):
            function_to_test(invalid_input)

    def test_function_name_with_empty_input_returns_none(self):
        """Test that function_name returns None with empty input."""
        # Arrange
        empty_input = ""

        # Act
        result = function_to_test(empty_input)

        # Assert
        assert result is None
```

### Best Practices

1. **One Assert Per Test (when possible)**
   ```python
   # Good
   def test_vaccine_code_is_set():
       vaccine = Vaccine(vaccine_code='TEST', vaccine_name='Test')
       assert vaccine.vaccine_code == 'TEST'

   # Avoid (multiple unrelated assertions)
   def test_vaccine_properties():
       vaccine = Vaccine(vaccine_code='TEST', vaccine_name='Test')
       assert vaccine.vaccine_code == 'TEST'
       assert vaccine.vaccine_name == 'Test'
       assert vaccine.vaccine_id is not None
   ```

2. **Use Descriptive Test Names**
   ```python
   # Good
   def test_get_nonexistent_vaccine_returns_none():

   # Bad
   def test_get_vaccine():
   ```

3. **Test Edge Cases**
   - Empty inputs
   - Null values
   - Boundary values
   - Invalid types
   - Very large/small numbers

4. **Use Fixtures for Setup**
   ```python
   @pytest.fixture
   def vaccine_data():
       return {'vaccine_code': 'TEST', 'vaccine_name': 'Test'}

   def test_create_vaccine(vaccine_data):
       vaccine = Vaccine(**vaccine_data)
       assert vaccine.vaccine_code == vaccine_data['vaccine_code']
   ```

---

## Security Testing

### SQL Injection Tests

```python
def test_sql_injection_in_area_code(crud_manager):
    """Test SQL injection prevention in area codes."""
    malicious_codes = [
        "'; DROP TABLE geographic_areas; --",
        "' OR '1'='1",
        "' UNION SELECT * FROM vaccines --"
    ]

    for code in malicious_codes:
        result = crud_manager.get_geographic_area(code)
        assert result is None
```

### XSS Prevention Tests

```python
def test_xss_in_vaccine_name(client):
    """Test XSS prevention in vaccine names."""
    xss_payloads = [
        '<script>alert("XSS")</script>',
        '<img src=x onerror=alert("XSS")>',
        'javascript:alert("XSS")'
    ]

    for payload in xss_payloads:
        response = client.post('/api/crud/vaccines',
            json={'vaccine_code': 'XSS', 'vaccine_name': payload})
        assert response.status_code in [201, 400, 409]
```

### Input Validation Tests

```python
def test_negative_coverage_rejected(client):
    """Test that negative coverage percentages are rejected."""
    response = client.post('/api/crud/coverage',
        json={
            'area_code': 'E10000001',
            'vaccine_code': 'MMR1',
            'coverage_percentage': -5.0
        })
    assert response.status_code == 400
```

---

## Continuous Integration

### GitHub Actions Workflow (Example)

```yaml
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
        python-version: '3.12'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## Troubleshooting

### Common Issues

**1. Tests fail due to database state**
```bash
# Solution: Ensure each test uses a clean database
# Use tmp_path fixture for test databases
```

**2. Flask session rollback errors**
```bash
# Solution: Add session.rollback() in fixture teardown
```

**3. Tests run slowly**
```bash
# Solution: Run tests in parallel
pytest tests/ -n auto
```

**4. Coverage not reflecting changes**
```bash
# Solution: Clear .pytest_cache and .coverage
rm -rf .pytest_cache .coverage htmlcov
pytest tests/ --cov=src --cov-report=html
```

---

## Testing Checklist

Before committing code, ensure:

- [ ] All tests pass (`pytest tests/`)
- [ ] Code coverage maintained or improved
- [ ] New features have corresponding tests
- [ ] Security tests pass
- [ ] No test warnings
- [ ] Tests run in < 10 minutes

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [Flask Testing](https://flask.palletsprojects.com/en/3.0.x/testing/)
