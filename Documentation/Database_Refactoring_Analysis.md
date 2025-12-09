# Database Source Code Refactoring Analysis

**Date:** 2025-12-09  
**Status:** Analysis Complete - Ready for Refactoring

---

## Executive Summary

The `backend_code/database_src` directory contains **19 Python files** with significant duplication, inconsistent naming, and unclear organization. This analysis identifies the issues and proposes a clean, maintainable structure while preserving all functionality.

### Key Issues Identified

1. **Duplicate Files**
   - `csv_cleaner.py` and `csv_cleaner(1).py` - Same functionality
   - `load_england_time_series.py` and `load_england_time_series_refactored.py` - Two versions

2. **Inconsistent Architecture**
   - Mix of functional and OOP approaches
   - `csv_data_loader.py` provides base class but not all loaders use it
   - Some loaders refactored, others not

3. **Unclear Responsibilities**
   - `vaccine_reference.py` vs `vaccine_matcher.py` - overlapping functionality
   - `loader_utils.py` - grab-bag of utilities
   - `csv_type_identifier.py` - unclear purpose

4. **Naming Confusion**
   - `csv_cleaner_v2.py` (deleted by git clean) suggests version control issues
   - Inconsistent naming patterns

---

## Current File Inventory

### Core Infrastructure (Keep & Clean)
| File | Purpose | Status | Lines |
|------|---------|--------|-------|
| `models.py` | SQLAlchemy ORM models | ✅ Good | 332 |
| `database.py` | Session management | ✅ Good | ~80 |
| `session_factory.py` | Session factory pattern | ⚠️ Review | ~90 |

### Data Loading - Base Classes
| File | Purpose | Status | Action |
|------|---------|--------|--------|
| `csv_data_loader.py` | Base loader class (OOP) | ✅ Keep | 5334 bytes |
| `ods_to_csv.py` | ODS to CSV conversion | ✅ Keep | 5830 bytes |

### Data Loading - Specific Loaders
| File | Purpose | Status | Action |
|------|---------|--------|--------|
| `load_reference_data.py` | Load dimension tables | ✅ Keep | 8950 bytes |
| `load_national_coverage.py` | Load national data | ✅ Keep | 6429 bytes |
| `load_local_authority.py` | Load UTLA data | ✅ Keep | 7749 bytes |
| `load_england_time_series.py` | Load England time series (OLD) | ❌ Remove | 4958 bytes |
| `load_england_time_series_refactored.py` | Load England time series (NEW) | ✅ Keep → Rename | 4726 bytes |
| `load_regional_time_series.py` | Load regional time series | ✅ Keep | 6867 bytes |
| `load_special_programs.py` | Load HepB/BCG data | ✅ Keep | 7281 bytes |

### CSV Processing Utilities
| File | Purpose | Status | Action |
|------|---------|--------|--------|
| `csv_cleaner.py` | CSV cleaning functions | ✅ Keep | 286 lines |
| `csv_cleaner(1).py` | **DUPLICATE** | ❌ Delete | 8950 bytes |
| `csv_type_identifier.py` | Identify CSV types | ⚠️ Review/Merge | 4110 bytes |

### Vaccine Matching
| File | Purpose | Status | Action |
|------|---------|--------|--------|
| `vaccine_reference.py` | Vaccine name matching | ✅ Keep | 3554 bytes |
| `vaccine_matcher.py` | Vaccine matching logic | ⚠️ Merge into above | 4610 bytes |

### Utilities
| File | Purpose | Status | Action |
|------|---------|--------|--------|
| `loader_utils.py` | Shared loader utilities | ⚠️ Review/Refactor | 2797 bytes |
| `__init__.py` | Package initialization | ✅ Keep | 58 bytes |

---

## Proposed Clean Architecture

### Directory Structure
```
backend_code/database_src/
├── __init__.py                      # Package exports
├── models.py                        # ✅ SQLAlchemy models (unchanged)
├── database.py                      # ✅ Session management (unchanged)
│
├── core/                            # NEW: Core utilities
│   ├── __init__.py
│   ├── csv_cleaner.py              # CSV cleaning functions
│   ├── csv_loader_base.py          # Base class for all loaders
│   ├── vaccine_matcher.py          # Unified vaccine matching
│   └── utils.py                    # Shared utilities
│
├── converters/                      # NEW: Format converters
│   ├── __init__.py
│   └── ods_to_csv.py               # ODS conversion
│
└── loaders/                         # NEW: Data loaders
    ├── __init__.py
    ├── reference_data.py           # Load dimension tables
    ├── national_coverage.py        # Load national data
    ├── local_authority.py          # Load UTLA data
    ├── england_time_series.py      # Load England historical
    ├── regional_time_series.py     # Load regional historical
    └── special_programs.py         # Load HepB/BCG
```

### Alternative: Flat Structure (Simpler)
```
backend_code/database_src/
├── __init__.py
├── models.py                        # ✅ ORM models
├── database.py                      # ✅ Session management
├── csv_cleaner.py                   # CSV utilities
├── csv_loader_base.py               # Base loader class
├── vaccine_matcher.py               # Vaccine matching
├── ods_to_csv.py                    # ODS conversion
├── load_reference_data.py           # Reference data loader
├── load_national_coverage.py        # National loader
├── load_local_authority.py          # UTLA loader
├── load_england_time_series.py      # England time series loader
├── load_regional_time_series.py     # Regional time series loader
└── load_special_programs.py         # Special programs loader
```

**Recommendation:** Use **Flat Structure** for simplicity and easier imports.

---

## Refactoring Actions

### Phase 1: Delete Duplicates
```bash
# Remove duplicate and obsolete files
rm csv_cleaner(1).py
rm load_england_time_series.py  # Keep refactored version
```

### Phase 2: Consolidate Vaccine Matching
- Merge `vaccine_matcher.py` into `vaccine_reference.py`
- Create single `vaccine_matcher.py` with all matching logic
- Update all imports

### Phase 3: Rename for Clarity
```
load_england_time_series_refactored.py → load_england_time_series.py
csv_data_loader.py → csv_loader_base.py
loader_utils.py → (merge into csv_loader_base.py or csv_cleaner.py)
```

### Phase 4: Standardize All Loaders
Ensure all loaders:
1. Inherit from `CSVDataLoader` base class
2. Follow same pattern (see `load_england_time_series_refactored.py`)
3. Have consistent error handling
4. Use same utility functions

### Phase 5: Update Tests
- Ensure all tests pass with new structure
- Update imports in test files
- No functionality changes - just reorganization

### Phase 6: Clean Up Utilities
- Review `csv_type_identifier.py` - merge into `csv_cleaner.py` if simple
- Review `loader_utils.py` - merge into base class
- Remove any unused functions

---

## Files to Delete

1. ✅ `csv_cleaner(1).py` - Exact duplicate
2. ✅ `load_england_time_series.py` - Replaced by refactored version
3. ⚠️ `csv_type_identifier.py` - Review first, likely merge
4. ⚠️ `loader_utils.py` - Merge into base class
5. ⚠️ `vaccine_matcher.py` - Merge with vaccine_reference.py
6. ⚠️ `session_factory.py` - Check if used, may be redundant with database.py

---

## Files to Rename

1. `load_england_time_series_refactored.py` → `load_england_time_series.py`
2. `csv_data_loader.py` → `csv_loader_base.py` (optional, for clarity)

---

## Files to Keep (Core)

### Infrastructure
- ✅ `models.py` - ORM models
- ✅ `database.py` - Session management
- ✅ `__init__.py` - Package init

### Utilities
- ✅ `csv_cleaner.py` - CSV cleaning functions
- ✅ `ods_to_csv.py` - ODS conversion
- ✅ `vaccine_matcher.py` - Unified vaccine matching (after merge)

### Loaders
- ✅ `csv_loader_base.py` - Base class for loaders
- ✅ `load_reference_data.py` - Reference data
- ✅ `load_national_coverage.py` - National coverage
- ✅ `load_local_authority.py` - Local authority
- ✅ `load_england_time_series.py` - England time series (refactored version)
- ✅ `load_regional_time_series.py` - Regional time series
- ✅ `load_special_programs.py` - Special programs

**Total: 13 clean, focused files (down from 19)**

---

## Test Coverage Requirements

All tests must pass after refactoring:

### Test Files
- `test_database.py` - Database connection tests
- `test_models.py` - ORM model tests
- `test_csv_cleaner.py` - CSV cleaning tests
- `test_load_reference_data.py` - Reference data loading
- `test_load_national_coverage.py` - National coverage loading
- `test_load_local_authority.py` - Local authority loading
- `test_load_england_time_series.py` - England time series loading
- `test_load_regional_time_series.py` - Regional time series loading
- `test_load_special_programs.py` - Special programs loading
- `test_ods_conversion.py` - ODS conversion tests

**All 10 test files must pass with 100% of current functionality preserved.**

---

## Implementation Plan

### Step 1: Analysis Complete ✅
- Inventory all files
- Identify duplicates
- Map dependencies

### Step 2: Create Backup
```bash
git add -A
git commit -m "Pre-refactoring backup"
```

### Step 3: Delete Obvious Duplicates
```bash
rm csv_cleaner(1).py
```

### Step 4: Consolidate Vaccine Matching
- Merge `vaccine_matcher.py` and `vaccine_reference.py`
- Create unified `vaccine_matcher.py`
- Update all imports

### Step 5: Rename Refactored Files
```bash
mv load_england_time_series_refactored.py load_england_time_series.py
# Delete old version (already done in step 3)
```

### Step 6: Review and Merge Utilities
- Check `csv_type_identifier.py` usage
- Check `loader_utils.py` usage
- Merge into appropriate files

### Step 7: Run All Tests
```bash
pytest tests/tests_database/ -v
```

### Step 8: Update Documentation
- Update import statements in README
- Update architecture diagrams
- Document final structure

---

## Success Criteria

1. ✅ All tests pass
2. ✅ No duplicate files
3. ✅ Clear, consistent naming
4. ✅ All loaders use base class
5. ✅ Single source of truth for each concern
6. ✅ Easy to understand file organization
7. ✅ Reduced from 19 to ~13 files

---

## Risk Mitigation

1. **Git Backup**: Commit before any changes
2. **Test-Driven**: Run tests after each change
3. **Incremental**: One file at a time
4. **Reversible**: Keep git history clean for easy rollback

---

## Next Steps

1. **Review this analysis** with stakeholder
2. **Get approval** for refactoring approach
3. **Execute refactoring** following implementation plan
4. **Verify all tests pass**
5. **Update documentation**

---

**Document Owner:** Amyna (Developer)  
**Last Updated:** 2025-12-09
