# UK Vaccination Coverage Dashboard System

A comprehensive web-based system for analyzing and visualizing UK vaccination coverage data from the COVER (Coverage of Vaccination Evaluated Rapidly) programme.

## Overview

This application provides:
- **Data Management**: SQLAlchemy ORM for storing vaccination coverage data across multiple geographic levels
- **Web Dashboard**: Flask application with three interactive dashboards
- **Analytics**: Statistical analysis with coverage classification and trend analysis
- **Data Export**: CSV export functionality
- **Activity Tracking**: Comprehensive user action logging
- **Visualizations**: Multiple chart types (bar, line, distribution, summary)

Built with a **4-layer architecture** ensuring clean separation of concerns, maintainability, and scalability.

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

For detailed installation instructions and troubleshooting, see [docs/SETUP.md](docs/SETUP.md).

### 2. Create and Populate Database

```bash
python create_database.py
```

This will:
- Create the database schema at `data/vaccination_coverage.db`
- Load reference data (geographic areas, vaccines, age cohorts, financial years)
- Load fact data from CSV files (if available)

### 3. Run the Flask Application

```bash
python app.py
```

Then open your browser to: `http://localhost:5000`

## Architecture

This project follows a **4-layer architecture** with strict unidirectional dependencies:

```
Layer 3 (Presentation)
    ↓
Layer 2 (Business Logic)
    ↓
Layer 1 (Database)
    ↓
Layer 0 (Data Ingestion)
```

### Layer 0: Data Ingestion & Cleaning
Handles raw data import, cleaning, and transformation.
- CSV cleaning utilities
- Data loaders (6 specialized loaders)
- ODS to CSV conversion
- Vaccine name matching

### Layer 1: Database Layer
Database models and session management.
- SQLAlchemy ORM models (9 tables)
- Database session factory
- Schema definitions

### Layer 2: Business Logic
Core application logic and data processing.
- CRUD operations
- Data filtering & analysis
- Coverage classification
- Export functionality
- Activity logging
- Table reconstruction

### Layer 3: Presentation
User interface and visualizations.
- Chart generation (4 chart types)
- Flask web interface
- REST API endpoints

For detailed architecture documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Project Structure

```
├── src/                                    # Source code
│   ├── layer0_data_ingestion/             # Layer 0: Data Ingestion
│   │   ├── csv_cleaner.py                 # CSV cleaning utilities
│   │   ├── csv_loader_base.py             # Base loader class
│   │   ├── load_reference_data.py         # Reference data loader
│   │   ├── load_national_coverage.py      # National data loader
│   │   ├── load_local_authority.py        # UTLA data loader
│   │   ├── load_england_timeseries.py     # England trends loader
│   │   ├── load_regional_timeseries.py    # Regional trends loader
│   │   ├── load_special_program.py        # Special programs loader
│   │   ├── ods_to_csv.py                  # ODS conversion
│   │   └── vaccine_matcher.py             # Vaccine name matching
│   │
│   ├── layer1_database/                   # Layer 1: Database
│   │   ├── models.py                      # SQLAlchemy ORM models (9 tables)
│   │   └── database.py                    # Session management
│   │
│   ├── layer2_business_logic/             # Layer 2: Business Logic
│   │   ├── crud.py                        # CRUD operations
│   │   ├── fs_analysis.py                 # Data analysis & classification
│   │   ├── export.py                      # CSV export
│   │   ├── user_log.py                    # Activity logging
│   │   └── table_builder.py               # Table reconstruction
│   │
│   └── layer3_presentation/               # Layer 3: Presentation
│       └── visualization.py               # Chart generation
│
├── tests/                                 # Test suite (21 test modules)
│   ├── layer0_data_ingestion/             # Tests for Layer 0
│   │   ├── test_csv_cleaner.py
│   │   ├── test_csv_loader_base.py
│   │   ├── test_load_*.py                 # Tests for all loaders
│   │   ├── test_ods_to_csv.py
│   │   └── test_vaccine_matcher.py
│   │
│   ├── layer1_database/                   # Tests for Layer 1
│   │   ├── test_models.py
│   │   └── test_database.py
│   │
│   ├── layer2_business_logic/             # Tests for Layer 2
│   │   ├── test_crud.py
│   │   ├── test_fs_analysis.py
│   │   ├── test_export.py
│   │   ├── test_user_log.py
│   │   └── test_table_builder.py
│   │
│   └── layer3_presentation/               # Tests for Layer 3
│       └── test_visualization.py
│
├── templates/                             # Flask HTML templates
│   ├── ods_tables.html                    # ODS table dashboard
│   ├── table_dashboard.html               # Interactive table view
│   └── dashboard.html                     # Charts dashboard
│
├── data/                                  # Data files
│   ├── csv_data/                          # CSV source files
│   ├── ods_data/                          # ODS source files
│   └── vaccination_coverage.db            # SQLite database (auto-created)
│
├── docs/                                  # Documentation
│   ├── ARCHITECTURE.md                    # Detailed architecture guide
│   ├── SETUP.md                           # Installation & setup guide
│   └── API.md                             # REST API documentation
│
├── static/                                # Static files (auto-created)
│   ├── charts/                            # Generated charts
│   └── exports/                           # Exported CSV files
│
├── logs/                                  # Log files (auto-created)
│   └── web_activity.log                   # User activity logs
│
├── app.py                                 # Flask web application
├── create_database.py                     # Database creation script
├── requirements.txt                       # Python dependencies
└── README.md                              # This file
```

## Database Schema

### Dimension Tables
- **GeographicArea**: Countries, regions, and local authorities (163 areas)
- **Vaccine**: Vaccine codes and names (16 vaccines)
- **AgeCohort**: Age groups for vaccination (4 cohorts: 12m, 24m, 5y, Special)
- **FinancialYear**: Financial years for time series (2009-2025)

### Fact Tables
- **NationalCoverage**: UK and country-level snapshots
- **LocalAuthorityCoverage**: UTLA-level coverage data
- **EnglandTimeSeries**: Historical England data (2009-2025)
- **RegionalTimeSeries**: Regional historical data
- **SpecialProgram**: HepB/BCG special programs

## Features

### Web Dashboard

Access three interactive dashboards:
- **ODS Tables** (`/`): View reconstructed ODS table formats
- **Table Dashboard** (`/tables`): Interactive table view with filtering
- **Charts Dashboard** (`/charts`): Visualizations and analytics

#### Dashboard Features:
- 📊 **Summary Statistics**: Count, mean, min, max coverage with classification
- 📈 **Charts**: Top areas, trends, distributions, summaries
- 📋 **Data Tables**: Filtered data with sortable columns
- 💾 **Export**: CSV export functionality
- 📝 **Activity Logs**: Track all user actions
- 🎨 **Coverage Classification**: Color-coded performance indicators (>=95% good, 85-95% warning, <85% low)

### API Endpoints

For complete API documentation with request/response examples, see [docs/API.md](docs/API.md).

#### Key Endpoints:
- **Data Analysis**: Filter data, get summaries, top areas, trends
- **Visualizations**: Generate charts (bar, line, distribution, summary)
- **Data Export**: CSV export with custom filtering
- **Activity Logging**: Track user actions and queries
- **CRUD Operations**: Manage vaccines and coverage data
- **Table Reconstruction**: Get ODS-formatted tables

## Testing

Run the full test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific layer tests
pytest tests/layer0_data_ingestion/
pytest tests/layer1_database/
pytest tests/layer2_business_logic/
pytest tests/layer3_presentation/

# Run specific test file
pytest tests/layer1_database/test_models.py
```

**Test Coverage**: 21 test modules organized by architectural layer
- **Layer 0**: CSV cleaning, data loaders, ODS conversion, vaccine matching
- **Layer 1**: Database models, session management
- **Layer 2**: CRUD operations, analysis, export, logging, table building
- **Layer 3**: Visualization generation

All modules follow Test-Driven Development (TDD) principles with comprehensive test coverage.

For detailed testing documentation, see [docs/TESTING.md](docs/TESTING.md).

## Usage Examples

### Example 1: Analyze MMR1 Coverage

```python
from src.layer1_database.database import get_session
from src.layer2_business_logic.fs_analysis import VaccinationAnalyzer

session = get_session()
analyzer = VaccinationAnalyzer(session)

# Get MMR1 data for 24-month cohort
data = analyzer.filter_data(vaccine_code='MMR1', cohort_name='24 months')

# Get summary statistics
summary = analyzer.get_summary(data)
print(f"Mean coverage: {summary['mean']}%")

# Classify coverage performance
classification = analyzer.classify_coverage(summary['mean'])
print(f"Performance: {classification}")  # 'good', 'warning', or 'low'

# Get top 10 performing areas
top_10 = analyzer.get_top_areas('MMR1', n=10, cohort_name='24 months')
```

### Example 2: Create Visualizations

```python
from src.layer3_presentation.visualization import VaccinationVisualizer
from pathlib import Path

visualizer = VaccinationVisualizer(output_dir=Path("static/charts"))

# Create top areas chart
visualizer.plot_top_areas(
    top_10,
    title="Top 10 Areas - MMR1 Coverage",
    filename="mmr1_top_areas.png"
)

# Create trend chart
trend = analyzer.get_trend('MMR1', cohort_name='24 months')
visualizer.plot_trend(
    trend,
    title="MMR1 Coverage Trend",
    filename="mmr1_trend.png"
)
```

### Example 3: Export Data

```python
from src.layer2_business_logic.export import DataExporter
from pathlib import Path

exporter = DataExporter()
exporter.export_to_csv(
    data,
    Path("static/exports/mmr1_coverage.csv")
)
```

## Architecture & Design Patterns

This project demonstrates several software engineering best practices:

### Design Patterns
- **Layered Architecture**: 4-layer separation with unidirectional dependencies
- **Template Method Pattern**: Base class (`csv_loader_base.py`) for CSV loaders with subclass implementations
- **ORM Pattern**: SQLAlchemy for database abstraction
- **Repository/DAO Pattern**: CRUD class provides data access layer
- **Factory Pattern**: Session factory for database connections

### Key Principles
- **Separation of Concerns**: Each layer has a single, well-defined responsibility
- **Dependency Inversion**: Higher layers depend on abstractions, not concrete implementations
- **Single Responsibility**: Each module handles one aspect of functionality
- **DRY (Don't Repeat Yourself)**: Shared logic centralized in base classes and utilities
- **Test-Driven Development**: Comprehensive test suite with 100%+ coverage

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Database** | SQLite with SQLAlchemy ORM |
| **Web Framework** | Flask |
| **Data Processing** | Pandas |
| **Visualization** | Matplotlib |
| **Testing** | Pytest |
| **Language** | Python 3.8+ |

## Development Methodology

This project follows professional software engineering practices:

### Test-Driven Development (TDD)
- Tests written before implementation
- RED-GREEN-REFACTOR cycle
- 100% code coverage for core modules
- All features validated with real data

### Version Control
- Git for version control
- Clean commit history
- Feature-based development

### Code Quality
- Type hints for all functions
- Comprehensive documentation
- Consistent code style
- Clear module boundaries

## Documentation

- **[SETUP.md](docs/SETUP.md)**: Installation, setup, and troubleshooting guide
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Detailed 4-layer architecture documentation
- **[API.md](docs/API.md)**: Complete REST API reference with examples
- **[TESTING.md](docs/TESTING.md)**: Testing guide and best practices

## Troubleshooting

For detailed troubleshooting, see [docs/SETUP.md](docs/SETUP.md).

### Common Issues

**"No data found" error**
- Ensure database is populated: `python create_database.py`
- Check vaccine code is valid (case-sensitive: 'MMR1' not 'mmr1')
- Verify cohort name matches database ('24 months' with space)

**Charts not displaying**
- Check `static/charts/` directory exists
- Ensure matplotlib is installed: `pip install matplotlib`
- Try refreshing the browser (Ctrl+F5)

**Port already in use**
- Change port in [app.py](app.py:298):
```python
app.run(debug=True, port=5001)  # Use different port
```

**Module import errors**
- Ensure you're in the project root directory
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version is 3.8+

## Data Sources

This system processes data from the UK Health Security Agency's COVER programme:
- **Coverage**: 163 geographic areas
- **Vaccines**: 16 different vaccines
- **Age Cohorts**: 4 cohorts (12m, 24m, 5y, Special)
- **Time Period**: Financial years 2009-2025

## Contributing

When contributing to this project:

1. **Follow the 4-layer architecture** - Place code in the appropriate layer
2. **Respect layer dependencies** - Only import from lower layers
3. **Write tests first** - Follow TDD principles
4. **Maintain test coverage** - Keep coverage above 90%
5. **Use type hints** - Add type hints for all functions
6. **Update documentation** - Document new features and changes
7. **Follow code style** - Maintain consistency with existing code

## License

This project is for educational purposes as part of the Programming for AI MSI course.

## Project Status

**Current Version**: 3.0.0

### Recent Updates
- ✅ Implemented 4-layer architecture
- ✅ Created comprehensive documentation
- ✅ Added coverage classification logic
- ✅ Reorganized test suite by layer
- ✅ Centralized business logic from front-end

### Technical Debt
- None currently - codebase is clean and well-organized

## Notes

- All user actions are logged to `logs/web_activity.log`
- Charts are cached in `static/charts/`
- CSV exports saved to `static/exports/`
- Database uses SQLite for simplicity (can be upgraded to PostgreSQL/MySQL)
- Auto-created directories: `static/`, `logs/`, `data/vaccination_coverage.db`

## Future Enhancements

Potential improvements for production deployment:
- User authentication and authorization
- Rate limiting for API endpoints
- Real-time updates with WebSockets
- Advanced filtering options in UI
- Chart customization interface
- Data validation at API layer
- Integration tests for Flask endpoints
- Docker containerization
- Database migration system (Alembic)
- Caching layer (Redis)
- API versioning
