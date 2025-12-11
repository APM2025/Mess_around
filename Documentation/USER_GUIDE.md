# UK Childhood Immunisation Coverage Data Insights Tool - User Guide

**Version 1.0.0**
**Last Updated: December 2025**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [System Overview](#system-overview)
4. [Installation Guide](#installation-guide)
5. [Using the Web Interface](#using-the-web-interface)
6. [API Reference](#api-reference)
7. [Data Management](#data-management)
8. [Analysis and Visualization](#analysis-and-visualization)
9. [Export Functionality](#export-functionality)
10. [Troubleshooting](#troubleshooting)
11. [FAQ](#faq)

---

## 1. Introduction

### 1.1 What is This Tool?

The UK Childhood Immunisation Coverage Data Insights Tool is a web-based application designed to help public health analysts, researchers, and policymakers analyze and visualize UK childhood immunisation coverage data from the COVER (Coverage of Vaccination Evaluated Rapidly) programme.

### 1.2 Who Should Use This Tool?

- **Public Health Analysts**: Monitor vaccination coverage trends and identify areas of concern
- **Healthcare Researchers**: Conduct studies on immunisation patterns and effectiveness
- **Policymakers**: Make evidence-based decisions about vaccination programmes
- **Healthcare Administrators**: Track performance metrics and compliance
- **Students and Educators**: Learn about public health data analysis

### 1.3 Key Features

- **Interactive Data Exploration**: Filter and analyze data by vaccine, geography, age cohort, and time period
- **Comprehensive Visualization**: Generate charts to visualize trends and comparisons
- **Statistical Analysis**: Calculate summary statistics (mean, median, standard deviation)
- **Data Management**: Create, read, update, and delete coverage records
- **Export Capabilities**: Export filtered data to CSV format
- **Activity Logging**: Track all database operations for audit trails
- **ODS Table Reconstruction**: View data in original NHS Digital table formats

---

## 2. Getting Started

### 2.1 System Requirements

**Minimum Requirements:**
- Operating System: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- Python: Version 3.12 or higher
- RAM: 4GB minimum (8GB recommended)
- Disk Space: 500MB for application and database
- Web Browser: Chrome 90+, Firefox 88+, Safari 14+, or Edge 90+

**Network Requirements:**
- No internet connection required (runs locally)
- Port 5000 must be available for web interface

### 2.2 Quick Start (5 Minutes)

```bash
# 1. Navigate to project directory
cd Mess_around

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py

# 4. Open your web browser and navigate to:
http://localhost:5000
```

That's it! The application is now running and ready to use.

---

## 3. System Overview

### 3.1 Application Architecture

The application follows a clean 4-layer architecture:

```
┌─────────────────────────────────────────────┐
│     Layer 3: Presentation (Web/API)         │
│  - Flask web application                    │
│  - REST API endpoints                       │
│  - Visualization generation                 │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│     Layer 2: Business Logic                 │
│  - CRUD operations                          │
│  - Filtering and analysis                   │
│  - Data export                              │
│  - Activity logging                         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│     Layer 1: Database (SQLAlchemy ORM)      │
│  - 8 database tables                        │
│  - Session management                       │
│  - Referential integrity                    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│     Layer 0: Data Ingestion                 │
│  - CSV/XLSX loading                         │
│  - Data cleaning and validation             │
│  - 5 different CSV structure types          │
└─────────────────────────────────────────────┘
```

### 3.2 Data Coverage

**Geographic Coverage:**
- **National Level**: UK, England, Wales, Scotland, Northern Ireland
- **Regional Level**: 9 NHS England regions
- **Local Level**: 153 Upper Tier Local Authorities (UTLAs)

**Vaccines Tracked (16 types):**
- DTaP/IPV/Hib (5-in-1 vaccine)
- MMR (Measles, Mumps, Rubella)
- PCV (Pneumococcal Conjugate Vaccine)
- Rotavirus
- MenB (Meningococcal B)
- Hib/MenC booster
- DTaP/IPV (4-in-1 pre-school booster)
- HPV (Human Papillomavirus)
- HepB (Hepatitis B) - special programmes
- BCG (TB vaccine) - special programmes

**Age Cohorts:**
- 12 months (1st birthday)
- 24 months (2nd birthday)
- 5 years
- 3 months (for special programmes)

**Time Period:**
- Financial years 2009-10 through 2024-25 (17 years)

---

## 4. Installation Guide

### 4.1 Step-by-Step Installation

#### Step 1: Install Python

**Windows:**
1. Download Python 3.12+ from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. Check "Add Python to PATH" during installation
4. Verify installation: `python --version`

**macOS:**
```bash
brew install python@3.12
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.12 python3-pip
python3 --version
```

#### Step 2: Clone or Download Project

```bash
# If using Git:
git clone <repository-url>
cd Mess_around

# Or extract from ZIP file:
unzip Mess_around.zip
cd Mess_around
```

#### Step 3: Create Virtual Environment (Recommended)

```bash
# Windows:
python -m venv venv
venv\Scripts\activate

# macOS/Linux:
python3 -m venv venv
source venv/bin/activate
```

#### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected dependencies:**
- Flask (web framework)
- SQLAlchemy (database ORM)
- Pandas (data manipulation)
- Matplotlib (visualization)
- Pytest (testing framework)

#### Step 5: Verify Installation

```bash
# Run tests to verify everything is working:
pytest tests/ -v

# Expected output: 324 tests passed
```

#### Step 6: Initialize Database

The database is pre-populated, but you can reload it:

```bash
python main.py
# Then access: http://localhost:5000
# Click "Reload Data" button on the dashboard
```

### 4.2 Configuration Options

Edit `main.py` to customize settings:

```python
# Change web server port (default: 5000)
app.run(debug=True, port=8080)

# Change database location
# Edit src/layer1_database/database.py:
DB_PATH = "data/vaccination_coverage.db"
```

---

## 5. Using the Web Interface

### 5.1 Launching the Application

```bash
# Start the server:
python main.py

# You should see:
# * Running on http://127.0.0.1:5000
# * WARNING: This is a development server. Do not use it in a production deployment.
```

Open your web browser and navigate to: `http://localhost:5000`

### 5.2 Main Dashboard

The dashboard provides access to all major features:

**Key Sections:**
1. **Data Analysis Panel**: Filter and analyze coverage data
2. **Visualization Tools**: Generate charts and graphs
3. **ODS Tables**: View data in original NHS Digital format
4. **Data Management**: CRUD operations on records
5. **Activity Logs**: View recent database operations
6. **Export Tools**: Download filtered data as CSV

### 5.3 Filtering Data

#### Basic Filtering

Use the filter panel to narrow down data:

1. **Select Vaccine**: Choose from dropdown (e.g., "MMR dose 1")
2. **Select Geographic Area**: Choose UK, country, region, or UTLA
3. **Select Age Cohort**: Choose 12 months, 24 months, or 5 years
4. **Select Financial Year**: Choose from 2009-10 to 2024-25
5. Click **"Apply Filter"**

#### Advanced Filtering

Combine multiple filters:

```javascript
// Example: Find MMR coverage in London UTLAs for 2023-24
Vaccine: "MMR dose 1"
Geographic Area: "London" (region)
Age Cohort: "24 months"
Financial Year: "2023-24"
```

**Results Display:**
- Table showing all matching records
- Summary statistics (mean, median, std dev)
- Option to visualize or export

### 5.4 Viewing Summary Statistics

After filtering, the system automatically calculates:

- **Mean**: Average coverage percentage
- **Median**: Middle value (50th percentile)
- **Standard Deviation**: Measure of variation
- **Minimum**: Lowest coverage percentage
- **Maximum**: Highest coverage percentage
- **Count**: Number of records matching filter

**Example Output:**
```
MMR dose 1 coverage at 24 months in London (2023-24):
- Mean: 87.3%
- Median: 88.1%
- Std Dev: 4.2%
- Min: 78.5% (UTLA: Westminster)
- Max: 94.2% (UTLA: Havering)
- Count: 33 UTLAs
```

### 5.5 Generating Visualizations

#### Chart Types Available

1. **Bar Charts**: Compare coverage across geographic areas
2. **Line Charts**: Show trends over time
3. **Histogram**: Distribution of coverage percentages
4. **Comparison Charts**: Side-by-side vaccine comparison

#### Creating a Chart

1. Apply filters to select data
2. Click **"Visualize"** button
3. Choose chart type from dropdown
4. Click **"Generate Chart"**
5. Chart appears in browser and saves to `static/charts/`

**Example: Time Trend Analysis**
```
Steps:
1. Vaccine: "DTaP/IPV/Hib dose 3"
2. Area: "England"
3. Cohort: "12 months"
4. Years: "All" (to show trend)
5. Chart Type: "Line Chart"
6. Result: Line graph showing coverage from 2009-2025
```

### 5.6 ODS Table View

NHS Digital publishes data in specific table formats. The tool can reconstruct these:

**Available ODS Tables:**
1. **Table 1**: Primary immunisations by 12 months
2. **Table 2**: Primary immunisations by 24 months
3. **Table 3**: Pre-school boosters by 5 years
4. **Table 4**: MMR coverage by 24 months and 5 years
5. **Table 5**: England time series (all vaccines)
6. **Table 6**: Regional time series
7. **Table 7**: Hepatitis B (special programmes)
8. **Table 8**: BCG (special programmes)

**How to Access:**
1. Click **"ODS Tables"** in navigation
2. Select table number
3. Select financial year
4. View formatted table matching NHS Digital layout

---

## 6. API Reference

### 6.1 API Overview

The application provides a RESTful API with 19 endpoints for programmatic access.

**Base URL**: `http://localhost:5000/api`

**Content Type**: `application/json`

**Authentication**: None (local application)

### 6.2 Core API Endpoints

#### 6.2.1 Data Reload

**Reload all data from CSV files**

```http
POST /api/reload-data
```

**Response:**
```json
{
  "status": "success",
  "message": "Data reloaded successfully",
  "records_loaded": {
    "geographic_areas": 163,
    "vaccines": 16,
    "age_cohorts": 4,
    "financial_years": 17,
    "national_coverage": 70,
    "local_authority_coverage": 2086
  }
}
```

#### 6.2.2 Get All Geographic Areas

**Retrieve list of all areas**

```http
GET /api/all-areas
```

**Response:**
```json
{
  "areas": [
    {"id": 1, "name": "United Kingdom", "code": "UK", "type": "Country"},
    {"id": 2, "name": "England", "code": "E92000001", "type": "Country"},
    {"id": 10, "name": "London", "code": "E12000007", "type": "Region"},
    {"id": 50, "name": "Birmingham", "code": "E08000025", "type": "UTLA"}
  ]
}
```

#### 6.2.3 Filter Coverage Data

**Get filtered coverage records with statistics**

```http
POST /api/tables/utla
Content-Type: application/json

{
  "vaccine_id": 1,
  "area_id": 10,
  "cohort_id": 2,
  "year_id": 15
}
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "area_name": "Westminster",
      "vaccine_name": "MMR dose 1",
      "coverage_percentage": 78.5,
      "denominator": 2500,
      "numerator": 1963
    }
  ],
  "statistics": {
    "mean": 87.3,
    "median": 88.1,
    "std_dev": 4.2,
    "min": 78.5,
    "max": 94.2,
    "count": 33
  }
}
```

### 6.3 CRUD Operations

#### 6.3.1 Add New Coverage Record

```http
POST /api/crud/coverage
Content-Type: application/json

{
  "table_name": "LocalAuthorityCoverage",
  "area_id": 50,
  "vaccine_id": 1,
  "cohort_id": 2,
  "year_id": 15,
  "denominator": 5000,
  "numerator": 4500
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Record added successfully",
  "record_id": 2087,
  "coverage_percentage": 90.0
}
```

#### 6.3.2 Update Coverage Record

```http
PUT /api/crud/coverage/{record_id}
Content-Type: application/json

{
  "numerator": 4600
}
```

#### 6.3.3 Delete Coverage Record

```http
DELETE /api/crud/coverage/{record_id}
```

### 6.4 Visualization API

**Generate comparison chart**

```http
POST /api/visualize/table-comparison
Content-Type: application/json

{
  "vaccine_ids": [1, 2, 3],
  "area_id": 2,
  "cohort_id": 2,
  "year_id": 15,
  "chart_type": "bar"
}
```

**Response:**
```json
{
  "status": "success",
  "chart_url": "/static/charts/comparison_20251211_143052.png"
}
```

### 6.5 Export API

**Export filtered data to CSV**

```http
POST /api/export/csv
Content-Type: application/json

{
  "table_name": "LocalAuthorityCoverage",
  "filters": {
    "vaccine_id": 1,
    "year_id": 15
  },
  "columns": ["area_name", "vaccine_name", "coverage_percentage"]
}
```

**Response:**
```json
{
  "status": "success",
  "download_url": "/downloads/export_20251211_143052.csv",
  "records_exported": 153
}
```

### 6.6 Activity Logs API

**Get recent activity logs**

```http
GET /api/logs/recent?limit=50
```

**Response:**
```json
{
  "logs": [
    {
      "id": 1234,
      "timestamp": "2025-12-11 14:30:52",
      "operation": "INSERT",
      "table_name": "LocalAuthorityCoverage",
      "record_id": 2087,
      "details": "Added coverage record for Birmingham, MMR dose 1"
    }
  ]
}
```

---

## 7. Data Management

### 7.1 Adding New Records

#### Via Web Interface

1. Navigate to **"Data Management"** section
2. Click **"Add New Record"**
3. Fill in the form:
   - Select geographic area
   - Select vaccine
   - Select age cohort
   - Select financial year
   - Enter denominator (eligible population)
   - Enter numerator (vaccinated children)
4. Click **"Submit"**
5. System validates and calculates coverage percentage
6. Confirmation message appears

#### Via API

```python
import requests
import json

url = "http://localhost:5000/api/crud/coverage"
data = {
    "table_name": "LocalAuthorityCoverage",
    "area_id": 50,      # Birmingham
    "vaccine_id": 1,    # MMR dose 1
    "cohort_id": 2,     # 24 months
    "year_id": 15,      # 2023-24
    "denominator": 5000,
    "numerator": 4500
}

response = requests.post(url, json=data)
print(response.json())
```

### 7.2 Updating Records

#### Via Web Interface

1. Navigate to **"Data Management"**
2. Search for record using filters
3. Click **"Edit"** button on desired record
4. Modify fields (denominator, numerator)
5. Click **"Update"**
6. System recalculates coverage percentage
7. Confirmation message appears

**Validation Rules:**
- Numerator must be ≤ Denominator
- Coverage percentage must be between 0-100%
- Denominator must be > 0
- All foreign key relationships must be valid

### 7.3 Deleting Records

#### Via Web Interface

1. Navigate to **"Data Management"**
2. Search for record
3. Click **"Delete"** button
4. Confirm deletion in popup dialog
5. Record is removed from database
6. Activity logged

**Warning**: Deletions are permanent and cannot be undone. The activity log maintains a record of the deletion.

### 7.4 Bulk Operations

#### Reload All Data

```bash
# Reloads all data from CSV files in data/csv_data/
# This will DELETE all existing data and reload fresh
```

**Via Web Interface:**
1. Click **"Reload Data"** button on dashboard
2. Confirm action
3. System clears database
4. Loads all CSV files
5. Shows summary of records loaded

**Via API:**
```python
response = requests.post("http://localhost:5000/api/reload-data")
```

### 7.5 Data Validation

All data operations are validated:

**Referential Integrity:**
- Area ID must exist in GeographicArea table
- Vaccine ID must exist in Vaccine table
- Cohort ID must exist in AgeCohort table
- Year ID must exist in FinancialYear table

**Business Logic:**
- `numerator ≤ denominator`
- `denominator > 0`
- `coverage_percentage = (numerator / denominator) × 100`
- `0 ≤ coverage_percentage ≤ 100`

**Uniqueness:**
- No duplicate records for same (area, vaccine, cohort, year) combination

### 7.6 Activity Logging

All data modifications are logged:

**Logged Operations:**
- INSERT: New record added
- UPDATE: Record modified
- DELETE: Record removed
- RELOAD: Bulk data reload

**Log Information:**
- Timestamp (UTC)
- Operation type
- Table name
- Record ID
- Before/after values (for updates)
- User identifier (if applicable)

**Viewing Logs:**
1. Click **"Activity Logs"** in navigation
2. Filter by date range, operation type, or table
3. Export logs to CSV for audit purposes

---

## 8. Analysis and Visualization

### 8.1 Statistical Analysis

#### Descriptive Statistics

After filtering data, view comprehensive statistics:

**Measures of Central Tendency:**
- **Mean**: Average coverage across filtered records
- **Median**: Middle value (less affected by outliers)
- **Mode**: Most common coverage percentage (if applicable)

**Measures of Dispersion:**
- **Standard Deviation**: Degree of variation from mean
- **Variance**: Square of standard deviation
- **Range**: Difference between max and min
- **Interquartile Range (IQR)**: Q3 - Q1

**Bounds:**
- **Minimum**: Lowest coverage percentage
- **Maximum**: Highest coverage percentage
- **Count**: Number of records

**Example Analysis:**

```
Vaccine: DTaP/IPV/Hib dose 3
Area: England (all UTLAs)
Cohort: 12 months
Year: 2023-24

Results (153 UTLAs):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mean:           93.8%
Median:         94.2%
Std Dev:        2.3%
Min:            85.1% (Westminster)
Max:            98.5% (Rutland)
Range:          13.4 percentage points

Interpretation:
- High overall coverage (mean ~94%)
- Low variation (std dev ~2%)
- Some areas of concern (Westminster at 85%)
- Several areas exceeding 95% target
```

#### Trend Analysis

Analyze changes over time:

1. Select vaccine and geographic area
2. Select "All Years"
3. View trend line showing coverage changes from 2009-2025
4. Identify:
   - Upward trends (improving coverage)
   - Downward trends (declining coverage)
   - Stable periods
   - Sudden changes (policy impacts)

**Example Trend Query:**

```
Question: Has MMR coverage at 24 months improved in England?

Filter:
- Vaccine: MMR dose 1
- Area: England
- Cohort: 24 months
- Years: All (2009-2025)

Result: Line chart showing coverage trend
- 2009-10: 89.2%
- 2014-15: 92.3% (peak)
- 2019-20: 90.6% (decline)
- 2023-24: 88.7% (continued decline)

Interpretation: Coverage has declined since 2014,
requiring policy intervention
```

#### Geographic Comparison

Compare coverage across different areas:

1. Select vaccine, cohort, and year
2. Select multiple areas (e.g., all regions)
3. Generate bar chart for visual comparison
4. Identify best and worst performers

### 8.2 Visualization Types

#### 8.2.1 Bar Charts

**Use Case**: Compare coverage across multiple geographic areas

**Example**: Compare MMR coverage across all London UTLAs

**Steps:**
1. Filter: MMR dose 1, London (region), 24 months, 2023-24
2. Chart Type: Bar Chart
3. X-axis: UTLA names
4. Y-axis: Coverage percentage
5. Reference line at 95% (WHO target)

**Output**: Bar chart showing all 33 London UTLAs with coverage values

#### 8.2.2 Line Charts

**Use Case**: Show trends over time

**Example**: Track England's DTaP/IPV/Hib coverage over 15 years

**Steps:**
1. Filter: DTaP/IPV/Hib dose 3, England, 12 months, All years
2. Chart Type: Line Chart
3. X-axis: Financial year
4. Y-axis: Coverage percentage
5. Add trend line (optional)

**Output**: Line graph showing temporal trends and patterns

#### 8.2.3 Histogram

**Use Case**: Understand distribution of coverage values

**Example**: Distribution of MMR coverage across all English UTLAs

**Steps:**
1. Filter: MMR dose 1, All English UTLAs, 24 months, 2023-24
2. Chart Type: Histogram
3. X-axis: Coverage percentage bins (e.g., 80-85%, 85-90%, etc.)
4. Y-axis: Number of UTLAs

**Output**: Histogram showing how many UTLAs fall in each coverage range

**Interpretation Example:**
```
Histogram results:
- 80-85%: 12 UTLAs (8%)
- 85-90%: 45 UTLAs (29%)
- 90-95%: 78 UTLAs (51%)
- 95-100%: 18 UTLAs (12%)

Insight: Only 12% of UTLAs meet WHO 95% target
```

#### 8.2.4 Comparison Charts

**Use Case**: Compare multiple vaccines side-by-side

**Example**: Compare uptake of all primary immunisations at 12 months

**Steps:**
1. Select multiple vaccines:
   - DTaP/IPV/Hib dose 3
   - PCV booster
   - Rotavirus dose 2
   - MenB booster
2. Area: England
3. Cohort: 12 months
4. Year: 2023-24
5. Chart Type: Grouped Bar Chart

**Output**: Side-by-side bars showing coverage for each vaccine

### 8.3 Exporting Visualizations

**Save Options:**
- **PNG**: High-resolution image (default, 300 DPI)
- **SVG**: Vector format (scalable, publication-ready)
- **PDF**: Document format

**File Locations:**
- All charts saved to `static/charts/` directory
- Filename format: `{chart_type}_{timestamp}.png`
- Example: `bar_chart_20251211_143052.png`

**Using Charts in Reports:**
1. Generate chart in application
2. Right-click on chart image
3. Select "Save Image As..."
4. Choose location and format
5. Embed in report/presentation

---

## 9. Export Functionality

### 9.1 CSV Export

Export filtered data for external analysis:

**Steps:**
1. Apply filters to select desired data
2. Click **"Export to CSV"** button
3. Choose columns to include:
   - Geographic area name
   - Vaccine name
   - Age cohort
   - Financial year
   - Denominator (eligible population)
   - Numerator (vaccinated children)
   - Coverage percentage
4. Click **"Generate CSV"**
5. File downloads automatically

**CSV Format:**
```csv
Area,Vaccine,Cohort,Year,Denominator,Numerator,Coverage
Westminster,MMR dose 1,24 months,2023-24,2500,1963,78.5
Camden,MMR dose 1,24 months,2023-24,2100,1890,90.0
Islington,MMR dose 1,24 months,2023-24,2300,2024,88.0
```

### 9.2 Full Database Export

Export entire database for backup:

```bash
# Using sqlite3 command-line tool:
sqlite3 data/vaccination_coverage.db .dump > backup.sql

# To restore:
sqlite3 data/vaccination_coverage_new.db < backup.sql
```

### 9.3 Excel Export

While not built-in, you can convert CSV to Excel:

**Option 1: Via Pandas (Python)**
```python
import pandas as pd

# Read CSV
df = pd.read_csv('export_20251211_143052.csv')

# Save as Excel
df.to_excel('vaccination_data.xlsx', index=False)
```

**Option 2: Open CSV in Excel**
1. Open Microsoft Excel
2. File → Open → Select CSV file
3. Follow import wizard
4. Save As → Excel Workbook (.xlsx)

---

## 10. Troubleshooting

### 10.1 Common Issues

#### Issue 1: Application Won't Start

**Symptoms:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
# Install dependencies:
pip install -r requirements.txt

# If using virtual environment, ensure it's activated:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### Issue 2: Port Already in Use

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**

**Windows:**
```bash
# Find process using port 5000:
netstat -ano | findstr :5000

# Kill process (replace PID):
taskkill /PID <PID> /F

# Or change port in main.py:
app.run(debug=True, port=8080)
```

**macOS/Linux:**
```bash
# Find and kill process:
lsof -ti:5000 | xargs kill -9

# Or change port:
app.run(debug=True, port=8080)
```

#### Issue 3: Database Connection Error

**Symptoms:**
```
sqlite3.OperationalError: unable to open database file
```

**Solution:**
```bash
# Check database file exists:
ls data/vaccination_coverage.db

# If missing, reload data:
python main.py
# Click "Reload Data" in web interface

# Check file permissions (macOS/Linux):
chmod 644 data/vaccination_coverage.db
```

#### Issue 4: Chart Generation Fails

**Symptoms:**
```
RuntimeError: Invalid DISPLAY variable
```

**Solution:**
```python
# This happens on headless servers
# Already configured in visualization.py:
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
```

#### Issue 5: Tests Failing

**Symptoms:**
```
pytest: command not found
```

**Solution:**
```bash
# Install pytest:
pip install pytest pytest-cov

# Run tests:
pytest tests/ -v

# If specific test fails, run with more detail:
pytest tests/test_specific.py -vv
```

### 10.2 Performance Issues

#### Slow Query Performance

**Symptoms**: Filtering takes >5 seconds

**Solutions:**
1. **Database Indexing**: Already implemented on foreign keys
2. **Reduce Data**: Filter by year first (reduces dataset)
3. **Clear Cache**: Restart application
4. **Check Disk Space**: Ensure adequate free space

#### Memory Issues

**Symptoms**: Application crashes with large datasets

**Solutions:**
```python
# Increase Python memory limit (if needed):
# Not typically required for this dataset (290KB DB)

# Process data in chunks:
chunk_size = 1000
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    process_chunk(chunk)
```

### 10.3 Data Issues

#### Missing Data

**Problem**: Some records have NULL values

**Check:**
```sql
-- Using sqlite3 command-line:
sqlite3 data/vaccination_coverage.db

-- Check for NULL values:
SELECT COUNT(*) FROM LocalAuthorityCoverage WHERE numerator IS NULL;

-- View problematic records:
SELECT * FROM LocalAuthorityCoverage WHERE numerator IS NULL;
```

**Solution**: Remove or impute missing values before analysis

#### Data Validation Errors

**Problem**: Cannot add record - validation fails

**Common Causes:**
- Numerator > Denominator
- Invalid foreign key (area, vaccine, cohort, or year ID doesn't exist)
- Duplicate record

**Solution:**
```python
# Verify foreign key exists:
# Check valid IDs via API:
GET http://localhost:5000/api/all-areas
GET http://localhost:5000/api/crud/vaccines

# Ensure numerator ≤ denominator
# Check for duplicates before inserting
```

### 10.4 Browser Compatibility

**Supported Browsers:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Not Supported:**
- Internet Explorer (any version)
- Chrome < 90
- Safari < 14

**If charts not displaying:**
1. Clear browser cache
2. Try different browser
3. Check browser console for errors (F12)

### 10.5 Getting Help

If you encounter issues not covered here:

1. **Check Logs:**
   ```bash
   # Application logs:
   cat logs/app.log

   # Database activity logs:
   # Access via web interface: /logs
   ```

2. **Run Tests:**
   ```bash
   pytest tests/ -v
   # Identifies which component is failing
   ```

3. **Check Documentation:**
   - README.md
   - Documentation/*.md files
   - API_DOCUMENTATION.md

4. **Debug Mode:**
   ```python
   # In main.py:
   app.run(debug=True)  # Enables detailed error messages
   ```

---

## 11. FAQ

### 11.1 General Questions

**Q: Is this application free to use?**
A: Yes, this is an academic project and is free for educational and research purposes.

**Q: Does it require internet connection?**
A: No, it runs entirely locally on your computer.

**Q: Can I use this for commercial purposes?**
A: Check the LICENSE file. Typically, academic projects are for educational use only.

**Q: How often is the data updated?**
A: NHS Digital publishes COVER data quarterly. You'll need to update CSV files manually and reload data.

### 11.2 Data Questions

**Q: Where does the data come from?**
A: NHS Digital COVER (Coverage of Vaccination Evaluated Rapidly) programme. Data is published quarterly at [digital.nhs.uk](https://digital.nhs.uk).

**Q: What time period is covered?**
A: Financial years 2009-10 through 2024-25 (17 years).

**Q: Why are some UTLAs missing?**
A: UTLAs boundaries have changed over time. The database includes 153 current UTLAs in England.

**Q: What does "coverage percentage" mean?**
A: (Number vaccinated / Eligible population) × 100. For example, if 4,500 of 5,000 eligible children are vaccinated, coverage is 90%.

**Q: Why is numerator sometimes > denominator?**
A: This shouldn't happen in clean data. If you see this, it indicates a data quality issue. The application prevents adding such records.

**Q: What is the WHO target for vaccine coverage?**
A: Generally 95% for herd immunity, though targets vary by vaccine.

### 11.3 Technical Questions

**Q: What database does it use?**
A: SQLite - a lightweight, file-based database requiring no server setup.

**Q: Can I use PostgreSQL or MySQL instead?**
A: Yes, SQLAlchemy supports multiple databases. Update `database.py` with your connection string.

**Q: How do I add a new vaccine?**
A: Use the API:
```python
POST /api/crud/vaccines
{
  "name": "COVID-19 Vaccine",
  "description": "COVID-19 vaccination"
}
```

**Q: Can I import data from Excel?**
A: Yes, the CSV loader accepts both CSV and XLSX files. Place files in `data/csv_data/` and reload.

**Q: How do I backup the database?**
A:
```bash
# Copy the database file:
cp data/vaccination_coverage.db data/vaccination_coverage_backup.db

# Or export to SQL:
sqlite3 data/vaccination_coverage.db .dump > backup.sql
```

**Q: Can multiple users access simultaneously?**
A: Currently designed for single-user local use. For multi-user, consider deploying with production WSGI server (Gunicorn) and PostgreSQL.

**Q: Is the application secure?**
A: Yes, it includes:
- SQL injection prevention (parameterized queries)
- XSS prevention (JSON API, no unsafe HTML)
- Input validation
- No authentication required (local use only)

For production deployment with sensitive data, add authentication.

### 11.4 Usage Questions

**Q: How do I find areas with low coverage?**
A:
1. Filter by vaccine, cohort, and year
2. View summary statistics - check "minimum" value
3. Generate histogram to see distribution
4. Sort results table by coverage (ascending)

**Q: Can I compare two different years?**
A: Yes:
1. Filter for year 1, export to CSV
2. Filter for year 2, export to CSV
3. Use Excel or Python to compare:
```python
import pandas as pd
df1 = pd.read_csv('year1.csv')
df2 = pd.read_csv('year2.csv')
comparison = df1.merge(df2, on=['Area', 'Vaccine'], suffixes=('_year1', '_year2'))
```

**Q: How do I identify trends?**
A:
1. Select vaccine and area
2. Select "All Years"
3. Generate line chart
4. Look for upward/downward slopes

**Q: Can I calculate my own statistics?**
A: Yes, export to CSV and use Excel, R, or Python for custom analysis.

### 11.5 Troubleshooting Questions

**Q: Why am I getting "No data found"?**
A: Your filter combination may not exist. Try:
- Broaden filters (e.g., select "All areas")
- Check if vaccine is available for that cohort/year
- Verify financial year is within 2009-2025

**Q: Charts are not saving**
A: Check:
- Write permissions on `static/charts/` directory
- Disk space available
- Matplotlib properly installed: `pip install matplotlib`

**Q: Application is slow**
A: Try:
- Filter by specific year (reduces dataset)
- Restart application
- Close other applications
- Check available RAM

**Q: Tests are failing**
A: Common causes:
- Dependencies not installed: `pip install -r requirements.txt`
- Python version < 3.12: `python --version`
- Database file locked: Close other connections

---

## Appendix A: Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+R | Reload data |
| Ctrl+E | Export to CSV |
| Ctrl+F | Open filter panel |
| Ctrl+V | Generate visualization |
| Ctrl+L | View activity logs |
| Ctrl+Q | Quit application (terminal) |
| F5 | Refresh browser page |
| Ctrl+Shift+I | Open browser developer tools |

---

## Appendix B: File Structure Reference

```
Mess_around/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── README.md                    # Project overview
├── CHANGELOG.md                 # Version history
│
├── src/                         # Source code (4 layers)
│   ├── layer0_data_ingestion/   # CSV loading and cleaning
│   ├── layer1_database/         # ORM models
│   ├── layer2_business_logic/   # CRUD and analysis
│   └── layer3_presentation/     # Web interface
│
├── data/
│   ├── csv_data/                # Source CSV files
│   ├── ods_data/                # Original ODS files
│   └── vaccination_coverage.db  # SQLite database
│
├── templates/                   # HTML templates
├── static/
│   ├── charts/                  # Generated visualizations
│   ├── css/                     # Stylesheets
│   └── js/                      # JavaScript
│
├── tests/                       # Test suite (324 tests)
├── logs/                        # Activity logs
└── Documentation/               # User guides and docs
```

---

## Appendix C: Glossary

**Age Cohort**: Group of children born in the same time period (e.g., children reaching their 2nd birthday in a financial year)

**BCG**: Bacillus Calmette-Guérin vaccine for tuberculosis

**COVER**: Coverage of Vaccination Evaluated Rapidly programme (NHS Digital)

**Coverage Percentage**: (Numerator / Denominator) × 100

**CRUD**: Create, Read, Update, Delete operations

**Denominator**: Number of children eligible for vaccination

**DTaP/IPV/Hib**: 5-in-1 vaccine (Diphtheria, Tetanus, Pertussis, Polio, Haemophilus influenzae type b)

**Financial Year**: April 1 to March 31 (e.g., 2023-24 = April 2023 to March 2024)

**Herd Immunity**: Protection of unvaccinated individuals when vaccination coverage is high enough

**HepB**: Hepatitis B vaccine

**HPV**: Human Papillomavirus vaccine

**MenB**: Meningococcal B vaccine

**MenC**: Meningococcal C vaccine

**MMR**: Measles, Mumps, Rubella vaccine

**NHS Digital**: Organization responsible for health data in England

**Numerator**: Number of children vaccinated

**ODS**: OpenDocument Spreadsheet format used by NHS Digital

**ORM**: Object-Relational Mapping (SQLAlchemy)

**PCV**: Pneumococcal Conjugate Vaccine

**RESTful API**: Web service following REST principles

**Rotavirus**: Vaccine preventing rotavirus gastroenteritis

**SQLAlchemy**: Python SQL toolkit and ORM

**UTLA**: Upper Tier Local Authority (e.g., county council, unitary authority)

**WHO**: World Health Organization

---

## Appendix D: Contact and Support

**Project Information:**
- **Institution**: University of Warwick
- **Course**: Programming for AI-MSI
- **Academic Year**: 2024-2025

**Documentation:**
- Full documentation in `Documentation/` directory
- API reference: `Documentation/04_API_DOCUMENTATION.md`
- Architecture guide: `Documentation/03_ARCHITECTURE.md`

**Technical Support:**
- Check README.md first
- Review troubleshooting section (Section 10)
- Run tests: `pytest tests/ -v`
- Check logs: `logs/app.log`

---

## Version History

**Version 1.0.0 (December 2025)**
- Initial release
- Full CRUD functionality
- Statistical analysis and visualization
- 76% test coverage (324 tests)
- Comprehensive documentation
- Security testing (SQL injection, XSS prevention)

---

**End of User Guide**

For technical details, see:
- `Documentation/03_ARCHITECTURE.md` - System architecture
- `Documentation/04_API_DOCUMENTATION.md` - Complete API reference
- `Documentation/05_TESTING_GUIDE.md` - Testing strategy
- `Documentation/06_SECURITY.md` - Security features

For development information, see:
- README.md - Quick start and overview
- CHANGELOG.md - Detailed version history
