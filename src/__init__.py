"""
Database Version 2 - Source Code

Clean, refactored database code with clear organization.

Core modules:
- models: SQLAlchemy ORM models
- database: Session management
- csv_cleaner: CSV cleaning utilities
- vaccine_matcher: Vaccine name matching
- ods_to_csv: ODS to CSV conversion

Data loaders:
- load_reference_data: Load dimension tables
- load_national_coverage: Load national coverage
- load_local_authority: Load local authority data
- load_england_time_series: Load England historical data
- load_regional_time_series: Load regional historical data
- load_special_programs: Load HepB/BCG programs
"""

__version__ = "2.0.0"
__author__ = "Amyna"

# Core exports
from .models import (
    Base,
    GeographicArea,
    Vaccine,
    AgeCohort,
    FinancialYear,
    NationalCoverage,
    LocalAuthorityCoverage,
    EnglandTimeSeries,
    RegionalTimeSeries,
    SpecialProgram,
    init_database
)

from .database import (
    create_test_session,
    create_production_session,
    get_session
)

__all__ = [
    # Models
    "Base",
    "GeographicArea",
    "Vaccine",
    "AgeCohort",
    "FinancialYear",
    "NationalCoverage",
    "LocalAuthorityCoverage",
    "EnglandTimeSeries",
    "RegionalTimeSeries",
    "SpecialProgram",
    "init_database",
    # Database
    "create_test_session",
    "create_production_session",
    "get_session",
]
