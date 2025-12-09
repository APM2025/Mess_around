# Database Schema Design

**Document Version:** 1.0  
**Date:** 2025-12-08  
**Status:** Approved  
**Database:** SQLite (development), upgradeable to PostgreSQL (production)

---

## Design Principles

### Normalization Level: 3rd Normal Form (3NF)
- Eliminate data redundancy
- Ensure data integrity through foreign key relationships
- Support efficient querying and updates

### Architecture Pattern: Star Schema
- **Dimension Tables:** Reference data (geography, vaccines, time periods)
- **Fact Tables:** Measurement data (vaccination coverage)
- Optimized for analytical queries (GROUP BY, JOIN, aggregations)

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Relational DB over NoSQL** | Structured data with clear relationships; supports complex SQL queries |
| **Normalized schema** | Reduces redundancy; satisfies academic learning outcomes (demonstrate normalization) |
| **Single fact table** | All 3 dataset types share same structure; simplifies queries |
| **Dimension tables** | Enable consistent reference data; support hierarchical relationships |
| **SQLite for MVP** | Zero-configuration; easily upgradeable; sufficient for ~10k records |

---

## Entity-Relationship Diagram (ERD)

### Textual ERD Representation

```
┌─────────────────────────┐
│  geographic_areas       │
├─────────────────────────┤
│ PK  id                  │
│ UNQ code                │──┐
│     name                │  │
│     type                │  │ Self-referencing
│ FK  parent_code         │◄─┘ (UTLA → Region → Country)
│     created_at          │
└─────────────────────────┘
         │
         │ 1
         │
         │ N
         ▼
┌─────────────────────────┐         ┌─────────────────────────┐
│  vaccines               │         │  age_cohorts            │
├─────────────────────────┤         ├─────────────────────────┤
│ PK  id                  │         │ PK  id                  │
│ UNQ code                │         │ UNQ name                │
│     full_name           │         │     age_in_months       │
│     short_name          │         │     birth_period_start  │
│     target_age_months   │         │     birth_period_end    │
│     created_at          │         │     created_at          │
└─────────────────────────┘         └─────────────────────────┘
         │                                   │
         │ 1                                 │ 1
         └──────────┬────────────────────────┘
                    │ N
                    ▼
         ┌─────────────────────────┐
         │  coverage_data          │◄────────┐
         ├─────────────────────────┤         │
         │ PK  id                  │         │ N
         │ FK  geographic_area_id  │         │
         │ FK  vaccine_id          │         │
         │ FK  age_cohort_id       │   ┌─────────────────────┐
         │ FK  reporting_period_id │   │ reporting_periods   │
         │     coverage_%          │   ├─────────────────────┤
         │     numerator           │   │ PK  id              │
         │     denominator         │   │     year            │
         │     is_suppressed       │   │     quarter         │
         │     is_confidential     │   │     period_type     │
         │     notes               │   │     data_collect_dt │
         │     dataset_type        │   │     created_at      │
         │     created_at          │   └─────────────────────┘
         │ UNQ(geo, vax, cohort,   │         ▲
         │     period)             │         │ 1
         └─────────────────────────┘─────────┘

┌─────────────────────────┐
│  data_load_log          │ (Audit table - no relationships)
├─────────────────────────┤
│ PK  id                  │
│     filename            │
│     sheet_name          │
│     rows_loaded         │
│     load_status         │
│     error_message       │
│     loaded_at           │
└─────────────────────────┘
```

### Cardinality Summary
- `geographic_areas` (1) → `coverage_data` (N)
- `vaccines` (1) → `coverage_data` (N)  
- `age_cohorts` (1) → `coverage_data` (N)
- `reporting_periods` (1) → `coverage_data` (N)
- `geographic_areas` (self-referential for hierarchy)

---

## Table Schemas

### Dimension Tables

#### 1. `geographic_areas`
**Purpose:** Store all geographic entities (countries, regions, UTLAs)

```sql
CREATE TABLE geographic_areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,           -- ONS code (e.g., 'E92000001' for England)
    name TEXT NOT NULL,                  -- Human-readable name
    type TEXT NOT NULL,                  -- 'country', 'region', 'utla'
    parent_code TEXT,                    -- ONS code of parent area (for hierarchy)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_code) REFERENCES geographic_areas(code),
    CHECK (type IN ('country', 'region', 'utla'))
);

CREATE INDEX idx_geo_code ON geographic_areas(code);
CREATE INDEX idx_geo_type ON geographic_areas(type);
```

**Sample Data:**
```
id | code       | name              | type    | parent_code
---|------------|-------------------|---------|-------------
1  | E92000001  | England           | country | NULL
2  | E12000004  | East Midlands     | region  | E92000001
3  | E10000019  | Lincolnshire      | utla    | E12000004
```

**Requirement:** DB-FR-005 (Logically organized data fields)

---

#### 2. `vaccines`
**Purpose:** Master list of vaccines in the COVER programme

```sql
CREATE TABLE vaccines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,           -- Standardized code (e.g., 'DTaP_IPV_Hib')
    full_name TEXT NOT NULL,             -- Full vaccine name
    short_name TEXT,                     -- Abbreviated name
    target_age_months INTEGER NOT NULL,  -- Typical age for administration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (target_age_months > 0)
);

CREATE INDEX idx_vaccine_code ON vaccines(code);
```

**Sample Data:**
```
id | code           | full_name                                   | short_name | target_age
---|----------------|---------------------------------------------|------------|------------
1  | DTaP_IPV_Hib   | Diphtheria, Tetanus, Pertussis, Polio, Hib | DTaP       | 12
2  | MMR            | Measles, Mumps, Rubella                     | MMR        | 12
3  | PCV            | Pneumococcal Conjugate Vaccine              | PCV        | 12
```

**Requirement:** DB-FR-005 (Clear field separation)

---

#### 3. `age_cohorts`
**Purpose:** Define birth cohorts being measured

```sql
CREATE TABLE age_cohorts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,           -- '12_months', '24_months', '5_years'
    age_in_months INTEGER NOT NULL,      -- 12, 24, 60
    birth_period_start DATE,             -- Start of birth period
    birth_period_end DATE,               -- End of birth period
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (age_in_months IN (12, 24, 60))
);
```

**Sample Data:**
```
id | name       | age_in_months | birth_period_start | birth_period_end
---|------------|---------------|--------------------|------------------
1  | 12_months  | 12            | 2023-04-01         | 2024-03-31
2  | 24_months  | 24            | 2022-04-01         | 2023-03-31
3  | 5_years    | 60            | 2019-04-01         | 2020-03-31
```

---

#### 4. `reporting_periods`
**Purpose:** Track when coverage data was collected

```sql
CREATE TABLE reporting_periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,               -- 2024
    quarter TEXT,                        -- 'Q1', 'Q2', NULL for annual
    period_type TEXT NOT NULL,           -- 'annual', 'quarterly'
    data_collection_date DATE,           -- When data was published
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(year, quarter),
    CHECK (period_type IN ('annual', 'quarterly'))
);
```

**Sample Data:**
```
id | year | quarter | period_type | data_collection_date
---|------|---------|-------------|---------------------
1  | 2024 | NULL    | annual      | 2025-08-28
2  | 2023 | NULL    | annual      | 2024-08-30
```

---

### Fact Table

#### 5. `coverage_data`
**Purpose:** Store all vaccination coverage measurements (supports all 3 dataset types)

```sql
CREATE TABLE coverage_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Keys (dimension references)
    geographic_area_id INTEGER NOT NULL,
    vaccine_id INTEGER NOT NULL,
    age_cohort_id INTEGER NOT NULL,
    reporting_period_id INTEGER NOT NULL,
    
    -- Measurements
    coverage_percentage REAL,            -- 91.3 (can be NULL if suppressed)
    numerator INTEGER,                   -- Number of children vaccinated
    denominator INTEGER,                 -- Total children in cohort
    
    -- Data Quality Flags
    is_suppressed BOOLEAN DEFAULT 0,     -- [z] notation from source
    is_confidential BOOLEAN DEFAULT 0,   -- [c] notation from source
    notes TEXT,                          -- Additional context
    
    -- Metadata
    dataset_type TEXT NOT NULL,          -- 'national', 'local_authority', 'time_series'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (geographic_area_id) REFERENCES geographic_areas(id) ON DELETE CASCADE,
    FOREIGN KEY (vaccine_id) REFERENCES vaccines(id) ON DELETE RESTRICT,
    FOREIGN KEY (age_cohort_id) REFERENCES age_cohorts(id) ON DELETE RESTRICT,
    FOREIGN KEY (reporting_period_id) REFERENCES reporting_periods(id) ON DELETE RESTRICT,
    
    -- Business Constraints
    CHECK (coverage_percentage IS NULL OR (coverage_percentage >= 0 AND coverage_percentage <= 100)),
    CHECK (numerator IS NULL OR numerator >= 0),
    CHECK (denominator IS NULL OR denominator > 0),
    CHECK (dataset_type IN ('national', 'local_authority', 'time_series')),
    
    -- Prevent duplicate entries
    UNIQUE(geographic_area_id, vaccine_id, age_cohort_id, reporting_period_id)
);

-- Performance Indexes
CREATE INDEX idx_coverage_geo ON coverage_data(geographic_area_id);
CREATE INDEX idx_coverage_vaccine ON coverage_data(vaccine_id);
CREATE INDEX idx_coverage_period ON coverage_data(reporting_period_id);
CREATE INDEX idx_coverage_dataset_type ON coverage_data(dataset_type);
```

**Sample Data:**
```
id | geo_id | vax_id | cohort_id | period_id | coverage_% | numerator | denominator | dataset_type
---|--------|--------|-----------|-----------|------------|-----------|-------------|----------------
1  | 1      | 1      | 1         | 1         | 91.3       | 523740    | 573740      | national
2  | 3      | 2      | 1         | 1         | 88.5       | 42000     | 47500       | local_authority
```

**Requirements:** DB-FR-001 (CREATE), DB-FR-002 (READ), DB-FR-003 (UPDATE), DB-FR-004 (DELETE)

---

### Audit Table

#### 6. `data_load_log`
**Purpose:** Track ETL operations for debugging and compliance

```sql
CREATE TABLE data_load_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    sheet_name TEXT,
    rows_loaded INTEGER,
    load_status TEXT NOT NULL,           -- 'success', 'partial', 'failed'
    error_message TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (load_status IN ('success', 'partial', 'failed'))
);
```

**Requirement:** EL-FR-002 (Logging user actions)

---

## Normalization Analysis

### 1st Normal Form (1NF) ✅
- All columns contain atomic values
- No repeating groups
- Each row is uniquely identifiable by primary key

### 2nd Normal Form (2NF) ✅
- Meets 1NF
- No partial dependencies (all non-key attributes depend on entire primary key)
- Dimension tables separate from fact table

### 3rd Normal Form (3NF) ✅
- Meets 2NF
- No transitive dependencies
- `vaccines.full_name` depends only on `vaccines.id`, not on other non-key attributes

**Conclusion:** Schema is fully normalized to 3NF.

---

## Sample Queries

### Query 1: National Summary by Vaccine
```sql
SELECT 
    v.short_name AS vaccine,
    AVG(cd.coverage_percentage) AS avg_coverage,
    MIN(cd.coverage_percentage) AS min_coverage,
    MAX(cd.coverage_percentage) AS max_coverage
FROM coverage_data cd
JOIN vaccines v ON cd.vaccine_id = v.id
JOIN geographic_areas ga ON cd.geographic_area_id = ga.id
WHERE ga.type = 'country'
  AND cd.dataset_type = 'national'
GROUP BY v.id, v.short_name
ORDER BY avg_coverage DESC;
```

### Query 2: Low-Coverage Local Authorities
```sql
SELECT 
    ga.name AS local_authority,
    v.short_name AS vaccine,
    cd.coverage_percentage
FROM coverage_data cd
JOIN geographic_areas ga ON cd.geographic_area_id = ga.id
JOIN vaccines v ON cd.vaccine_id = v.id
WHERE ga.type = 'utla'
  AND cd.coverage_percentage < 90
  AND cd.dataset_type = 'local_authority'
ORDER BY cd.coverage_percentage ASC
LIMIT 10;
```

### Query 3: Year-over-Year Trends
```sql
SELECT 
    rp.year,
    v.short_name AS vaccine,
    AVG(cd.coverage_percentage) AS avg_coverage
FROM coverage_data cd
JOIN vaccines v ON cd.vaccine_id = v.id
JOIN reporting_periods rp ON cd.reporting_period_id = rp.id
WHERE cd.dataset_type = 'time_series'
GROUP BY rp.year, v.id
ORDER BY rp.year, v.short_name;
```

---

## Security Considerations

### SQL Injection Prevention (SEC-FR-002)
- **Use parameterized queries** via SQLAlchemy ORM
- **Never concatenate user input** into SQL strings
- **Input validation** before database queries

### Credential Management (DB-NFR-002)
- Database connection string in `config/settings.ini`
- No hardcoded passwords in source code
- Environment variables for production

---

## Requirements Traceability

| Requirement | Implementation |
|-------------|----------------|
| DB-FR-001 (Persist/CREATE) | `INSERT INTO coverage_data` |
| DB-FR-002 (READ) | `SELECT FROM coverage_data WHERE...` |
| DB-FR-003 (UPDATE) | `UPDATE coverage_data SET... WHERE...` |
| DB-FR-004 (DELETE) | `DELETE FROM coverage_data WHERE...` |
| DB-FR-005 (Structured model) | Normalized 3NF schema with clear field separation |
| DB-NFR-001 (Testable) | Integration tests verify CRUD operations |
| DB-NFR-002 (Config credentials) | Connection string in config file |
| SEC-FR-002 (SQL injection) | SQLAlchemy ORM with parameterized queries |

---

## Implementation Notes

### Technology Stack
- **ORM:** SQLAlchemy (Python)
- **Database:** SQLite (development), PostgreSQL (production-ready)
- **Migrations:** Alembic (optional, for schema versioning)

### File Location
- **Schema definition:** `backend_code/database_src/models.py`
- **Connection management:** `backend_code/database_src/database.py`
- **Database file:** `data/vaccination_coverage.db` (SQLite)

---

**Document Owner:** Amyna (Developer)  
**Last Updated:** 2025-12-08
