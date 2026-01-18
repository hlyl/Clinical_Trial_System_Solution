# CTSR Streamlit Frontend

Professional web-based frontend for the Clinical Trial Systems Register (CTSR) built with Streamlit.

## Features

### 📊 Dashboard
- Key performance indicators (KPIs) for vendors, systems, trials, and confirmations
- Interactive charts for status distributions and vendor analysis
- System health and data quality metrics
- Real-time API connectivity status

### 🏭 Vendor Management
- Browse vendors with filtering by type and active status
- Create new vendors with validation
- Edit and manage existing vendors
- Track vendor contact information

### 💻 System Management
- Browse system instances with category and validation status filters
- Create new system instances with version tracking
- Edit system details and validation status
- Support for multiple system categories (EDC, LIMS, LMS, IRT, RTSM)

### 🧪 Trial Management
- View and filter trials by status
- Create new clinical trials with protocol information
- Assign systems to trials with criticality levels
- Track trial lead and organizational information

### ✅ Confirmations
- Browse confirmations with status filtering
- Create new confirmations for infrastructure, regulatory, and data validation
- Review and approve/reject pending confirmations
- Audit trail for confirmation updates

### 📊 Reports & Analytics
- System overview statistics and distributions
- System analysis by category and validation status
- Compliance and data quality reports
- Trial coverage analysis
- Export data in CSV, Excel, or JSON formats

### ⚙️ Settings
- Configure API connection (base URL and user email)
- Manage user preferences and display settings
- Notification preferences
- Session and cache management
- Configuration import/export

## Prerequisites

- Python 3.9+
- pip or conda
- CTSR Backend API running (default: http://localhost:8001)

## Installation

### 1. Clone the repository
```bash
cd Clinical_Trial_System_Solution/streamlit-app
```

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
# OR
poetry install
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your settings
export API_BASE_URL=http://localhost:8001
```

## Running the Application

### Start the Streamlit app
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501` by default.

### Configuration via UI
When you first run the app:
1. Navigate to Settings → API Configuration
2. Enter your API base URL (default: `http://localhost:8001`)
3. Enter your email for audit trail tracking
4. Click "Save API Settings" to verify connectivity

## Project Structure

```
streamlit-app/
├── app.py                      # Main entry point with routing
├── pyproject.toml              # Project configuration and dependencies
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment configuration
│
├── app/
│   ├── __init__.py
│   ├── utils/
│   │   ├── api_client.py      # API communication layer
│   │   └── components.py      # Reusable UI components
│   │
│   └── pages/
│       ├── __init__.py
│       ├── dashboard.py       # KPI dashboard and overview
│       ├── vendors.py         # Vendor CRUD operations
│       ├── systems.py         # System management
│       ├── trials.py          # Trial management
│       ├── confirmations.py   # Confirmation workflows
│       ├── reports.py         # Analytics and exports
│       └── settings.py        # Application configuration
```

## Key Components

### API Client (`app/utils/api_client.py`)
Abstraction layer for all CTSR backend API calls:
- Vendor CRUD operations
- System instance management
- Trial management
- Trial-system linking
- Confirmations handling
- Admin statistics

**Usage:**
```python
from app.utils.api_client import api_client

# Example: List vendors
vendors = api_client.list_vendors(
    vendor_type="CRO",
    is_active=True,
    user_email="user@company.com"
)
```

### UI Components (`app/utils/components.py`)
Reusable Streamlit components:
- `format_date()` - Format dates consistently
- `format_datetime()` - Format datetime stamps
- `status_badge()` - HTML status indicators with colors
- `render_metric_cards()` - Dashboard metrics display
- `render_dataframe_with_actions()` - Tables with action buttons
- `render_form_section()` - Multi-field form builder
- Notification functions (`show_success()`, `show_error()`, etc.)

**Usage:**
```python
from app.utils.components import render_form_section, show_success

data = render_form_section(
    title="Create Item",
    fields=[
        {"name": "item_name", "type": "text", "label": "Item Name"},
        {"name": "category", "type": "select", "label": "Category", "options": ["A", "B"]},
    ]
)

if data:
    show_success("Item created!")
```

## Session State Management

The app uses Streamlit session state for:
- `user_email` - Current user email for audit trail
- `api_base_url` - Backend API URL
- `refresh_trigger` - Counter to trigger page refreshes after CRUD operations

These persist across page navigations and user interactions.

## API Integration

### Health Check
The sidebar automatically checks API connectivity:
```python
health = api_client.get_health()
```

### Error Handling
All API calls include error handling and user feedback:
- Failed requests return `None`
- Error messages are displayed via `show_error()`
- Loading states provide user feedback during requests

### Pagination
List endpoints support pagination:
- `limit` - Records per page (default: 50, max: 1000)
- `offset` - Starting record number for pagination

## User Experience Features

### Intuitive Navigation
- Sidebar with clear navigation links
- Tabbed interfaces for related operations (Browse, Create, Manage)
- Consistent naming and organization

### Data Display
- Responsive DataFrames that adapt to screen size
- Sortable and filterable tables
- Interactive charts (Plotly) for visualization

### Validation & Feedback
- Form validation before submission
- Clear error messages for failed operations
- Success notifications after completed actions
- Loading indicators during API calls

### Performance
- Pagination for large datasets
- Configurable records-per-page
- Session state caching
- Efficient API calls

## Customization

### Adding New Pages
1. Create file in `app/pages/newpage.py`
2. Implement `render()` function
3. Add to routing in `app.py`
4. Add navigation in sidebar

### Styling
Streamlit theming can be customized via:
- `.streamlit/config.toml` (create if needed)
- Settings page in the app UI
- Custom CSS and markdown

### API Endpoints
Update `app/utils/api_client.py` to add new API methods:
```python
def new_endpoint(self, param1: str, user_email: str = "dev@localhost"):
    return self._make_request(
        "GET",
        "/api/v1/new-endpoint",
        user_email=user_email,
        params={"param1": param1}
    )
```

## Troubleshooting

### API Connection Issues
- Verify backend API is running on the configured URL
- Check `API_BASE_URL` in Settings
- Ensure firewall allows access to API port
- Check browser console for network errors

### Data Not Loading
- Verify API connectivity in Settings
- Check user email is set correctly
- Try clearing cache via Settings → Data Management
- Check API logs for errors

### Performance Issues
- Reduce records-per-page in Settings
- Check API response times
- Clear cache if UI is sluggish
- Restart the Streamlit app

### Module Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.9 or higher
- Check PYTHONPATH includes project directory

## Development

### Adding Dependencies
```bash
# Using pip
pip install package-name
pip freeze > requirements.txt

# Using poetry
poetry add package-name
```

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
black app/
isort app/
pylint app/
```

## Deployment

### Docker
```bash
docker build -t ctsr-streamlit .
docker run -p 8501:8501 -e API_BASE_URL=http://backend:8001 ctsr-streamlit
```

### Streamlit Cloud
1. Push code to GitHub
2. Create Streamlit account at streamlit.io
3. Deploy by selecting GitHub repo
4. Set environment variables in Streamlit Cloud dashboard

### Production Considerations
- Use HTTPS for API connections
- Implement authentication/authorization
- Set up monitoring and logging
- Configure CORS if backend is on different domain
- Use environment variables for configuration

## Configuration Options

### Environment Variables
```bash
API_BASE_URL              # Backend API URL (default: http://localhost:8001)
STREAMLIT_CLIENT_THEME    # light/dark theme
STREAMLIT_LOGGER_LEVEL    # Logging level
```

### Streamlit Config (`.streamlit/config.toml`)
```toml
[client]
showErrorDetails = false
toolbarMode = "viewer"

[server]
port = 8501
headless = true
```

## API Specification

See backend [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) for complete API documentation.

Key endpoints:
- `GET /health` - Health check
- `GET /api/v1/vendors` - List vendors
- `GET /api/v1/systems` - List systems
- `GET /api/v1/trials` - List trials
- `GET /api/v1/confirmations` - List confirmations
- `GET /api/v1/admin/stats` - Dashboard statistics

## Support & Contributing

For issues, feature requests, or contributions:
1. Check existing GitHub issues
2. Create detailed bug reports with reproduction steps
3. Submit pull requests with clear descriptions
4. Follow project code style (Black, isort)

## License

See [LICENSE](../LICENSE) file for details.

## Authors

Clinical Trial Systems Register Team

## Version History

### v1.0.0 (Current)
- Initial release
- Full CRUD for vendors, systems, trials, confirmations
- Dashboard with KPIs and charts
- Reports and analytics
- Settings and configuration
- Multi-tab interfaces for intuitive UX
