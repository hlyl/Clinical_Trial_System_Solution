"""Streamlit application configuration and entry point."""

import os
from pathlib import Path
from typing import Optional

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

# Theme configuration
st.markdown(
    """
    <style>
        /* Custom CSS for better UX */
        .reportview-container {
            background: #f0f2f6;
        }
        .stMetric {
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .stCard {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
        }
        h1 {
            color: #1f77b4;
            border-bottom: 3px solid #1f77b4;
            padding-bottom: 10px;
        }
        h2 {
            color: #0056b3;
            margin-top: 25px;
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
        st.session_state.api_base_url = os.getenv(
            "API_BASE_URL", "http://localhost:8001"
        )
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
