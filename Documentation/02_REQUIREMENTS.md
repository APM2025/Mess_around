# Requirements Specification

## Requirements Analysis

This document captures all functional and non-functional requirements for the Childhood Immunisation Coverage Data Insights Tool.

---

## 1. Data Access & Loading

| ID | Requirement | Acceptance Criteria | Category | Priority |
|----|-------------|---------------------|----------|----------|
| DA-FR-001 | System shall load public health data from at least one external file (CSV, XLSX) or from the configured structured data store. | Dataset loads from file or store without failure and is accessible in memory. | Functional | Must |
| DA-FR-002 | System shall store loaded data in a structured Python object (e.g., DataFrame) for processing. | User can view a preview of the loaded dataset. | Functional | Must |
| DA-NFR-001 | Load operations shall present clear, non-technical error messages for invalid paths or malformed files. | Errors shown without program crashing. | Reliability | Must |

---

## 2. Data Cleaning & Structuring

| ID | Requirement | Acceptance Criteria | Category | Priority |
|----|-------------|---------------------|----------|----------|
| DC-FR-001 | System shall detect and handle missing or inconsistent values. | Missing/inconsistent values are removed, flagged, or appropriately handled. | Functional | Must |
| DC-FR-002 | System shall convert relevant fields to correct types (e.g., dates, numeric coverage values). | Dates represented as datetime; numerics as float/int. | Functional | Must |
| DC-FR-003 | System shall normalise column names or field labels as needed. | Dataset uses consistent internal field names. | Functional | Should |
| DC-NFR-001 | Data cleaning operations shall be testable independently. | Cleaning functions run correctly on test data. | Supportability | Should |

---

## 3. Persistence: Structured Data Store & Full CRUD

| ID | Requirement | Acceptance Criteria | Category | Priority |
|----|-------------|---------------------|----------|----------|
| DB-FR-001 | System shall persist cleaned/ingested data into a robust, structured data store upon loading (CREATE). | Data is written to the store and can be read back exactly, forming the source of truth. | Functional | Must |
| DB-FR-002 | System shall support reading the primary public health dataset from the data store for filtering and summary operations (READ). | Filter queries against the store return identical results to in-memory operations. | Functional | Must |
| DB-FR-003 | System shall allow authenticated users to modify existing records (e.g., correct a data entry error) in the persisted dataset (UPDATE). | User actions successfully update the selected row(s); changes reflect in subsequent reads. | Functional | Should |
| DB-FR-004 | System shall allow authenticated users to remove specific records or datasets from the persisted storage (DELETE). | User actions successfully delete the selected record(s). | Functional | Should |
| DB-FR-005 | System shall use a structured data model that logically organizes data fields for efficient retrieval and reporting. | The model clearly separates fields for geography, vaccine, age_group, year, and metrics; sample queries are performant. | Functional | Must |
| DB-NFR-001 | Data store access shall be testable via integration tests. | Test suite includes data store read/write checks using a test environment. | Supportability | Must |
| DB-NFR-002 | Data store credentials shall be configurable via environment variables or config files. | System reads credentials from env/config; no plaintext credentials in source. | Security | Must |

---

## 4. Filtering & Summary Views

| ID | Requirement | Acceptance Criteria | Category | Priority |
|----|-------------|---------------------|----------|----------|
| FS-FR-001 | System shall allow filtering data by geographic level (e.g., country, region, local authority). | Filtered output contains only matching geographic records. | Functional | Must |
| FS-FR-002 | System shall allow filtering by vaccine type. | Output shows only the selected vaccine(s). | Functional | Must |
| FS-FR-003 | System shall allow filtering by reporting year or age group. | Output reflects selected year or age category. | Functional | Should |
| FS-FR-004 | System shall generate summary statistics such as mean, min, max, and counts. | Summary values correct for the current filtered dataset. | Functional | Must |
| FS-FR-005 | System shall produce simple trend information over available years. | Trend output displays values in chronological order. | Functional | Should |
| FS-NFR-001 | Filtering and summary operations shall respond within 1 second for typical dataset sizes. | Output displayed promptly. | Performance | Should |

---

## 5. Presentation Layer

| ID | Requirement | Acceptance Criteria | Category | Priority |
|----|-------------|---------------------|----------|----------|
| PR-FR-001 | System shall provide a user interface via either a command-line menu or a simple UI. | User can select operations from a menu or UI screen. | Usability | Must |
| PR-FR-002 | System shall display filtered data in a readable table format. | Tables visible in console or UI window. | Functional | Must |
| PR-FR-003 | System shall generate basic visual outputs of key data trends and comparisons. | Visualisation appears with labelled axes and title, clearly conveying the requested comparison. | Functional | Should |
| PR-NFR-001 | Presentation functions shall handle empty or missing outputs gracefully. | If no data is available, a clear message is shown. | Reliability | Must |

---

## 6. Security & Input Validation

| ID | Requirement | Acceptance Criteria | Category | Priority |
|----|-------------|---------------------|----------|----------|
| SEC-FR-001 | System shall validate and sanitise all user-provided inputs used in file paths or data store queries. | Invalid inputs rejected with a clear error; allowed inputs conform to expected patterns. | Security | Must |
| SEC-FR-002 | System shall prevent code injection attacks (e.g., SQL injection) for all data persistence operations. | Tests with malicious payloads do not alter schema/data; queries execute safely. | Security | Must |
| SEC-FR-003 | System shall not write secrets (DB passwords, API keys) into source code or logs. | Codebase contains no hard-coded secrets; logs omit full secrets. | Security | Must |
| SEC-FR-004 | The data store connection shall use a least-privilege account (where the data store supports users). | User account lacks unnecessary privileges. | Security | Should |
| SEC-NFR-001 | Input validation and neutralisation checks shall be demonstrable in tests. | Unit/integration tests assert that malicious inputs are neutralised. | Supportability | Must |

---

## 7. Data Export & Logging

| ID | Requirement | Acceptance Criteria | Category | Priority |
|----|-------------|---------------------|----------|----------|
| EL-FR-001 | System shall allow exporting filtered data or summary results to a CSV file. | Exported file matches the displayed data. | Functional | Should |
| EL-FR-002 | System shall log user-selected actions and security-relevant events to a log file, excluding sensitive information. | Logs include timestamp, action type, and event description; no secrets written. | Reliability / Security | Should |
| EL-NFR-001 | Log files shall not disrupt program performance. | Logging occurs without slowing the system noticeably. | Performance | Should |

---

## Requirements Summary

**Total Requirements:** 33  
**Must-Have (Priority):** 20  
**Should-Have (Priority):** 13

**Categories:**
- Functional: 24
- Non-Functional: 9
  - Security: 5
  - Performance: 2
  - Reliability: 3
  - Supportability: 3
  - Usability: 1
