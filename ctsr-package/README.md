# CTSR - Clinical Trial Systems Register

## Package Contents

This package contains all essential artifacts for developing the Clinical Trial Systems Register (CTSR).

```
ctsr-package/
├── context.md                              # Complete background documentation
├── README.md                               # This file
├── api/
│   └── openapi.yaml                        # OpenAPI 3.1 specification (24 endpoints)
├── database/
│   └── schema.sql                          # PostgreSQL DDL + seed data + audit triggers
├── schemas/
│   ├── ctsr_vendor_upload_schema_v1.1.json # JSON Schema for vendor uploads
│   └── sample_upload_ICON_CRO.json         # Example vendor upload file
├── docs/
│   └── (architecture diagrams if needed)
└── terraform/
    └── (infrastructure as code if needed)
```

## Quick Start

### 1. Read the Context
Start with `context.md` - it contains everything you need to know about:
- Business purpose and regulatory requirements
- Data model and entity relationships
- Core workflows (vendor upload, trial linking, confirmations)
- API endpoints and UI screens

### 2. Set Up Database
```bash
# Create PostgreSQL database
createdb ctsr

# Run schema
psql -d ctsr -f database/schema.sql
```

### 3. Start API Development
```bash
# Create project with UV
uv init ctsr-api
cd ctsr-api
uv add fastapi uvicorn sqlalchemy asyncpg pydantic

# Use openapi.yaml as your contract
```

### 4. Start Streamlit UI
```bash
uv init ctsr-ui
cd ctsr-ui
uv add streamlit httpx pandas

# Create pages per context.md UI section
```

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Database | PostgreSQL | Simpler than Databricks, JSONB for flexibility |
| API | FastAPI | Modern, async, auto-docs from OpenAPI |
| Frontend | Streamlit | Fast to build, Python-native, good for internal tools |
| Schema Version | 1.1 | Adds data_hosting_region, structured interfaces |

## Schema Version 1.1 Changes

New required field: `data_hosting_region` (EU, US, CHINA, APAC_OTHER, UK, GLOBAL_DISTRIBUTED)

New optional fields:
- `supported_studies` - Array of protocol IDs for impact analysis
- `interfaces` - Structured objects with system_name, direction, data_type
- `validation_evidence_link` - URI to validation documentation

## Development Guidelines

- Python 3.12+ with UV for environment management
- Type hints everywhere
- Pydantic for validation
- Fail fast - throw errors, don't hide them
- Single responsibility per function

## Regulatory Alignment

- ICH E6(R3) Section 3.16.1(x) - Sponsor system documentation
- FDA CSA Guidance - Risk-based validation
- EU Annex 11 - Computerized systems
- 21 CFR Part 11 - Electronic records

---

*Last updated: January 2026*
