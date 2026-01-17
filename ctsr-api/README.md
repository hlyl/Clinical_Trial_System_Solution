# CTSR API - Backend Implementation

FastAPI backend for the Clinical Trial Systems Register (CTSR).

## Status: Phase 2 Complete ✅

**Phase 1 - Foundation:**
- ✅ Project structure with UV
- ✅ Configuration management (Pydantic Settings)
- ✅ SQLAlchemy async database layer
- ✅ Core FastAPI app with CORS and error handling
- ✅ Health endpoint (`GET /health`)
- ✅ Lookups endpoint (`GET /api/v1/lookups`)
- ✅ All ORM models for database tables

**Phase 2 - Vendors CRUD:**
- ✅ Authentication framework (Azure AD JWT + local dev bypass)
- ✅ Role-based authorization (VIEWER, TRIAL_LEAD, ADMIN)
- ✅ Vendor endpoints (4 endpoints)
- ✅ Pagination helpers
- ✅ Error handling (404, 409, 422)
- ✅ Service layer pattern

**Endpoints Working:**
- `GET /` - API info
- `GET /health` - Health check (no auth)
- `GET /api/v1/lookups` - Reference data (no auth)
- `GET /api/v1/vendors` - List vendors (requires VIEWER role)
- `POST /api/v1/vendors` - Create vendor (requires ADMIN role)
- `GET /api/v1/vendors/{id}` - Get vendor (requires VIEWER role)
- `PUT /api/v1/vendors/{id}` - Update vendor (requires ADMIN role)
- `GET /docs` - Interactive API documentation

## Quick Start

### Prerequisites
- Python 3.12+
- UV package manager
- PostgreSQL database running (see root docker-compose.yml)

### Installation

```bash
cd ctsr-api

# Install dependencies (automatic with uv run)
uv sync

# Start the development server
uv run uvicorn api.main:app --reload --port 8001
```

### Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ctsr
POSTGRES_USER=ctsr_user
POSTGRES_PASSWORD=ctsr_dev_password

# API
API_HOST=0.0.0.0
API_PORT=8001
API_DEBUG=true

# Authentication (disabled for local dev)
AZURE_AD_ENABLED=false
```

### Testing Endpoints

```bash
# Health check
curl http://localhost:8001/health

# Lookups (reference data)
curl http://localhost:8001/api/v1/lookups

# Interactive docs
open http://localhost:8001/docs
```

## Project Structure

```
ctsr-api/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings management
│   ├── exceptions.py        # Custom exceptions
│   ├── auth.py              # Authentication & authorization
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py          # SQLAlchemy base
│   │   ├── database.py      # Connection & sessions
│   │   └── models.py        # ORM models
│   ├── models/              # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── lookups.py
│   │   └── vendors.py
│   ├── routers/             # API endpoints
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── lookups.py
│   │   └── vendors.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── lookups.py
│   │   └── vendors.py
│   └── utils/               # Utilities
│       ├── __init__.py
│       └── pagination.py
├── tests/                   # Test suite (TODO)
├── .env                     # Environment config
├── .env.example             # Example config
├── pyproject.toml           # UV project file
└── README.md               # This file
```

## Database Models

All database tables have corresponding SQLAlchemy ORM models:

**Lookup Tables:**
- `SystemCategory` - System category codes
- `ValidationStatus` - Validation status codes
- `Criticality` - Criticality level codes

**Core Tables:**
- `Vendor` - Platform vendors and service providers
- `SystemInstance` - System catalog
- `Trial` - Clinical trials
- `TrialSystemLink` - Trial-system relationships
- `Confirmation` - Periodic confirmations
- `LinkSnapshot` - Point-in-time captures
- `UploadLog` - Vendor upload processing
- `SystemInstanceAudit` - Audit trail

## Next Phases

**Phase 3: Systems CRUD** (Ready to implement)
- System instance management endpoints (4 endpoints)
- Search and filtering by category, vendor, validation status
- Audit trail integration
- System detail with linked trials and change history

**Phase 4: Trials & Trial Systems**
- Trial management endpoints
- System linking workflow
- Criticality assignment and override
- Trial detail with linked systems

**Phase 5: Confirmations & Exports**
- 6-month periodic confirmations
- DB lock confirmations
- eTMF export generation

**Phase 6: Admin Endpoints**
- Dashboard statistics
- Upload monitoring
- System administration

## Development Guidelines

- **Type hints everywhere** - All functions have type annotations
- **Async/await** - All endpoints use async
- **Fail fast** - Raise exceptions for invalid state
- **Single responsibility** - Each function has one clear purpose
- **No overengineering** - Simple solutions preferred

## Technology Stack

- **FastAPI** - Modern async web framework
- **SQLAlchemy 2.0** - ORM with async support
- **asyncpg** - Async PostgreSQL driver
- **Pydantic v2** - Data validation
- **Uvicorn** - ASGI server

## Documentation

- API Docs: http://localhost:8001/docs (Swagger UI)
- ReDoc: http://localhost:8001/redoc
- OpenAPI Spec: See `../ctsr-package/api/openapi.yaml`

## License

Internal Novo Nordisk project.
