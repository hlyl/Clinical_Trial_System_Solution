"""Trials page - Manage clinical trials."""

import streamlit as st
import pandas as pd

from app.utils.api_client import api_client
from app.utils.components import show_success, show_error, format_date


def render():
    """Render the trials page."""
    st.title("🧪 Clinical Trials")
    st.write("Manage clinical trial information and system assignments")

    tab1, tab2, tab3 = st.tabs(["📋 Browse", "➕ Create", "🔗 Assign Systems"])

    with tab1:
        render_browse_tab()

    with tab2:
        render_create_tab()

    with tab3:
        render_assign_tab()


def render_browse_tab():
    """Render browse trials tab."""
    st.subheader("Browse Trials")

    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Trial Status",
            options=["All", "ACTIVE", "PLANNED", "COMPLETED", "ON_HOLD"],
        )

    with col2:
        sort_by = st.selectbox(
            "Sort by",
            options=["Created (Newest)", "Created (Oldest)", "Protocol Number"],
        )

    with col3:
        limit = st.number_input("Records per page", min_value=10, max_value=100, value=50)

    with st.spinner("Loading trials..."):
        status_param = None if status_filter == "All" else status_filter
        response = api_client.list_trials(
            trial_status=status_param,
            limit=limit,
            user_email=st.session_state.user_email,
        )

    if not response:
        st.error("Failed to load trials.")
        return

    trials = response.get("data", [])

    if not trials:
        st.info("No trials found.")
        return

    df = pd.DataFrame(trials)
    df["Status"] = df.get("trial_status", "")
    df["Created"] = df.get("created_at", "").apply(format_date)

    display_df = df[["protocol_number", "trial_title", "Status", "Created"]].copy()
    display_df.columns = ["Protocol", "Title", "Status", "Created"]

    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_create_tab():
    """Render create trial tab."""
    st.subheader("Create New Trial")

    with st.form("create_trial_form"):
        col1, col2 = st.columns(2)

        with col1:
            protocol_number = st.text_input("Protocol Number *", placeholder="PROTO-2026-001")
            trial_title = st.text_input("Trial Title *", placeholder="Study Title")

        with col2:
            trial_phase = st.selectbox(
                "Trial Phase",
                options=["PHASE_1", "PHASE_2", "PHASE_3", "PHASE_4"],
            )
            therapeutic_area = st.text_input("Therapeutic Area", placeholder="e.g., ONCOLOGY")

        indication = st.text_input("Indication", placeholder="Disease/condition")
        
        col1, col2 = st.columns(2)

        with col1:
            trial_lead_name = st.text_input("Trial Lead Name")

        with col2:
            trial_lead_email = st.text_input("Trial Lead Email", placeholder="lead@pharma.com")

        st.divider()

        submitted = st.form_submit_button("✅ Create Trial", type="primary")

        if submitted:
            if not protocol_number or not trial_title:
                show_error("Please fill in all required fields marked with *")
                return

            with st.spinner("Creating trial..."):
                result = api_client.create_trial(
                    protocol_number=protocol_number,
                    trial_title=trial_title,
                    trial_phase=trial_phase,
                    therapeutic_area=therapeutic_area or None,
                    indication=indication or None,
                    trial_lead_name=trial_lead_name or None,
                    trial_lead_email=trial_lead_email or None,
                    user_email=st.session_state.user_email,
                )

            if result:
                show_success(f"Trial '{protocol_number}' created successfully!")
                st.session_state.refresh_trigger += 1
                st.rerun()
            else:
                show_error("Failed to create trial.")


def render_assign_tab():
    """Render assign systems to trials tab."""
    st.subheader("Assign Systems to Trials")

    col1, col2 = st.columns(2)

    with col1:
        with st.spinner("Loading trials..."):
            response = api_client.list_trials(limit=100, user_email=st.session_state.user_email)
            trials = response.get("data", []) if response else []

        trial_options = [t["protocol_number"] for t in trials]
        selected_trial = st.selectbox("Select Trial", options=trial_options)

    with col2:
        with st.spinner("Loading systems..."):
            response = api_client.list_systems(limit=100, user_email=st.session_state.user_email)
            systems = response.get("data", []) if response else []

        system_options = [s["instance_code"] for s in systems]
        selected_system = st.selectbox("Select System", options=system_options)

    if selected_trial and selected_system:
        trial = next((t for t in trials if t["protocol_number"] == selected_trial), None)
        system = next((s for s in systems if s["instance_code"] == selected_system), None)

        if trial and system:
            criticality = st.selectbox(
                "Criticality Level",
                options=["CRITICAL", "STANDARD", "SUPPORTING"],
            )

            if st.button("🔗 Link System to Trial", type="primary"):
                with st.spinner("Linking..."):
                    result = api_client.link_system_to_trial(
                        trial_id=trial["trial_id"],
                        system_id=system["instance_id"],
                        criticality_code=criticality,
                        user_email=st.session_state.user_email,
                    )

                if result:
                    show_success(f"System linked to trial successfully!")
                    st.session_state.refresh_trigger += 1
                    st.rerun()
                else:
                    show_error("Failed to link system to trial.")
