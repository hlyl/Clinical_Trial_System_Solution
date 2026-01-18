# Clinical Trial Systems Register (CTSR)

Regulatory compliance solution for documenting IT systems used in clinical trials per ICH E6(R3) requirements.

## Project Status: ✅ Core API Complete

**All 24 REST API endpoints implemented:**
- Phase 1: Foundation (2 endpoints) ✅
- Phase 2: Vendors CRUD (4 endpoints) ✅
- Phase 3: Systems CRUD (4 endpoints) ✅
- Phase 4: Trials + Trial Systems (7 endpoints) ✅
- Phase 5: Confirmations + Exports (6 endpoints) ✅
- Phase 6: Admin Dashboard (1 endpoint) ✅

See [`ctsr-api/README.md`](./ctsr-api/README.md) for complete API documentation.

## Quick Start

### 1. Start PostgreSQL Database

```bash
# Start the database
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f postgres
```

### 2. Verify Database Setup

```bash
# Connect to database
docker-compose exec postgres psql -U ctsr_user -d ctsr

# Inside psql, verify tables:
\dt ctsr.*

# Exit psql
\q
```

### 3. Stop Database

```bash
# Stop services
docker-compose down

# Stop and remove all data (clean slate)
docker-compose down -v
```

## Database Connection

- **Host**: localhost
- **Port**: 5432
- **Database**: ctsr
- **User**: ctsr_user
- **Password**: ctsr_dev_password
- **Connection String**: `postgresql://ctsr_user:ctsr_dev_password@localhost:5432/ctsr`

## Documentation

See the [ctsr-package](./ctsr-package) folder for complete documentation:
- [context.md](./ctsr-package/context.md) - Complete background and requirements
- [API specification](./ctsr-package/api/openapi.yaml) - OpenAPI 3.1 spec with 24 endpoints
- [Database schema](./ctsr-package/database/schema.sql) - PostgreSQL DDL with audit triggers
- [Upload schema](./ctsr-package/schemas/ctsr_vendor_upload_schema_v1.1.json) - JSON Schema for vendor uploads

## Architecture

**Backend API (ctsr-api/):** FastAPI REST API with 24 endpoints - ✅ COMPLETE
- Authentication: Azure AD JWT (local dev bypass mode)
- Database: PostgreSQL with async SQLAlchemy ORM
- Endpoints: Health, Lookups, Vendors, Systems, Trials, Confirmations, Admin

**Frontend UI:** Streamlit application - 🚧 TODO

**Azure Functions:** Serverless processors - 🚧 TODO
- Vendor upload processor
- Reminder scheduler

## Next Steps

1. ✅ ~~Implement FastAPI backend~~ **COMPLETE**
2. 🚧 Implement Streamlit UI
3. 🚧 Implement Azure Functions for upload processing
