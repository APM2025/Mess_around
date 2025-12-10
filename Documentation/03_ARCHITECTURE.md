# Planned Architecture

## System Architecture Design

This document outlines the planned architecture for the Childhood Immunisation Coverage Data Insights Tool.

---

## Architecture Pattern: Layered Architecture

The system follows a **4-layer architecture** to ensure separation of concerns, testability, and maintainability.

```
┌─────────────────────────────────────────────┐
│   Layer 3: Presentation (Flask Web App)    │
│   - Web interface / API endpoints          │
│   - User interaction / Visualization       │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│   Layer 2: Business Logic                  │
│   - CRUD operations / Filtering            │
│   - Summary statistics / Analytics         │
│   - Data export services                   │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│   Layer 1: Database (Persistence)          │
│   - SQLAlchemy ORM models                  │
│   - Database schema / Session management   │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│   Layer 0: Data Ingestion                  │
│   - CSV/XLSX file loading                  │
│   - Data cleaning / Validation             │
└─────────────────────────────────────────────┘
```

---

## Layer Details

### Layer 0: Data Ingestion
**Responsibility:** Load and clean raw data

**Components:**
- File loaders (CSV, XLSX)
- Data cleaning functions
- Column normalization
- Type conversion
- Missing value handling

**Technologies:**
- Pandas for data manipulation
- Custom data cleaners

---

### Layer 1: Database (Persistence)
**Responsibility:** Data storage and retrieval

**Components:**
- Database models (ORM)
- Schema definitions
- Session management
- Migration support

**Technologies:**
- SQLAlchemy ORM
- SQLite database

**Key Models:**
- GeographicArea
- Vaccine
- AgeCohort
- FinancialYear
- Coverage (National/Local/Regional)

---

### Layer 2: Business Logic
**Responsibility:** Data processing and analysis

**Components:**
- CRUD operations
- Filtering service
- Summary statistics calculator
- Trend analyzer
- Data export service
- Activity logger

**Technologies:**
- Pure Python
- Pandas for aggregations

---

### Layer 3: Presentation
**Responsibility:** User interface and interaction

**Components:**
- Flask web application
- API endpoints (RESTful)
- Visualization generator
- Template rendering

**Technologies:**
- Flask web framework
- Matplotlib for charts
- HTML/CSS/JavaScript

---

## Data Flow

### 1. Initial Data Load
```
CSV Files → Data Ingestion → Database → Ready for Analysis
```

### 2. User Query Flow
```
User Request → Flask Route → Business Logic → Database Query → Response
```

### 3. Visualization Flow
```
User Filter → Business Logic → Data Processing → Matplotlib → PNG Chart → User
```

---

## Database Schema (Planned)

### Reference Tables
- **GeographicArea**: Stores countries, regions, local authorities
- **Vaccine**: Vaccine types (MMR, DTaP, etc.)
- **AgeCohort**: Age groups (12 months, 24 months, 5 years)
- **FinancialYear**: Reporting years

### Fact Tables
- **NationalCoverage**: Coverage data for UK and countries
- **LocalAuthorityCoverage**: UTLA-level coverage
- **RegionalCoverage**: Regional data
- **EnglandTimeSeries**: England historical trends

**Relationships:**
- Many-to-one from coverage tables to reference tables
- Foreign keys ensure referential integrity

---

## Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Data Ingestion** | Pandas | Industry standard for data manipulation |
| **Database** | SQLite + SQLAlchemy | Lightweight, no setup required, ORM benefits |
| **Business Logic** | Python | Clean, testable, maintainable |
| **Presentation** | Flask | Lightweight, easy to learn, flexible |
| **Visualization** | Matplotlib | Standard Python plotting library |
| **Testing** | Pytest | TDD-friendly, comprehensive features |

---

## Development Practices

### Test-Driven Development (TDD)
1. Write test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor for quality (REFACTOR)

### Code Organization
```
project/
├── src/
│   ├── layer0_data_ingestion/
│   ├── layer1_database/
│   ├── layer2_business_logic/
│   └── layer3_presentation/
├── tests/
│   ├── layer0_data_ingestion/
│   ├── layer1_database/
│   ├── layer2_business_logic/
│   └── layer3_presentation/
├── data/
└── Documentation/
```

---

## Security Architecture

### Input Validation
- All user inputs validated and sanitized
- File path validation
- Query parameter validation

### Database Security
- Parameterized queries (SQLAlchemy ORM)
- No raw SQL with user input
- Least-privilege access

### Secrets Management
- Environment variables for credentials
- No hard-coded passwords
- Secrets excluded from logs

---

## Performance Considerations

**Target Performance:**
- Filteringoperations: < 1 second
- Visualization generation: < 2 seconds
- Database queries: < 500ms

**Strategies:**
- Database indexing on frequently queried fields
- Efficient SQL queries via ORM
- Caching for frequently accessed data
- Limit result sets where appropriate

---

## Scalability

**Current Scope:** Single-user desktop application

**Future Scalability (Out of Scope):**
- Multi-user support
- Cloud deployment
- Real-time data feeds
- Advanced analytics

---

## Error Handling Strategy

1. **User-Friendly Messages:** Non-technical error descriptions
2. **Graceful Degradation:** System continues if non-critical errors occur
3. **Logging:** All errors logged for debugging
4. **Validation:** Input validated before processing

---

## Success Metrics

Architecture will be considered successful if:
- ✅ Each layer can be tested independently
- ✅ Clean separation of concerns maintained
- ✅ Performance targets met
- ✅ Easy to add new features
- ✅ Code is maintainable and readable
