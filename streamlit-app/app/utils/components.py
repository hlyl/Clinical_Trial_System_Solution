"""UI component utilities for Streamlit."""

from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
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
    """Return HTML for status badge using Novo Nordisk CVI spot colors."""
    # Novo Nordisk CVI Spot Colors
    # Lava Red: error/failed/overdue states
    # Golden Yellow: warning/pending/planned states
    # Forest Green: success/active/confirmed/healthy states
    # True Blue: neutral/completed states
    # Warm Grey: inactive states
    status_colors = {
        "ACTIVE": "#228B22",  # Forest Green
        "PLANNED": "#FFD700",  # Golden Yellow
        "COMPLETED": "#001965",  # True Blue
        "PENDING": "#FFD700",  # Golden Yellow
        "CONFIRMED": "#228B22",  # Forest Green
        "OVERDUE": "#DC143C",  # Lava Red
        "VALIDATED": "#228B22",  # Forest Green
        "FAILED": "#DC143C",  # Lava Red
        "HEALTHY": "#228B22",  # Forest Green
        "UNHEALTHY": "#DC143C",  # Lava Red
        "INACTIVE": "#C9C0B7",  # Warm Grey
    }
    color = status_colors.get(status, "#8B8D8F")  # Granite Grey as fallback

    # Use white text for dark colors, True Blue for light colors
    dark_colors = ["#228B22", "#001965", "#DC143C", "#8B8D8F", "#C9C0B7"]
    text_color = "#FFFFFF" if color in dark_colors else "#001965"

    badge_style = (
        f"background-color: {color}; color: {text_color}; padding: 6px 12px; "
        f"border-radius: 24px; font-weight: 500; font-size: 0.875rem;"
    )
    return f"<span style='{badge_style}'>{status}</span>"


def render_metric_cards(metrics: Dict[str, Any]):
    """Render metric cards in a row."""
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics.items()):
        with col:
            st.metric(label, value)


def render_dataframe_with_actions(
    df: pd.DataFrame,
    key_column: str,
    on_view: Optional[callable] = None,
    on_edit: Optional[callable] = None,
    on_delete: Optional[callable] = None,
) -> Optional[str]:
    """Render dataframe with action buttons.

    Returns the ID of the row that was clicked, or None.
    """
    if df.empty:
        st.info("No data available.")
        return None

    # Add action column
    action_cols = []
    if on_view or on_edit or on_delete:
        action_cols.append("Actions")

    display_df = df.copy()

    # Display table
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Buttons below table
    st.write("---")

    row_id = None
    for idx, row in df.iterrows():
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

        row_id_value = str(row[key_column])

        with col1:
            if on_view and st.button("👁️ View", key=f"view_{idx}_{row_id_value}"):
                on_view(row_id_value)
                row_id = row_id_value

        with col2:
            if on_edit and st.button("✏️ Edit", key=f"edit_{idx}_{row_id_value}"):
                on_edit(row_id_value)
                row_id = row_id_value

        with col3:
            if on_delete and st.button("🗑️ Delete", key=f"delete_{idx}_{row_id_value}"):
                on_delete(row_id_value)
                row_id = row_id_value

    return row_id


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
