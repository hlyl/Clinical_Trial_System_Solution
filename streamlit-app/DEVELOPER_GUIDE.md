# CTSR Frontend Developer Guide

## Adding New Features

This guide explains how to extend the CTSR Streamlit frontend with new features.

## Project Structure

```
streamlit-app/
├── app.py                          # Main entry point
├── pyproject.toml                  # Project config
├── requirements.txt                # Dependencies
├── app/
│   ├── __init__.py
│   ├── utils/
│   │   ├── api_client.py          # API communication
│   │   └── components.py          # UI components
│   └── pages/
│       ├── __init__.py
│       ├── dashboard.py
│       ├── vendors.py
│       ├── systems.py
│       ├── trials.py
│       ├── confirmations.py
│       ├── reports.py
│       └── settings.py
└── tests/                          # Unit tests
```

## Adding a New API Method

### Step 1: Add to APIClient

Edit `app/utils/api_client.py`:

```python
def my_new_endpoint(
    self,
    param1: str,
    param2: Optional[str] = None,
    user_email: str = "dev@localhost",
    **kwargs,
) -> Optional[Dict[str, Any]]:
    """Get my new endpoint data.
    
    Args:
        param1: Required parameter
        param2: Optional parameter
        user_email: User email for audit
        **kwargs: Additional parameters
        
    Returns:
        Response JSON or None if error
    """
    params = {
        "param1": param1,
        "limit": kwargs.get("limit", 50),
        "offset": kwargs.get("offset", 0),
    }
    if param2:
        params["param2"] = param2

    return self._make_request(
        "GET",
        "/api/v1/my-endpoint",
        user_email=user_email,
        params=params,
    )
```

### Step 2: Use in Your Page

```python
from app.utils.api_client import api_client

# In your page render function
response = api_client.my_new_endpoint(
    param1="value",
    user_email=st.session_state.user_email
)

if response:
    data = response.get("data", [])
    # Process data
```

## Adding a New Page

### Step 1: Create Page File

Create `app/pages/myfeature.py`:

```python
"""My Feature page description."""

import streamlit as st
from app.utils.api_client import api_client
from app.utils.components import show_success, show_error


def render():
    """Render the page."""
    st.title("🔧 My Feature")
    st.write("Feature description")
    
    tab1, tab2 = st.tabs(["Browse", "Create"])
    
    with tab1:
        render_browse_tab()
    
    with tab2:
        render_create_tab()


def render_browse_tab():
    """Render browse tab."""
    st.subheader("Browse Items")
    
    with st.spinner("Loading..."):
        response = api_client.my_new_endpoint(
            param1="value",
            user_email=st.session_state.user_email
        )
    
    if not response:
        st.error("Failed to load data")
        return
    
    items = response.get("data", [])
    
    if items:
        # Display items
        st.dataframe(items)
    else:
        st.info("No items found")


def render_create_tab():
    """Render create tab."""
    st.subheader("Create Item")
    
    with st.form("create_item_form"):
        field1 = st.text_input("Field 1")
        field2 = st.selectbox("Field 2", options=["A", "B"])
        
        submitted = st.form_submit_button("Create", type="primary")
        
        if submitted:
            if not field1:
                show_error("Please fill all required fields")
                return
            
            with st.spinner("Creating..."):
                result = api_client.create_my_item(
                    field1=field1,
                    field2=field2,
                    user_email=st.session_state.user_email
                )
            
            if result:
                show_success("Item created!")
                st.session_state.refresh_trigger += 1
                st.rerun()
            else:
                show_error("Failed to create item")
```

### Step 2: Add to Router

Edit `app.py` and add to the page selector:

```python
# In the selectbox options
options=[
    "Dashboard",
    "Vendors",
    "Systems",
    "Trials",
    "Confirmations",
    "Reports",
    "My Feature",  # Add here
    "Settings",
],
```

### Step 3: Add Page Routing

In `app.py`, add to routing section:

```python
elif page == "My Feature":
    from app.pages import myfeature
    myfeature.render()
```

## Adding UI Components

### Create Reusable Component

Edit `app/utils/components.py`:

```python
def my_custom_component(
    title: str,
    data: List[Dict],
    on_action: Optional[Callable] = None,
) -> Optional[Dict]:
    """Custom component for displaying data.
    
    Args:
        title: Component title
        data: Data to display
        on_action: Callback function for actions
        
    Returns:
        Selected row data or None
    """
    st.subheader(title)
    
    if not data:
        st.info("No data")
        return None
    
    df = pd.DataFrame(data)
    
    # Add selection
    selected_index = st.radio(
        "Select",
        options=range(len(df)),
        label_visibility="collapsed"
    )
    
    if selected_index is not None:
        return df.iloc[selected_index].to_dict()
    
    return None
```

### Use in Your Page

```python
from app.utils.components import my_custom_component

selected = my_custom_component(
    title="Select Item",
    data=items,
    on_action=lambda x: print(x)
)

if selected:
    st.write(selected)
```

## Working with Forms

### Multi-Field Forms

Use the `render_form_section` component:

```python
from app.utils.components import render_form_section

fields = [
    {
        "name": "email",
        "type": "email",
        "label": "Email Address",
        "required": True
    },
    {
        "name": "category",
        "type": "select",
        "label": "Category",
        "options": ["A", "B", "C"],
        "required": True
    },
    {
        "name": "description",
        "type": "textarea",
        "label": "Description",
        "required": False
    },
    {
        "name": "active",
        "type": "checkbox",
        "label": "Active",
        "default": True
    }
]

form_data = render_form_section(
    title="Create Item",
    fields=fields
)
```

## Session State Management

### Initialize Session State

In `app.py` main function:

```python
if "my_state_key" not in st.session_state:
    st.session_state.my_state_key = None
```

### Use Session State

```python
# Read
current_value = st.session_state.my_state_key

# Write
st.session_state.my_state_key = new_value

# Increment counter
st.session_state.refresh_trigger += 1

# Trigger rerun
st.rerun()
```

## Working with DataFrames

### Display with Actions

```python
from app.utils.components import render_dataframe_with_actions

# Create action handler
def handle_action(row_index, action):
    if action == "edit":
        # Edit row
        pass
    elif action == "delete":
        # Delete row
        pass

render_dataframe_with_actions(
    df=items_df,
    actions=["edit", "delete"],
    on_action=handle_action,
)
```

### Paginate Large Datasets

```python
page = st.number_input("Page", min_value=1)
page_size = 50
start_idx = (page - 1) * page_size
end_idx = start_idx + page_size

page_data = items[start_idx:end_idx]
st.dataframe(page_data)

total_pages = (len(items) + page_size - 1) // page_size
st.caption(f"Page {page} of {total_pages}")
```

## Error Handling

### API Error Handling

```python
from app.utils.components import show_error, show_warning

try:
    result = api_client.some_endpoint(...)
    if not result:
        show_error("Operation failed")
        return
    
    data = result.get("data")
    if not data:
        show_warning("No data returned")
        return
        
except Exception as e:
    show_error(f"Unexpected error: {str(e)}")
    return
```

### Form Validation

```python
def validate_form(data):
    """Validate form data."""
    errors = []
    
    if not data.get("name"):
        errors.append("Name is required")
    
    if data.get("email") and "@" not in data["email"]:
        errors.append("Invalid email format")
    
    if len(data.get("password", "")) < 8:
        errors.append("Password must be at least 8 characters")
    
    return errors

# In your form
if submitted:
    errors = validate_form(form_data)
    if errors:
        for error in errors:
            show_error(error)
        return
    
    # Process valid form
```

## Styling and Theming

### Custom CSS

In `app.py` or individual pages:

```python
st.markdown(
    """
    <style>
        .custom-box {
            background-color: #f0f2f6;
            border-radius: 8px;
            padding: 20px;
            border-left: 4px solid #1f77b4;
        }
        .success-text {
            color: #09ab3b;
            font-weight: bold;
        }
        .error-text {
            color: #ff2b2b;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)
```

### Use Custom Styles

```python
st.markdown(
    '<div class="custom-box">Custom content</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<span class="success-text">Success!</span>',
    unsafe_allow_html=True
)
```

## Testing Your Feature

### Unit Test Example

Create `tests/test_myfeature.py`:

```python
import pytest
from app.utils.api_client import APIClient


def test_my_endpoint():
    """Test my endpoint."""
    client = APIClient()
    result = client.my_new_endpoint(param1="test")
    assert result is not None
    assert "data" in result


def test_form_validation():
    """Test form validation."""
    from app.pages.myfeature import validate_form
    
    errors = validate_form({"name": ""})
    assert len(errors) > 0
    assert "name" in errors[0].lower()
```

### Run Tests

```bash
pytest tests/ -v
```

## Performance Optimization

### Use Caching

```python
@st.cache_data
def load_reference_data():
    """Cache reference data."""
    return api_client.get_lookups()

# Use cached data
lookups = load_reference_data()
```

### Lazy Loading

```python
@st.cache_resource
def get_api_client():
    """Get cached API client."""
    return APIClient()

api = get_api_client()
```

### Pagination for Large Datasets

```python
limit = st.number_input("Records per page", value=50, max_value=1000)
offset = (page - 1) * limit

response = api_client.list_items(limit=limit, offset=offset)
```

## Common Patterns

### Browse-Create-Manage Pattern

All pages follow this structure:

```python
def render():
    tab1, tab2, tab3 = st.tabs(["Browse", "Create", "Manage"])
    
    with tab1:
        render_browse_tab()  # Display list
    with tab2:
        render_create_tab()  # Create form
    with tab3:
        render_manage_tab()  # Update form
```

### Refresh After Mutation

```python
# After create/update/delete
st.session_state.refresh_trigger += 1
st.rerun()  # Rerun to reflect changes
```

### Conditional Display

```python
# Show admin features only if user is admin
if st.session_state.get("is_admin", False):
    st.sidebar.link_button("Admin", "/admin")
```

## Debugging Tips

### Display Debug Info

```python
import streamlit as st

# Show session state
with st.expander("🐛 Debug Info"):
    st.json({
        "user_email": st.session_state.user_email,
        "api_url": st.session_state.api_base_url,
        "refresh_trigger": st.session_state.refresh_trigger,
    })
```

### Log API Calls

```python
import logging

logger = logging.getLogger(__name__)

response = api_client.my_endpoint()
logger.info(f"API response: {response}")
```

### Browser Console Debugging

```python
st.write("<script>console.log('Debug message')</script>", unsafe_allow_html=True)
```

## Best Practices

1. **Always handle None responses** from API calls
2. **Use st.session_state** for persistence across reruns
3. **Show loading indicators** during API calls
4. **Validate forms** before submission
5. **Use meaningful error messages** for users
6. **Cache expensive operations** with @st.cache_data
7. **Follow the Browse-Create-Manage pattern** for consistency
8. **Write docstrings** for all functions
9. **Test error scenarios** as well as happy paths
10. **Monitor performance** with large datasets

## Resources

- [Streamlit Docs](https://docs.streamlit.io)
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)
- [Pydantic Docs](https://docs.pydantic.dev)
- [Plotly Docs](https://plotly.com/python)
- [Backend API Docs](../IMPLEMENTATION_PLAN.md)

## Getting Help

- Check existing page implementations for examples
- Review utility functions in `app/utils/`
- Check browser console (F12) for errors
- Review backend API documentation
- Ask team members or create GitHub issue
