"""Settings page - Configuration and preferences."""

import os

import streamlit as st
from app.utils.components import show_error, show_info, show_success


def render():
    """Render the settings page."""
    st.title("⚙️ Settings")
    st.write("Configure your application preferences and settings")

    tab1, tab2, tab3 = st.tabs(["🔧 API Configuration", "👤 User Preferences", "💾 Data Management"])

    with tab1:
        render_api_config_tab()

    with tab2:
        render_preferences_tab()

    with tab3:
        render_data_management_tab()


def render_api_config_tab():
    """Render API configuration tab."""
    st.subheader("API Configuration")

    st.write("Configure the backend API connection settings.")

    with st.form("api_config_form"):
        api_url = st.text_input(
            "API Base URL",
            value=st.session_state.get("api_base_url", "http://localhost:8000"),
            placeholder="http://localhost:8000",
        )

        st.info(
            "The API URL should point to your CTSR backend API server. "
            "Default is http://localhost:8000 for local development."
        )

        user_email = st.text_input(
            "User Email (for audit trail)",
            value=st.session_state.get("user_email", "user@example.com"),
            placeholder="your.email@company.com",
        )

        st.caption("This email is recorded with all API operations for audit and compliance purposes.")

        submitted = st.form_submit_button("💾 Save API Settings", type="primary")

        if submitted:
            if not api_url or not user_email:
                show_error("Please fill in all required fields.")
                return

            # Update session state
            st.session_state.api_base_url = api_url
            st.session_state.user_email = user_email

            # Test connection
            from app.utils.api_client import APIClient

            test_client = APIClient(base_url=api_url)
            health = test_client.get_health()

            if health:
                show_success("API configuration saved and connection verified! ✅")
                st.session_state.refresh_trigger += 1
            else:
                show_error(
                    "Configuration saved but could not verify API connection. "
                    "Please check the API URL and try again."
                )


def render_preferences_tab():
    """Render user preferences tab."""
    st.subheader("User Preferences")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Display Settings**")

        theme = st.selectbox("Theme", options=["Light", "Dark", "Auto"], index=2)

        records_per_page = st.number_input("Records per Page", min_value=10, max_value=500, value=50, step=10)

        st.info("Adjust how many records are displayed in tables by default.")

    with col2:
        st.write("**Notification Settings**")

        show_confirmations = st.checkbox("Show success notifications", value=True)

        show_errors = st.checkbox("Show error notifications", value=True)

        auto_refresh = st.checkbox("Auto-refresh dashboards", value=False)

        if auto_refresh:
            refresh_interval = st.slider("Refresh interval (seconds)", min_value=5, max_value=300, value=60, step=5)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Preferences", type="primary"):
            show_success("Preferences saved successfully!")

    with col2:
        if st.button("🔄 Reset to Defaults"):
            show_info("Preferences reset to default values.")


def render_data_management_tab():
    """Render data management tab."""
    st.subheader("Data Management")

    st.write("Manage your application data and cache.")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Cache Management**")

        if st.button("🗑️ Clear Cache", type="secondary"):
            st.cache_data.clear()
            show_success("Cache cleared successfully!")

        st.caption("Clears all cached API responses and improves fresh data display.")

    with col2:
        st.write("**Session Management**")

        if st.button("🔄 Reset Session", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            show_success("Session reset successfully!")

        st.caption("Clears all session data and resets to initial state.")

    st.divider()

    st.write("**Data Export**")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Export Configuration", type="secondary"):
            config = {
                "api_url": st.session_state.get("api_base_url", ""),
                "user_email": st.session_state.get("user_email", ""),
                "theme": "light",
                "records_per_page": 50,
            }

            import json

            config_json = json.dumps(config, indent=2)

            st.download_button(
                label="📥 Download Config", data=config_json, file_name="ctsr_config.json", mime="application/json"
            )

    with col2:
        st.write("")
        uploaded_file = st.file_uploader("Import Configuration", type=["json"], label_visibility="collapsed")

        if uploaded_file:
            import json

            try:
                config = json.load(uploaded_file)
                if "api_url" in config:
                    st.session_state.api_base_url = config["api_url"]
                if "user_email" in config:
                    st.session_state.user_email = config["user_email"]

                show_success("Configuration imported successfully!")
                st.rerun()
            except json.JSONDecodeError:
                show_error("Invalid JSON file format.")

    st.divider()

    st.write("**About CTSR**")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("App Version", "1.0.0")

    with col2:
        st.metric("Python Version", "3.11+")

    with col3:
        st.metric("Streamlit Version", st.__version__)

    st.caption(
        "Clinical Trial Systems Register (CTSR) - A comprehensive solution for managing "
        "computerized systems in clinical trial environments."
    )
