# UML Diagrams

## Overview

This document contains comprehensive UML diagrams for the UK Childhood Immunisation Coverage Data Insights Tool, including Entity-Relationship diagrams, class diagrams, sequence diagrams, and component diagrams.

---

## Table of Contents

1. [Entity-Relationship (ER) Diagram](#entity-relationship-er-diagram)
2. [Class Diagrams](#class-diagrams)
3. [Sequence Diagrams](#sequence-diagrams)
4. [Component Diagram](#component-diagram)
5. [Deployment Diagram](#deployment-diagram)
6. [Activity Diagrams](#activity-diagrams)
7. [State Diagrams](#state-diagrams)

---

## Entity-Relationship (ER) Diagram

### Database Schema Overview

```
┌─────────────────────────┐
│   GeographicArea        │
├─────────────────────────┤
│ PK area_code (VARCHAR)  │
│    area_name (VARCHAR)  │
│    area_type (VARCHAR)  │
└─────────────────────────┘
           │ 1
           │
           │ *
┌─────────────────────────────────────┐
│   NationalCoverage                  │
├─────────────────────────────────────┤
│ PK coverage_id (INTEGER)            │
│ FK area_code → GeographicArea       │
│ FK vaccine_code → Vaccine           │
│ FK cohort_name → AgeCohort          │
│ FK year → FinancialYear             │
│    eligible_population (INTEGER)    │
│    vaccinated_count (INTEGER)       │
│    coverage_percentage (FLOAT)      │
└─────────────────────────────────────┘
           │ *               │ *
           │                 │
        1 │                 │ 1
┌─────────────────────────┐ ┌─────────────────────────┐
│   Vaccine               │ │   AgeCohort             │
├─────────────────────────┤ ├─────────────────────────┤
│ PK vaccine_code         │ │ PK cohort_name          │
│    vaccine_name         │ │    age_in_months        │
└─────────────────────────┘ └─────────────────────────┘

           │ *
           │
        1 │
┌─────────────────────────┐
│   FinancialYear         │
├─────────────────────────┤
│ PK year (INTEGER)       │
│    year_label (VARCHAR) │
└─────────────────────────┘
```

### Detailed ER Diagram with All Tables

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Reference Tables                           │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐
│  GeographicArea      │    │  Vaccine             │    │  AgeCohort           │
├──────────────────────┤    ├──────────────────────┤    ├──────────────────────┤
│ PK area_code         │    │ PK vaccine_code      │    │ PK cohort_name       │
│    area_name         │    │    vaccine_name      │    │    age_in_months     │
│    area_type         │    └──────────────────────┘    └──────────────────────┘
└──────────────────────┘

┌──────────────────────┐
│  FinancialYear       │
├──────────────────────┤
│ PK year              │
│    year_label        │
└──────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          Fact Tables                                │
└─────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────┐
│  NationalCoverage                 │
├───────────────────────────────────┤
│ PK coverage_id                    │
│ FK area_code → GeographicArea     │
│ FK vaccine_code → Vaccine         │
│ FK cohort_name → AgeCohort        │
│ FK year → FinancialYear           │
│    eligible_population            │
│    vaccinated_count               │
│    coverage_percentage            │
│ UNIQUE(area, vaccine, cohort, yr) │
└───────────────────────────────────┘

┌───────────────────────────────────┐
│  LocalAuthorityCoverage           │
├───────────────────────────────────┤
│ PK coverage_id                    │
│ FK area_code → GeographicArea     │
│ FK vaccine_code → Vaccine         │
│ FK cohort_name → AgeCohort        │
│ FK year → FinancialYear           │
│    eligible_population            │
│    vaccinated_count               │
│    coverage_percentage            │
│ UNIQUE(area, vaccine, cohort, yr) │
└───────────────────────────────────┘

┌───────────────────────────────────┐
│  EnglandTimeSeries                │
├───────────────────────────────────┤
│ PK series_id                      │
│ FK vaccine_code → Vaccine         │
│ FK cohort_name → AgeCohort        │
│ FK year → FinancialYear           │
│    eligible_population            │
│    vaccinated_count               │
│    coverage_percentage            │
│ UNIQUE(vaccine, cohort, year)     │
└───────────────────────────────────┘

┌───────────────────────────────────┐
│  RegionalTimeSeries               │
├───────────────────────────────────┤
│ PK series_id                      │
│ FK area_code → GeographicArea     │
│ FK vaccine_code → Vaccine         │
│ FK cohort_name → AgeCohort        │
│ FK year → FinancialYear           │
│    eligible_population            │
│    vaccinated_count               │
│    coverage_percentage            │
│ UNIQUE(area, vaccine, cohort, yr) │
└───────────────────────────────────┘

┌───────────────────────────────────┐
│  SpecialPrograms                  │
├───────────────────────────────────┤
│ PK program_id                     │
│ FK area_code → GeographicArea     │
│ FK vaccine_code → Vaccine         │
│ FK year → FinancialYear           │
│    program_type (HepB/BCG)        │
│    births_count                   │
│    vaccinated_count               │
│    coverage_percentage            │
│ UNIQUE(area, vaccine, year, type) │
└───────────────────────────────────┘
```

### Relationship Cardinalities

```
GeographicArea  1 ────< * NationalCoverage
GeographicArea  1 ────< * LocalAuthorityCoverage
GeographicArea  1 ────< * RegionalTimeSeries
GeographicArea  1 ────< * SpecialPrograms

Vaccine         1 ────< * NationalCoverage
Vaccine         1 ────< * LocalAuthorityCoverage
Vaccine         1 ────< * EnglandTimeSeries
Vaccine         1 ────< * RegionalTimeSeries
Vaccine         1 ────< * SpecialPrograms

AgeCohort       1 ────< * NationalCoverage
AgeCohort       1 ────< * LocalAuthorityCoverage
AgeCohort       1 ────< * EnglandTimeSeries
AgeCohort       1 ────< * RegionalTimeSeries

FinancialYear   1 ────< * NationalCoverage
FinancialYear   1 ────< * LocalAuthorityCoverage
FinancialYear   1 ────< * EnglandTimeSeries
FinancialYear   1 ────< * RegionalTimeSeries
FinancialYear   1 ────< * SpecialPrograms
```

---

## Class Diagrams

### Layer 1: Database Models

```
┌─────────────────────────────────────────┐
│           <<abstract>>                  │
│              Base                       │
├─────────────────────────────────────────┤
│ - metadata: MetaData                    │
├─────────────────────────────────────────┤
│                                         │
└─────────────────────────────────────────┘
                    △
                    │ (inherits)
                    │
    ┌───────────────┼───────────────┬─────────────────┐
    │               │               │                 │
┌───────────────────────────┐ ┌──────────────────────────┐
│   GeographicArea          │ │   Vaccine                │
├───────────────────────────┤ ├──────────────────────────┤
│ + area_code: String(50)   │ │ + vaccine_code: String   │
│ + area_name: String(200)  │ │ + vaccine_name: String   │
│ + area_type: String(50)   │ └──────────────────────────┘
├───────────────────────────┤
│ + __repr__(): String      │ ┌──────────────────────────┐
│ + to_dict(): Dict         │ │   AgeCohort              │
└───────────────────────────┘ ├──────────────────────────┤
                              │ + cohort_name: String    │
┌───────────────────────────┐ │ + age_in_months: Integer │
│   FinancialYear           │ └──────────────────────────┘
├───────────────────────────┤
│ + year: Integer           │
│ + year_label: String      │
└───────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│              NationalCoverage                             │
├───────────────────────────────────────────────────────────┤
│ + coverage_id: Integer                                    │
│ + area_code: String (FK → GeographicArea.area_code)      │
│ + vaccine_code: String (FK → Vaccine.vaccine_code)       │
│ + cohort_name: String (FK → AgeCohort.cohort_name)       │
│ + year: Integer (FK → FinancialYear.year)                │
│ + eligible_population: Integer                            │
│ + vaccinated_count: Integer                               │
│ + coverage_percentage: Float                              │
├───────────────────────────────────────────────────────────┤
│ + area: relationship(GeographicArea)                      │
│ + vaccine: relationship(Vaccine)                          │
│ + cohort: relationship(AgeCohort)                         │
│ + financial_year: relationship(FinancialYear)             │
├───────────────────────────────────────────────────────────┤
│ + __repr__(): String                                      │
│ + to_dict(): Dict                                         │
│ + calculate_coverage(): Float                             │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│           LocalAuthorityCoverage                          │
├───────────────────────────────────────────────────────────┤
│ + coverage_id: Integer                                    │
│ + area_code: String (FK)                                  │
│ + vaccine_code: String (FK)                               │
│ + cohort_name: String (FK)                                │
│ + year: Integer (FK)                                      │
│ + eligible_population: Integer                            │
│ + vaccinated_count: Integer                               │
│ + coverage_percentage: Float                              │
├───────────────────────────────────────────────────────────┤
│ + area: relationship(GeographicArea)                      │
│ + vaccine: relationship(Vaccine)                          │
│ + cohort: relationship(AgeCohort)                         │
│ + financial_year: relationship(FinancialYear)             │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│              EnglandTimeSeries                            │
├───────────────────────────────────────────────────────────┤
│ + series_id: Integer                                      │
│ + vaccine_code: String (FK)                               │
│ + cohort_name: String (FK)                                │
│ + year: Integer (FK)                                      │
│ + eligible_population: Integer                            │
│ + vaccinated_count: Integer                               │
│ + coverage_percentage: Float                              │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│              SpecialPrograms                              │
├───────────────────────────────────────────────────────────┤
│ + program_id: Integer                                     │
│ + area_code: String (FK)                                  │
│ + vaccine_code: String (FK)                               │
│ + year: Integer (FK)                                      │
│ + program_type: String                                    │
│ + births_count: Integer                                   │
│ + vaccinated_count: Integer                               │
│ + coverage_percentage: Float                              │
└───────────────────────────────────────────────────────────┘
```

### Layer 2: Business Logic Classes

```
┌─────────────────────────────────────────────────────────┐
│                    CRUDManager                          │
├─────────────────────────────────────────────────────────┤
│ - session: Session                                      │
│ - logger: UserActivityLogger                            │
├─────────────────────────────────────────────────────────┤
│ + __init__(session: Session)                            │
│                                                         │
│ # Geographic Area Operations                           │
│ + create_geographic_area(area_code, name, type): Area  │
│ + get_geographic_area(area_code): Area                 │
│ + update_geographic_area(area_code, name): Area        │
│ + delete_geographic_area(area_code): bool              │
│ + get_all_geographic_areas(): List[Area]               │
│                                                         │
│ # Vaccine Operations                                   │
│ + create_vaccine(code, name): Vaccine                  │
│ + get_vaccine(code): Vaccine                           │
│ + update_vaccine(code, name): Vaccine                  │
│ + delete_vaccine(code): bool                           │
│ + get_all_vaccines(): List[Vaccine]                    │
│                                                         │
│ # Coverage Operations                                  │
│ + create_national_coverage(data): NationalCoverage     │
│ + upsert_coverage_by_codes(data): Coverage            │
│ + get_coverage_by_filters(filters): List[Coverage]    │
│ + update_row_vaccines(area, cohort, year, data): int  │
│ + delete_coverage_by_codes(data): bool                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│               FilteringSummaryAnalyzer                  │
├─────────────────────────────────────────────────────────┤
│ - session: Session                                      │
├─────────────────────────────────────────────────────────┤
│ + filter_coverage(area_code, vaccine_code,             │
│                  cohort_name, year): List[Coverage]    │
│ + calculate_summary_statistics(data): Dict             │
│ + get_trend_data(vaccine, cohort): List[Dict]          │
│ + compare_areas(vaccine, cohort, year): List[Dict]     │
│ + get_top_performing_areas(vaccine, cohort, year, n)   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  TableBuilder                           │
├─────────────────────────────────────────────────────────┤
│ - session: Session                                      │
├─────────────────────────────────────────────────────────┤
│ + build_table_1(cohort, year): Dict                    │
│ + build_utla_table(cohort, year, filters): Dict        │
│ + build_regional_table(cohort): Dict                   │
│ + build_england_summary(cohort, year): Dict            │
│ + build_hepb_table(year): Dict                         │
│ + build_bcg_table(year): Dict                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 DataExporter                            │
├─────────────────────────────────────────────────────────┤
│ - session: Session                                      │
├─────────────────────────────────────────────────────────┤
│ + export_to_csv(data, filename): String                │
│ + export_filtered_data(filters, filename): String      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              UserActivityLogger                         │
├─────────────────────────────────────────────────────────┤
│ - log_file: String                                      │
├─────────────────────────────────────────────────────────┤
│ + log_action(action_type, target, details): void       │
│ + get_recent_logs(n): List[Dict]                       │
│ + get_log_summary(): Dict                              │
└─────────────────────────────────────────────────────────┘
```

### Layer 0: Data Ingestion Classes

```
┌─────────────────────────────────────────────────────────┐
│           <<abstract>>                                  │
│           CSVLoaderBase                                 │
├─────────────────────────────────────────────────────────┤
│ # session: Session                                      │
│ # file_path: String                                     │
│ # logger: UserActivityLogger                            │
├─────────────────────────────────────────────────────────┤
│ + __init__(session, file_path)                          │
│ + load(): void                                          │
│ # read_csv(): DataFrame                                 │
│ # clean_data(df): DataFrame                             │
│ # validate_data(df): bool                               │
│ # transform_data(df): DataFrame                         │
│ # load_to_database(df): void                            │
└─────────────────────────────────────────────────────────┘
                    △
                    │ (inherits)
                    │
    ┌───────────────┼───────────────┬─────────────────┐
    │               │               │                 │
┌──────────────────────────┐ ┌────────────────────────────┐
│ ReferenceDataLoader      │ │ NationalCoverageLoader     │
├──────────────────────────┤ ├────────────────────────────┤
│ + load(): void           │ │ + load(): void             │
│ - load_vaccines(): void  │ │ - clean_data(df): DF       │
│ - load_areas(): void     │ │ - load_to_database(df)     │
│ - load_cohorts(): void   │ └────────────────────────────┘
│ - load_years(): void     │
└──────────────────────────┘ ┌────────────────────────────┐
                             │ LocalAuthorityLoader       │
┌──────────────────────────┐ ├────────────────────────────┤
│ EnglandTimeSeriesLoader  │ │ + load(): void             │
├──────────────────────────┤ │ - transform_data(df): DF   │
│ + load(): void           │ └────────────────────────────┘
│ - transform_data(df): DF │
└──────────────────────────┘ ┌────────────────────────────┐
                             │ SpecialProgramsLoader      │
┌──────────────────────────┐ ├────────────────────────────┤
│ CSVCleaner               │ │ + load(): void             │
├──────────────────────────┤ │ - load_hepb(): void        │
│ + clean_numeric(val): fl │ │ - load_bcg(): void         │
│ + clean_string(val): str │ └────────────────────────────┘
│ + remove_asterisks(val)  │
│ + handle_missing(val)    │
└──────────────────────────┘ ┌────────────────────────────┐
                             │ VaccineMatcher             │
┌──────────────────────────┐ ├────────────────────────────┤
│ ODSToCSVConverter        │ │ + match_vaccine_name(): str│
├──────────────────────────┤ │ + normalize_name(): str    │
│ + convert(file): DF      │ │ - fuzzy_match(): str       │
└──────────────────────────┘ └────────────────────────────┘
```

### Layer 3: Presentation Classes

```
┌─────────────────────────────────────────────────────────┐
│                   Flask Application                     │
├─────────────────────────────────────────────────────────┤
│ + app: Flask                                            │
│ + session: Session                                      │
│ + crud_manager: CRUDManager                             │
│ + table_builder: TableBuilder                           │
│ + analyzer: FilteringSummaryAnalyzer                    │
│ + logger: UserActivityLogger                            │
├─────────────────────────────────────────────────────────┤
│ # Routes                                                │
│ + index(): HTML                                         │
│ + ods_tables(): HTML                                    │
│ + logs(): HTML                                          │
│                                                         │
│ # API Endpoints - CRUD                                 │
│ + get_vaccines(): JSON                                  │
│ + create_vaccine(): JSON                                │
│ + update_vaccine(): JSON                                │
│ + delete_vaccine(): JSON                                │
│ + create_update_coverage(): JSON                        │
│ + delete_coverage(): JSON                               │
│ + update_row(): JSON                                    │
│ + delete_row(): JSON                                    │
│                                                         │
│ # API Endpoints - Tables                               │
│ + get_table_1(): JSON                                   │
│ + get_utla_table(): JSON                                │
│ + get_regional_table(): JSON                            │
│ + get_england_summary(): JSON                           │
│ + get_hepb_table(): JSON                                │
│ + get_bcg_table(): JSON                                 │
│                                                         │
│ # API Endpoints - Data                                 │
│ + get_areas(): JSON                                     │
│ + get_all_areas(): JSON                                 │
│ + export_csv(): JSON                                    │
│                                                         │
│ # API Endpoints - Logs                                 │
│ + get_recent_logs(): JSON                               │
│ + get_log_summary(): JSON                               │
│                                                         │
│ # API Endpoints - Admin                                │
│ + reload_database(): JSON                               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              VisualizationGenerator                     │
├─────────────────────────────────────────────────────────┤
│ - session: Session                                      │
│ - output_dir: String                                    │
├─────────────────────────────────────────────────────────┤
│ + generate_bar_chart(data, title, filename): String    │
│ + generate_line_chart(data, title, filename): String   │
│ + generate_histogram(data, title, filename): String    │
│ + generate_comparison_chart(data, filename): String    │
│ - save_figure(fig, filename): String                   │
└─────────────────────────────────────────────────────────┘
```

---

## Sequence Diagrams

### 1. Create Vaccine Sequence

```
User          Flask App       CRUDManager      Database      Logger
 │                │                │              │            │
 │  POST /api/    │                │              │            │
 │  crud/vaccines │                │              │            │
 ├───────────────>│                │              │            │
 │                │                │              │            │
 │                │ Validate Input │              │            │
 │                ├───────────────>│              │            │
 │                │                │              │            │
 │                │ create_vaccine()              │            │
 │                ├───────────────>│              │            │
 │                │                │              │            │
 │                │                │ INSERT INTO  │            │
 │                │                ├─────────────>│            │
 │                │                │              │            │
 │                │                │  Success     │            │
 │                │                │<─────────────┤            │
 │                │                │              │            │
 │                │                │ log_action("create")      │
 │                │                ├──────────────────────────>│
 │                │                │              │            │
 │                │   Vaccine obj  │              │            │
 │                │<───────────────┤              │            │
 │                │                │              │            │
 │  201 Created   │                │              │            │
 │  + JSON data   │                │              │            │
 │<───────────────┤                │              │            │
 │                │                │              │            │
```

### 2. Filter and Query Coverage Data Sequence

```
User       Flask App    FilteringAnalyzer   CRUDManager   Database
 │             │               │               │            │
 │  POST       │               │               │            │
 │  /api/tables│               │               │            │
 │  /utla      │               │               │            │
 ├────────────>│               │               │            │
 │             │               │               │            │
 │             │ Parse Filters │               │            │
 │             ├──────────────>│               │            │
 │             │               │               │            │
 │             │               │ filter_coverage()          │
 │             │               ├──────────────>│            │
 │             │               │               │            │
 │             │               │               │ SELECT ... │
 │             │               │               ├───────────>│
 │             │               │               │            │
 │             │               │               │ Results    │
 │             │               │               │<───────────┤
 │             │               │               │            │
 │             │               │  Coverage data│            │
 │             │               │<──────────────┤            │
 │             │               │               │            │
 │             │               │ calculate_stats()          │
 │             │               ├───────────────>│            │
 │             │               │               │            │
 │             │               │  Statistics   │            │
 │             │               │<───────────────┤           │
 │             │               │               │            │
 │             │  Table data   │               │            │
 │             │<──────────────┤               │            │
 │             │               │               │            │
 │  200 OK     │               │               │            │
 │  + JSON     │               │               │            │
 │<────────────┤               │               │            │
 │             │               │               │            │
```

### 3. Data Loading Sequence

```
Main Script    DatabaseReload   CSVLoader    CSVCleaner   Database   Logger
    │               │              │             │           │         │
    │ reload_all()  │              │             │           │         │
    ├──────────────>│              │             │           │         │
    │               │              │             │           │         │
    │               │ load_reference_data()      │           │         │
    │               ├─────────────>│             │           │         │
    │               │              │             │           │         │
    │               │              │ read_csv()  │           │         │
    │               │              ├────────────>│           │         │
    │               │              │             │           │         │
    │               │              │ clean_data()│           │         │
    │               │              ├────────────>│           │         │
    │               │              │             │           │         │
    │               │              │  Cleaned DF │           │         │
    │               │              │<────────────┤           │         │
    │               │              │             │           │         │
    │               │              │ INSERT INTO vaccines    │         │
    │               │              ├─────────────────────────>         │
    │               │              │             │           │         │
    │               │              │ INSERT INTO areas       │         │
    │               │              ├─────────────────────────>         │
    │               │              │             │           │         │
    │               │              │ log_action("data_load") │         │
    │               │              ├─────────────────────────────────>│
    │               │              │             │           │         │
    │               │   Success    │             │           │         │
    │               │<─────────────┤             │           │         │
    │               │              │             │           │         │
    │               │ load_national_coverage()   │           │         │
    │               ├─────────────>│             │           │         │
    │               │              │             │           │         │
    │               │              │  (similar process)      │         │
    │               │              │             │           │         │
    │   Success     │              │             │           │         │
    │<──────────────┤              │             │           │         │
    │               │              │             │           │         │
```

### 4. Update Coverage with Validation Sequence

```
User     Flask App    Validator    CRUDManager   Database   Logger
 │           │            │            │            │          │
 │  POST     │            │            │            │          │
 │  /api/crud│            │            │            │          │
 │  /coverage│            │            │            │          │
 ├──────────>│            │            │            │          │
 │           │            │            │            │          │
 │           │ Validate   │            │            │          │
 │           │ Required   │            │            │          │
 │           │ Fields     │            │            │          │
 │           ├───────────>│            │            │          │
 │           │            │            │            │          │
 │           │ Validate   │            │            │          │
 │           │ Types &    │            │            │          │
 │           │ Ranges     │            │            │          │
 │           ├───────────>│            │            │          │
 │           │            │            │            │          │
 │           │ Validate   │            │            │          │
 │           │ Relationships           │            │          │
 │           ├───────────>│            │            │          │
 │           │            │            │            │          │
 │           │   Valid    │            │            │          │
 │           │<───────────┤            │            │          │
 │           │            │            │            │          │
 │           │ upsert_coverage()       │            │          │
 │           ├────────────────────────>│            │          │
 │           │            │            │            │          │
 │           │            │            │ BEGIN TRAN │          │
 │           │            │            ├───────────>│          │
 │           │            │            │            │          │
 │           │            │            │ SELECT ... │          │
 │           │            │            ├───────────>│          │
 │           │            │            │            │          │
 │           │            │            │ UPDATE/    │          │
 │           │            │            │ INSERT     │          │
 │           │            │            ├───────────>│          │
 │           │            │            │            │          │
 │           │            │            │ COMMIT     │          │
 │           │            │            ├───────────>│          │
 │           │            │            │            │          │
 │           │            │            │ log_action()          │
 │           │            │            ├──────────────────────>│
 │           │            │            │            │          │
 │           │            │  Coverage  │            │          │
 │           │<────────────────────────┤            │          │
 │           │            │            │            │          │
 │  200 OK   │            │            │            │          │
 │<──────────┤            │            │            │          │
 │           │            │            │            │          │
```

### 5. Error Handling Sequence

```
User     Flask App    CRUDManager   Database   Session
 │           │            │            │          │
 │  POST     │            │            │          │
 │  invalid  │            │            │          │
 │  data     │            │            │          │
 ├──────────>│            │            │          │
 │           │            │            │          │
 │           │ Validate   │            │          │
 │           │ Input      │            │          │
 │           │   ❌ FAIL  │            │          │
 │           │            │            │          │
 │  400 Bad  │            │            │          │
 │  Request  │            │            │          │
 │<──────────┤            │            │          │
 │           │            │            │          │
 │           │            │            │          │
 │  POST     │            │            │          │
 │  valid    │            │            │          │
 │  but      │            │            │          │
 │  conflict │            │            │          │
 ├──────────>│            │            │          │
 │           │            │            │          │
 │           │ ✓ Valid    │            │          │
 │           │            │            │          │
 │           │ create()   │            │          │
 │           ├───────────>│            │          │
 │           │            │            │          │
 │           │            │ INSERT     │          │
 │           │            ├───────────>│          │
 │           │            │            │          │
 │           │            │ Integrity  │          │
 │           │            │ Error!     │          │
 │           │            │<───────────┤          │
 │           │            │            │          │
 │           │            │ session.   │          │
 │           │            │ rollback() │          │
 │           │            ├────────────────────>  │
 │           │            │            │          │
 │           │  Exception │            │          │
 │           │<───────────┤            │          │
 │           │            │            │          │
 │  409      │            │            │          │
 │  Conflict │            │            │          │
 │<──────────┤            │            │          │
 │           │            │            │          │
```

---

## Component Diagram

### System Components and Dependencies

```
┌───────────────────────────────────────────────────────────────┐
│                    Presentation Layer (Layer 3)               │
│  ┌─────────────────────┐        ┌─────────────────────┐      │
│  │   Flask Web App     │        │  Visualization      │      │
│  │                     │        │  Generator          │      │
│  │  - Routes           │        │                     │      │
│  │  - API Endpoints    │        │  - Matplotlib       │      │
│  │  - Templates        │        │  - Chart Generation │      │
│  └──────────┬──────────┘        └─────────────────────┘      │
└─────────────┼────────────────────────────────────────────────┘
              │ uses
              ▼
┌───────────────────────────────────────────────────────────────┐
│                  Business Logic Layer (Layer 2)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ CRUDManager  │  │  Filtering   │  │ Table        │       │
│  │              │  │  Summary     │  │ Builder      │       │
│  │ - Create     │  │  Analyzer    │  │              │       │
│  │ - Read       │  │              │  │ - Table 1    │       │
│  │ - Update     │  │ - Filter     │  │ - UTLA Table │       │
│  │ - Delete     │  │ - Statistics │  │ - Regional   │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                  │                │
│  ┌──────┴─────────────────┴──────────────────┴──────┐        │
│  │           Data Export        User Logger          │        │
│  │                                                    │        │
│  │  - CSV Export               - Activity Logging    │        │
│  │  - Filtered Export          - Log Queries         │        │
│  └────────────────────────┬───────────────────────────┘       │
└───────────────────────────┼───────────────────────────────────┘
                            │ uses
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                   Database Layer (Layer 1)                    │
│  ┌────────────────────────────────────────────────────┐      │
│  │              SQLAlchemy ORM Models                 │      │
│  │                                                     │      │
│  │  GeographicArea  Vaccine  AgeCohort  FinancialYear│      │
│  │  NationalCoverage  LocalAuthorityCoverage          │      │
│  │  EnglandTimeSeries  RegionalTimeSeries             │      │
│  │  SpecialPrograms                                   │      │
│  └────────────────────────┬───────────────────────────┘      │
│                           │                                   │
│  ┌────────────────────────┴───────────────────────────┐      │
│  │              Session Management                     │      │
│  │                                                     │      │
│  │  - create_session()                                │      │
│  │  - init_database()                                 │      │
│  └────────────────────────┬───────────────────────────┘      │
└───────────────────────────┼───────────────────────────────────┘
                            │ reads/writes
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                       SQLite Database                         │
│                     immunisation_data.db                      │
│                                                               │
│  Tables: vaccines, geographic_areas, age_cohorts,            │
│          financial_years, national_coverage,                 │
│          local_authority_coverage, england_time_series,      │
│          regional_time_series, special_programs              │
└───────────────────────────┬───────────────────────────────────┘
                            │ loaded from
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                  Data Ingestion Layer (Layer 0)               │
│  ┌────────────────────────────────────────────────────┐      │
│  │              CSV Loaders (Base Class)              │      │
│  │                                                     │      │
│  │  - ReferenceDataLoader                             │      │
│  │  - NationalCoverageLoader                          │      │
│  │  - LocalAuthorityLoader                            │      │
│  │  - EnglandTimeSeriesLoader                         │      │
│  │  - RegionalTimeSeriesLoader                        │      │
│  │  - SpecialProgramsLoader                           │      │
│  └────────────────────────┬───────────────────────────┘      │
│                           │                                   │
│  ┌────────────────────────┴───────────────────────────┐      │
│  │         Data Cleaning & Transformation             │      │
│  │                                                     │      │
│  │  - CSVCleaner                                      │      │
│  │  - VaccineMatcher                                  │      │
│  │  - ODSToCSVConverter                               │      │
│  └────────────────────────┬───────────────────────────┘      │
└───────────────────────────┼───────────────────────────────────┘
                            │ reads from
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                         CSV Data Files                        │
│                                                               │
│  - reference_data.csv                                        │
│  - Table 1 - UK coverage by country.csv                     │
│  - Table 4 - Local authority data for UTLA.csv              │
│  - Table 5 - HepB and BCG.csv                               │
│  - Table 6 - Regional time series.csv                       │
│  - Table 7 - England time series.csv                        │
└───────────────────────────────────────────────────────────────┘
```

---

## Deployment Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    Client Machine (Browser)                    │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Web Browser (Chrome/Firefox)                 │ │
│  │                                                           │ │
│  │  - HTML/CSS/JavaScript                                   │ │
│  │  - REST API Client                                       │ │
│  └───────────────────────────┬──────────────────────────────┘ │
└────────────────────────────────┼────────────────────────────────┘
                                 │
                                 │ HTTP/HTTPS
                                 │ (Port 5000)
                                 ▼
┌────────────────────────────────────────────────────────────────┐
│                    Application Server                          │
│                     (Local/Production)                         │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │           Flask Web Server (Development)                 │ │
│  │              OR                                           │ │
│  │           Gunicorn/uWSGI (Production)                    │ │
│  │                                                           │ │
│  │  - Python 3.12 Runtime                                   │ │
│  │  - Flask Application                                     │ │
│  │  - REST API Endpoints                                    │ │
│  └───────────────────────────┬──────────────────────────────┘ │
│                               │                                │
│  ┌────────────────────────────┴────────────────────────────┐  │
│  │              Application Components                      │  │
│  │                                                          │  │
│  │  Layer 3: Flask App + Visualization                     │  │
│  │  Layer 2: CRUD + Analysis + Export + Logging            │  │
│  │  Layer 1: SQLAlchemy ORM + Session Management           │  │
│  │  Layer 0: CSV Loaders + Cleaners                        │  │
│  └────────────────────────────┬────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────┘
                                 │
                                 │ SQLite Protocol
                                 ▼
┌────────────────────────────────────────────────────────────────┐
│                    Data Storage                                │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │           SQLite Database File                           │ │
│  │         immunisation_data.db                             │ │
│  │                                                           │ │
│  │  - 8 Tables                                              │ │
│  │  - ~3,000+ Records                                       │ │
│  │  - File Size: ~2-5 MB                                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                Static Files                              │ │
│  │                                                           │ │
│  │  - CSS Stylesheets                                       │ │
│  │  - JavaScript Files                                      │ │
│  │  - Generated Charts (PNG)                                │ │
│  │  - Exported CSV Files                                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                 Log Files                                │ │
│  │                                                           │ │
│  │  - user_actions.log                                      │ │
│  │  - error.log                                             │ │
│  │  - application.log                                       │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘

                        PRODUCTION DEPLOYMENT
                        (Optional - Not Current)

┌────────────────────────────────────────────────────────────────┐
│                     Reverse Proxy Server                       │
│                    (Nginx or Apache)                           │
│                                                                │
│  - Port 80/443 (HTTP/HTTPS)                                   │
│  - SSL/TLS Termination                                        │
│  - Load Balancing (if scaled)                                 │
│  - Static File Serving                                        │
│  - Rate Limiting                                              │
│  - Security Headers                                           │
└────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Proxy Pass
                                 ▼
┌────────────────────────────────────────────────────────────────┐
│                   WSGI Server (Gunicorn)                       │
│                                                                │
│  - Multiple Worker Processes                                  │
│  - Process Management                                         │
│  - Auto-restart on failure                                    │
└────────────────────────────────────────────────────────────────┘
```

---

## Activity Diagrams

### 1. Data Loading Activity Diagram

```
         (Start)
            │
            ▼
     ┌──────────────┐
     │ Check if     │
     │ database     │
     │ exists       │
     └──────┬───────┘
            │
      ┌─────┴─────┐
      │ Exists?   │
      └─────┬─────┘
            │
      ┌─────┴─────┐
      │ No        │ Yes
      │           │
      ▼           ▼
┌───────────┐  (Skip
│ Delete    │   Loading)
│ existing  │
│ database  │
└─────┬─────┘
      │
      ▼
┌───────────────┐
│ Load Reference│
│ Data          │
│ - Vaccines    │
│ - Areas       │
│ - Cohorts     │
│ - Years       │
└───────┬───────┘
        │
        ▼
  ┌─────────────┐
  │ Load        │
  │ National    │
  │ Coverage    │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ Load Local  │
  │ Authority   │
  │ Coverage    │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ Load Time   │
  │ Series Data │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ Load Special│
  │ Programs    │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ Commit to   │
  │ Database    │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │ Log Success │
  └──────┬──────┘
         │
         ▼
      (End)
```

### 2. API Request Handling Activity Diagram

```
         (Start)
            │
            ▼
     ┌──────────────┐
     │ Receive HTTP │
     │ Request      │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Parse JSON   │
     │ Body         │
     └──────┬───────┘
            │
      ┌─────┴─────┐
      │ Valid     │
      │ JSON?     │
      └─────┬─────┘
            │
      ┌─────┴─────┐
      │ No        │ Yes
      │           │
      ▼           ▼
┌──────────┐  ┌──────────────┐
│ Return   │  │ Validate     │
│ 400 Bad  │  │ Required     │
│ Request  │  │ Fields       │
└────┬─────┘  └──────┬───────┘
     │               │
     │         ┌─────┴─────┐
     │         │ Valid?    │
     │         └─────┬─────┘
     │               │
     │         ┌─────┴─────┐
     │         │ No        │ Yes
     │         │           │
     │         ▼           ▼
     │    ┌─────────┐  ┌──────────────┐
     │    │ Return  │  │ Validate     │
     │    │ 400     │  │ Data Types   │
     │    └────┬────┘  │ & Ranges     │
     │         │       └──────┬───────┘
     │         │              │
     │         │        ┌─────┴─────┐
     │         │        │ Valid?    │
     │         │        └─────┬─────┘
     │         │              │
     │         │        ┌─────┴─────┐
     │         │        │ No        │ Yes
     │         │        │           │
     │         │        ▼           ▼
     │         │   ┌─────────┐  ┌──────────────┐
     │         │   │ Return  │  │ Execute      │
     │         │   │ 400     │  │ Business     │
     │         │   └────┬────┘  │ Logic        │
     │         │        │       └──────┬───────┘
     │         │        │              │
     │         │        │        ┌─────┴─────┐
     │         │        │        │ Database  │
     │         │        │        │ Operation │
     │         │        │        └─────┬─────┘
     │         │        │              │
     │         │        │        ┌─────┴─────┐
     │         │        │        │ Success?  │
     │         │        │        └─────┬─────┘
     │         │        │              │
     │         │        │        ┌─────┴─────┐
     │         │        │        │ No        │ Yes
     │         │        │        │           │
     │         │        │        ▼           ▼
     │         │        │   ┌─────────┐  ┌──────────┐
     │         │        │   │ Session │  │ Commit   │
     │         │        │   │ Rollback│  │          │
     │         │        │   └────┬────┘  └────┬─────┘
     │         │        │        │            │
     │         │        │        ▼            ▼
     │         │        │   ┌─────────┐  ┌──────────┐
     │         │        │   │ Log     │  │ Log      │
     │         │        │   │ Error   │  │ Action   │
     │         │        │   └────┬────┘  └────┬─────┘
     │         │        │        │            │
     │         │        │        ▼            ▼
     │         │        │   ┌─────────┐  ┌──────────┐
     │         │        │   │ Return  │  │ Return   │
     │         │        │   │ 404/409 │  │ 200/201  │
     │         │        │   │ /500    │  │ + Data   │
     └─────────┴────────┴───┴────┬────┴──┴────┬─────┘
                                 │            │
                                 └─────┬──────┘
                                       │
                                       ▼
                                    (End)
```

### 3. Batch Update Activity Diagram

```
         (Start)
            │
            ▼
     ┌──────────────┐
     │ Receive batch│
     │ update       │
     │ request      │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Begin        │
     │ Transaction  │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ For each     │
     │ vaccine in   │
     │ batch        │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Validate     │
     │ vaccine data │
     └──────┬───────┘
            │
      ┌─────┴─────┐
      │ Valid?    │
      └─────┬─────┘
            │
      ┌─────┴─────┐
      │ No        │ Yes
      │           │
      ▼           ▼
┌──────────┐  ┌──────────────┐
│ Mark for │  │ Update/      │
│ rollback │  │ Insert       │
└────┬─────┘  │ Coverage     │
     │        └──────┬───────┘
     │               │
     │         ┌─────┴─────┐
     │         │ Success?  │
     │         └─────┬─────┘
     │               │
     │         ┌─────┴─────┐
     │         │ No        │ Yes
     │         │           │
     │         ▼           ▼
     │    ┌─────────┐  ┌──────────┐
     │    │ Mark for│  │ Continue │
     │    │ rollback│  │ to next  │
     └────┴────┬────┴──┴────┬─────┘
               │            │
               └─────┬──────┘
                     │
                     ▼
              ┌──────────────┐
              │ More         │
              │ vaccines?    │
              └──────┬───────┘
                     │
               ┌─────┴─────┐
               │ Yes       │ No
               │           │
               ▼           ▼
         (Loop back)  ┌──────────┐
                      │ Any      │
                      │ errors?  │
                      └────┬─────┘
                           │
                     ┌─────┴─────┐
                     │ Yes       │ No
                     │           │
                     ▼           ▼
              ┌──────────┐  ┌──────────┐
              │ Rollback │  │ Commit   │
              │ All      │  │ All      │
              └────┬─────┘  └────┬─────┘
                   │             │
                   ▼             ▼
              ┌──────────┐  ┌──────────┐
              │ Return   │  │ Return   │
              │ 400/500  │  │ 200      │
              │ + errors │  │ + count  │
              └────┬─────┘  └────┬─────┘
                   │             │
                   └─────┬───────┘
                         │
                         ▼
                      (End)
```

---

## State Diagrams

### 1. Coverage Record State Diagram

```
                    [Initial State]
                          │
                          ▼
                   ┌──────────────┐
                   │  Non-Existent│
                   └──────┬───────┘
                          │
              create_coverage()
                          │
                          ▼
                   ┌──────────────┐
                   │   Created    │
                   │   (Persisted)│
                   └──────┬───────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
  update_coverage()  delete_coverage()   │
           │              │              │
           ▼              ▼              │
    ┌──────────┐   ┌──────────┐        │
    │ Updated  │   │ Deleted  │        │
    │          │   │ (Removed)│        │
    └────┬─────┘   └──────────┘        │
         │               │              │
         │               ▼              │
         │         [Final State]        │
         │                              │
         └──────────────────────────────┘
            (cycle continues)
```

### 2. Database Session State Diagram

```
              [Initial State]
                    │
                    ▼
             ┌──────────────┐
             │    Closed    │
             └──────┬───────┘
                    │
           create_session()
                    │
                    ▼
             ┌──────────────┐
             │     Open     │
             │    (Idle)    │
             └──────┬───────┘
                    │
       ┌────────────┼────────────┐
       │            │            │
  begin_trans()  close()     query()
       │            │            │
       ▼            ▼            ▼
┌────────────┐ ┌──────────┐ ┌──────────┐
│Transaction │ │  Closed  │ │Executing │
│ Active     │ └──────────┘ │  Query   │
└──────┬─────┘      │        └────┬─────┘
       │            ▼             │
       │      [Final State]       │
       │                          │
┌──────┴────┐              ┌─────┴──────┐
│commit()   │ rollback()   │ Results    │
│           │              │ Returned   │
└─────┬─────┘──────┬───────┴────────────┘
      │            │              │
      ▼            ▼              │
┌──────────┐ ┌──────────┐        │
│Committed │ │ Rolled   │        │
│          │ │ Back     │        │
└────┬─────┘ └────┬─────┘        │
     │            │              │
     └────────────┴──────────────┘
                  │
                  ▼
           ┌──────────────┐
           │     Open     │
           │    (Idle)    │
           └──────────────┘
```

### 3. API Request Lifecycle State Diagram

```
       [Client Initiates]
              │
              ▼
       ┌──────────────┐
       │   Received   │
       └──────┬───────┘
              │
     parse_request()
              │
              ▼
       ┌──────────────┐
       │   Parsed     │
       └──────┬───────┘
              │
    ┌─────────┴─────────┐
    │                   │
validate()         validate()
 (success)          (failure)
    │                   │
    ▼                   ▼
┌──────────┐     ┌──────────────┐
│Validated │     │ Validation   │
│          │     │ Failed       │
└────┬─────┘     └──────┬───────┘
     │                  │
execute()               │
     │                  │
     ▼                  │
┌──────────┐           │
│Processing│           │
└────┬─────┘           │
     │                  │
┌────┴────┐            │
│Success? │            │
└────┬────┘            │
     │                  │
┌────┴────┐            │
│Yes   No │            │
│    │    │            │
▼    ▼    │            │
┌─────────────┐        │
│  Success    │        │
│  200/201    │        │
└──────┬──────┘        │
       │               │
       │    ┌──────────┴────────┐
       │    │    Error          │
       │    │  400/404/409/500  │
       │    └──────────┬────────┘
       │               │
       └───────────────┘
              │
        send_response()
              │
              ▼
       ┌──────────────┐
       │   Response   │
       │   Sent       │
       └──────┬───────┘
              │
              ▼
        [Complete]
```

---

## Use Case Diagram

```
                         System Boundary
    ┌────────────────────────────────────────────────────────┐
    │   UK Childhood Immunisation Coverage Data Insights    │
    │                                                        │
    │                                                        │
    │   ┌──────────────────────────────────────────┐       │
    │   │  View Coverage Data                      │       │
    │   └──────────────────────────────────────────┘       │
    │             △                                         │
    │             │ <<extends>>                             │
    │   ┌─────────┴──────────────────────────────┐         │
    │   │  Filter by Geography/Vaccine/Year      │         │
    │   └────────────────────────────────────────┘         │
    │                                                        │
    │   ┌──────────────────────────────────────────┐       │
    │   │  Generate Summary Statistics             │       │
    │   └──────────────────────────────────────────┘       │
    │                                                        │
    │   ┌──────────────────────────────────────────┐       │
    │   │  View Trend Analysis                     │       │
    │   └──────────────────────────────────────────┘       │
    │                                                        │
┌────┤   ┌──────────────────────────────────────────┐       │
│Public  │  Generate Visualizations                 │       │
│Health  └──────────────────────────────────────────┘       │
│Analyst                                                     │
└────┤   ┌──────────────────────────────────────────┐       │
    │   │  Export Data to CSV                      │       │
    │   └──────────────────────────────────────────┘       │
    │                                                        │
    │   ┌──────────────────────────────────────────┐       │
    │   │  Create/Update Coverage Records          │       │
    │   └──────────────────────────────────────────┘       │
    │                                                        │
    │   ┌──────────────────────────────────────────┐       │
    │   │  Delete Coverage Records                 │       │
    │   └──────────────────────────────────────────┘       │
    │                                                        │
    │   ┌──────────────────────────────────────────┐       │
    │   │  View Activity Logs                      │       │
    │   └──────────────────────────────────────────┘       │
    │                                                        │
    │   ┌──────────────────────────────────────────┐       │
    │   │  Manage Vaccines                         │       │
    │   └──────────────────────────────────────────┘       │
    │                                                        │
    │   ┌──────────────────────────────────────────┐       │
┌────┤  │  Reload Database from CSV                │       │
│System  └──────────────────────────────────────────┘       │
│Admin                                                       │
└────┤   ┌──────────────────────────────────────────┐       │
    │   │  View System Logs                        │       │
    │   └──────────────────────────────────────────┘       │
    │                                                        │
    └────────────────────────────────────────────────────────┘
```

---

## Package Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                           src                                 │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  layer3_presentation                                   │  │
│  │  ├── flask_app.py                                      │  │
│  │  └── visualization.py                                  │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│                           │ depends on                        │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  layer2_business_logic                                 │  │
│  │  ├── crud.py                                           │  │
│  │  ├── fs_analysis.py                                    │  │
│  │  ├── table_builder.py                                  │  │
│  │  ├── export.py                                         │  │
│  │  ├── user_log.py                                       │  │
│  │  ├── database_reload.py                                │  │
│  │  └── ods_conversion.py                                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│                           │ depends on                        │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  layer1_database                                       │  │
│  │  ├── models.py                                         │  │
│  │  └── database.py                                       │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│                           │ persists to                       │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  SQLite Database                                       │  │
│  │  immunisation_data.db                                  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  layer0_data_ingestion                                 │  │
│  │  ├── csv_loader_base.py                                │  │
│  │  ├── csv_cleaner.py                                    │  │
│  │  ├── load_reference_data.py                            │  │
│  │  ├── load_national_coverage.py                         │  │
│  │  ├── load_local_authority.py                           │  │
│  │  ├── load_england_time_series.py                       │  │
│  │  ├── load_regional_time_series.py                      │  │
│  │  ├── load_special_programs.py                          │  │
│  │  ├── vaccine_matcher.py                                │  │
│  │  └── ods_to_csv.py                                     │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│                           │ loads from                        │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  CSV Data Files (data/)                                │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                           tests                               │
├───────────────────────────────────────────────────────────────┤
│  ├── layer0_data_ingestion/ (93 tests)                       │
│  ├── layer1_database/ (25 tests)                             │
│  ├── layer2_business_logic/ (156 tests)                      │
│  └── layer3_presentation/ (50 tests)                         │
└───────────────────────────────────────────────────────────────┘
```

---

## Summary

This document provides comprehensive UML diagrams for the UK Childhood Immunisation Coverage Data Insights Tool, including:

1. **ER Diagram**: Complete database schema with relationships
2. **Class Diagrams**: All layers with detailed class structures
3. **Sequence Diagrams**: Key workflows and interactions
4. **Component Diagram**: System architecture and dependencies
5. **Deployment Diagram**: Physical deployment architecture
6. **Activity Diagrams**: Process flows for key operations
7. **State Diagrams**: Object lifecycle management
8. **Use Case Diagram**: System functionality from user perspective
9. **Package Diagram**: Code organization and dependencies

All diagrams use standard UML notation and are suitable for technical documentation and academic submission.

---

**Version:** 1.0.0
**Last Updated:** December 2024
**Status:** ✅ Complete
