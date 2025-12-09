# Dataset Structure and Scope

**Document Version:** 1.0  
**Date:** 2025-12-08  
**Status:** Approved

---

## Overview

This document describes the structure of the COVER (Coverage of Vaccination Evaluated Rapidly) programme dataset and defines the scope for the Data Insights Dashboard project.

---

## Data Source

**Dataset:** COVER Annual Data Tables 2024-2025  
**Format:** ODS (OpenDocument Spreadsheet)  
**Provider:** UK Health Security Agency (UKHSA)  
**File:** `cover_anual_data_tables_2024_to_2025.ods`  
**Total Sheets:** 22 sheets

---

## Dataset Structure: 3 Primary Dataset Types

The COVER dataset is organized into **3 distinct dataset types**, each serving different analytical purposes:

### 1. National Aggregates Dataset (Snapshot Data)

**Purpose:** High-level national comparisons across UK countries

**Sheets:**
- `T1_UK12m` - 12-month cohort (children aged 12 months)
- `T2_UK24m` - 24-month cohort (children aged 24 months)
- `T3_UK5y` - 5-year cohort (children aged 5 years)

**Structure:**
- **Rows:** 4 UK countries (England, Scotland, Wales, Northern Ireland)
- **Columns:** Multiple vaccines per age cohort
- **Granularity:** Country-level aggregates
- **Time Period:** Single reporting year (2024-2025)

**Sample Data (T1_UK12m):**
```
Country           | DTaP/IPV/Hib | PCV   | Rotavirus | MenB
------------------|--------------|-------|-----------|------
England           | 91.3%        | 93.1% | 88.8%     | 91.0%
Northern Ireland  | 91.0%        | 93.7% | 88.0%     | 91.0%
Scotland          | 94.5%        | 95.4% | 92.2%     | 94.0%
Wales             | 94.1%        | 95.7% | 92.0%     | 93.8%
```

**Use Cases:**
- Compare vaccination coverage between UK countries
- Identify national performance benchmarks
- High-level policy decision support

---

### 2. Local Authority Geographic Dataset (Snapshot Data)

**Purpose:** Detailed regional analysis and identification of low-coverage areas

**Sheets:**
- `T4a_UTLA12m`, `T4b_UTLA12m` - 12-month cohort by Upper Tier Local Authority
- `T5a_UTLA24m`, `T5b_UTLA24m` - 24-month cohort by UTLA
- `T6a_UTLA5y`, `T6b_UTLA5y` - 5-year cohort by UTLA
- `T7_UTLAHepB`, `T8_UTLABCG` - Specific vaccines by UTLA

**Structure:**
- **Rows:** ~150 Upper Tier Local Authorities (UTLAs)
- **Columns:** Multiple vaccines per age cohort
- **Granularity:** Local authority level (cities, counties)
- **Time Period:** Single reporting year (2024-2025)

**Sample Data (T4a_UTLA12m - first 5 rows):**
```
UTLA Name         | ONS Code  | DTaP/IPV/Hib | MMR   | Coverage Status
------------------|-----------|--------------|-------|----------------
Birmingham        | E08000025 | 89.2%        | 87.5% | Below target
Manchester        | E08000003 | 90.1%        | 88.9% | Below target
Leeds             | E08000035 | 92.3%        | 91.2% | On target
...
```

**Use Cases:**
- Compare coverage across geographic regions
- Identify underperforming local authorities for targeted interventions
- Analyze geographic patterns (urban vs rural, regional variations)
- Support local public health planning

---

### 3. Time Series / Trends Dataset (Historical Data)

**Purpose:** Analyze coverage trends over multiple years

**Sheets:**
- `T9_Eng12m` - England 12-month trends over time
- `T10_Eng24m` - England 24-month trends over time
- `T11_Eng5y` - England 5-year trends over time
- `T14_RegDTaP24m` - DTaP coverage by region over time
- `T15_RegMMR24m` - MMR coverage by region over time
- Additional trend sheets

**Structure:**
- **Rows:** Geographic areas (England-level or regional)
- **Columns:** Years (multiple years of historical data)
- **Granularity:** National or regional level
- **Time Period:** Multi-year historical data

**Sample Data (T9_Eng12m - conceptual):**
```
Vaccine       | 2020  | 2021  | 2022  | 2023  | 2024  | Trend
--------------|-------|-------|-------|-------|-------|-------
DTaP/IPV/Hib  | 92.1% | 91.8% | 91.5% | 91.3% | 91.3% | ↓ Declining
MMR           | 93.5% | 93.2% | 93.0% | 93.1% | 93.1% | → Stable
PCV           | 93.0% | 92.8% | 92.5% | 92.3% | 92.0% | ↓ Declining
```

**Use Cases:**
- Identify long-term trends (improving or declining coverage)
- Evaluate impact of policy interventions
- Forecast future coverage rates
- Compare year-over-year performance

---

## Project Scope: All 3 Datasets

**Decision:** The MVP will support **all 3 dataset types** to provide comprehensive analytical capabilities.

### Rationale:
1. **Demonstrates full feature set** - Showcases filtering, summarization, and trend analysis
2. **Real-world value** - Public health analysts need all 3 perspectives
3. **Academic rigor** - Shows understanding of complex data modeling
4. **Scalable architecture** - Proves system can handle diverse data sources

### Implementation Priority:
1. **Phase 1:** Local Authority Dataset (T4a/T4b) - Most complex, proves architecture
2. **Phase 2:** National Aggregates (T1-T3) - Add high-level summaries
3. **Phase 3:** Time Series (T9-T15) - Enable trend analysis

---

## Data Characteristics

### Common Fields Across All Datasets:
- **Geographic identifiers:** Name, ONS code, type (country/region/UTLA)
- **Vaccine codes:** Standardized abbreviations (DTaP/IPV/Hib, MMR, PCV, etc.)
- **Coverage metrics:** Percentage, numerator (vaccinated), denominator (cohort size)
- **Age cohorts:** 12 months, 24 months, 5 years
- **Data quality flags:** `[c]` confidential, `[z]` suppressed/not applicable

### Data Cleaning Challenges:
- **Metadata rows:** First 5-6 rows contain titles/notes (need to skip)
- **Inconsistent column headers:** Vary by sheet
- **Mixed data types:** Percentages, counts, text flags
- **Geographic hierarchies:** UTLAs nest within regions within countries

---

## Requirements Mapping

| Dataset Type | Requirements Satisfied |
|--------------|----------------------|
| **All 3** | DA-FR-001 (Load from multiple sources) |
| **Local Authority** | FS-FR-001, FS-FR-002 (Geographic filtering) |
| **National + Local** | FS-FR-004 (Summary statistics by groups) |
| **Time Series** | FS-FR-005 (Trends over time) |

---

## Next Steps

1. Design relational database schema to accommodate all 3 dataset types
2. Implement data loaders for each dataset type
3. Build unified data cleaning pipeline
4. Create analysis functions for cross-dataset queries

---

**Document Owner:** Amyna (Developer)  
**Last Updated:** 2025-12-08
