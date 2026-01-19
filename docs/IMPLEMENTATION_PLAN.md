# CTSR Implementation Plan & Status

**Last Updated:** January 18, 2026
**Current Status:** Backend API + Streamlit UI complete; CI green ✅

---

## 📊 Project Status Overview

### ✅ COMPLETED: Backend API (ctsr-api/) and Streamlit UI

**Backend Completion (6 phases):**
- **Phase 1:** Foundation - Health check, Lookups
- **Phase 2:** Vendors CRUD - List/Create/Get/Update
- **Phase 3:** Systems CRUD - List/Create/Get/Update (with audit trail)
- **Phase 4:** Trials + Trial Systems - Trial CRUD + Link/Unlink systems
- **Phase 5:** Confirmations + Exports - Confirmation workflow + eTMF exports
- **Phase 6:** Admin Dashboard - Aggregated statistics

**Streamlit UI Completion:**
- Native Streamlit styling (custom CSS removed per request)
- Trial-system linking fixed (body payload + criticality codes CRIT/MAJ/STD)
- Duplicate link prevention with user messaging
- Vendor dropdown filter between trial and system selection
- Linked systems table shows vendor, criticality, status

**Technology Stack (current):**
- FastAPI 0.128.0 (async REST API)
- SQLAlchemy 2.0.45 (async ORM)
- asyncpg 0.31.0 (PostgreSQL driver)
- Pydantic 2.7.4 + pydantic-settings 2.3.0 (pinned for compatibility)
- Python 3.11 (single version in CI)
- Pip workflows (no pandas; lean deps)

**Database:**
- PostgreSQL 15-alpine
- Schema: `ctsr` with seeded lookup tables (system categories, validation statuses, criticality)
- 11 tables with audit triggers

**Authentication:**
- Azure AD JWT support (disabled for local dev)
- Role-based access: VIEWER, TRIAL_LEAD, ADMIN
- Local dev bypass mode active

**CI/CD & Testing:**
- GitHub Actions pipelines green (backend, frontend, integration)
- Integration workflow seeds lookup tables and uses DATABASE_URL/TEST_DATABASE_URL
- Pre-commit: black, isort, flake8; Python 3.11 only

### 🚧 TODO: Next Implementation Phases

1. **Optional**: Production deployment hardening (monitoring, TLS, secrets management)
2. **Optional**: Add Excel export (if reintroducing lightweight dependency) — currently CSV/JSON only
3. **Optional**: Azure Functions integration (if needed by roadmap)

---

## 🔧 Environment Setup

### Prerequisites on New Machine

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Docker & Docker Compose
# (Follow official Docker docs for your OS)

# Install PostgreSQL client tools (for psql)
sudo apt-get install postgresql-client  # Ubuntu/Debian
brew install postgresql                 # macOS
```

### Clone & Setup

```bash
# Clone repository
git clone https://github.com/hlyl/Clinical_Trial_System_Solution.git
cd Clinical_Trial_System_Solution

# Start PostgreSQL database
docker-compose up -d

# Verify database is running
docker-compose ps
docker-compose logs -f postgres

# Verify tables are created
docker-compose exec postgres psql -U ctsr_user -d ctsr -c "\dt ctsr.*"
```

### Backend API Setup

```bash
cd ctsr-api

# Install dependencies (UV handles automatically)
uv sync

# Verify environment
uv run python --version  # Should be 3.13.7

# Start development server
uv run uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload

# In another terminal, test API
curl http://localhost:8001/health
curl http://localhost:8001/api/v1/lookups
```

### Environment Variables

File: `ctsr-api/.env`
```env
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
AZURE_AD_TENANT_ID=
AZURE_AD_CLIENT_ID=
AZURE_AD_AUDIENCE=

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8501

# Logging
LOG_LEVEL=INFO
```

---

## 🧪 Testing Current Implementation

### Test All Endpoints

```bash
# Health & Lookups (no auth)
curl http://localhost:8001/health | jq .
curl http://localhost:8001/api/v1/lookups | jq .

# Vendors
curl http://localhost:8001/api/v1/vendors | jq .
curl http://localhost:8001/api/v1/vendors/<vendor-id> | jq .

# Systems
curl "http://localhost:8001/api/v1/systems?limit=10" | jq .
curl http://localhost:8001/api/v1/systems/<system-id> | jq .

# Trials
curl "http://localhost:8001/api/v1/trials?limit=10" | jq .
curl http://localhost:8001/api/v1/trials/<trial-id> | jq .

# Confirmations
curl "http://localhost:8001/api/v1/confirmations?limit=10" | jq .
curl http://localhost:8001/api/v1/confirmations/<confirmation-id> | jq .

# Admin Dashboard
curl http://localhost:8001/api/v1/admin/dashboard | jq .
```

### Sample Test Data IDs

From existing seed data (check database for current IDs):
```sql
-- In psql:
SELECT trial_id, protocol_number FROM ctsr.trials;
SELECT instance_id, instance_code FROM ctsr.system_instances;
SELECT vendor_id, vendor_name FROM ctsr.vendors;
SELECT confirmation_id, confirmation_type FROM ctsr.confirmations;
```

### API Documentation

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- OpenAPI Spec: `ctsr-package/api/openapi.yaml`

---

## 📁 Project Structure

```
Clinical_Trial_System_Solution/
├── docker-compose.yml          # PostgreSQL database
├── README.md                   # Project overview
├── IMPLEMENTATION_PLAN.md      # This file
│
├── ctsr-package/              # Documentation & specs
│   ├── context.md             # Complete requirements
│   ├── README.md
│   ├── api/
│   │   └── openapi.yaml       # API specification
│   ├── database/
│   │   └── schema.sql         # PostgreSQL DDL + seed data
│   └── schemas/
│       └── ctsr_vendor_upload_schema_v1.1.json
│
└── ctsr-api/                  # ✅ COMPLETE - Backend API
    ├── README.md              # API documentation
    ├── pyproject.toml         # UV dependencies
    ├── .env                   # Environment config
    └── api/
        ├── main.py            # FastAPI app
        ├── config.py          # Settings
        ├── auth.py            # Authentication
        ├── exceptions.py      # Custom exceptions
        ├── db/
        │   ├── base.py
        │   ├── database.py    # DB connection
        │   └── models.py      # SQLAlchemy ORM (11 tables)
        ├── models/            # Pydantic schemas
        │   ├── lookups.py
        │   ├── vendors.py
        │   ├── systems.py
        │   ├── trials.py
        │   ├── confirmations.py
        │   └── admin.py
        ├── routers/           # API endpoints
        │   ├── health.py
        │   ├── lookups.py
        │   ├── vendors.py
        │   ├── systems.py
        │   ├── trials.py
        │   ├── confirmations.py
        │   └── admin.py
        ├── services/          # Business logic
        │   ├── lookups.py
        │   ├── vendors.py
        │   ├── systems.py
        │   ├── trials.py
        │   ├── confirmations.py
        │   └── admin.py
        └── utils/
            └── pagination.py
```

---

## 🎯 Next Phase: Streamlit UI

### Implementation Plan

**Phase 1: Project Setup**
```bash
# Create UI directory
mkdir ctsr-ui
cd ctsr-ui

# Initialize with UV
uv init
uv add streamlit requests python-dotenv pandas

# Create basic structure
mkdir pages components
touch Home.py config.py
touch components/auth.py components/api_client.py
```

**Phase 2: Core Pages**

1. **Home.py** - Landing page with navigation
2. **pages/1_📊_Dashboard.py** - Dashboard with stats from `/api/v1/admin/dashboard`
3. **pages/2_🖥️_System_Catalog.py** - Browse systems from `/api/v1/systems`
4. **pages/3_🔬_My_Trials.py** - Trial management from `/api/v1/trials`
5. **pages/4_✅_Confirmations.py** - Confirmation workflow from `/api/v1/confirmations`
6. **pages/5_📄_Exports.py** - Export generation
7. **pages/6_⚙️_Admin.py** - Admin features (vendors, system admin)

**Phase 3: Components**

```python
# components/api_client.py
import requests
from typing import Optional, Dict, Any

class CTSRClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: Dict) -> Any:
        response = requests.post(f"{self.base_url}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()

    # Add put, delete methods...
```

**Phase 4: Key Features**

- **Search & Filter** - All list pages need filtering UI
- **CRUD Forms** - Create/Update forms with validation
- **Data Tables** - Paginated tables with sorting
- **Role-Based Views** - Show/hide features based on user role
- **Notifications** - Success/error messages using st.toast()
- **File Upload** - For vendor uploads (future)

### UI Development Tips

```python
# Streamlit session state for API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = CTSRClient()

# Pagination pattern
page = st.number_input("Page", min_value=1, value=1)
limit = st.selectbox("Items per page", [10, 25, 50, 100])
offset = (page - 1) * limit

response = api_client.get("/api/v1/systems",
                          params={"limit": limit, "offset": offset})

# Display data
for item in response['data']:
    st.write(item)

# Show pagination info
st.caption(f"Showing {offset+1}-{offset+len(response['data'])} of {response['meta']['total']}")
```

---

## 🧪 Testing Phase: Test Infrastructure

### Unit Tests Structure

```bash
cd ctsr-api
mkdir -p tests/{unit,integration,fixtures}

# Install test dependencies
uv add --dev pytest pytest-asyncio pytest-cov httpx
```

**Test Files:**
```
tests/
├── conftest.py                 # Pytest fixtures
├── fixtures/
│   ├── sample_vendor.json
│   ├── sample_system.json
│   └── sample_trial.json
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_validators.py
└── integration/
    ├── test_vendors_api.py
    ├── test_systems_api.py
    ├── test_trials_api.py
    ├── test_confirmations_api.py
    └── test_admin_api.py
```

**Sample Test:**
```python
# tests/integration/test_vendors_api.py
import pytest
from httpx import AsyncClient
from api.main import app

@pytest.mark.asyncio
async def test_list_vendors():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/vendors")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
```

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=api --cov-report=html

# Run specific test file
uv run pytest tests/integration/test_vendors_api.py -v

# Run with output
uv run pytest -s
```

---

## ⚡ Azure Functions Phase

### Function App Structure

```bash
# Create functions directory
mkdir ctsr-functions
cd ctsr-functions

# Initialize Azure Functions (requires Azure Functions Core Tools)
func init . --python

# Create functions
func new --name VendorUploadProcessor --template "Blob trigger"
func new --name ReminderScheduler --template "Timer trigger"
```

**Function 1: Vendor Upload Processor**
- **Trigger:** Blob Storage (new JSON files in container)
- **Input:** JSON file matching `ctsr_vendor_upload_schema_v1.1.json`
- **Process:** Parse, validate, upsert systems to database
- **Output:** Update `upload_logs` table

**Function 2: Reminder Scheduler**
- **Trigger:** Timer (daily at 6 AM)
- **Process:** Find trials needing confirmations, create pending confirmations
- **Notification:** Send emails to trial leads

**Function 3: Validation Alert Scanner**
- **Trigger:** Timer (weekly)
- **Process:** Check for expiring validation status, create alerts
- **Notification:** Alert dashboard

---

## 🔑 Key Technical Notes

### Database Field Name Mappings

**Important:** ORM field names differ from logical names:

| Table | Logical Name | ORM Field Name |
|-------|-------------|----------------|
| SystemInstance | system_instance_id | `instance_id` |
| SystemInstance | system_identifier | `instance_code` |
| SystemInstance | system_name | `platform_name` |
| TrialSystemLink | trial_system_id | `link_id` |
| TrialSystemLink | criticality | `criticality_code` |
| Trial | - | No `is_active` field, use `trial_status` |

### Common Queries

```sql
-- Get all active systems
SELECT * FROM ctsr.system_instances WHERE is_active = true;

-- Get trial with linked systems
SELECT t.*, tsl.*, si.*
FROM ctsr.trials t
LEFT JOIN ctsr.trial_system_links tsl ON t.trial_id = tsl.trial_id
LEFT JOIN ctsr.system_instances si ON tsl.instance_id = si.instance_id
WHERE t.trial_id = '<trial-id>';

-- Get pending confirmations
SELECT * FROM ctsr.confirmations
WHERE confirmation_status = 'PENDING'
  AND due_date < CURRENT_DATE;
```

### Error Handling Patterns

All services use:
- `NotFoundError(resource, identifier)` - 404 responses
- `ConflictError(message, details)` - 409 responses
- `ValidationError(message, field, details)` - 422 responses

### Pagination Pattern

All list endpoints return:
```json
{
  "data": [...],
  "meta": {
    "total": 100,
    "limit": 20,
    "offset": 0
  }
}
```

---

## 📚 Reference Documentation

### Key Files to Review

1. **Requirements:** `ctsr-package/context.md` - Full background
2. **API Spec:** `ctsr-package/api/openapi.yaml` - All endpoint details
3. **Database:** `ctsr-package/database/schema.sql` - Schema + seed data
4. **Upload Schema:** `ctsr-package/schemas/ctsr_vendor_upload_schema_v1.1.json`

### Useful Commands

```bash
# Database backup
docker-compose exec postgres pg_dump -U ctsr_user ctsr > backup.sql

# Database restore
docker-compose exec -T postgres psql -U ctsr_user ctsr < backup.sql

# View API logs
uv run uvicorn api.main:app --log-level debug

# Check database connections
docker-compose exec postgres psql -U ctsr_user -d ctsr -c "SELECT * FROM pg_stat_activity WHERE datname='ctsr';"

# Reset database
docker-compose down -v
docker-compose up -d
# Wait for schema to load
```

---

## 🎬 Quick Start on New Machine

**5-Minute Setup:**

```bash
# 1. Clone repo
git clone https://github.com/hlyl/Clinical_Trial_System_Solution.git
cd Clinical_Trial_System_Solution

# 2. Start database
docker-compose up -d

# 3. Start API
cd ctsr-api
uv run uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload

# 4. Test in another terminal
curl http://localhost:8001/health
curl http://localhost:8001/api/v1/admin/dashboard | jq .

# 5. Open docs
# Visit http://localhost:8001/docs
```

**Next Step:** Start building Streamlit UI or write tests!

---

## 📋 Checklist for Continuation


- [ ] Start PostgreSQL with docker-compose
- [ ] Verify database schema loaded
- [ ] Start backend API (port 8001)
- [ ] Test all endpoints working
- [ ] Review this document completely
- [ ] Decide: UI first or Tests first?
- [ ] Create new directory (`ctsr-ui` or `tests/`)
- [ ] Begin implementation!

---

**Good luck with the next phase! All the groundwork is complete.** 🚀
