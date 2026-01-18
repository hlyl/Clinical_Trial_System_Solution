"""UI component utilities for Streamlit."""

from datetime import datetime
from typing import Any, Dict, Optional

import streamlit as st


def format_date(date_str: Optional[str]) -> str:
    """Format ISO date string to readable format."""
    if not date_str:
        return "-"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return date_str


def format_datetime(datetime_str: Optional[str]) -> str:
    """Format ISO datetime string to readable format."""
    if not datetime_str:
        return "-"
    try:
        dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y %H:%M")
    except Exception:
        return datetime_str


def status_badge(status: str) -> str:
    """Return HTML for status badge with standard colors."""
    status_colors = {
        "ACTIVE": "#00CC00",  # Green
        "PLANNED": "#FFA500",  # Orange
        "COMPLETED": "#0068C9",  # Blue
        "PENDING": "#FFA500",  # Orange
        "CONFIRMED": "#00CC00",  # Green
        "OVERDUE": "#FF4B4B",  # Red
        "VALIDATED": "#00CC00",  # Green
        "FAILED": "#FF4B4B",  # Red
        "HEALTHY": "#00CC00",  # Green
        "UNHEALTHY": "#FF4B4B",  # Red
        "INACTIVE": "#808495",  # Gray
    }
    color = status_colors.get(status, "#808495")
    text_color = "#FFFFFF"

    badge_style = (
        f"background-color: {color}; color: {text_color}; padding: 4px 12px; "
        f"border-radius: 12px; font-weight: 500; font-size: 0.875rem; display: inline-block;"
    )
    return f"<span style='{badge_style}'>{status}</span>"


def render_metric_cards(metrics: Dict[str, Any]):
    """Render metric cards in a row."""
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics.items()):
        with col:
            st.metric(label, value)


def render_form_section(
    title: str,
    fields: Dict[str, Dict[str, Any]],
    key_prefix: str = "",
) -> Dict[str, Any]:
    """Render a form section with multiple fields.

    Args:
        title: Section title
        fields: Dict of field_name -> {type, label, value, ...options}
        key_prefix: Prefix for field keys

    Returns:
        Dict of field_name -> user_input
    """
    st.subheader(title)

    results = {}
    cols_count = 2

    cols = st.columns(cols_count)

    for idx, (field_name, field_config) in enumerate(fields.items()):
        col = cols[idx % cols_count]
        field_type = field_config.get("type", "text")
        label = field_config.get("label", field_name.replace("_", " ").title())
        value = field_config.get("value", "")
        key = f"{key_prefix}_{field_name}" if key_prefix else field_name

        with col:
            if field_type == "text":
                results[field_name] = st.text_input(
                    label,
                    value=value,
                    key=key,
                    help=field_config.get("help"),
                )
            elif field_type == "email":
                results[field_name] = st.text_input(
                    label,
                    value=value,
                    key=key,
                    help=field_config.get("help"),
                )
            elif field_type == "textarea":
                results[field_name] = st.text_area(
                    label,
                    value=value,
                    key=key,
                    height=100,
                    help=field_config.get("help"),
                )
            elif field_type == "number":
                results[field_name] = st.number_input(
                    label,
                    value=value if value else 0,
                    key=key,
                    help=field_config.get("help"),
                )
            elif field_type == "select":
                results[field_name] = st.selectbox(
                    label,
                    options=field_config.get("options", []),
                    index=0,
                    key=key,
                    help=field_config.get("help"),
                )
            elif field_type == "multiselect":
                results[field_name] = st.multiselect(
                    label,
                    options=field_config.get("options", []),
                    default=[],
                    key=key,
                    help=field_config.get("help"),
                )
            elif field_type == "checkbox":
                results[field_name] = st.checkbox(
                    label,
                    value=value if isinstance(value, bool) else False,
                    key=key,
                    help=field_config.get("help"),
                )
            elif field_type == "date":
                results[field_name] = st.date_input(
                    label,
                    value=value,
                    key=key,
                    help=field_config.get("help"),
                )

    return results


def show_error(message: str, title: str = "Error"):
    """Show error message."""
    st.error(f"**{title}:** {message}")


def show_success(message: str, title: str = "Success"):
    """Show success message."""
    st.success(f"**{title}:** {message}")


def show_warning(message: str, title: str = "Warning"):
    """Show warning message."""
    st.warning(f"**{title}:** {message}")


def show_info(message: str, title: str = "Info"):
    """Show info message."""
    st.info(f"**{title}:** {message}")
