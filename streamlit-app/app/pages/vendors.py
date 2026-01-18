"""Vendors page - Manage vendors."""

from datetime import datetime

import streamlit as st

from app.utils.api_client import api_client
from app.utils.components import format_date, render_form_section, show_error, show_success


def render():
    """Render the vendors page."""
    st.title("🏢 Vendor Management")
    st.write("Manage clinical trial service vendors and platform providers")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Browse", "➕ Create", "🔧 Manage"])

    with tab1:
        render_browse_tab()

    with tab2:
        render_create_tab()

    with tab3:
        render_manage_tab()


def render_browse_tab():
    """Render the browse vendors tab."""
    st.subheader("Browse Vendors")

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        vendor_type_filter = st.selectbox(
            "Vendor Type",
            options=[
                "All",
                "CRO",
                "FSP",
                "TECH_VENDOR",
                "CENTRAL_LAB",
                "IMAGING",
                "ECG_VENDOR",
                "BIOANALYTICAL",
                "LOGISTICS",
                "SPECIALTY",
                "INTERNAL",
            ],
        )

    with col2:
        is_active_filter = st.checkbox("Active Only", value=True)

    with col3:
        limit = st.number_input("Records per page", min_value=10, max_value=100, value=50)

    # Fetch vendors
    with st.spinner("Loading vendors..."):
        vendor_type_param = None if vendor_type_filter == "All" else vendor_type_filter
        response = api_client.list_vendors(
            vendor_type=vendor_type_param,
            is_active=is_active_filter,
            limit=limit,
            user_email=st.session_state.user_email,
        )

    if not response:
        st.error("Failed to load vendors.")
        return

    vendors = response.get("data", [])
    meta = response.get("meta", {})

    if not vendors:
        st.info("No vendors found.")
        return

    display_data = [
        {
            "Code": v.get("vendor_code", ""),
            "Name": v.get("vendor_name", ""),
            "Type": v.get("vendor_type", "").replace("_", " "),
            "Status": "✅ Active" if v.get("is_active") else "❌ Inactive",
            "Contact": v.get("contact_email", ""),
            "Created": format_date(v.get("created_at", "")),
        }
        for v in vendors
    ]

    st.dataframe(display_data, use_container_width=True, hide_index=True)

    # Pagination info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"Total: {meta.get('total', 0)} vendors")
    with col2:
        st.caption(f"Showing: {len(vendors)} vendors")


def render_create_tab():
    """Render the create vendor tab."""
    st.subheader("Create New Vendor")

    with st.form("create_vendor_form"):
        vendor_code = st.text_input(
            "Vendor Code *",
            placeholder="e.g., ICON_CRO",
            help="Uppercase alphanumeric and underscore only",
        )

        vendor_name = st.text_input(
            "Vendor Name *",
            placeholder="e.g., ICON Clinical",
        )

        vendor_type = st.selectbox(
            "Vendor Type *",
            options=[
                "CRO",
                "FSP",
                "TECH_VENDOR",
                "CENTRAL_LAB",
                "IMAGING",
                "ECG_VENDOR",
                "BIOANALYTICAL",
                "LOGISTICS",
                "SPECIALTY",
                "INTERNAL",
            ],
        )

        col1, col2 = st.columns(2)

        with col1:
            contact_name = st.text_input(
                "Contact Name",
                placeholder="Primary contact person",
            )

        with col2:
            contact_email = st.text_input(
                "Contact Email",
                placeholder="contact@vendor.com",
            )

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            submitted = st.form_submit_button("✅ Create Vendor", type="primary")

        with col2:
            st.form_submit_button("Clear", type="secondary", disabled=True)

        if submitted:
            if not vendor_code or not vendor_name or not vendor_type:
                show_error("Please fill in all required fields marked with *")
                return

            with st.spinner("Creating vendor..."):
                result = api_client.create_vendor(
                    vendor_code=vendor_code,
                    vendor_name=vendor_name,
                    vendor_type=vendor_type,
                    contact_name=contact_name or None,
                    contact_email=contact_email or None,
                    user_email=st.session_state.user_email,
                )

            if result:
                show_success(f"Vendor '{vendor_name}' created successfully!")
                st.session_state.refresh_trigger += 1
                st.rerun()
            else:
                show_error("Failed to create vendor. Check vendor code uniqueness.")


def render_manage_tab():
    """Render the manage vendors tab."""
    st.subheader("Manage Vendors")

    # Search/select vendor
    col1, col2 = st.columns([3, 1])

    with col1:
        selected_vendor_code = st.selectbox(
            "Select Vendor",
            options=[],
            placeholder="Loading vendors...",
            key="manage_vendor_select",
        )

    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()

    # Fetch vendors for selection
    with st.spinner("Loading vendors..."):
        response = api_client.list_vendors(
            limit=100,
            user_email=st.session_state.user_email,
        )

    if response:
        vendors = response.get("data", [])
        vendor_codes = [v["vendor_code"] for v in vendors]

        # Re-create selectbox with actual data
        selected_vendor_code = st.selectbox(
            "Select Vendor",
            options=vendor_codes,
            key="manage_vendor_select_actual",
        )

        if selected_vendor_code:
            # Find selected vendor
            selected_vendor = next(
                (v for v in vendors if v["vendor_code"] == selected_vendor_code),
                None,
            )

            if selected_vendor:
                st.subheader(f"Edit: {selected_vendor['vendor_name']}")

                with st.form(f"edit_vendor_form_{selected_vendor['vendor_id']}"):
                    vendor_name = st.text_input(
                        "Vendor Name",
                        value=selected_vendor.get("vendor_name", ""),
                    )

                    vendor_type = st.selectbox(
                        "Vendor Type",
                        options=[
                            "CRO",
                            "FSP",
                            "TECH_VENDOR",
                            "CENTRAL_LAB",
                            "IMAGING",
                            "ECG_VENDOR",
                            "BIOANALYTICAL",
                            "LOGISTICS",
                            "SPECIALTY",
                            "INTERNAL",
                        ],
                        index=[
                            "CRO",
                            "FSP",
                            "TECH_VENDOR",
                            "CENTRAL_LAB",
                            "IMAGING",
                            "ECG_VENDOR",
                            "BIOANALYTICAL",
                            "LOGISTICS",
                            "SPECIALTY",
                            "INTERNAL",
                        ].index(selected_vendor.get("vendor_type", "CRO")),
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        contact_name = st.text_input(
                            "Contact Name",
                            value=selected_vendor.get("contact_name", ""),
                        )

                    with col2:
                        contact_email = st.text_input(
                            "Contact Email",
                            value=selected_vendor.get("contact_email", ""),
                        )

                    is_active = st.checkbox(
                        "Active",
                        value=selected_vendor.get("is_active", True),
                    )

                    st.divider()

                    col1, col2 = st.columns(2)

                    with col1:
                        submitted = st.form_submit_button("✅ Save Changes", type="primary")

                    with col2:
                        st.form_submit_button("Cancel", type="secondary", disabled=True)

                    if submitted:
                        with st.spinner("Updating vendor..."):
                            result = api_client.update_vendor(
                                vendor_id=selected_vendor["vendor_id"],
                                vendor_name=vendor_name,
                                vendor_type=vendor_type,
                                contact_name=contact_name or None,
                                contact_email=contact_email or None,
                                is_active=is_active,
                                user_email=st.session_state.user_email,
                            )

                        if result:
                            show_success("Vendor updated successfully!")
                            st.session_state.refresh_trigger += 1
                            st.rerun()
                        else:
                            show_error("Failed to update vendor.")

                # Vendor details
                st.divider()
                st.subheader("Details")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Vendor ID", str(selected_vendor["vendor_id"])[:8] + "...")

                with col2:
                    st.metric("Code", selected_vendor["vendor_code"])

                with col3:
                    st.metric("Status", "Active" if selected_vendor["is_active"] else "Inactive")

                with col4:
                    st.metric("Created", format_date(selected_vendor["created_at"]))
