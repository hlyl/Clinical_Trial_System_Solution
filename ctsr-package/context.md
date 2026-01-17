# CTSR - Clinical Trial Systems Register

## Context for Development

This document provides the essential background for developing the Clinical Trial Systems Register (CTSR), a regulatory compliance solution for documenting IT systems used in global clinical trials.

---

## 1. Business Purpose

### Why This System Exists

Pharmaceutical sponsors (like Novo Nordisk) must maintain documentation of all computerized systems used in clinical trials per **ICH E6(R3)** regulatory requirements. During regulatory inspections, sponsors must demonstrate:

1. They know what systems are used in each trial
2. Those systems are validated and fit for purpose
3. There is ongoing oversight of system changes
4. Data flows between systems are understood

### The Problem Being Solved

- **CROs and vendors manage many systems** on behalf of the sponsor
- **No central inventory** exists today - information is scattered
- **Inspection prep is painful** - teams scramble to compile system lists
- **Validation status tracking is manual** - expiration dates are missed

### The Solution

A central registry where:
1. Vendors upload system information via JSON files
2. Trial teams link relevant systems to their trials
3. Periodic confirmations ensure data stays current
4. eTMF-ready exports are generated at database lock

---

## 2. Regulatory Requirements

### ICH E6(R3) Section 3.16.1(x)

Sponsors must maintain documentation of computerized systems including:
- System use, functionality, and interfaces
- Validation status
- Access controls and security measures
- Who is responsible for system management

### Key Compliance Concepts

| Concept | Description |
|---------|-------------|
| **Validation** | Documented evidence that a system does what it's supposed to do |
| **21 CFR Part 11** | FDA regulation for electronic records and signatures |
| **EU Annex 11** | European regulation for computerized systems in GxP |
| **CSA** | Computer Software Assurance - risk-based validation approach |
| **eTMF** | Electronic Trial Master File - where trial documentation is archived |

### Data Criticality Classification

| Level | Code | Description | Examples |
|-------|------|-------------|----------|
| Critical | CRIT | Direct impact on participant safety and/or primary endpoint data | EDC, IRT, Safety DB |
| Major | MAJ | Impact on secondary endpoints, compliance, or operations | CTMS, eTMF, Central Lab |
| Standard | STD | Supporting functions with indirect impact | Training LMS, Archival |

---

## 3. System Architecture

### Technology Stack

| Component | Technology |
|-----------|------------|
| Database | Azure PostgreSQL Flexible Server |
| API | Python FastAPI |
| Frontend | Streamlit |
| Background Jobs | Azure Functions |
| File Storage | Azure Blob Storage |
| Authentication | Azure AD (Entra ID) |

### High-Level Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Vendor    │────▶│ Blob Storage │────▶│ Azure Function  │
│ JSON Upload │     │              │     │ (processor)     │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                  │
                                                  ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Streamlit  │────▶│   FastAPI    │────▶│   PostgreSQL    │
│     UI      │     │     API      │     │                 │
└─────────────┘     └──────────────┘     └─────────────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │  eTMF Export    │
                                         │  (CSV/PDF)      │
                                         └─────────────────┘
```

### Key Integrations

| System | Integration Type | Purpose |
|--------|------------------|---------|
| CTMS | API (read) | Sync trial list, receive DB lock trigger |
| eTMF | File export | Deliver system inventory at database lock |
| Azure AD | OAuth2/OIDC | User authentication and role management |

---

## 4. Data Model

### Core Entities

```
vendors (platform vendors and service providers)
    │
    ├──▶ system_instances (the catalog of systems)
    │         │
    │         └──▶ trial_system_links (many-to-many with trials)
    │                    │
    │                    └──▶ link_snapshots (point-in-time captures)
    │
trials (from CTMS)
    │
    └──▶ confirmations (6-month periodic + DB lock)
```

### Entity Details

#### vendors
| Field | Type | Description |
|-------|------|-------------|
| vendor_id | UUID | Primary key |
| vendor_code | VARCHAR(50) | Unique code (e.g., ICON_CRO) |
| vendor_name | VARCHAR(200) | Display name |
| vendor_type | ENUM | CRO, FSP, TECH_VENDOR, CENTRAL_LAB, etc. |

#### system_instances
| Field | Type | Description |
|-------|------|-------------|
| instance_id | UUID | Primary key |
| instance_code | VARCHAR(100) | Vendor-assigned unique code |
| platform_vendor_id | UUID | FK to vendors (who makes it) |
| service_provider_id | UUID | FK to vendors (who runs it) |
| category_code | VARCHAR(20) | EDC, IRT, eCOA, etc. |
| platform_name | VARCHAR(200) | e.g., "Medidata Rave EDC" |
| platform_version | VARCHAR(50) | e.g., "2024.1.3" |
| validation_status_code | VARCHAR(20) | VALIDATED, VAL_EXPIRED, etc. |
| validation_date | DATE | When validated |
| validation_expiry | DATE | When re-validation due |
| data_hosting_region | VARCHAR(20) | EU, US, CHINA, etc. |
| hosting_model | VARCHAR(20) | SAAS, ON_PREM, etc. |

#### trials
| Field | Type | Description |
|-------|------|-------------|
| trial_id | UUID | Primary key |
| protocol_number | VARCHAR(50) | e.g., "NN1250-1839" |
| trial_title | VARCHAR(500) | Full title |
| trial_status | ENUM | PLANNED, ACTIVE, DB_LOCKED, CLOSED |
| trial_lead_email | VARCHAR(200) | Responsible person |
| next_confirmation_due | DATE | When 6-month confirmation needed |

#### trial_system_links
| Field | Type | Description |
|-------|------|-------------|
| link_id | UUID | Primary key |
| trial_id | UUID | FK to trials |
| instance_id | UUID | FK to system_instances |
| criticality_code | VARCHAR(10) | CRIT, MAJ, STD |
| assignment_status | ENUM | ACTIVE, CONFIRMED, REPLACED, LOCKED |
| usage_start_date | DATE | When system started being used |

#### confirmations
| Field | Type | Description |
|-------|------|-------------|
| confirmation_id | UUID | Primary key |
| trial_id | UUID | FK to trials |
| confirmation_type | ENUM | PERIODIC, DB_LOCK |
| confirmed_date | DATE | When confirmed |
| confirmed_by | VARCHAR(200) | User who confirmed |
| systems_count | INTEGER | Number of systems at confirmation |

---

## 5. System Categories

The full list of system categories vendors can report:

| Code | Name | Default Criticality |
|------|------|---------------------|
| EDC | Electronic Data Capture | CRIT |
| eCOA | Electronic Clinical Outcome Assessment | CRIT |
| eDIARY | Electronic Patient Diary | CRIT |
| eSOURCE | eSource / Direct Data Capture | CRIT |
| IRT | Interactive Response Technology | CRIT |
| CTMS | Clinical Trial Management System | MAJ |
| TMF | Trial Master File | MAJ |
| SITE | Site Management / Feasibility | STD |
| SAFETY | Safety Database / Pharmacovigilance | CRIT |
| SAE_REPORT | SAE Collection & Reporting | CRIT |
| LAB | Central Laboratory LIMS | CRIT |
| BIOBANK | Biomarker / Sample Management | MAJ |
| ECG | Central ECG Processing | CRIT |
| IMG | Medical Imaging / Central Read | CRIT |
| PK | Pharmacokinetic Data Management | MAJ |
| CODING | Medical Coding (MedDRA, WHODrug) | MAJ |
| STAT | Statistical Analysis Environment | MAJ |
| SUB | Regulatory Submissions (eCTD) | STD |
| TELE | Telemedicine / Virtual Visits | MAJ |
| eCONSENT | Electronic Informed Consent | CRIT |
| DHT | Digital Health Technology / Wearables | MAJ |
| RPM | Remote Patient Monitoring | MAJ |
| DTP | Direct-to-Patient Portal | MAJ |
| IDMC | Data Monitoring Committee Platform | MAJ |
| ADJUD | Endpoint Adjudication System | MAJ |
| TRAIN | Training Management | STD |
| ARCHIVE | Long-term Data Archive | STD |
| INTEG | Integration Platform | STD |
| OTHER | Other | STD |

---

## 6. Core Workflows

### Workflow 1: Vendor Upload Processing

```
1. Vendor uploads JSON file to Azure Blob Storage (via SAS token)
2. Blob trigger fires Azure Function
3. Function validates JSON against schema (v1.1)
4. For each system_instance in upload:
   - If instance_code exists → UPDATE
   - If instance_code is new → INSERT
5. If supported_studies provided → validate against CTMS trial list
6. Log results to upload_log table
7. Notify admin on errors
```

### Workflow 2: Trial System Linking

```
1. Trial Lead opens trial in UI
2. Clicks "Add System"
3. Browses/searches system catalog (filters by category, vendor, etc.)
4. Selects system instance
5. Sets criticality (default from category or override with reason)
6. Sets usage start date
7. System link created with ACTIVE status
```

### Workflow 3: 6-Month Confirmation

```
1. Scheduler identifies trials due for confirmation (next_confirmation_due)
2. Sends reminder emails at 14 days, 7 days, and overdue
3. Trial Lead opens confirmation screen
4. Sees all linked systems with changes highlighted
5. Reviews each system (can expand for details)
6. Checks attestation: "I confirm these systems are complete and accurate"
7. Adds optional notes
8. Submits confirmation
9. System creates:
   - confirmation record
   - link_snapshot for each system (captures state at confirmation)
10. Updates trial.next_confirmation_due to +6 months
```

### Workflow 4: Database Lock Export

```
1. CTMS triggers DB lock (API call or manual in CTSR)
2. Trial status updated to DB_LOCKED
3. All system links locked (no further changes)
4. Trial Lead clicks "Generate Export"
5. System generates:
   - CSV file with all system inventory data
   - PDF report with executive summary and attestation
6. Files uploaded to Blob Storage
7. Download links provided (SAS tokens, 24-hour expiry)
8. Files archived for eTMF filing
```

---

## 7. User Roles

| Role | Permissions |
|------|-------------|
| CTSR_VIEWER | Read-only access to all trials and systems |
| CTSR_TRIAL_LEAD | Link/unlink systems, confirm, export for assigned trials |
| CTSR_ADMIN | Full access: manage vendors, view uploads, all trials |

---

## 8. API Endpoints (24 total)

| Tag | Endpoints | Purpose |
|-----|-----------|---------|
| Health | 1 | GET /health |
| Lookups | 1 | GET /lookups (all reference data) |
| Vendors | 4 | CRUD for vendors |
| Systems | 4 | CRUD for system_instances |
| Trials | 2 | List and detail |
| Trial Systems | 4 | Link, unlink, update, list |
| Confirmations | 3 | List, create, get detail |
| Exports | 2 | Create and download |
| Admin | 3 | Dashboard, upload list, upload detail |

---

## 9. Vendor Upload JSON Schema (v1.1)

### Required Fields

```json
{
  "schema_version": "1.1",
  "vendor_code": "ICON_CRO",
  "upload_timestamp": "2024-12-08T14:30:00Z",
  "system_instances": [...]
}
```

### Required Fields per System Instance

- instance_code
- platform_name
- platform_version
- system_category
- validation_status
- hosting_model
- data_hosting_region (NEW in v1.1)

### Key Optional Fields

- supported_studies (array of protocol IDs)
- interfaces (structured: system_name, direction, data_type)
- validation_evidence_link (URI)
- validation_date / validation_expiry
- part11_compliant, annex11_compliant, soc2_certified, iso27001_certified

See `schemas/ctsr_vendor_upload_schema_v1.1.json` for full specification.

---

## 10. UI Screens (Streamlit)

### Dashboard (Home)
- Total systems count, by category, by validation status
- Alerts: validation expiring, confirmations due
- Recent activity feed

### System Catalog
- Searchable, filterable table
- Columns: Instance Code, Platform, Version, Category, Vendor, Validation Status, Hosting Region
- Click row → System Detail

### System Detail
- All system attributes
- Interfaces list
- Linked trials
- Change history (audit log)

### Trial List
- Filterable by status, therapeutic area
- Shows confirmation status (due date, overdue flag)
- Click row → Trial Detail

### Trial Detail
- Trial info header
- Linked systems table with criticality
- Confirmation history
- Actions: Add System, Confirm Systems, Generate Export

### Confirmation Screen
- List of linked systems with change indicators
- Expand/collapse for details
- Attestation checkbox
- Notes field
- Submit button

### Admin: Upload Monitor
- Table of recent uploads
- Status, vendor, timestamp, records processed
- Click row → processing details and errors

---

## 11. Development Guidelines

### Python Style
- Python 3.12+
- Use UV for environment management
- Type hints everywhere
- Pydantic for data validation
- async/await for API endpoints

### Design Principles
1. Don't overengineer - simple beats complex
2. No fallbacks - one correct path
3. Fail fast - throw errors when preconditions aren't met
4. Separation of concerns - single responsibility per function

### Database
- PostgreSQL 15+
- UUID primary keys
- Audit triggers for system_instances
- JSONB for flexible storage (raw uploads, snapshots)

### API
- FastAPI with OpenAPI documentation
- Bearer token authentication (Azure AD JWT)
- Consistent error responses
- Pagination on all list endpoints

---

## 12. File Structure (Recommended)

```
ctsr/
├── api/
│   ├── main.py              # FastAPI app
│   ├── routers/
│   │   ├── health.py
│   │   ├── lookups.py
│   │   ├── vendors.py
│   │   ├── systems.py
│   │   ├── trials.py
│   │   ├── confirmations.py
│   │   ├── exports.py
│   │   └── admin.py
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic
│   └── db/                  # Database access
├── functions/
│   ├── process_upload/      # Blob trigger function
│   └── send_reminders/      # Timer trigger function
├── ui/
│   ├── app.py               # Streamlit main
│   └── pages/
│       ├── dashboard.py
│       ├── systems.py
│       ├── trials.py
│       └── admin.py
├── schemas/
│   └── ctsr_vendor_upload_schema_v1.1.json
├── database/
│   └── schema.sql
├── terraform/
│   └── main.tf
└── tests/
```

---

## 13. Quick Reference

### Validation Status Codes
| Code | Name | Requires Attention |
|------|------|-------------------|
| VALIDATED | Validated | No |
| VAL_PLANNED | Validation Planned | No |
| VAL_IN_PROGRESS | Validation In Progress | No |
| VAL_EXPIRED | Validation Expired | Yes |
| NOT_VALIDATED | Not Validated | Yes |
| DECOMMISSIONED | Decommissioned | No |

### Hosting Models
| Code | Description |
|------|-------------|
| SAAS | SaaS Multi-tenant |
| SAAS_ST | SaaS Single-tenant |
| PAAS | Platform as a Service |
| IAAS | Infrastructure as a Service |
| ON_PREM | On-premise |
| HYBRID | Hybrid deployment |

### Data Hosting Regions
| Code | Description |
|------|-------------|
| EU | European Union |
| US | United States |
| UK | United Kingdom |
| CHINA | China |
| APAC_OTHER | Asia-Pacific (other) |
| GLOBAL_DISTRIBUTED | Globally distributed |

### Trial Statuses
| Status | Description |
|--------|-------------|
| PLANNED | Trial planned, not yet active |
| ACTIVE | Trial is running |
| DB_LOCKED | Database locked, no changes |
| CLOSED | Trial closed and archived |

---

*Last updated: January 2026*
*Schema version: 1.1*
