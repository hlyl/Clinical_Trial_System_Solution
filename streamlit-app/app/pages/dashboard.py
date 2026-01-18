"""Dashboard page - Overview and key metrics."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from app.utils.api_client import api_client
from app.utils.components import render_metric_cards, format_datetime


def render():
    """Render the dashboard page."""
    st.title("📊 Dashboard")
    st.write("System overview and key performance indicators")

    # Fetch data
    with st.spinner("Loading dashboard data..."):
        stats = api_client.get_admin_stats(st.session_state.user_email)
        lookups = api_client.get_lookups()

    if not stats:
        st.error("Failed to load dashboard data.")
        return

    # Key metrics
    st.subheader("Key Metrics", divider=True)

    metrics = {
        "Total Vendors": stats.get("total_vendors", 0),
        "Total Systems": stats.get("total_systems", 0),
        "Active Trials": stats.get("active_trials", 0),
        "Pending Confirmations": stats.get("pending_confirmations", 0),
        "Validated Systems": stats.get("validated_systems", 0),
        "Failed Validations": stats.get("failed_validations", 0),
    }

    render_metric_cards(metrics)

    # Status distribution charts
    st.subheader("Status Distribution", divider=True)

    col1, col2, col3 = st.columns(3)

    # Trial status distribution
    with col1:
        trial_statuses = stats.get("trial_status_distribution", {})
        if trial_statuses:
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=list(trial_statuses.keys()),
                        values=list(trial_statuses.values()),
                        marker=dict(
                            colors=["#28a745", "#ffc107", "#6c757d"]
                        ),
                    )
                ]
            )
            fig.update_layout(
                title="Trials by Status",
                height=300,
                margin=dict(l=0, r=0, t=30, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

    # Validation status distribution
    with col2:
        validation_statuses = stats.get("validation_status_distribution", {})
        if validation_statuses:
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=list(validation_statuses.keys()),
                        values=list(validation_statuses.values()),
                        marker=dict(
                            colors=["#28a745", "#ffc107", "#dc3545", "#6c757d"]
                        ),
                    )
                ]
            )
            fig.update_layout(
                title="Systems by Validation Status",
                height=300,
                margin=dict(l=0, r=0, t=30, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

    # Confirmation status distribution
    with col3:
        confirmation_statuses = stats.get(
            "confirmation_status_distribution", {}
        )
        if confirmation_statuses:
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=list(confirmation_statuses.keys()),
                        values=list(confirmation_statuses.values()),
                        marker=dict(
                            colors=["#28a745", "#17a2b8", "#dc3545"]
                        ),
                    )
                ]
            )
            fig.update_layout(
                title="Confirmations by Status",
                height=300,
                margin=dict(l=0, r=0, t=30, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

    # Vendor distribution
    st.subheader("Vendor Distribution", divider=True)

    vendor_types = stats.get("vendor_type_distribution", {})
    if vendor_types:
        fig = go.Figure(
            data=[
                go.Bar(
                    x=list(vendor_types.keys()),
                    y=list(vendor_types.values()),
                    marker=dict(color="#1f77b4"),
                )
            ]
        )
        fig.update_layout(
            title="Vendors by Type",
            xaxis_title="Vendor Type",
            yaxis_title="Count",
            height=300,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Recent activity
    st.subheader("System Information", divider=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "API Base URL",
            st.session_state.api_base_url,
        )

    with col2:
        st.metric(
            "User Email",
            st.session_state.user_email,
        )

    with col3:
        health = api_client.get_health(st.session_state.user_email)
        if health:
            st.metric(
                "API Status",
                health.get("status", "Unknown").upper(),
            )

    with col4:
        if health:
            st.metric(
                "Database",
                health.get("database", "Unknown")[:30],
            )

    # Data quality indicators
    st.subheader("Data Quality", divider=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        missing_validations = stats.get("systems_missing_validation", 0)
        st.metric("Systems Pending Validation", missing_validations)

    with col2:
        expiring_validations = stats.get(
            "systems_validation_expiring_soon", 0
        )
        st.metric("Validations Expiring Soon", expiring_validations)

    with col3:
        incomplete_trials = stats.get("trials_missing_systems", 0)
        st.metric("Trials Missing Systems", incomplete_trials)
