# UK Vaccination Coverage Dashboard System

A comprehensive web-based system for analyzing and visualizing UK vaccination coverage data from the COVER (Coverage of Vaccination Evaluated Rapidly) programme.

## Overview

This application provides:
- **Data Management**: SQLAlchemy ORM for storing vaccination coverage data across multiple geographic levels
- **Web Dashboard**: Flask application for interactive data exploration and visualization
- **Analytics**: Statistical analysis of vaccination coverage rates
- **Data Export**: CSV export functionality
- **Activity Tracking**: User action logging
- **Visualizations**: Multiple chart types (bar, line, distribution, summary)

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

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

## Project Structure

```
├── src/                          # Source code
│   ├── models.py                 # SQLAlchemy ORM models (9 tables)
│   ├── database.py               # Database session management
│   ├── csv_cleaner.py            # CSV cleaning utilities
│   ├── csv_loader_base.py        # Base class for data loaders
│   ├── load_*.py                 # Data loading modules (6 loaders)
│   ├── crud.py                   # CRUD operations
│   ├── fs_analysis.py            # Data filtering & analysis
│   ├── visualization.py          # Chart generation (4 chart types)
│   ├── export.py                 # CSV export functionality
│   ├── user_log.py               # Activity logging
│   ├── table_builder.py          # Table reconstruction
│   └── vaccine_matcher.py        # Vaccine name matching
│
├── tests/                        # Test suite (14 test modules)
│   ├── test_models.py
│   ├── test_database.py
│   ├── test_csv_cleaner.py
│   ├── test_crud.py
│   ├── test_load_*.py            # Tests for all loaders
│   ├── test_export.py
│   ├── test_visualization.py
│   ├── test_fs_analysis.py
│   └── test_user_log.py
│
├── scripts/                      # Demo and utility scripts
│   ├── test_analysis.py          # Manual test for analysis module
│   ├── demo_crud.py              # CRUD operations demo
│   ├── demo_logging_and_export.py # Logging & export demo
│   └── demo_visualizations.py    # Visualization demo
│
├── templates/                    # Flask HTML templates
│   ├── ods_tables.html
│   ├── table_dashboard.html
│   └── dashboard.html
│
├── data/                         # Data files
│   ├── csv_data/                 # CSV source files (17 files)
│   ├── ods_data/                 # ODS source files
│   └── vaccination_coverage.db   # SQLite database
│
├── Documentation/                # Technical documentation
├── app.py                        # Flask web application
├── create_database.py            # Database creation script
├── requirements.txt              # Python dependencies
└── README.md                     # This file
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

Access three dashboards:
- **ODS Tables** (`/`): View reconstructed ODS table formats
- **Table Dashboard** (`/tables`): Interactive table view
- **Charts Dashboard** (`/charts`): Visualizations and analytics

#### Dashboard Features:
- 📊 **Summary Statistics**: Count, mean, min, max coverage
- 📈 **Charts**: Top areas, trends, distributions, summaries
- 📋 **Data Tables**: Filtered data with export
- 📝 **Activity Logs**: Track all user actions

### API Endpoints

#### Data Analysis
- `GET /api/vaccines` - List all vaccines
- `POST /api/filter` - Filter vaccination data
- `POST /api/summary` - Get summary statistics
- `POST /api/top-areas` - Get top performing areas
- `POST /api/trend` - Get coverage trend over time

#### Visualizations
- `POST /api/visualize/top-areas` - Generate top areas chart
- `POST /api/visualize/trend` - Generate trend chart
- `POST /api/visualize/summary` - Generate summary chart
- `POST /api/visualize/distribution` - Generate distribution chart

#### Data Management
- `POST /api/export/csv` - Export data to CSV
- `GET /api/logs/recent` - Get recent activity logs
- `GET/POST/PUT/DELETE /api/crud/vaccines` - Manage vaccines

### Command Line Tools

#### Analysis Demo
```bash
python scripts/test_analysis.py
```

#### CRUD Demo
```bash
python scripts/demo_crud.py
```

#### Logging & Export Demo
```bash
python scripts/demo_logging_and_export.py
```

#### Visualization Demo
```bash
python scripts/demo_visualizations.py
```

## Testing

Run the full test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_models.py
```

**Test Coverage**: 14 test modules with comprehensive coverage
- Database models and schema
- CSV cleaning functionality
- All data loaders
- CRUD operations
- Analysis queries
- Export functionality
- Visualization generation
- User logging

## Usage Examples

### Example 1: Analyze MMR1 Coverage

```python
from src.database import get_session
from src.fs_analysis import VaccinationAnalyzer

session = get_session()
analyzer = VaccinationAnalyzer(session)

# Get MMR1 data for 24-month cohort
data = analyzer.filter_data(vaccine_code='MMR1', cohort_name='24 months')

# Get summary statistics
summary = analyzer.get_summary(data)
print(f"Mean coverage: {summary['mean']}%")

# Get top 10 performing areas
top_10 = analyzer.get_top_areas('MMR1', n=10, cohort_name='24 months')
```

### Example 2: Create Visualizations

```python
from src.visualization import VaccinationVisualizer
from pathlib import Path

visualizer = VaccinationVisualizer(output_dir=Path("charts"))

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
from src.export import DataExporter

exporter = DataExporter()
exporter.export_to_csv(
    data,
    Path("exports/mmr1_coverage.csv")
)
```

## Architecture & Design Patterns

- **Template Method Pattern**: Base class for CSV loaders with subclass implementations
- **ORM Pattern**: SQLAlchemy for database abstraction
- **Repository/DAO Pattern**: CRUD class provides data access layer
- **Factory Pattern**: Session factory for database connections
- **Separation of Concerns**: Clean layering (models → loaders → CRUD → analysis → API)

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

This project was built using **Test-Driven Development (TDD)**:
- Tests written before implementation
- RED-GREEN-REFACTOR cycle followed
- 100% code coverage for core modules
- All features validated with real data

## Troubleshooting

### "No data found" error
- Ensure database is populated: `python create_database.py`
- Check vaccine code is valid (e.g., 'MMR1' not 'mmr1')
- Verify cohort name matches database ('24 months' with space)

### Charts not displaying
- Check `static/charts/` directory exists
- Ensure matplotlib is installed
- Try refreshing the browser (Ctrl+F5)

### Port already in use
Change port in app.py:
```python
app.run(debug=True, port=5001)  # Use different port
```

## Data Sources

This system processes data from the UK Health Security Agency's COVER programme:
- **Coverage**: 163 geographic areas
- **Vaccines**: 16 different vaccines
- **Age Cohorts**: 4 cohorts (12m, 24m, 5y, Special)
- **Time Period**: Financial years 2009-2025

## Contributing

When contributing:
1. Follow TDD principles - write tests first
2. Maintain test coverage above 90%
3. Use type hints for all functions
4. Follow existing code style
5. Update documentation for new features

## License

This project is for educational purposes as part of the Programming for AI MSI course.

## Notes

- All user actions are logged to `logs/web_activity.log`
- Charts are cached in `static/charts/`
- CSV exports saved to `static/exports/`
- Database uses SQLite for simplicity (can be upgraded to PostgreSQL/MySQL)

## Future Enhancements

Potential improvements:
- User authentication and authorization
- Real-time updates with WebSockets
- Advanced filtering options
- Chart customization UI
- Data validation at API layer
- Integration tests for Flask endpoints
- Docker containerization
- Database migration system (Alembic)
