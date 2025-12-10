# API Documentation

REST API endpoints for the UK Vaccination Coverage Dashboard.

## Base URL

```
http://localhost:5000
```

## Endpoints

### Reference Data

#### GET `/api/vaccines`
Get list of all vaccines in the database.

**Response:**
```json
[
  {
    "vaccine_id": 1,
    "vaccine_code": "MMR1",
    "vaccine_name": "MMR (First Dose)",
    "vaccine_description": "Measles, Mumps, Rubella"
  }
]
```

#### GET `/api/cohorts`
Get list of all age cohorts.

**Response:**
```json
[
  {
    "cohort_id": 1,
    "cohort_name": "12 months",
    "age_months": 12
  }
]
```

---

### Data Analysis

#### POST `/api/filter`
Filter vaccination coverage data.

**Request Body:**
```json
{
  "vaccine_code": "MMR1",
  "area_type": "utla",
  "cohort_name": "24 months"
}
```

**Response:**
```json
[
  {
    "area_name": "Lincolnshire",
    "coverage": 93.5,
    "vaccine_code": "MMR1",
    "vaccine_name": "MMR1"
  }
]
```

#### POST `/api/summary`
Get summary statistics.

**Request Body:**
```json
{
  "vaccine_code": "MMR1",
  "cohort_name": "24 months"
}
```

**Response:**
```json
{
  "count": 150,
  "mean": 92.5,
  "min": 85.0,
  "max": 98.0
}
```

#### POST `/api/top-areas`
Get top performing areas.

**Request Body:**
```json
{
  "vaccine_code": "MMR1",
  "n": 10,
  "cohort_name": "24 months"
}
```

**Response:**
```json
[
  {
    "area_name": "Rutland",
    "coverage": 98.5,
    "vaccine_code": "MMR1"
  }
]
```

#### POST `/api/trend`
Get coverage trend over time.

**Request Body:**
```json
{
  "vaccine_code": "MMR1",
  "cohort_name": "24 months"
}
```

**Response:**
```json
[
  {
    "year": "2020-2021",
    "coverage": 90.5
  },
  {
    "year": "2021-2022",
    "coverage": 91.2
  }
]
```

---

### Visualizations

#### POST `/api/visualize/top-areas`
Generate top areas bar chart.

**Request Body:**
```json
{
  "vaccine_code": "MMR1",
  "n": 10,
  "cohort_name": "24 months"
}
```

**Response:**
```json
{
  "chart_url": "/static/charts/top_areas_MMR1.png",
  "timestamp": "2024-12-10T10:30:00"
}
```

#### POST `/api/visualize/trend`
Generate trend line chart.

**Request Body:**
```json
{
  "vaccine_code": "MMR1",
  "cohort_name": "24 months"
}
```

**Response:**
```json
{
  "chart_url": "/static/charts/trend_MMR1.png"
}
```

#### POST `/api/visualize/summary`
Generate summary statistics chart.

**Request Body:**
```json
{
  "vaccine_code": "MMR1",
  "cohort_name": "24 months"
}
```

#### POST `/api/visualize/distribution`
Generate coverage distribution histogram.

**Request Body:**
```json
{
  "vaccine_code": "MMR1",
  "cohort_name": "24 months"
}
```

---

### Data Export

#### POST `/api/export/csv`
Export filtered data to CSV.

**Request Body:**
```json
{
  "vaccine_code": "MMR1",
  "cohort_name": "24 months",
  "filename": "mmr1_coverage.csv"
}
```

**Response:**
```json
{
  "file_url": "/static/exports/mmr1_coverage.csv",
  "record_count": 150
}
```

---

### Activity Logging

#### GET `/api/logs/recent`
Get recent activity logs.

**Query Parameters:**
- `limit` (optional): Number of records (default: 50)

**Response:**
```json
[
  {
    "timestamp": "2024-12-10T10:30:15",
    "action": "filter_data",
    "details": "vaccine=MMR1, cohort=24 months"
  }
]
```

---

### CRUD Operations

#### POST `/api/crud/vaccines`
Create a new vaccine.

**Request Body:**
```json
{
  "vaccine_code": "NEW1",
  "vaccine_name": "New Vaccine",
  "vaccine_description": "Description"
}
```

#### PUT `/api/crud/vaccines/{vaccine_id}`
Update a vaccine.

#### DELETE `/api/crud/vaccines/{vaccine_id}`
Delete a vaccine.

#### GET `/api/crud/coverage/{area_code}`
Get coverage data for a specific area.

---

### Table Reconstruction

#### POST `/api/tables/uk-by-country`
Get UK coverage table by country.

**Request Body:**
```json
{
  "cohort_name": "12 months",
  "year": 2024
}
```

**Response:**
```json
{
  "title": "Table 1. Completed primary immunisations...",
  "data": [...]
}
```

#### POST `/api/tables/utla`
Get UTLA coverage table.

**Query Parameters:**
- `cohort` (required): "12 months", "24 months", or "5 years"
- `year` (optional): Financial year start (default: 2024)
- `filters` (optional): JSON filter criteria

**Response:**
```json
[
  {
    "code": "E10000019",
    "local_authority": "Lincolnshire",
    "coverage_at_24_months_MMR1": 93.5
  }
]
```

---

## Error Responses

All endpoints return standard error responses:

### 400 Bad Request
```json
{
  "error": "Missing required parameter: vaccine_code"
}
```

### 404 Not Found
```json
{
  "error": "Vaccine not found: INVALID"
}
```

### 500 Internal Server Error
```json
{
  "error": "Database connection failed"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production use, consider adding rate limiting middleware.

## Authentication

Currently no authentication is required. For production use, implement authentication for:
- CRUD operations (POST/PUT/DELETE)
- Data export
- Activity logs

## CORS

CORS is enabled for all origins in development mode. Restrict in production:

```python
from flask_cors import CORS
CORS(app, origins=["https://yourdomain.com"])
```
