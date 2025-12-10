# UK Childhood Immunisation Coverage Data Insights Tool

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-324%20passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-76%25-yellow.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

A comprehensive Python-based web application for analyzing and visualizing UK childhood immunisation coverage data from the COVER (Coverage of Vaccination Evaluated Rapidly) programme.

## 🎯 Project Overview

This tool enables public health analysts, researchers, and policymakers to interactively explore childhood immunisation data through:
- **Interactive filtering** by geography, vaccine type, age cohort, and year
- **Statistical analysis** with summary statistics and trend analysis
- **Data visualization** with charts and graphs
- **CRUD operations** for data management
- **CSV export** capabilities
- **Activity logging** for audit trails

**Data Source:** UK Health Security Agency (UKHSA) COVER Programme

## ✨ Key Features

### Data Management
- ✅ Load data from multiple CSV/XLSX formats
- ✅ Automatic data cleaning and validation
- ✅ SQLite database with SQLAlchemy ORM
- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ Support for 163 geographic areas, 16 vaccines, 4 age cohorts

### Analysis & Visualization
- ✅ Filter by vaccine, geography, cohort, or year
- ✅ Calculate summary statistics (mean, median, std dev)
- ✅ Compare areas and identify trends
- ✅ Generate interactive charts (bar, line, distribution)
- ✅ Export filtered data to CSV

### Web Interface
- ✅ Flask-based web application
- ✅ RESTful API endpoints
- ✅ Interactive dashboard
- ✅ ODS table reconstruction
- ✅ Real-time data updates

### Security & Quality
- ✅ **100% passing tests** (324 tests)
- ✅ **76% code coverage**
- ✅ SQL injection protection
- ✅ XSS prevention
- ✅ Input validation and sanitization
- ✅ Comprehensive error handling

## 🏗️ Architecture

**4-Layer Architecture** for clean separation of concerns:

```
┌──────────────────────────────────────────────┐
│  Layer 3: Presentation (Flask Web App)      │
│  - Web interface & API endpoints            │
│  - Visualization generation                 │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│  Layer 2: Business Logic                    │
│  - CRUD operations & filtering              │
│  - Statistics & analytics                   │
│  - Export & logging services                │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│  Layer 1: Database (SQLite + SQLAlchemy)    │
│  - ORM models (8 tables)                    │
│  - Session management                       │
│  - Data integrity constraints               │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│  Layer 0: Data Ingestion                    │
│  - CSV/XLSX file loading (5 formats)        │
│  - Data cleaning & validation               │
│  - Type conversion                          │
└──────────────────────────────────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.12 or higher
- pip package manager
- Git

### Quick Start

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Mess_around
```

2. **Create a virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python main.py
```

5. **Access the web interface:**
Open your browser to http://localhost:5000

## 🚀 Usage

### Running the Web Application

```bash
python main.py
```

The application will:
1. Load data from CSV files (if database doesn't exist)
2. Start the Flask web server on port 5000
3. Open automatically in your default browser

### Using the API

**Get all vaccines:**
```bash
curl http://localhost:5000/api/crud/vaccines
```

**Filter UTLA data:**
```bash
curl -X POST http://localhost:5000/api/tables/utla \
  -H "Content-Type: application/json" \
  -d '{"cohort_name": "24 months", "year": 2024}'
```

**Create/Update coverage data:**
```bash
curl -X POST http://localhost:5000/api/crud/coverage \
  -H "Content-Type: application/json" \
  -d '{
    "area_code": "E10000001",
    "vaccine_code": "MMR1",
    "cohort_name": "24 months",
    "year": 2024,
    "eligible_population": 1000,
    "vaccinated_count": 950
  }'
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/layer2_business_logic/test_crud.py

# Run tests in parallel (faster)
pytest tests/ -n auto
```

## 📊 Data Model

### Reference Tables
- **GeographicArea** (163 areas): UK, countries, regions, UTLAs
- **Vaccine** (16 vaccines): MMR, DTaP/IPV/Hib, PCV, Rotavirus, etc.
- **AgeCohort** (4 cohorts): 12 months, 24 months, 5 years, 3 months
- **FinancialYear** (17 years): 2009-2010 through 2024-2025

### Fact Tables
- **NationalCoverage**: UK and country-level data (~70 records)
- **LocalAuthorityCoverage**: UTLA-level data (~2,086 records)
- **EnglandTimeSeries**: Historical England data (~205 records)
- **RegionalTimeSeries**: Regional trends
- **SpecialPrograms**: HepB and BCG data (~623 records)

## 🗂️ Project Structure

```
Mess_around/
├── src/                          # Source code
│   ├── layer0_data_ingestion/    # CSV loaders & cleaners
│   ├── layer1_database/          # ORM models & sessions
│   ├── layer2_business_logic/    # CRUD, analysis, exports
│   └── layer3_presentation/      # Flask app & visualization
├── tests/                        # Test suite (324 tests)
│   ├── layer0_data_ingestion/
│   ├── layer1_database/
│   ├── layer2_business_logic/
│   └── layer3_presentation/
├── data/                         # CSV data files
├── templates/                    # HTML templates
├── static/                       # CSS, JS, charts
├── logs/                         # Activity logs
├── Documentation/                # Project documentation
├── main.py                       # Application entry point
├── create_database.py            # Database initialization
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🧪 Testing

### Test Coverage

**Overall Coverage: 76%**

```
High Coverage Modules (>90%):
✓ Database models (99%)
✓ CRUD operations (96%)
✓ Database layer (96%)
✓ Reference data loading (94%)
✓ User logging (90%)

All 324 tests passing!
```

### Test Categories
- **Unit Tests**: Individual function testing
- **Integration Tests**: Layer interaction testing
- **Security Tests**: SQL injection, XSS prevention
- **End-to-End Tests**: Full user workflows

### Security Testing
✅ SQL Injection Prevention (6 tests)
✅ XSS Prevention (3 tests)
✅ Input Validation (7 tests)
✅ Error Handling (11 tests)

## 🔒 Security Features

1. **SQL Injection Protection**
   - Parameterized queries via SQLAlchemy ORM
   - No raw SQL with user input
   - Comprehensive testing with malicious inputs

2. **XSS Prevention**
   - JSON API responses (naturally safe)
   - Input sanitization
   - No unsafe HTML rendering

3. **Input Validation**
   - Required field checking
   - Type validation (int, float, string)
   - Range validation (0-100% coverage)
   - Length limits on text fields
   - Relationship validation (vaccinated ≤ eligible)

4. **Error Handling**
   - Graceful degradation
   - User-friendly error messages
   - Session rollbacks on database errors
   - Proper HTTP status codes

## 📈 Performance

**Target Performance Metrics:**
- Filter operations: < 1 second ✅
- Visualization generation: < 2 seconds ✅
- Database queries: < 500ms ✅
- Full test suite: ~7 minutes ✅

## 🛠️ Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Language** | Python 3.12 | Main programming language |
| **Web Framework** | Flask | Web application & API |
| **Database** | SQLite | Data persistence |
| **ORM** | SQLAlchemy | Database abstraction |
| **Data Processing** | Pandas | Data manipulation |
| **Visualization** | Matplotlib | Chart generation |
| **Testing** | Pytest | Test framework |
| **Code Quality** | Pytest-cov | Coverage reporting |

## 📚 Documentation

Comprehensive documentation available in `Documentation/`:

1. [Project Overview](Documentation/01_PROJECT_OVERVIEW.md) - Purpose, scope, stakeholders
2. [Requirements Specification](Documentation/02_REQUIREMENTS.md) - Functional & non-functional requirements
3. [Architecture Design](Documentation/03_ARCHITECTURE.md) - System architecture & design decisions
4. [API Documentation](Documentation/04_API_DOCUMENTATION.md) - API endpoints & usage
5. [Testing Guide](Documentation/05_TESTING_GUIDE.md) - Test strategy & coverage
6. [Security Documentation](Documentation/06_SECURITY.md) - Security features & testing
7. [Deployment Guide](Documentation/07_DEPLOYMENT.md) - Setup & deployment instructions
8. [UML Diagrams](Documentation/08_UML_DIAGRAMS.md) - ER diagrams, class diagrams, sequence diagrams

## 🤝 Contributing

This is an academic project developed for coursework. Contributions follow standard practices:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest tests/`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **UK Health Security Agency** for providing COVER programme data
- **NHS England** for public health data infrastructure
- **University of Warwick** for academic support
- **Python Community** for excellent libraries and tools

## 📞 Contact

**Project Maintainer:** [Your Name]
**Institution:** University of Warwick
**Course:** Programming for AI-MSI
**Academic Year:** 2024-2025

## 🔮 Future Enhancements

Potential future improvements (out of current scope):
- Multi-user authentication & authorization
- Real-time data feeds from UKHSA APIs
- Predictive modeling & forecasting
- Mobile application
- Cloud deployment
- Advanced analytics dashboard
- Data quality monitoring
- Automated reporting

---

**Version:** 1.0.0
**Last Updated:** December 2024
**Status:** Production Ready ✅
