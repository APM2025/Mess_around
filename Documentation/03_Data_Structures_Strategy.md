# Data Structures Strategy

**Document Version:** 1.0  
**Date:** 2025-12-08  
**Status:** Approved

---

## Overview

This document defines the strategy for using **Python data structures** (dictionaries, lists, sets) in conjunction with the **relational database** throughout the data pipeline.

---

## Key Principle: Hybrid Approach

**Use the right tool for the right job:**

```
In-Memory Data Structures    ←→    Persistent Relational Database
(Dictionaries, Lists)                (SQLite/PostgreSQL)
        ↓                                    ↓
   Processing & Logic               Long-term Storage & Queries
```

---

## Data Flow Architecture

### Complete Pipeline

```
[1. EXTRACT]
ODS File (sheets)
    ↓ pd.read_excel()
pandas DataFrame
    ↓ .to_dict('records')
List of Dictionaries (in-memory)

[2. TRANSFORM - Data Cleaning]
Raw Dictionaries
    ↓ Cleaning functions
    ↓ Validation
    ↓ Normalization
Cleaned Dictionaries

[3. LOAD - Database Persistence]
Cleaned Dictionaries
    ↓ ORM mapping
    ↓ session.add()
SQLite Database Tables

[4. QUERY - Analysis]
SQL Queries
    ↓ ORM objects
Dictionaries (for API/UI)
    ↓ JSON serialization
Flask Response
```

---

## When to Use Each Approach

### Use Python Data Structures (Dictionaries/Lists) For:

#### 1. **ETL Processing (Extract-Transform-Load)**
```python
# EXTRACT: Load from ODS → dictionaries
def load_ods_sheet(filepath, sheet_name):
    df = pd.read_excel(filepath, sheet_name=sheet_name, engine='odf', skiprows=5)
    # Convert DataFrame to list of dictionaries for processing
    records = df.to_dict('records')
    return records
    # Returns: [{"area": "England", "vaccine": "MMR", "coverage": 91.3}, ...]
```

**Why dictionaries here?**
- ✅ Easy to iterate and transform
- ✅ Flexible structure during cleaning
- ✅ Works well with pandas

---

#### 2. **Data Cleaning & Validation**
```python
def clean_vaccine_record(raw_record):
    """
    Transform raw dictionary into cleaned structure
    """
    # Use lookups dictionaries for fast validation
    vaccine_mapping = {
        "DTaP/IPV/Hib": "DTaP_IPV_Hib",
        "DTaP-IPV-Hib": "DTaP_IPV_Hib",  # Handle variations
        "MMR": "MMR"
    }
    
    cleaned = {
        "geographic_code": extract_ons_code(raw_record["area"]),
        "vaccine_code": vaccine_mapping.get(raw_record["vaccine"]),
        "coverage": float(raw_record["coverage"]) if raw_record["coverage"] else None,
        "is_suppressed": "[z]" in str(raw_record.get("notes", ""))
    }
    
    return cleaned
```

**Why dictionaries here?**
- ✅ Flexible schema during transformation
- ✅ Easy to add/remove fields
- ✅ Fast key-based lookups

**Requirement:** DC-FR-003 (Create data structures)

---

#### 3. **Reference Data Lookups (In-Memory Cache)**
```python
# Build lookup dictionaries on application startup
VACCINE_LOOKUP = {
    "DTaP_IPV_Hib": {
        "id": 1,
        "full_name": "Diphtheria, Tetanus, Pertussis, Polio, Haemophilus influenzae type b",
        "age": 12
    },
    "MMR": {
        "id": 2,
        "full_name": "Measles, Mumps, Rubella",
        "age": 12
    }
}

def get_vaccine_id(vaccine_code):
    """Fast O(1) lookup instead of database query"""
    return VACCINE_LOOKUP.get(vaccine_code, {}).get("id")
```

**Why dictionaries here?**
- ✅ O(1) lookup time (faster than database query)
- ✅ Reduces database load
- ✅ Reference data doesn't change often

---

#### 4. **API Responses (JSON Serialization)**
```python
@app.route('/api/coverage/region/<region_code>')
def get_region_coverage(region_code):
    # Query database → convert to dictionary for JSON
    results = query_coverage_by_region(region_code)
    
    response_data = {
        "region": region_code,
        "vaccines": [
            {
                "name": r.vaccine.short_name,
                "coverage": r.coverage_percentage,
                "cohort_size": r.denominator
            }
            for r in results
        ]
    }
    
    return jsonify(response_data)
```

**Why dictionaries here?**
- ✅ Flask requires JSON (dict → JSON conversion)
- ✅ Easy to structure API responses

**Requirement:** PR-FR-001 (User interface for data display)

---

### Use Relational Database For:

#### 1. **Persistent Storage**
```python
def save_coverage_records(cleaned_records):
    """
    Save cleaned dictionaries to database
    """
    for record in cleaned_records:
        # Create ORM object from dictionary
        coverage = CoverageData(
            geographic_area_id=record["geo_id"],
            vaccine_id=record["vaccine_id"],
            coverage_percentage=record["coverage"]
        )
        session.add(coverage)
    
    session.commit()  # Persist to disk
```

**Why database here?**
- ✅ Survives program restart
- ✅ ACID transactions (atomicity, consistency)
- ✅ Enforces data integrity (foreign keys)

**Requirements:** DB-FR-001 (CREATE), DB-FR-002 (READ)

---

#### 2. **Complex Queries & Filtering**
```python
def get_low_coverage_areas(vaccine_code, threshold=90):
    """
    Find UTLAs with coverage below threshold
    
    SQL equivalent:
    SELECT ga.name, cd.coverage_percentage
    FROM coverage_data cd
    JOIN geographic_areas ga ON cd.geographic_area_id = ga.id
    WHERE cd.vaccine_id = ... AND cd.coverage_percentage < 90
    """
    results = session.query(CoverageData)\
        .join(GeographicArea)\
        .join(Vaccine)\
        .filter(Vaccine.code == vaccine_code)\
        .filter(CoverageData.coverage_percentage < threshold)\
        .filter(GeographicArea.type == 'utla')\
        .all()
    
    return results
```

**Why database here?**
- ✅ Optimized JOIN operations
- ✅ Indexed lookups (fast filtering)
- ✅ Declarative syntax (easier to reason about)

**Requirement:** FS-FR-001 to FS-FR-004 (Filtering and summaries)

---

#### 3. **Aggregations & Statistics**
```python
def get_national_summary():
    """
    Calculate mean, min, max coverage by vaccine
    """
    from sqlalchemy import func
    
    summary = session.query(
        Vaccine.short_name,
        func.avg(CoverageData.coverage_percentage).label('mean_coverage'),
        func.min(CoverageData.coverage_percentage).label('min_coverage'),
        func.max(CoverageData.coverage_percentage).label('max_coverage'),
        func.count(CoverageData.id).label('record_count')
    )\
    .join(Vaccine)\
    .group_by(Vaccine.id)\
    .all()
    
    return summary
```

**Why database here?**
- ✅ Efficient aggregation functions (AVG, MIN, MAX, COUNT)
- ✅ Database engine optimizes calculations
- ✅ Handles large datasets efficiently

**Requirement:** FS-FR-004 (Summary statistics)

---

#### 4. **CRUD Operations (Create, Read, Update, Delete)**
```python
# UPDATE example
def update_coverage_percentage(record_id, new_percentage):
    record = session.query(CoverageData).filter_by(id=record_id).first()
    record.coverage_percentage = new_percentage
    session.commit()

# DELETE example
def delete_coverage_record(record_id):
    session.query(CoverageData).filter_by(id=record_id).delete()
    session.commit()
```

**Why database here?**
- ✅ Transactional integrity (rollback on error)
- ✅ Concurrency control (multiple users)
- ✅ Audit trail (created_at timestamps)

**Requirements:** DB-FR-003 (UPDATE), DB-FR-004 (DELETE)

---

## Comparison Table

| Feature | Python Dicts/Lists | Relational Database |
|---------|-------------------|---------------------|
| **Persistence** | ❌ Lost on exit | ✅ Survives restart |
| **Complex queries** | ❌ Manual loops | ✅ SQL/ORM queries |
| **Relationships** | ❌ Manual implementation | ✅ Foreign keys enforced |
| **Data validation** | ⚠️ Manual checks | ✅ Constraints enforced |
| **Concurrency** | ❌ Race conditions | ✅ Transactions & locks |
| **Performance (large data)** | ❌ O(n) scans | ✅ O(log n) with indexes |
| **Flexibility** | ✅ Dynamic schema | ⚠️ Schema changes costly |
| **Processing speed** | ✅ Fast for transforms | ⚠️ Slower for iterative ops |
| **Serialization** | ✅ Easy JSON export | ⚠️ Requires conversion |

---

## Example: End-to-End Data Flow

### Step 1: Load & Parse (Dictionaries)
```python
# Extract from ODS
raw_records = load_ods_sheet("data/file.ods", "T4a_UTLA12m")
# Returns: [{"UTLA": "Birmingham", "MMR": "87.5%"}, ...]
```

### Step 2: Clean & Transform (Dictionaries)
```python
# Clean each record
cleaned_records = []
for raw in raw_records:
    cleaned = {
        "geo_code": extract_ons_code(raw["UTLA"]),
        "vaccine_code": "MMR",
        "coverage": parse_percentage(raw["MMR"])
    }
    cleaned_records.append(cleaned)
```

### Step 3: Enrich with IDs (Dictionary + Database Lookup)
```python
# Look up dimension IDs
enriched_records = []
for record in cleaned_records:
    enriched = {
        **record,
        "geo_id": get_geographic_id(record["geo_code"]),  # DB lookup
        "vaccine_id": VACCINE_LOOKUP[record["vaccine_code"]]["id"]  # Dict lookup
    }
    enriched_records.append(enriched)
```

### Step 4: Persist (Database)
```python
# Save to database
for record in enriched_records:
    coverage = CoverageData(
        geographic_area_id=record["geo_id"],
        vaccine_id=record["vaccine_id"],
        coverage_percentage=record["coverage"]
    )
    session.add(coverage)

session.commit()
```

### Step 5: Query & Analyze (Database → Dictionaries)
```python
# Complex query using database
low_coverage = session.query(CoverageData)\
    .filter(CoverageData.coverage_percentage < 90)\
    .all()

# Convert to dictionaries for API response
api_response = {
    "low_coverage_areas": [
        {
            "area": record.geographic_area.name,
            "coverage": record.coverage_percentage
        }
        for record in low_coverage
    ]
}

return jsonify(api_response)
```

---

## Design Patterns Used

### 1. **Data Transfer Object (DTO) Pattern**
Use dictionaries as DTOs to transfer data between layers:
```python
# Layer boundary: Cleaning → Persistence
def save_cleaned_data(cleaned_dtos: List[Dict]) -> None:
    for dto in cleaned_dtos:
        entity = map_dto_to_entity(dto)
        session.add(entity)
```

### 2. **Repository Pattern**
Database queries wrapped in repository methods that return dictionaries:
```python
class CoverageRepository:
    def find_by_region(self, region_code: str) -> List[Dict]:
        records = session.query(CoverageData)...
        return [record.to_dict() for record in records]
```

### 3. **Cache-Aside Pattern**
Use dictionaries to cache frequently-accessed reference data:
```python
_vaccine_cache = None

def get_all_vaccines() -> Dict:
    global _vaccine_cache
    if _vaccine_cache is None:
        _vaccine_cache = {v.code: v for v in session.query(Vaccine).all()}
    return _vaccine_cache
```

---

## Requirements Mapping

| Requirement | Implementation |
|-------------|----------------|
| **DC-FR-003** (Create data structures) | Dictionaries/lists for cleaning pipeline |
| **DB-FR-001** (Persist data) | Save dictionaries to database via ORM |
| **DB-FR-002** (Read data) | Query database, convert to dicts for API |
| **FS-FR-001** (Filtering) | Database queries with WHERE clauses |
| **FS-FR-004** (Summaries) | Database aggregation functions |

---

## Best Practices

### 1. **Typed Dictionaries (Python 3.8+)**
```python
from typing import TypedDict

class VaccineCoverageDTO(TypedDict):
    geographic_code: str
    vaccine_code: str
    coverage_percentage: float
    is_suppressed: bool

# Provides type hints and IDE autocomplete
def process_record(record: VaccineCoverageDTO) -> None:
    print(record["coverage_percentage"])  # Type-safe
```

### 2. **Validation with Pydantic (Optional)**
```python
from pydantic import BaseModel, validator

class CoverageRecord(BaseModel):
    coverage_percentage: float
    
    @validator('coverage_percentage')
    def validate_percentage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Coverage must be between 0 and 100')
        return v
```

### 3. **Avoid Over-Fetching**
Don't load entire database into dictionaries:
```python
# ❌ BAD: Load all records into memory
all_records = [r.to_dict() for r in session.query(CoverageData).all()]

# ✅ GOOD: Query only what you need
recent_records = session.query(CoverageData)\
    .filter(CoverageData.reporting_period_id == current_period)\
    .limit(100)\
    .all()
```

---

## Summary

- **Dictionaries** = Temporary processing, flexibility, speed
- **Database** = Persistence, relationships, complex queries
- **Use both strategically** for optimal performance and maintainability

---

**Document Owner:** Amyna (Developer)  
**Last Updated:** 2025-12-08
