# UK Vaccination Coverage Database Documentation

## Overview
This SQLite database contains UK vaccination coverage data for children aged up to 5 years, organized into a normalized relational structure. The database includes:

- **National aggregate data** - UK and country-level vaccination coverage (2024-2025)
- **Local authority data** - Coverage by Upper Tier Local Authority (UTLA) in England (2024-2025)
- **Time series data** - Historical coverage data for England (2009-2025)

---

## Database Schema

### Reference Tables

#### `geographic_areas`
Stores all geographic entities (countries, regions, local authorities)

| Column | Type | Description |
|--------|------|-------------|
| area_code | TEXT (PK) | Unique identifier for the geographic area |
| area_name | TEXT | Name of the area |
| area_type | TEXT | Type: 'country', 'region', or 'utla' |
| parent_region_code | TEXT (FK) | Parent region for UTLAs |
| ods_code | TEXT | Organisation Data Service code |
| notes | TEXT | Additional notes |

#### `vaccines`
Catalog of all vaccines tracked

| Column | Type | Description |
|--------|------|-------------|
| vaccine_id | INTEGER (PK) | Auto-incrementing ID |
| vaccine_code | TEXT (UNIQUE) | Short code for vaccine |
| vaccine_name | TEXT | Full vaccine name |
| vaccine_description | TEXT | Description |

**Vaccines included:**
- DTaP/IPV/Hib/HepB (6-in-1)
- DTaP/IPV/Hib (5-in-1)
- PCV (Pneumococcal) - doses 1, 2, and booster
- Rotavirus
- MenB (Meningococcal B) and booster
- MenC (Meningococcal C)
- MMR (Measles, Mumps, Rubella) - doses 1 and 2
- Hib/MenC booster
- dTaP/IPV booster (pre-school)
- Hepatitis B (neonatal)
- BCG (TB vaccine)

#### `age_cohorts`
Age groups for vaccination tracking

| Column | Type | Description |
|--------|------|-------------|
| cohort_id | INTEGER (PK) | Auto-incrementing ID |
| cohort_name | TEXT (UNIQUE) | Name of cohort |
| age_months | INTEGER | Age in months |
| birth_year_start | INTEGER | Birth year range start |
| birth_year_end | INTEGER | Birth year range end |
| description | TEXT | Description |

**Cohorts:**
- 12 months (born Apr 2023 - Mar 2024)
- 24 months (born Apr 2022 - Mar 2023)
- 5 years (born Apr 2019 - Mar 2020)
- 3 months (for BCG vaccine)

#### `financial_years`
Financial years for data collection

| Column | Type | Description |
|--------|------|-------------|
| year_id | INTEGER (PK) | Auto-incrementing ID |
| year_label | TEXT (UNIQUE) | Label (e.g., "2024-2025") |
| year_start | INTEGER | Start year |
| year_end | INTEGER | End year |
| evaluation_start_date | TEXT | Start date |
| evaluation_end_date | TEXT | End date |

---

### Fact Tables

#### `national_coverage`
Current year national/UK coverage data

| Column | Type | Description |
|--------|------|-------------|
| coverage_id | INTEGER (PK) | Auto-incrementing ID |
| year_id | INTEGER (FK) | Reference to financial_years |
| area_code | TEXT (FK) | Reference to geographic_areas |
| cohort_id | INTEGER (FK) | Reference to age_cohorts |
| vaccine_id | INTEGER (FK) | Reference to vaccines |
| eligible_population | INTEGER | Number of eligible children |
| vaccinated_count | INTEGER | Number vaccinated |
| coverage_percentage | REAL | Coverage percentage |
| notes | TEXT | Additional notes |

**Unique constraint:** (year_id, area_code, cohort_id, vaccine_id)

#### `local_authority_coverage`
Current year local authority (UTLA) coverage data

| Column | Type | Description |
|--------|------|-------------|
| coverage_id | INTEGER (PK) | Auto-incrementing ID |
| year_id | INTEGER (FK) | Reference to financial_years |
| area_code | TEXT (FK) | Reference to geographic_areas |
| cohort_id | INTEGER (FK) | Reference to age_cohorts |
| vaccine_id | INTEGER (FK) | Reference to vaccines |
| eligible_population | INTEGER | Number of eligible children |
| vaccinated_count | INTEGER | Number vaccinated |
| coverage_percentage | REAL | Coverage percentage |
| notes | TEXT | Additional notes |

**Unique constraint:** (year_id, area_code, cohort_id, vaccine_id)

#### `england_time_series`
Historical England coverage data (2009-2025)

| Column | Type | Description |
|--------|------|-------------|
| series_id | INTEGER (PK) | Auto-incrementing ID |
| year_id | INTEGER (FK) | Reference to financial_years |
| cohort_id | INTEGER (FK) | Reference to age_cohorts |
| vaccine_id | INTEGER (FK) | Reference to vaccines |
| eligible_population | INTEGER | Number of eligible children |
| vaccinated_count | INTEGER | Number vaccinated |
| coverage_percentage | REAL | Coverage percentage |
| notes | TEXT | Additional notes |

**Unique constraint:** (year_id, cohort_id, vaccine_id)

#### `regional_time_series`
Regional coverage over time

| Column | Type | Description |
|--------|------|-------------|
| series_id | INTEGER (PK) | Auto-incrementing ID |
| year_id | INTEGER (FK) | Reference to financial_years |
| area_code | TEXT (FK) | Reference to geographic_areas |
| cohort_id | INTEGER (FK) | Reference to age_cohorts |
| vaccine_id | INTEGER (FK) | Reference to vaccines |
| eligible_population | INTEGER | Number of eligible children |
| coverage_percentage | REAL | Coverage percentage |
| notes | TEXT | Additional notes |

**Unique constraint:** (year_id, area_code, cohort_id, vaccine_id)

#### `special_programs`
Special vaccination programs (Hepatitis B, BCG)

| Column | Type | Description |
|--------|------|-------------|
| program_id | INTEGER (PK) | Auto-incrementing ID |
| year_id | INTEGER (FK) | Reference to financial_years |
| area_code | TEXT (FK) | Reference to geographic_areas |
| program_type | TEXT | 'HepB' or 'BCG' |
| cohort_id | INTEGER (FK) | Reference to age_cohorts |
| eligible_population | INTEGER | Number of eligible children |
| vaccinated_count | INTEGER | Number vaccinated |
| coverage_percentage | REAL | Coverage percentage |
| coverage_range | TEXT | Range for suppressed data |
| notes | TEXT | Additional notes |

**Unique constraint:** (year_id, area_code, program_type, cohort_id)

---

## Data Volumes

- **Geographic Areas**: 163 areas (4 countries, 9 regions, 150 local authorities)
- **Vaccines**: 16 different vaccines
- **Age Cohorts**: 4 cohorts
- **Financial Years**: 17 years (2009-2025)
- **National Coverage**: ~70 records
- **Local Authority Coverage**: ~2,086 records
- **England Time Series**: ~205 records
- **Special Programs**: ~623 records

---

## Key Features

### 1. Normalized Structure
- Eliminates data redundancy
- Maintains referential integrity
- Enables efficient querying and updates

### 2. Hierarchical Geography
- Countries → Regions → Local Authorities
- Easy aggregation at any level

### 3. Time Series Support
- Track vaccination trends over 15+ years
- Compare historical performance

### 4. Flexible Querying
- Join tables to get detailed insights
- Aggregate data at any geographic or temporal level
- Compare across vaccines, cohorts, and areas

---

## Usage Tips

- Always join with reference tables to get human-readable names
- Use appropriate indexes for common query patterns
- Filter by `year_id` for specific time periods
- Use `area_type` to distinguish between countries, regions, and UTLAs
- Check `notes` fields for data quality issues or special circumstances

---

## Data Quality Notes

- Some values may be suppressed due to small numbers (marked as [c])
- Some values may be listed as ranges (e.g., "35% to 69%")
- Historical data may have quality issues noted in the original source
- London UTLAs in 2024-2025 may have underestimated coverage due to system changes

---

## Implementation Status

✅ Database schema defined (SQLAlchemy ORM models)  
🔄 Data loaders (in progress)  
⏳ API endpoints (planned)  
⏳ Visualization layer (planned)
