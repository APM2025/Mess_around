# Database Version 2 - Clean Architecture

**Created:** 2025-12-09  
**Purpose:** Clean, refactored database code with clear organization

---

## Directory Structure

```
database_version_2/
├── src/                          # Source code
│   ├── __init__.py              # Package initialization
│   ├── models.py                # SQLAlchemy ORM models
│   ├── database.py              # Session management
│   ├── csv_cleaner.py           # CSV cleaning utilities
│   ├── vaccine_matcher.py       # Vaccine name matching
│   ├── ods_to_csv.py            # ODS to CSV conversion
│   ├── csv_loader_base.py       # Base class for all loaders
│   ├── load_reference_data.py   # Load dimension tables
│   ├── load_national_coverage.py    # Load national coverage
│   ├── load_local_authority.py      # Load local authority data
│   ├── load_england_time_series.py  # Load England historical data
│   ├── load_regional_time_series.py # Load regional historical data
│   └── load_special_programs.py     # Load HepB/BCG programs
│
└── tests/                       # Test files
    ├── __init__.py
    ├── test_database.py         # Database connection tests
    ├── test_models.py           # ORM model tests
    ├── test_csv_cleaner.py      # CSV cleaning tests
    ├── test_load_reference_data.py
    ├── test_load_national_coverage.py
    ├── test_load_local_authority.py
    ├── test_load_england_time_series.py
    ├── test_load_regional_time_series.py
    ├── test_load_special_programs.py
    └── test_ods_conversion.py
```

---

## Design Principles

### 1. **Clean Separation**
- Source code in `src/`
- Tests in `tests/`
- One-to-one mapping between modules and test files

### 2. **Consistent Architecture**
- All loaders inherit from `CSVDataLoader` base class
- Shared utilities in dedicated modules
- No duplicate code

### 3. **Clear Naming**
- No version numbers in filenames (use git for versions)
- Descriptive, consistent naming patterns
- No duplicate files

### 4. **Single Responsibility**
- Each module has one clear purpose
- No overlapping functionality
- Easy to understand and maintain

---

## File Descriptions

### Core Infrastructure

#### `models.py`
SQLAlchemy ORM models for all database tables:
- Reference tables: `GeographicArea`, `Vaccine`, `AgeCohort`, `FinancialYear`
- Fact tables: `NationalCoverage`, `LocalAuthorityCoverage`, `EnglandTimeSeries`, `RegionalTimeSeries`, `SpecialProgram`

#### `database.py`
Database session management:
- `create_test_session()` - Create test database
- `create_production_session()` - Create production database
- `get_session()` - Convenience wrapper

### Utilities

#### `csv_cleaner.py`
CSV cleaning and parsing utilities:
- `find_header_row()` - Locate header row in CSV
- `extract_vaccine_name()` - Extract vaccine name from column header
- `clean_numeric_value()` - Clean numeric values (commas, markers, ranges)
- `is_data_row()` - Identify data rows vs metadata
- `load_cleaned_csv()` - Load and clean entire CSV file

#### `vaccine_matcher.py`
Unified vaccine name matching:
- `CANONICAL_VACCINES` - Master vaccine list
- `match_vaccine_from_header()` - Match vaccine from column header
- `VaccineMatcher` class - Fuzzy matching with aliases

#### `ods_to_csv.py`
Convert ODS files to CSV:
- `convert_ods_to_csv()` - Convert single sheet
- `convert_all_sheets()` - Convert all sheets in ODS file

### Base Classes

#### `csv_loader_base.py`
Base class for all data loaders:
- Common CSV loading logic
- Shared utility methods
- Consistent error handling
- Template method pattern

### Data Loaders

All loaders follow the same pattern:
1. Inherit from `CSVDataLoader`
2. Implement `_get_sheet_type()`
3. Implement `_load_reference_data()`
4. Implement `_process_row()`
5. Expose `load_*_from_csv()` function

#### `load_reference_data.py`
Load dimension tables (one-time setup):
- Geographic areas (countries, regions, UTLAs)
- Vaccines catalog
- Age cohorts
- Financial years

#### `load_national_coverage.py`
Load UK/country-level coverage data (current year)

#### `load_local_authority.py`
Load UTLA-level coverage data (current year)

#### `load_england_time_series.py`
Load England historical coverage (2009-2025)

#### `load_regional_time_series.py`
Load regional historical coverage

#### `load_special_programs.py`
Load special vaccination programs (HepB, BCG)

---

## Key Improvements Over Version 1

### ✅ No Duplicates
- Removed `csv_cleaner(1).py`
- Removed duplicate `load_england_time_series.py`
- Single source of truth for each concern

### ✅ Consistent Architecture
- All loaders use base class
- No mix of functional/OOP approaches
- Uniform error handling

### ✅ Clear Organization
- Source and tests separated
- Logical file grouping
- Easy to navigate

### ✅ Better Naming
- No version numbers in filenames
- Descriptive, consistent names
- Clear purpose for each file

### ✅ Reduced Complexity
- 13 source files (down from 19)
- Clear dependencies
- Easier to maintain

---

## Usage

### Import Pattern
```python
# From within the project
from database_version_2.src.models import GeographicArea, Vaccine
from database_version_2.src.database import create_test_session
from database_version_2.src.load_reference_data import load_all_reference_data
```

### Running Tests
```bash
# Run all tests
pytest database_version_2/tests/ -v

# Run specific test file
pytest database_version_2/tests/test_database.py -v

# Run with coverage
pytest database_version_2/tests/ --cov=database_version_2.src
```

### Loading Data
```python
from pathlib import Path
from database_version_2.src.database import create_production_session
from database_version_2.src.load_reference_data import load_all_reference_data
from database_version_2.src.load_national_coverage import load_all_national_coverage

# Create session
session = create_production_session("data/vaccination_coverage.db")

# Load reference data first
load_all_reference_data(Path("data/csv"), session)

# Load fact data
load_all_national_coverage(Path("data/csv"), session)

session.close()
```

---

## Testing Strategy

### Test Coverage
- ✅ Database connection and session management
- ✅ ORM model validation
- ✅ CSV cleaning functions
- ✅ All data loaders
- ✅ ODS conversion

### Test Principles
- Use pytest fixtures for database setup
- Temporary databases for isolation
- Test both success and error cases
- Verify data integrity

---

## Migration from Version 1

To migrate from the old structure:

1. Update import statements:
   ```python
   # Old
   from backend_code.database_src.models import Vaccine
   
   # New
   from database_version_2.src.models import Vaccine
   ```

2. Use refactored loaders (all use base class now)

3. Run tests to verify functionality

---

## Requirements Traceability

| Requirement | Implementation |
|-------------|----------------|
| DB-FR-001 (CREATE) | All loader modules |
| DB-FR-002 (READ) | `models.py` with SQLAlchemy |
| DB-FR-003 (UPDATE) | Loader modules (upsert logic) |
| DB-FR-004 (DELETE) | Session management |
| DB-FR-005 (Structured) | Normalized schema in `models.py` |
| DC-FR-001 (Handle missing) | `csv_cleaner.py` |
| DC-FR-002 (Type conversion) | `csv_cleaner.py` |
| DB-NFR-001 (Testable) | All test files |
| DB-NFR-002 (Configurable) | `database.py` |

---

**Maintainer:** Amyna  
**Last Updated:** 2025-12-09
