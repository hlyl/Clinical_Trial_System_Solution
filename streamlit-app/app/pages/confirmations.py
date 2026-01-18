"""Confirmations page - Manage confirmations."""

import pandas as pd
import streamlit as st
from app.utils.api_client import api_client
from app.utils.components import format_date, show_error, show_success


def render():
    """Render the confirmations page."""
    st.title("✅ Confirmations")
    st.write("Manage system validation confirmations and approvals")

    tab1, tab2, tab3 = st.tabs(["📋 Browse", "➕ New", "🔍 Review"])

    with tab1:
        render_browse_tab()

    with tab2:
        render_create_tab()

    with tab3:
        render_review_tab()


def render_browse_tab():
    """Render browse confirmations tab."""
    st.subheader("Browse Confirmations")

    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Confirmation Status",
            options=["All", "PENDING", "COMPLETED", "OVERDUE"],
        )

    with col2:
        confirmation_type = st.selectbox(
            "Confirmation Type",
            options=["All", "PERIODIC", "DB_LOCK"],
        )

    with col3:
        limit = st.number_input("Records per page", min_value=10, max_value=100, value=50)

    with st.spinner("Loading confirmations..."):
        status_param = None if status_filter == "All" else status_filter
        type_param = None if confirmation_type == "All" else confirmation_type

        response = api_client.list_confirmations(
            confirmation_status=status_param,
            confirmation_type=type_param,
            limit=limit,
            user_email=st.session_state.user_email,
        )

    if not response:
        st.error("Failed to load confirmations.")
        return

    confirmations = response.get("data", [])

    if not confirmations:
        st.info("No confirmations found.")
        return

    df = pd.DataFrame(confirmations)
    # Show plain text status instead of HTML badge to avoid raw markup in table
    df["Status"] = df["confirmation_status"] if "confirmation_status" in df.columns else ""
    df["Type"] = df["confirmation_type"] if "confirmation_type" in df.columns else ""
    df["Created"] = df["created_at"].apply(format_date) if "created_at" in df.columns else ""

    display_df = df[["confirmation_id", "confirmation_type", "Status", "Created"]].copy()
    display_df.columns = ["ID", "Type", "Status", "Created"]

    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_create_tab():
    """Render create confirmation tab."""
    st.subheader("Create New Confirmation")

    with st.form("create_confirmation_form"):
        col1, col2 = st.columns(2)

        with col1:
            confirmation_type = st.selectbox(
                "Confirmation Type *",
                options=["INFRASTRUCTURE_CHECK", "REGULATORY_REVIEW", "DATA_VALIDATION"],
            )
            trial_id = st.number_input("Trial ID *", min_value=1)

        with col2:
            system_id = st.number_input("System ID *", min_value=1)
            confirmed_by = st.text_input("Confirmed By", placeholder="Name/Role")

        confirmation_notes = st.text_area("Confirmation Notes", placeholder="Details about this confirmation...")

        col1, col2 = st.columns(2)

        with col1:
            confirmed_date = st.date_input("Confirmation Date")

        with col2:
            confirmation_status = st.selectbox(
                "Status",
                options=["PENDING", "CONFIRMED", "REJECTED"],
            )

        st.divider()

        submitted = st.form_submit_button("✅ Create Confirmation", type="primary")

        if submitted:
            if not confirmation_type or trial_id <= 0 or system_id <= 0:
                show_error("Please fill in all required fields marked with *")
                return

            with st.spinner("Creating confirmation..."):
                result = api_client.create_confirmation(
                    confirmation_type=confirmation_type,
                    trial_id=trial_id,
                    system_id=system_id,
                    confirmed_by=confirmed_by or None,
                    confirmation_notes=confirmation_notes or None,
                    confirmation_status=confirmation_status,
                    confirmed_date=confirmed_date.isoformat(),
                    user_email=st.session_state.user_email,
                )

            if result:
                show_success("Confirmation created successfully!")
                st.session_state.refresh_trigger += 1
                st.rerun()
            else:
                show_error("Failed to create confirmation.")


def render_review_tab():
    """Render review/update confirmations tab."""
    st.subheader("Review Confirmations")

    with st.spinner("Loading confirmations..."):
        response = api_client.list_confirmations(
            confirmation_status="PENDING", limit=100, user_email=st.session_state.user_email
        )
        confirmations = response.get("data", []) if response else []

    if not confirmations:
        st.info("No pending confirmations to review.")
        return

    confirmation_ids = [str(c["confirmation_id"]) for c in confirmations]
    selected_id = st.selectbox("Select Confirmation", options=confirmation_ids)

    if selected_id:
        confirmation = next((c for c in confirmations if str(c["confirmation_id"]) == selected_id), None)

        if confirmation:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Confirmation Type", confirmation.get("confirmation_type", "N/A"))
            with col2:
                st.metric("Current Status", confirmation.get("confirmation_status", "N/A"))
            with col3:
                st.metric("Trial ID", confirmation.get("trial_id", "N/A"))

            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Notes**")
                st.write(confirmation.get("confirmation_notes", "No notes"))

            with col2:
                st.write("**Created**")
                st.write(format_date(confirmation.get("created_at", "")))

            st.divider()

            new_status = st.selectbox(
                "Update Status",
                options=["CONFIRMED", "REJECTED"],
            )

            update_notes = st.text_area("Review Notes", placeholder="Add your review comments...")

            if st.button("🔄 Update Confirmation", type="primary"):
                with st.spinner("Updating..."):
                    result = api_client.update_confirmation(
                        confirmation_id=confirmation["confirmation_id"],
                        confirmation_status=new_status,
                        confirmation_notes=update_notes or None,
                        user_email=st.session_state.user_email,
                    )

                if result:
                    show_success("Confirmation updated successfully!")
                    st.session_state.refresh_trigger += 1
                    st.rerun()
                else:
                    show_error("Failed to update confirmation.")
