"""Systems page - Manage system instances."""

import streamlit as st
import pandas as pd

from app.utils.api_client import api_client
from app.utils.components import show_success, show_error, format_date


def render():
    """Render the systems page."""
    st.title("💻 System Instances")
    st.write("Manage computerized systems used in clinical trials")

    tab1, tab2, tab3 = st.tabs(["📋 Browse", "➕ Create", "🔧 Manage"])

    with tab1:
        render_browse_tab()

    with tab2:
        render_create_tab()

    with tab3:
        render_manage_tab()


def render_browse_tab():
    """Render browse systems tab."""
    st.subheader("Browse Systems")

    col1, col2, col3 = st.columns(3)

    with col1:
        category_filter = st.selectbox(
            "Category",
            options=["All", "EDC", "LIMS", "LMS", "IRT", "RTSM", "OTHER"],
        )

    with col2:
        validation_filter = st.selectbox(
            "Validation Status",
            options=["All", "VALIDATED", "FAILED", "PENDING", "EXPIRED"],
        )

    with col3:
        limit = st.number_input("Records per page", min_value=10, max_value=100, value=50)

    with st.spinner("Loading systems..."):
        category_param = None if category_filter == "All" else category_filter
        validation_param = None if validation_filter == "All" else validation_filter
        response = api_client.list_systems(
            category_code=category_param,
            validation_status=validation_param,
            limit=limit,
            user_email=st.session_state.user_email,
        )

    if not response:
        st.error("Failed to load systems.")
        return

    systems = response.get("data", [])

    if not systems:
        st.info("No systems found.")
        return

    df = pd.DataFrame(systems)
    df["Category"] = df.get("category_code", "")
    df["Validation"] = df.get("validation_status_code", "")
    df["Created"] = df.get("created_at", "").apply(format_date)

    display_df = df[["instance_code", "platform_name", "Category", "Validation", "Created"]].copy()
    display_df.columns = ["Code", "Platform", "Category", "Status", "Created"]

    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_create_tab():
    """Render create system tab."""
    st.subheader("Create New System Instance")

    with st.form("create_system_form"):
        col1, col2 = st.columns(2)

        with col1:
            instance_code = st.text_input("Instance Code *", placeholder="e.g., SYS_001")
            platform_name = st.text_input("Platform Name *", placeholder="e.g., EDC Platform")

        with col2:
            category_code = st.selectbox(
                "Category *",
                options=["EDC", "LIMS", "LMS", "IRT", "RTSM", "OTHER"],
            )
            validation_status = st.selectbox(
                "Validation Status *",
                options=["VALIDATED", "FAILED", "PENDING"],
            )

        platform_version = st.text_input("Platform Version", placeholder="e.g., 1.0.0")
        instance_name = st.text_input("Instance Name", placeholder="e.g., Production")

        st.divider()

        submitted = st.form_submit_button("✅ Create System", type="primary")

        if submitted:
            if not instance_code or not platform_name:
                show_error("Please fill in all required fields marked with *")
                return

            with st.spinner("Creating system..."):
                result = api_client.create_system(
                    instance_code=instance_code,
                    category_code=category_code,
                    platform_name=platform_name,
                    validation_status_code=validation_status,
                    platform_version=platform_version or None,
                    instance_name=instance_name or None,
                    user_email=st.session_state.user_email,
                )

            if result:
                show_success(f"System '{instance_code}' created successfully!")
                st.session_state.refresh_trigger += 1
                st.rerun()
            else:
                show_error("Failed to create system.")


def render_manage_tab():
    """Render manage systems tab."""
    st.subheader("Manage Systems")

    with st.spinner("Loading systems..."):
        response = api_client.list_systems(
            limit=100,
            user_email=st.session_state.user_email,
        )

    if not response:
        st.error("Failed to load systems.")
        return

    systems = response.get("data", [])

    if not systems:
        st.info("No systems available to manage.")
        return

    system_codes = [s["instance_code"] for s in systems]
    selected_code = st.selectbox("Select System", options=system_codes)

    if selected_code:
        system = next(s for s in systems if s["instance_code"] == selected_code)

        with st.form("update_system_form"):
            col1, col2 = st.columns(2)

            with col1:
                instance_code = st.text_input(
                    "Instance Code",
                    value=system.get("instance_code", "")
                )
                platform_name = st.text_input(
                    "Platform Name",
                    value=system.get("platform_name", "")
                )

            with col2:
                category_code = st.selectbox(
                    "Category",
                    options=["EDC", "LIMS", "LMS", "IRT", "RTSM", "OTHER"],
                    index=["EDC", "LIMS", "LMS", "IRT", "RTSM", "OTHER"].index(
                        system.get("category_code", "EDC")
                    )
                )
                validation_status = st.selectbox(
                    "Validation Status",
                    options=["VALIDATED", "FAILED", "PENDING", "EXPIRED"],
                    index=["VALIDATED", "FAILED", "PENDING", "EXPIRED"].index(
                        system.get("validation_status_code", "PENDING")
                    )
                )

            platform_version = st.text_input(
                "Platform Version",
                value=system.get("platform_version", "")
            )
            instance_name = st.text_input(
                "Instance Name",
                value=system.get("instance_name", "")
            )

            is_active = st.checkbox(
                "Active",
                value=system.get("is_active", True)
            )

            st.divider()

            submitted = st.form_submit_button("💾 Update System", type="primary")

            if submitted:
                if not instance_code or not platform_name:
                    show_error("Instance Code and Platform Name are required.")
                    return

                with st.spinner("Updating system..."):
                    result = api_client.update_system(
                        system_id=system["instance_id"],
                        instance_code=instance_code,
                        platform_name=platform_name,
                        category_code=category_code,
                        validation_status_code=validation_status,
                        platform_version=platform_version or None,
                        instance_name=instance_name or None,
                        is_active=is_active,
                        user_email=st.session_state.user_email,
                    )

                if result:
                    show_success(f"System '{instance_code}' updated successfully!")
                    st.session_state.refresh_trigger += 1
                    st.rerun()
                else:
                    show_error("Failed to update system.")
