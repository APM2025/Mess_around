# Childhood Immunisation Coverage Data Insights Tool

## Project Overview

This project develops a Python-based data insights tool for analyzing public health data from the UK Health Security Agency's Coverage of Vaccination Evaluated Rapidly (COVER) programme.

## Purpose Statement

**Enable public health analysts to interactively explore childhood immunisation data through filtering, visualisation, and statistical analysis for evidence-based decisions.**

## Data Source

**Dataset:** COVER Programme Annual Report
**Provider:** UK Health Security Agency (UKHSA)

**Why This Dataset:**
- Trusted, authoritative source for UK immunisation data
- Covers multiple age cohorts (12 months, 24 months, 5 years, 3 months)
- Spans 163 geographic areas (UK, countries, regions, local authorities)
- Tracks 16 different vaccines across 17 years (2009-2025)
- Difficult to interpret quickly without visualization tools
- High value for public health research and policy decisions

## Project Status

**Version:** 1.0.0
**Status:** ✅ Production Ready
**Last Updated:** December 2024

**Key Metrics:**
- **Tests:** 324 passing (100% pass rate)
- **Code Coverage:** 76%
- **Test Execution Time:** ~7 minutes
- **Data Records:** ~3,000+ coverage records
- **API Endpoints:** 19 RESTful endpoints

## Scope

### In Scope ✅
- ✅ Load data from multiple CSV/XLSX formats (6 file types)
- ✅ Store data in structured SQLite database (8 tables)
- ✅ Filter by geography, vaccine, cohort, and year
- ✅ Generate summary statistics (mean, median, std dev)
- ✅ Interactive visualizations (bar, line, distribution charts)
- ✅ Full CRUD operations for data management
- ✅ CSV export capabilities
- ✅ Activity logging and audit trails
- ✅ RESTful API with Flask web framework
- ✅ Comprehensive test suite (324 tests)
- ✅ Security testing (SQL injection, XSS prevention)
- ✅ Input validation and error handling
- ✅ Complete documentation

### Out of Scope ⚠️
- Predictive modeling and forecasting
- Real-time data feeds from UKHSA APIs
- Multi-user authentication and authorization
- Mobile applications
- Cloud deployment
- Advanced analytics dashboards
- Data quality monitoring
- Automated reporting

## Stakeholder Analysis

| Stakeholder | Category | Influence | Power | Key Interests |
|------------|----------|-----------|-------|---------------|
| Public Health Analysts | Primary | High | Medium | Data exploration, filtering, trends |
| Developer | Primary | High | High | Code quality, maintainability, testing |
| COVER Programme (UKHSA) | Secondary | Medium | Medium | Data accuracy, proper usage |
| NHS/UKHSA Decision Makers | Secondary | Medium | Low | Evidence-based policy insights |
| Academic Researchers | Secondary | Medium | Low | Research data access |
| General Public | Tertiary | Low | Low | Transparency in immunisation rates |
| Regulatory Bodies | Tertiary | Low | Medium | Compliance, data protection |

## Architecture

**4-Layer Architecture** for clean separation of concerns:

```
┌─────────────────────────────────────────────┐
│  Layer 3: Presentation (Flask Web App)     │
│  - 19 API endpoints                        │
│  - Visualization generation                │
│  - 50 tests                                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Layer 2: Business Logic                   │
│  - CRUD operations & filtering             │
│  - Statistics & analytics                  │
│  - Export & logging services               │
│  - 156 tests                               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Layer 1: Database (SQLite + SQLAlchemy)   │
│  - 8 ORM models                            │
│  - Session management                      │
│  - Data integrity constraints              │
│  - 25 tests                                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Layer 0: Data Ingestion                   │
│  - 6 CSV/XLSX loaders                      │
│  - Data cleaning & validation              │
│  - Type conversion                         │
│  - 93 tests                                │
└─────────────────────────────────────────────┘
```

**Development Methodology:** Test-Driven Development (TDD)

**Technologies:** Python 3.12, Flask, SQLite, SQLAlchemy, Pandas, Matplotlib, Pytest

## Key Features Implemented

### Data Management
- ✅ Automatic data loading from 6 CSV/XLSX file formats
- ✅ Data cleaning and validation (handling commas, asterisks, missing values)
- ✅ SQLite database with 8 tables and full referential integrity
- ✅ Support for 163 geographic areas, 16 vaccines, 4 cohorts, 17 years

### Analysis Capabilities
- ✅ Interactive filtering by multiple dimensions
- ✅ Summary statistics calculation (mean, median, std dev)
- ✅ Trend analysis across years
- ✅ Comparison of geographic areas
- ✅ Special programs tracking (HepB, BCG)

### Visualizations
- ✅ Bar charts for coverage comparison
- ✅ Line charts for trend analysis
- ✅ Distribution histograms
- ✅ PNG export of all visualizations

### Web Interface
- ✅ RESTful API with 19 endpoints
- ✅ JSON responses for all operations
- ✅ Interactive dashboard
- ✅ ODS table reconstruction
- ✅ Real-time data updates

### Security & Quality
- ✅ 100% passing tests (324/324)
- ✅ 76% code coverage
- ✅ SQL injection protection via ORM
- ✅ XSS prevention via JSON responses
- ✅ Comprehensive input validation
- ✅ Error handling with proper HTTP codes
- ✅ Activity logging for audit trails

## Success Criteria

**Original Goals:**
- [✅] Load and process COVER programme data
- [✅] Enable interactive data exploration
- [✅] Generate visualizations and statistics
- [✅] Provide CRUD operations
- [✅] Export capabilities
- [✅] Comprehensive testing (>70% coverage)
- [✅] Security testing and protection

**Additional Achievements:**
- [✅] 100% test pass rate (324/324 tests)
- [✅] 76% code coverage (exceeds 70% target)
- [✅] Complete documentation suite
- [✅] Security tests for SQL injection and XSS
- [✅] RESTful API design
- [✅] Activity logging system

## Project Constraints

**Technical Constraints:**
- Python 3.12+ required
- Single-user desktop application (no multi-user auth)
- Local SQLite database (not distributed)
- No real-time data feeds (manual CSV loading)

**Time Constraints:**
- Academic project with semester deadline
- Iterative development with TDD approach

**Resource Constraints:**
- Single developer
- Local development environment
- No cloud infrastructure

## Risk Assessment

**Mitigated Risks:**
- ✅ **Data Quality:** Comprehensive data cleaning and validation
- ✅ **Security Vulnerabilities:** SQL injection and XSS testing
- ✅ **Code Quality:** TDD with 324 tests
- ✅ **Documentation:** Complete documentation suite

**Accepted Risks:**
- ⚠️ **No Authentication:** Acceptable for single-user local deployment
- ⚠️ **No Rate Limiting:** Acceptable for local use
- ⚠️ **SQLite Limitations:** Acceptable for dataset size

## Future Enhancements

Potential improvements (out of current scope):
- Multi-user authentication and authorization
- Real-time data feeds from UKHSA APIs
- Predictive modeling and forecasting
- Mobile application development
- Cloud deployment (AWS, Azure, GCP)
- Advanced analytics dashboard
- Data quality monitoring
- Automated reporting
- Integration with other health datasets

## Project Timeline

**Development Phases:**
1. ✅ Requirements Analysis
2. ✅ Architecture Design
3. ✅ Layer 0: Data Ingestion (93 tests)
4. ✅ Layer 1: Database (25 tests)
5. ✅ Layer 2: Business Logic (156 tests)
6. ✅ Layer 3: Presentation (50 tests)
7. ✅ Security Testing (SQL injection, XSS)
8. ✅ Input Validation Enhancement
9. ✅ Documentation Completion
10. ✅ Final Testing and Deployment

## Deliverables

**Code:**
- [✅] Source code (4-layer architecture)
- [✅] Test suite (324 tests, 76% coverage)
- [✅] Database schema and migrations

**Documentation:**
- [✅] Project Overview (this document)
- [✅] Requirements Specification
- [✅] Architecture Design
- [✅] API Documentation
- [✅] Testing Guide
- [✅] Security Documentation
- [✅] Deployment Guide
- [✅] UML Diagrams
- [✅] README.md
- [✅] CHANGELOG.md

**Data:**
- [✅] Sample COVER programme data
- [✅] Database initialization scripts
- [✅] Data cleaning utilities

## Contact Information

**Project Maintainer:** Amyn Ali
**Institution:** University of Warwick
**Course:** Programming for AI-MSI
**Academic Year:** 2024-2025

## License

This project is licensed under the MIT License.
