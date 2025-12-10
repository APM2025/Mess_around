# Layered Architecture

This codebase follows a strict 4-layer architecture pattern.

## Layer 0: Data Ingestion & Cleaning
**Purpose**: Raw data loading, format conversion, data cleaning, and validation.
**Dependencies**: None (lowest layer)

### Modules (`src/layer0_data_ingestion/`)
- `ods_to_csv.py` - ODS file to CSV conversion
- `csv_cleaner.py` - Data cleaning and normalization
- `vaccine_matcher.py` - Vaccine name matching and canonicalization
- `csv_loader_base.py` - Base class for CSV loaders (Template Method pattern)
- `load_reference_data.py` - Load reference/dimension data
- `load_national_coverage.py` - Load national coverage data
- `load_local_authority.py` - Load local authority coverage data
- `load_england_time_series.py` - Load England time series data
- `load_regional_time_series.py` - Load regional time series data
- `load_special_programs.py` - Load special programs data (HepB, BCG)

### Tests (`tests/layer0_data_ingestion/`)
- All corresponding test files

---

## Layer 1: Database Layer
**Purpose**: Database schema, models, connections, and session management.
**Dependencies**: Layer 0 (for initial data loading)

### Modules (`src/layer1_database/`)
- `models.py` - SQLAlchemy ORM models (9 tables)
- `database.py` - Database session management and connection

### Tests (`tests/layer1_database/`)
- `test_models.py`
- `test_database.py`

---

## Layer 2: Business Logic Layer
**Purpose**: Core business operations, data analysis, transformations, and CRUD.
**Dependencies**: Layer 1 (database), Layer 0 (for data types)

### Modules (`src/layer2_business_logic/`)
- `fs_analysis.py` - Filtering, statistics, and data analysis
- `table_builder.py` - ODS table reconstruction and formatting
- `crud.py` - Create, Read, Update, Delete operations
- `export.py` - Data export functionality (CSV)
- `user_log.py` - Activity logging

### Tests (`tests/layer2_business_logic/`)
- All corresponding test files

---

## Layer 3: Presentation Layer
**Purpose**: User-facing interfaces, visualization, and API endpoints.
**Dependencies**: Layer 2 (business logic)

### Modules (`src/layer3_presentation/`)
- `visualization.py` - Chart generation (matplotlib)

### Application Files (root)
- `app.py` - Flask application with REST API endpoints
- `create_database.py` - Database initialization script

### Templates (`templates/`)
- `dashboard.html` - Analytics dashboard
- `table_dashboard.html` - Table view with CRUD
- `ods_tables.html` - ODS-compliant table format

### Tests (`tests/layer3_presentation/`)
- `test_visualization.py`
- `test_flask_app.py`

---

## Entry Points (Root Directory)

Entry point scripts live in the project root directory, **outside the layered architecture**. These are orchestration scripts that coordinate multiple layers and serve as the primary interface for users and deployment.

### Why Entry Points Are Outside Layers

1. **Cross-layer orchestration**: Entry points use components from multiple layers
2. **Application lifecycle**: They handle initialization, startup, and shutdown
3. **User convenience**: Easier to discover and run from the project root
4. **Architectural independence**: They don't belong to any single layer

### Entry Point Scripts

#### `create_database.py` - Database Initialization Script
**Purpose**: Creates database schema and loads initial data

**What it does**:
1. Creates the database schema (Layer 1)
2. Loads reference data (Layer 0)
3. Loads fact data from CSV files (Layer 0)
4. Verifies data integrity
5. Reports statistics

**Usage**:
```bash
python create_database.py
```

**Dependencies**:
- Layer 1 (database models and session)
- Layer 0 (all data loaders)

**When to run**:
- First time setup
- After database schema changes
- To reset the database to initial state

---

#### `app.py` - Flask Web Application
**Purpose**: Runs the web server and exposes the REST API

**What it does**:
1. Initializes Flask application
2. Sets up routes and API endpoints
3. Coordinates Layer 2 (business logic) and Layer 3 (presentation)
4. Handles HTTP requests/responses
5. Serves HTML templates

**Usage**:
```bash
python app.py
```

**Dependencies**:
- Layer 3 (visualization)
- Layer 2 (business logic, CRUD, analysis, export)
- Layer 1 (database session)

**When to run**:
- To start the web application
- For development and testing
- For production deployment (with WSGI server)

---

### Entry Points vs. Layered Modules

| Aspect | Entry Points | Layered Modules |
|--------|--------------|-----------------|
| Location | Root directory | `src/layer[0-3]_*/` |
| Purpose | Orchestration | Single responsibility |
| Dependencies | Multi-layer | Single layer below |
| User access | Direct execution | Imported by other code |
| Examples | `app.py`, `create_database.py` | `models.py`, `fs_analysis.py` |

---

## Dependency Rules

```
Layer 3 (Presentation)
    ↓ uses
Layer 2 (Business Logic)
    ↓ uses
Layer 1 (Database)
    ↓ uses
Layer 0 (Data Ingestion)
    ↓ uses
External Libraries (pandas, sqlalchemy, etc.)
```

**IMPORTANT**:
- Higher layers can import from lower layers
- Lower layers CANNOT import from higher layers
- Layers should only import from the layer immediately below
- Skip-level imports (e.g., Layer 3 → Layer 0) should be minimized

---

## Import Examples

### Layer Imports

```python
# Layer 0 - No internal imports (only external libraries)
from pathlib import Path
import pandas as pd

# Layer 1 - Can import Layer 0
from src.layer0_data_ingestion.csv_cleaner import clean_csv_data
from src.layer1_database.models import Vaccine

# Layer 2 - Can import Layer 1 (and Layer 0 if needed)
from src.layer1_database.models import LocalAuthorityCoverage
from src.layer1_database.database import get_session
from src.layer2_business_logic.fs_analysis import VaccinationAnalyzer

# Layer 3 - Can import Layer 2
from src.layer2_business_logic.table_builder import TableBuilder
from src.layer3_presentation.visualization import VaccinationVisualizer
```

### Entry Point Imports

Entry points can import from any layer as needed:

```python
# create_database.py - Database initialization script
from src.layer1_database.database import get_session
from src.layer1_database.models import Vaccine, GeographicArea
from src.layer0_data_ingestion.load_reference_data import load_vaccines
from src.layer0_data_ingestion.load_national_coverage import load_national_coverage

# app.py - Flask web application
from flask import Flask, render_template
from src.layer1_database.database import get_session
from src.layer2_business_logic.fs_analysis import VaccinationAnalyzer
from src.layer2_business_logic.crud import VaccinationCRUD
from src.layer3_presentation.visualization import VaccinationVisualizer
```
