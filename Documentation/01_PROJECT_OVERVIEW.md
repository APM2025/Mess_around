# Childhood Immunisation Coverage Data Insights Tool

## Project Overview

This project develops a Python-based data insights tool for analyzing public health data from the UK Health Security Agency's Cover of Vaccination Evaluated Rapidly (COVER) programme.

## Purpose Statement

**Enable public health analysts to interactively explore childhood immunisation data through filtering, visualisation, and statistical analysis for evidence-based decisions.**

## Data Source

**Dataset:** COVER Programme Annual Report  
**Provider:** UK Health Security Agency  

**Why This Dataset:**
- Trusted, authoritative source
- Covers multiple age cohorts and geographic regions  
- Difficult to interpret quickly without visualization
- High value for public health research

## Scope

### In Scope
- Load data from CSV/XLSX files
- Store data in structured database
- Filter by geography, vaccine, year, age
- Generate summary statistics and trends
- Interactive visualizations
- CRUD operations
- CSV export
- Activity logging
- Web interface

### Out of Scope
- Predictive modeling
- Real-time data feeds
- Multi-user authentication  
- Mobile applications

## Stakeholder Analysis

| Stakeholder | Category | Influence | Power |
|------------|----------|-----------|-------|
| Public Health Analysts | Primary | High | Medium |
| Developer | Primary | High | Medium |
| COVER Programme | Secondary | Medium | Medium |
| NHS/UKHSA Decision Makers | Secondary | Medium | Low |
| General Public | Tertiary | Low | Low |
| Regulatory Bodies | Tertiary | Low | Medium |

## Architecture

**4-Layer Architecture:**
- Layer 0: Data Ingestion
- Layer 1: Database (SQLite + SQLAlchemy)
- Layer 2: Business Logic  
- Layer 3: Presentation (Flask)

**Development:** Test-Driven Development (TDD)

**Technologies:** Python, Flask, SQLite, Pandas, Matplotlib, Pytest
