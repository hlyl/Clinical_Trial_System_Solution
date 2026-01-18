"""Trials page - Manage clinical trials."""

import streamlit as st

from app.utils.api_client import api_client
from app.utils.components import format_date, show_error, show_success


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
        _ = st.selectbox(
            "Sort by",
            options=["Created (Newest)", "Created (Oldest)", "Protocol Number"],
        )  # noqa: F841

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

    display_data = [
        {
            "Protocol": t.get("protocol_number", ""),
            "Title": t.get("trial_title", ""),
            "Status": t.get("trial_status", ""),
            "Created": format_date(t.get("created_at", "")),
        }
        for t in trials
    ]

    st.dataframe(display_data, use_container_width=True, hide_index=True)


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

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.spinner("Loading trials..."):
            response = api_client.list_trials(limit=100, user_email=st.session_state.user_email)
            trials = response.get("data", []) if response else []

        trial_options = [t["protocol_number"] for t in trials]
        selected_trial = st.selectbox("Select Trial", options=trial_options)

    with col2:
        with st.spinner("Loading systems and vendors..."):
            response = api_client.list_systems(limit=100, user_email=st.session_state.user_email)
            systems = response.get("data", []) if response else []

            response = api_client.list_vendors(limit=100, user_email=st.session_state.user_email)
            vendors = response.get("data", []) if response else []

        # Create vendor lookup map
        vendor_map = {v["vendor_id"]: v["vendor_name"] for v in vendors}

        # Get unique vendors from systems
        unique_vendors = sorted(set(vendor_map.get(s.get("platform_vendor_id"), "Unknown Vendor") for s in systems))
        vendor_options = ["All Vendors"] + unique_vendors

        selected_vendor = st.selectbox("Select Vendor", options=vendor_options)

    with col3:
        # Filter systems by selected vendor
        if selected_vendor == "All Vendors":
            filtered_systems = systems
        else:
            filtered_systems = [
                s for s in systems if vendor_map.get(s.get("platform_vendor_id"), "Unknown Vendor") == selected_vendor
            ]

        # Create system display options with vendor info
        system_display_map = {}
        system_options = []
        for s in filtered_systems:
            vendor_name = vendor_map.get(s.get("platform_vendor_id"), "Unknown Vendor")
            display_text = f"{s['instance_code']} ({vendor_name})"
            system_display_map[display_text] = s
            system_options.append(display_text)

        selected_system_display = st.selectbox("Select System", options=system_options)
        selected_system = system_display_map.get(selected_system_display) if selected_system_display else None

    # Display linked systems for selected trial
    if selected_trial:
        trial = next((t for t in trials if t["protocol_number"] == selected_trial), None)
        if trial:
            st.divider()
            st.subheader(f"Systems Linked to {selected_trial}")

            with st.spinner("Loading linked systems..."):
                trial_systems = api_client.get_trial_systems(trial["trial_id"], st.session_state.user_email)
                linked_systems = trial_systems.get("data", []) if trial_systems else []

            if linked_systems:
                # Create a dataframe for display
                linked_systems_df = []
                for ls in linked_systems:
                    # Find the system in the systems list to get vendor info
                    system_info = next((s for s in systems if s["instance_id"] == ls["instance_id"]), {})
                    vendor_name = vendor_map.get(system_info.get("platform_vendor_id"), "Unknown")

                    linked_systems_df.append(
                        {
                            "System Code": ls.get("instance_code", "N/A"),
                            "Vendor": vendor_name,
                            "System Name": ls.get("instance_name", "N/A"),
                            "Criticality": ls.get("criticality_code", "N/A"),
                            "Status": ls.get("assignment_status", "N/A"),
                        }
                    )

                st.dataframe(linked_systems_df, use_container_width=True, hide_index=True)
            else:
                st.info("No systems linked to this trial yet")

            st.divider()

    if selected_trial and selected_system:
        trial = next((t for t in trials if t["protocol_number"] == selected_trial), None)

        if trial and selected_system:
            criticality = st.selectbox(
                "Criticality Level",
                options=["CRIT", "MAJ", "STD"],
                format_func=lambda x: {"CRIT": "Critical", "MAJ": "Major", "STD": "Standard"}[x],
            )

            # Check if system is already linked to this trial
            trial_systems = api_client.get_trial_systems(trial["trial_id"], st.session_state.user_email)
            linked_systems = trial_systems.get("data", []) if trial_systems else []
            is_already_linked = any(ls["instance_id"] == selected_system["instance_id"] for ls in linked_systems)

            if is_already_linked:
                st.warning(f"This system is already linked to trial {selected_trial}")
            else:
                if st.button("🔗 Link System to Trial", type="primary"):
                    with st.spinner("Linking..."):
                        result = api_client.link_system_to_trial(
                            trial_id=trial["trial_id"],
                            system_id=selected_system["instance_id"],
                            criticality_code=criticality,
                            user_email=st.session_state.user_email,
                        )

                    if result:
                        show_success("System linked to trial successfully!")
                        st.session_state.refresh_trigger += 1
                        st.rerun()
                    else:
                        show_error("Failed to link system to trial.")
