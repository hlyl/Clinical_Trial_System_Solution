# CTSR API - Backend Implementation

FastAPI backend for the Clinical Trial Systems Register (CTSR).

## Status: All 6 Phases Complete ✅

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

**Phase 3 - Systems CRUD:**
- ✅ System instance endpoints (list, create, get detail, update)
- ✅ Filtering and search by category, validation status, hosting region, vendor
- ✅ System detail returns linked trials and audit history
- ✅ Audit trail persisted on create/update
- ✅ JSONB support for interfaces and metadata

**Phase 4 - Trials + Trial Systems:**
- ✅ Trial management endpoints (list, create, get detail, update)
- ✅ System linking workflow (link, update link, unlink)
- ✅ Criticality assignment and override
- ✅ Trial detail with linked systems and metadata
- ✅ Complex filtering (protocol, status, phase, lead, search)

**Phase 5 - Confirmations + Exports:**
- ✅ Confirmation management (list, create, update)
- ✅ Confirmation submission with snapshot capture
- ✅ Point-in-time system state preservation
- ✅ Export generation (PDF/EXCEL simulation)
- ✅ Overdue detection and filtering
- ✅ Business rules (no updates after completion)

**Phase 6 - Admin Dashboard:**
- ✅ Comprehensive dashboard statistics endpoint
- ✅ Trial, system, confirmation aggregations
- ✅ Recent activities tracking
- ✅ Validation alerts placeholder
- ✅ Real-time metrics from database

**Total: 24 Endpoints Implemented**

**Endpoints Working:**
- `GET /` - API info
- `GET /health` - Health check (no auth)
- `GET /api/v1/lookups` - Reference data (no auth)

**Vendors (Phase 2):**
- `GET /api/v1/vendors` - List vendors (VIEWER)
- `POST /api/v1/vendors` - Create vendor (ADMIN)
- `GET /api/v1/vendors/{id}` - Get vendor (VIEWER)
- `PUT /api/v1/vendors/{id}` - Update vendor (ADMIN)

**Systems (Phase 3):**
- `GET /api/v1/systems` - List systems with filters/search (VIEWER)
- `POST /api/v1/systems` - Create system (ADMIN)
- `GET /api/v1/systems/{id}` - Get system detail with trials & audit (VIEWER)
- `PUT /api/v1/systems/{id}` - Update system (ADMIN)

**Trials (Phase 4):**
- `GET /api/v1/trials` - List trials with filters (VIEWER)
- `POST /api/v1/trials` - Create trial (TRIAL_LEAD)
- `GET /api/v1/trials/{id}` - Get trial detail with linked systems (VIEWER)
- `PUT /api/v1/trials/{id}` - Update trial (TRIAL_LEAD)
- `POST /api/v1/trials/{id}/systems` - Link system to trial (TRIAL_LEAD)
- `PUT /api/v1/trials/{trial_id}/systems/{link_id}` - Update link (TRIAL_LEAD)
- `DELETE /api/v1/trials/{trial_id}/systems/{link_id}` - Unlink system (TRIAL_LEAD)

**Confirmations (Phase 5):**
- `GET /api/v1/confirmations` - List confirmations with filters (VIEWER)
- `POST /api/v1/confirmations` - Create confirmation (TRIAL_LEAD)
- `GET /api/v1/confirmations/{id}` - Get confirmation detail with snapshots (VIEWER)
- `PUT /api/v1/confirmations/{id}` - Update confirmation (TRIAL_LEAD)
- `POST /api/v1/confirmations/{id}/submit` - Submit confirmation (TRIAL_LEAD)
- `POST /api/v1/confirmations/exports` - Generate eTMF export (TRIAL_LEAD)

**Admin (Phase 6):**
- `GET /api/v1/admin/dashboard` - Dashboard statistics (ADMIN)

**Documentation:**
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

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
│   ├── main.py              # FastAPI app with all routers
│   ├── config.py            # Settings management
│   ├── exceptions.py        # Custom exceptions
│   ├── auth.py              # Authentication & authorization
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py          # SQLAlchemy base
│   │   ├── database.py      # Connection & sessions
│   │   └── models.py        # ORM models (11 tables)
│   ├── models/              # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── lookups.py       # Reference data schemas
│   │   ├── vendors.py       # Vendor CRUD schemas
│   │   ├── systems.py       # System CRUD schemas
│   │   ├── trials.py        # Trial & linking schemas
│   │   ├── confirmations.py # Confirmation & export schemas
│   │   └── admin.py         # Dashboard statistics schemas
│   ├── routers/             # API endpoints
│   │   ├── __init__.py
│   │   ├── health.py        # Health check
│   │   ├── lookups.py       # Reference data
│   │   ├── vendors.py       # Vendor management (4 endpoints)
│   │   ├── systems.py       # System management (4 endpoints)
│   │   ├── trials.py        # Trial management (7 endpoints)
│   │   ├── confirmations.py # Confirmations (6 endpoints)
│   │   └── admin.py         # Admin dashboard (1 endpoint)
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── lookups.py       # Lookup service
│   │   ├── vendors.py       # Vendor service
│   │   ├── systems.py       # System service with audit
│   │   ├── trials.py        # Trial & linking service
│   │   ├── confirmations.py # Confirmation & export service
│   │   └── admin.py         # Dashboard aggregation service
│   └── utils/               # Utilities
│       ├── __init__.py
│       └── pagination.py    # Pagination helpers
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
- `SystemInstance` - System catalog (with audit trail)
- `Trial` - Clinical trials (synced from CTMS)
- `TrialSystemLink` - Trial-system relationships with criticality
- `Confirmation` - Periodic and DB lock confirmations
- `LinkSnapshot` - Point-in-time system state captures
- `UploadLog` - Vendor upload processing history
- `SystemInstanceAudit` - Complete audit trail for systems

## Completed Features

✅ **Authentication & Authorization**
- Azure AD JWT validation (disabled in local dev)
- Role-based access control (VIEWER, TRIAL_LEAD, ADMIN)
- Dependency injection for auth checks

✅ **Vendor Management**
- Full CRUD operations
- Conflict detection (duplicate names)
- Soft delete support

✅ **System Management**
- Full CRUD with filtering & search
- Audit trail on every change
- JSONB support for flexible interfaces/metadata
- Linked trials in detail view

✅ **Trial Management**
- Trial CRUD operations
- System linking workflow
- Criticality assignment with override reasons
- Trial detail shows all linked systems

✅ **Confirmation Workflow**
- Periodic (6-month) and DB lock confirmations
- Point-in-time snapshot capture
- Status tracking (PENDING → COMPLETED)
- Overdue detection
- Export generation (PDF/EXCEL simulation)

✅ **Admin Dashboard**
- Real-time statistics aggregation
- Trial, system, confirmation metrics
- Recent activity tracking
- Systems by criticality breakdown

✅ **Infrastructure**
- Async/await throughout
- Service layer pattern
- Pagination support
- Comprehensive error handling
- API documentation (Swagger + ReDoc)

## Remaining Work

🚧 **Backend:**
- Unit tests and integration tests
- Azure Functions for vendor uploads
- Reminder scheduler function

🚧 **Frontend:**
- Streamlit UI implementation
- All CRUD screens
- Dashboard visualizations

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
