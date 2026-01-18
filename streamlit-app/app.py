"""Streamlit application configuration and entry point."""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Page configuration
st.set_page_config(
    page_title="CTSR - Clinical Trial Systems Register",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/hlyl/Clinical_Trial_System_Solution",
        "Report a bug": "https://github.com/hlyl/Clinical_Trial_System_Solution/issues",
        "About": "Clinical Trial Systems Register v0.1.0",
    },
)

# Novo Nordisk CVI Theme configuration
st.markdown(
    """
    <style>
        /* Novo Nordisk Corporate Visual Identity */
        /* Color Palette */
        :root {
            --nn-true-blue: #001965;
            --nn-snow-white: #FFFFFF;
            --nn-sea-blue: #0055B8;
            --nn-light-blue: #7AB3E6;
            --nn-ocean-green: #4DA398;
            --nn-rose-pink: #F5D1D8;
            --nn-warm-grey: #C9C0B7;
            --nn-granite-grey: #8B8D8F;
            --nn-lava-red: #DC143C;
            --nn-golden-yellow: #FFD700;
            --nn-forest-green: #228B22;
        }

        /* Base Layout */
        .reportview-container, .main .block-container {
            background: var(--nn-light-blue);
            font-family: Arial, sans-serif;
        }

        /* Top header bar - Light Blue instead of black */
        header[data-testid="stHeader"] {
            background-color: var(--nn-light-blue) !important;
        }

        /* App header toolbar */
        .stApp > header {
            background-color: var(--nn-light-blue) !important;
        }

        /* Main toolbar area */
        [data-testid="stToolbar"] {
            background-color: var(--nn-light-blue) !important;
        }

        /* Bottom bar/footer - Light Blue instead of black */
        footer {
            background-color: var(--nn-light-blue) !important;
        }

        [data-testid="stBottom"] {
            background-color: var(--nn-light-blue) !important;
        }

        .stApp > footer {
            background-color: var(--nn-light-blue) !important;
        }

        /* Bottom element containers */
        [data-testid="stBottomBlockContainer"] {
            background-color: var(--nn-light-blue) !important;
        }

        /* Typography - Novo Nordisk Style */
        h1, h2, h3, h4, h5, h6 {
            color: var(--nn-true-blue) !important;
            font-weight: 300 !important;
        }

        h1 {
            font-size: 2.5rem !important;
            border-bottom: 2px solid var(--nn-sea-blue);
            padding-bottom: 12px;
            margin-bottom: 24px;
        }

        h2 {
            font-size: 1.75rem !important;
            margin-top: 32px;
            margin-bottom: 16px;
        }

        h3 {
            font-size: 1.25rem !important;
            font-weight: 400 !important;
        }

        /* Body text should be True Blue, not black */
        body, .stMarkdown, p, div, span, label {
            color: var(--nn-true-blue) !important;
        }

        /* Metric Cards - Clean, rounded corners */
        .stMetric {
            background-color: var(--nn-snow-white);
            border-radius: 8px;
            padding: 16px;
            border: 1px solid rgba(0, 25, 101, 0.1);
            box-shadow: 0 2px 4px rgba(0, 25, 101, 0.05);
        }

        .stMetric label {
            color: var(--nn-sea-blue) !important;
            font-size: 0.875rem !important;
        }

        .stMetric [data-testid="stMetricValue"] {
            color: var(--nn-true-blue) !important;
            font-weight: 500 !important;
        }

        /* Buttons - Novo Nordisk Style (rounded, True Blue) */
        .stButton button {
            background-color: var(--nn-true-blue);
            color: var(--nn-snow-white);
            border-radius: 24px;
            border: none;
            padding: 10px 24px;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .stButton button:hover {
            background-color: var(--nn-sea-blue);
            box-shadow: 0 4px 8px rgba(0, 25, 101, 0.2);
        }

        /* Secondary buttons */
        .stButton button[kind="secondary"] {
            background-color: transparent;
            color: var(--nn-true-blue);
            border: 2px solid var(--nn-true-blue);
        }

        .stButton button[kind="secondary"]:hover {
            background-color: rgba(0, 25, 101, 0.05);
        }

        /* Sidebar - Light Blue background with True Blue accents */
        section[data-testid="stSidebar"] {
            background-color: var(--nn-light-blue);
            border-right: 1px solid rgba(0, 25, 101, 0.1);
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: var(--nn-true-blue) !important;
        }

        /* Input fields - subtle rounded corners */
        .stTextInput input, .stSelectbox select, .stNumberInput input, .stTextArea textarea {
            border-radius: 4px;
            border: 1px solid var(--nn-granite-grey);
            background-color: var(--nn-snow-white);
            color: var(--nn-true-blue);
        }

        .stTextInput input:focus, .stSelectbox select:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
            border-color: var(--nn-sea-blue);
            box-shadow: 0 0 0 1px var(--nn-sea-blue);
        }

        /* Dropdown specific styling */
        .stSelectbox > div > div {
            background-color: var(--nn-snow-white);
            border-color: var(--nn-granite-grey);
        }

        /* Date inputs */
        .stDateInput input {
            border-radius: 4px;
            border: 1px solid var(--nn-granite-grey);
            background-color: var(--nn-snow-white);
            color: var(--nn-true-blue);
        }

        /* Dataframe/Table styling */
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
        }

        /* Table/Grid elements - use Granite Grey instead of black */
        .stDataFrame table {
            color: var(--nn-granite-grey);
        }

        .stDataFrame thead tr th {
            background-color: var(--nn-snow-white) !important;
            color: var(--nn-true-blue) !important;
            border-bottom: 2px solid var(--nn-granite-grey) !important;
        }

        .stDataFrame tbody tr td {
            border-bottom: 1px solid var(--nn-granite-grey) !important;
            color: var(--nn-granite-grey) !important;
        }

        /* Grid lines */
        .element-container, .stMarkdown table {
            border-color: var(--nn-granite-grey) !important;
        }

        table {
            border-color: var(--nn-granite-grey) !important;
        }

        table th, table td {
            border-color: var(--nn-granite-grey) !important;
        }

        /* Success/Error/Warning states using spot colors */
        .stSuccess {
            background-color: rgba(34, 139, 34, 0.1);
            color: var(--nn-forest-green);
            border-left: 4px solid var(--nn-forest-green);
            border-radius: 4px;
        }

        .stError {
            background-color: rgba(220, 20, 60, 0.1);
            color: var(--nn-lava-red);
            border-left: 4px solid var(--nn-lava-red);
            border-radius: 4px;
        }

        .stWarning {
            background-color: rgba(255, 215, 0, 0.1);
            color: #8B7500;
            border-left: 4px solid var(--nn-golden-yellow);
            border-radius: 4px;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            color: var(--nn-sea-blue);
            border-radius: 4px 4px 0 0;
            font-weight: 500;
        }

        .stTabs [aria-selected="true"] {
            background-color: var(--nn-true-blue);
            color: var(--nn-snow-white);
        }

        /* Dividers */
        hr {
            border-color: rgba(0, 25, 101, 0.15);
        }

        /* Cards/Expanders */
        .streamlit-expanderHeader {
            background-color: rgba(0, 85, 184, 0.05);
            border-radius: 4px;
            color: var(--nn-true-blue);
        }

        /* Remove black text - enforce True Blue throughout */
        * {
            color: var(--nn-true-blue);
        }

        /* Links */
        a {
            color: var(--nn-sea-blue) !important;
            text-decoration: none;
        }

        a:hover {
            color: var(--nn-light-blue) !important;
            text-decoration: underline;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_session_state():
    """Initialize session state variables."""
    if "user_email" not in st.session_state:
        st.session_state.user_email = "dev@localhost"
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8001")
    if "refresh_trigger" not in st.session_state:
        st.session_state.refresh_trigger = 0
    if "selected_vendor_id" not in st.session_state:
        st.session_state.selected_vendor_id = None
    if "selected_system_id" not in st.session_state:
        st.session_state.selected_system_id = None
    if "selected_trial_id" not in st.session_state:
        st.session_state.selected_trial_id = None


def main():
    """Main Streamlit application."""
    initialize_session_state()

    # Sidebar navigation
    with st.sidebar:
        st.image(
            "https://img.icons8.com/color/96/000000/test-tube.png",
            width=60,
        )
        st.title("CTSR")
        st.caption("Clinical Trial Systems Register")
        st.divider()

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Vendors",
                "Systems",
                "Trials",
                "Confirmations",
                "Reports",
                "Settings",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        # API Status
        st.subheader("System Status", divider=True)
        try:
            from app.utils.api_client import api_client

            health = api_client.get_health()
            if health and health.get("status") == "healthy":
                st.success("✅ API: Connected")
                st.caption(f"DB: {health.get('database', 'Unknown')}")
            else:
                st.error("❌ API: Disconnected")
        except Exception as e:
            st.error("❌ API: Error")
            st.caption(str(e)[:50])

        st.divider()
        st.caption(f"User: {st.session_state.user_email}")
        st.caption(f"API: {st.session_state.api_base_url}")

    # Page routing
    if page == "Dashboard":
        from app.pages import dashboard

        dashboard.render()
    elif page == "Vendors":
        from app.pages import vendors

        vendors.render()
    elif page == "Systems":
        from app.pages import systems

        systems.render()
    elif page == "Trials":
        from app.pages import trials

        trials.render()
    elif page == "Confirmations":
        from app.pages import confirmations

        confirmations.render()
    elif page == "Reports":
        from app.pages import reports

        reports.render()
    elif page == "Settings":
        from app.pages import settings

        settings.render()


if __name__ == "__main__":
    main()
