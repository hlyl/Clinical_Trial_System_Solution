"""Reports page - Analytics and exports."""

from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
from app.utils.api_client import api_client
from app.utils.components import show_error, show_info


def render():
    """Render the reports page."""
    st.title("📊 Reports & Analytics")
    st.write("View system analysis, compliance reports, and export data")

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🔍 System Analysis", "📋 Compliance", "💾 Export Data"])

    with tab1:
        render_overview_tab()

    with tab2:
        render_analysis_tab()

    with tab3:
        render_compliance_tab()

    with tab4:
        render_export_tab()


def render_overview_tab():
    """Render overview tab."""
    st.subheader("System Overview Report")

    with st.spinner("Loading statistics..."):
        stats = api_client.get_admin_stats(user_email=st.session_state.user_email)

    if not stats:
        st.error("Failed to load statistics.")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Vendors", stats.get("total_vendors", 0), delta="Active Systems")

    with col2:
        st.metric("Total Systems", stats.get("total_systems", 0), delta="Validated")

    with col3:
        st.metric("Active Trials", stats.get("active_trials", 0), delta="In Progress")

    with col4:
        st.metric("Pending Confirmations", stats.get("pending_confirmations", 0), delta="Awaiting Review")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Trial Status Distribution**")
        trial_status = stats.get("trial_status_distribution", {})
        if trial_status:
            fig = px.pie(values=list(trial_status.values()), names=list(trial_status.keys()), title="Trials by Status")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.write("**System Validation Status**")
        validation_status = stats.get("system_validation_distribution", {})
        if validation_status:
            fig = px.pie(
                values=list(validation_status.values()),
                names=list(validation_status.keys()),
                title="Systems by Validation Status",
            )
            st.plotly_chart(fig, use_container_width=True)


def render_analysis_tab():
    """Render system analysis tab."""
    st.subheader("System Analysis")

    with st.spinner("Loading systems..."):
        response = api_client.list_systems(limit=1000, user_email=st.session_state.user_email)
        systems = response.get("data", []) if response else []

    if not systems:
        st.info("No systems available for analysis.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Systems by Category**")
        df = pd.DataFrame(systems)
        category_counts = df.get("category_code", pd.Series()).value_counts()
        if not category_counts.empty:
            fig = px.bar(
                x=category_counts.index,
                y=category_counts.values,
                labels={"x": "Category", "y": "Count"},
                title="Systems by Category",
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.write("**Systems by Status**")
        status_counts = df.get("validation_status", pd.Series()).value_counts()
        if not status_counts.empty:
            fig = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                labels={"x": "Status", "y": "Count"},
                title="Systems by Validation Status",
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.write("**System Details**")
    display_df = df[["instance_code", "platform_name", "category_code", "validation_status", "created_at"]].copy()
    display_df.columns = ["Code", "Platform", "Category", "Status", "Created"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_compliance_tab():
    """Render compliance reports tab."""
    st.subheader("Compliance & Quality Reports")

    report_type = st.selectbox(
        "Select Report Type",
        options=[
            "Data Quality Score",
            "System Validation Coverage",
            "Trial System Coverage",
            "Confirmation Status Overview",
        ],
    )

    if report_type == "Data Quality Score":
        st.write("**Data Quality Metrics**")

        with st.spinner("Calculating metrics..."):
            stats = api_client.get_admin_stats(user_email=st.session_state.user_email)

        if stats:
            col1, col2, col3 = st.columns(3)

            with col1:
                validated = stats.get("validated_systems", 0)
                total = stats.get("total_systems", 0)
                pct = (validated / total * 100) if total > 0 else 0
                st.metric("System Validation", f"{pct:.1f}%", f"{validated}/{total}")

            with col2:
                pending = stats.get("pending_confirmations", 0)
                st.metric("Pending Reviews", pending, f"{pending} awaiting")

            with col3:
                failed = stats.get("failed_validations", 0)
                st.metric("Failed Validations", failed, "items to fix")

    elif report_type == "System Validation Coverage":
        st.write("**System Coverage Analysis**")

        with st.spinner("Analyzing coverage..."):
            response = api_client.list_systems(limit=1000, user_email=st.session_state.user_email)
            systems = response.get("data", []) if response else []

        if systems:
            df = pd.DataFrame(systems)
            validated = len(df[df.get("validation_status") == "VALIDATED"])
            total = len(df)

            st.progress(validated / total if total > 0 else 0)
            st.write(f"**Coverage**: {validated}/{total} systems ({validated/total*100:.1f}%)")

            st.write("**Systems Needing Validation**")
            pending = df[df.get("validation_status") != "VALIDATED"]
            if not pending.empty:
                st.dataframe(
                    pending[["instance_code", "platform_name", "validation_status"]],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.success("All systems validated! ✅")

    elif report_type == "Trial System Coverage":
        st.write("**Trial System Assignment Coverage**")
        st.info("Shows which trials have systems assigned for their validations.")

        with st.spinner("Loading data..."):
            trials_response = api_client.list_trials(limit=1000, user_email=st.session_state.user_email)
            trials = trials_response.get("data", []) if trials_response else []

        if trials:
            st.metric("Total Trials", len(trials))
            st.write("**Trial Status Breakdown**")

            status_counts = pd.DataFrame(trials).get("trial_status", pd.Series()).value_counts()
            if not status_counts.empty:
                fig = px.bar(x=status_counts.index, y=status_counts.values, labels={"x": "Status", "y": "Count"})
                st.plotly_chart(fig, use_container_width=True)

    else:  # Confirmation Status Overview
        st.write("**Confirmation Status Overview**")

        with st.spinner("Loading confirmations..."):
            response = api_client.list_confirmations(limit=1000, user_email=st.session_state.user_email)
            confirmations = response.get("data", []) if response else []

        if confirmations:
            df = pd.DataFrame(confirmations)
            status_counts = df.get("confirmation_status", pd.Series()).value_counts()

            col1, col2, col3 = st.columns(3)

            with col1:
                pending = len(df[df.get("confirmation_status") == "PENDING"])
                st.metric("Pending", pending)

            with col2:
                confirmed = len(df[df.get("confirmation_status") == "CONFIRMED"])
                st.metric("Confirmed", confirmed)

            with col3:
                rejected = len(df[df.get("confirmation_status") == "REJECTED"])
                st.metric("Rejected", rejected)

            if not status_counts.empty:
                fig = px.pie(
                    values=status_counts.values, names=status_counts.index, title="Confirmation Status Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)


def render_export_tab():
    """Render data export tab."""
    st.subheader("Export Data")

    st.write("Export data in various formats for external use and archiving.")

    export_format = st.selectbox("Export Format", options=["CSV", "Excel", "JSON"])

    export_type = st.selectbox(
        "Select Data to Export",
        options=[
            "All Vendors",
            "All Systems",
            "All Trials",
            "All Confirmations",
            "System Validation Report",
            "Trial Compliance Report",
        ],
    )

    if st.button("📥 Generate Export", type="primary"):
        with st.spinner(f"Generating {export_format} export..."):
            data = None

            if export_type == "All Vendors":
                response = api_client.list_vendors(limit=10000, user_email=st.session_state.user_email)
                data = response.get("data", []) if response else []

            elif export_type == "All Systems":
                response = api_client.list_systems(limit=10000, user_email=st.session_state.user_email)
                data = response.get("data", []) if response else []

            elif export_type == "All Trials":
                response = api_client.list_trials(limit=10000, user_email=st.session_state.user_email)
                data = response.get("data", []) if response else []

            elif export_type == "All Confirmations":
                response = api_client.list_confirmations(limit=10000, user_email=st.session_state.user_email)
                data = response.get("data", []) if response else []

            else:
                show_info("This report type requires processing. Coming soon!")
                return

            if not data:
                show_error("No data available for export.")
                return

            df = pd.DataFrame(data)

            # Generate download file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ctsr_export_{export_type.lower().replace(' ', '_')}_{timestamp}"

            if export_format == "CSV":
                csv = df.to_csv(index=False)
                st.download_button(label="📥 Download CSV", data=csv, file_name=f"{filename}.csv", mime="text/csv")

            elif export_format == "Excel":
                import io

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Data")
                buffer.seek(0)
                st.download_button(
                    label="📥 Download Excel",
                    data=buffer.getvalue(),
                    file_name=f"{filename}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            else:  # JSON
                import json

                json_str = json.dumps(data, indent=2, default=str)
                st.download_button(
                    label="📥 Download JSON", data=json_str, file_name=f"{filename}.json", mime="application/json"
                )

            show_info(f"Export ready: {len(df)} records")
