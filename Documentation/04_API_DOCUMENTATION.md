# API Documentation

## Overview

This document provides comprehensive documentation for all API endpoints in the UK Childhood Immunisation Coverage Data Insights Tool.

**Base URL:** `http://localhost:5000`

**Content Type:** All endpoints accept and return `application/json` unless otherwise specified.

---

## Table of Contents

1. [Vaccine Management](#vaccine-management)
2. [Coverage Data Management](#coverage-data-management)
3. [Table Queries](#table-queries)
4. [Geographic Areas](#geographic-areas)
5. [Data Export](#data-export)
6. [Activity Logs](#activity-logs)
7. [System Administration](#system-administration)

---

## Vaccine Management

### GET /api/crud/vaccines
Get all vaccines in the database.

**Response:**
```json
[
  {
    "vaccine_code": "MMR1",
    "vaccine_name": "Measles, Mumps and Rubella (1st dose)"
  },
  {
    "vaccine_code": "DTaP/IPV/Hib",
    "vaccine_name": "Diphtheria, Tetanus, Pertussis, Polio, and Haemophilus influenzae type b"
  }
]
```

### POST /api/crud/vaccines
Create a new vaccine.

**Request Body:**
```json
{
  "vaccine_code": "NEW_VAC",
  "vaccine_name": "New Vaccine Name"
}
```

**Validation:**
- `vaccine_code`: Required, max 50 characters
- `vaccine_name`: Required, max 200 characters

**Response (201):**
```json
{
  "vaccine_code": "NEW_VAC",
  "vaccine_name": "New Vaccine Name"
}
```

**Error Responses:**
- `400`: Missing required fields or empty values
- `409`: Vaccine code already exists
- `500`: Internal server error

### PUT /api/crud/vaccines
Update an existing vaccine.

**Request Body:**
```json
{
  "vaccine_code": "MMR1",
  "vaccine_name": "Updated Vaccine Name"
}
```

**Response (200):**
```json
{
  "vaccine_code": "MMR1",
  "vaccine_name": "Updated Vaccine Name"
}
```

**Error Responses:**
- `400`: Invalid input
- `404`: Vaccine not found

### DELETE /api/crud/vaccines
Delete a vaccine.

**Request Body:**
```json
{
  "vaccine_code": "NEW_VAC"
}
```

**Response (200):**
```json
{
  "message": "Vaccine deleted"
}
```

**Error Responses:**
- `404`: Vaccine not found

---

## Coverage Data Management

### POST /api/crud/coverage
Create or update a coverage record.

**Request Body:**
```json
{
  "area_code": "E10000001",
  "vaccine_code": "MMR1",
  "cohort_name": "24 months",
  "year": 2024,
  "eligible_population": 1000,
  "vaccinated_count": 950,
  "coverage_percentage": 95.0
}
```

**Validation:**
- `area_code`: Required
- `vaccine_code`: Required
- `cohort_name`: Optional (default: "24 months")
- `year`: Integer, 2000-2100 range
- `coverage_percentage`: 0-100 range
- `eligible_population`: Non-negative, max 10,000,000
- `vaccinated_count`: Non-negative, must be ≤ eligible_population

**Response (200):**
```json
{
  "message": "Record saved",
  "id": 123
}
```

**Error Responses:**
- `400`: Invalid input (detailed error message provided)
- `404`: Reference data not found (vaccine, cohort, area, or year)

### DELETE /api/crud/coverage
Delete a coverage record.

**Request Body:**
```json
{
  "area_code": "E10000001",
  "vaccine_code": "MMR1",
  "cohort_name": "24 months",
  "year": 2024
}
```

**Response (200):**
```json
{
  "message": "Record deleted"
}
```

**Error Responses:**
- `404`: Record not found

### POST /api/crud/row
Update multiple vaccines for a single area/cohort/year (batch operation).

**Request Body:**
```json
{
  "area_code": "E10000001",
  "cohort_name": "12 months",
  "year": 2024,
  "vaccine_updates": [
    {
      "vaccine_code": "MMR1",
      "eligible_population": 1000,
      "vaccinated_count": 950
    },
    {
      "vaccine_code": "DTaP/IPV/Hib",
      "eligible_population": 1000,
      "vaccinated_count": 980
    }
  ]
}
```

**Response (200):**
```json
{
  "message": "Row updated",
  "updated_count": 2
}
```

### DELETE /api/crud/row
Delete all vaccine records for a specific area/cohort/year.

**Request Body:**
```json
{
  "area_code": "E10000001",
  "cohort_name": "12 months",
  "year": 2024
}
```

**Response (200):**
```json
{
  "message": "Row deleted",
  "deleted_count": 5
}
```

---

## Table Queries

### POST /api/tables/table1
Get Table 1 (UK coverage by country).

**Request Body:**
```json
{
  "cohort_name": "12 months",
  "year": 2024
}
```

**Response (200):**
```json
{
  "title": "Table 1. Completed primary immunisations...",
  "data": [
    {
      "area": "United Kingdom",
      "MMR1": 95.5,
      "DTaP/IPV/Hib": 94.3,
      ...
    }
  ]
}
```

### POST /api/tables/utla
Get UTLA (Upper Tier Local Authority) coverage table.

**Request Body:**
```json
{
  "cohort_name": "24 months",
  "year": 2024,
  "filters": {
    "area_name": "Birmingham",
    "MMR1": ">90"
  }
}
```

**Response (200):**
```json
{
  "title": "Table 4. Completed primary immunisations...",
  "cohort": "24 months",
  "year": 2024,
  "row_count": 15,
  "total_rows": 150,
  "filtered": true,
  "data": [...]
}
```

### POST /api/tables/regional
Get regional time series table.

**Request Body:**
```json
{
  "cohort_name": "24 months"
}
```

**Response (200):**
```json
{
  "cohort": "24 months",
  "row_count": 45,
  "data": [...]
}
```

### POST /api/tables/england-summary
Get England summary statistics.

**Request Body:**
```json
{
  "cohort_name": "24 months",
  "year": 2024
}
```

**Response (200):**
```json
{
  "cohort": "24 months",
  "year": 2024,
  "statistics": {
    "mean_coverage": 93.5,
    "median_coverage": 94.0,
    "std_dev": 2.3
  }
}
```

### POST /api/tables/hepb
Get Hepatitis B special program table.

**Request Body:**
```json
{
  "year": 2024
}
```

### POST /api/tables/bcg
Get BCG special program table.

**Request Body:**
```json
{
  "year": 2024
}
```

---

## Geographic Areas

### GET /api/areas
Get all UTLA (Upper Tier Local Authority) areas.

**Response (200):**
```json
[
  {
    "code": "E10000001",
    "name": "Hartlepool"
  },
  {
    "code": "E10000002",
    "name": "Middlesbrough"
  }
]
```

### GET /api/all-areas
Get all geographic areas (countries, regions, and UTLAs).

**Response (200):**
```json
[
  {
    "code": "K02000001",
    "name": "United Kingdom",
    "type": "country"
  },
  {
    "code": "E12000001",
    "name": "North East",
    "type": "region"
  },
  {
    "code": "E10000001",
    "name": "Hartlepool",
    "type": "utla"
  }
]
```

---

## Data Export

### POST /api/export/csv
Export filtered data to CSV.

**Request Body:**
```json
{
  "vaccine_code": "MMR1",
  "cohort_name": "24 months",
  "area_type": "utla"
}
```

**Response (200):**
```json
{
  "download_url": "/static/exports/MMR1_export.csv",
  "row_count": 150
}
```

**Error Responses:**
- `404`: No data found for the specified filters

---

## Activity Logs

### GET /api/logs/recent
Get recent activity logs.

**Query Parameters:**
- `n`: Number of logs to retrieve (default: 20)

**Example:**
```
GET /api/logs/recent?n=10
```

**Response (200):**
```json
{
  "logs": [
    {
      "timestamp": "2024-12-10 19:00:00",
      "action_type": "create",
      "target": "vaccine",
      "details": "code=NEW_VAC"
    }
  ]
}
```

### GET /api/logs/summary
Get activity log summary statistics.

**Response (200):**
```json
{
  "total_actions": 1234,
  "actions_by_type": {
    "create": 45,
    "update": 123,
    "delete": 12,
    "query": 1054
  },
  "recent_activity": [...]
}
```

---

## System Administration

### POST /api/reload-data
Reload database from CSV files (admin operation).

**Request Body:** None

**Response (200):**
```json
{
  "message": "Database reloaded successfully",
  "status": "success",
  "summary": {
    "vaccines_loaded": 16,
    "areas_loaded": 163,
    "coverage_records_loaded": 2500
  }
}
```

**Error Responses:**
- `500`: Reload failed (error details in response)

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Detailed error message"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `404`: Not Found
- `409`: Conflict (duplicate)
- `500`: Internal Server Error

---

## Security

### Input Validation

All endpoints validate input data:
- Required field checking
- Type validation
- Range checking
- Length limits
- Relationship validation

### SQL Injection Prevention

All database queries use SQLAlchemy ORM with parameterized queries. Direct SQL injection is not possible.

### XSS Prevention

All API responses use JSON format, which is naturally safe from XSS attacks.

---

## Rate Limiting

Currently not implemented. Future versions may include rate limiting for production deployments.

---

## Versioning

**Current Version:** v1.0.0

API versioning will be implemented in future releases using URL prefixes (e.g., `/api/v2/`).
