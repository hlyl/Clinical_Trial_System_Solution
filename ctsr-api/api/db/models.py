"""SQLAlchemy ORM models for CTSR database tables."""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID, uuid4

from api.db.base import Base
from sqlalchemy import ARRAY, Boolean, CheckConstraint, Date, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

# =============================================================================
# Lookup Tables
# =============================================================================


class SystemCategory(Base):
    """System category lookup table."""

    __tablename__ = "lkp_system_category"
    __table_args__ = {"schema": "ctsr"}

    category_code: Mapped[str] = mapped_column(String(20), primary_key=True)
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    default_criticality: Mapped[str] = mapped_column(String(10), nullable=False, default="STD")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ValidationStatus(Base):
    """Validation status lookup table."""

    __tablename__ = "lkp_validation_status"
    __table_args__ = {"schema": "ctsr"}

    status_code: Mapped[str] = mapped_column(String(20), primary_key=True)
    status_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    requires_attention: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Criticality(Base):
    """Criticality level lookup table."""

    __tablename__ = "lkp_criticality"
    __table_args__ = {"schema": "ctsr"}

    criticality_code: Mapped[str] = mapped_column(String(10), primary_key=True)
    criticality_name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


# =============================================================================
# Core Tables
# =============================================================================


class Vendor(Base):
    """Vendor table - platform vendors, service providers, CROs."""

    __tablename__ = "vendors"
    __table_args__ = (
        Index("idx_vendors_code", "vendor_code"),
        Index("idx_vendors_type", "vendor_type", postgresql_where=text("is_active = TRUE")),
        {"schema": "ctsr"},
    )

    vendor_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    vendor_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    vendor_name: Mapped[str] = mapped_column(String(200), nullable=False)
    vendor_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        info={
            "check": CheckConstraint(
                "vendor_type IN ('CRO', 'FSP', 'TECH_VENDOR', 'CENTRAL_LAB', "
                "'IMAGING', 'ECG_VENDOR', 'BIOANALYTICAL', 'LOGISTICS', 'SPECIALTY', 'INTERNAL')"
            )
        },
    )
    contact_name: Mapped[Optional[str]] = mapped_column(String(200))
    contact_email: Mapped[Optional[str]] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(200))
    updated_by: Mapped[Optional[str]] = mapped_column(String(200))


class SystemInstance(Base):
    """System instance table - the catalog of systems."""

    __tablename__ = "system_instances"
    __table_args__ = (
        Index("idx_instances_code", "instance_code"),
        Index(
            "idx_instances_category",
            "category_code",
            postgresql_where=text("is_active = TRUE"),
        ),
        Index(
            "idx_instances_validation",
            "validation_status_code",
            postgresql_where=text("is_active = TRUE"),
        ),
        Index("idx_instances_platform_vendor", "platform_vendor_id"),
        Index("idx_instances_service_provider", "service_provider_id"),
        Index(
            "idx_instances_hosting_region",
            "data_hosting_region",
            postgresql_where=text("is_active = TRUE"),
        ),
        {"schema": "ctsr"},
    )

    instance_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    instance_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    platform_vendor_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    service_provider_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    category_code: Mapped[str] = mapped_column(String(20), nullable=False)
    platform_name: Mapped[str] = mapped_column(String(200), nullable=False)
    platform_version: Mapped[Optional[str]] = mapped_column(String(50))
    instance_name: Mapped[Optional[str]] = mapped_column(String(200))
    instance_environment: Mapped[str] = mapped_column(String(20), default="PRODUCTION")
    validation_status_code: Mapped[str] = mapped_column(String(20), nullable=False)
    validation_date: Mapped[Optional[date]] = mapped_column(Date)
    validation_expiry: Mapped[Optional[date]] = mapped_column(Date)
    validation_evidence_link: Mapped[Optional[str]] = mapped_column(String(500))
    hosting_model: Mapped[Optional[str]] = mapped_column(String(20))
    data_hosting_region: Mapped[Optional[str]] = mapped_column(String(20))
    description: Mapped[Optional[str]] = mapped_column(Text)
    supported_studies: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    interfaces: Mapped[Optional[dict]] = mapped_column(JSONB)
    part11_compliant: Mapped[Optional[bool]] = mapped_column(Boolean)
    annex11_compliant: Mapped[Optional[bool]] = mapped_column(Boolean)
    soc2_certified: Mapped[Optional[bool]] = mapped_column(Boolean)
    iso27001_certified: Mapped[Optional[bool]] = mapped_column(Boolean)
    last_major_change_date: Mapped[Optional[date]] = mapped_column(Date)
    last_major_change_desc: Mapped[Optional[str]] = mapped_column(String(500))
    next_planned_change_date: Mapped[Optional[date]] = mapped_column(Date)
    next_planned_change_desc: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(200))
    updated_by: Mapped[Optional[str]] = mapped_column(String(200))


class Trial(Base):
    """Trial table - clinical trials synced from CTMS."""

    __tablename__ = "trials"
    __table_args__ = (
        Index("idx_trials_protocol", "protocol_number"),
        Index("idx_trials_status", "trial_status"),
        Index("idx_trials_lead", "trial_lead_email"),
        Index(
            "idx_trials_confirmation_due",
            "next_confirmation_due",
            postgresql_where=text("trial_status = 'ACTIVE'"),
        ),
        {"schema": "ctsr"},
    )

    trial_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    protocol_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    trial_title: Mapped[str] = mapped_column(String(500), nullable=False)
    trial_phase: Mapped[Optional[str]] = mapped_column(String(20))
    trial_status: Mapped[str] = mapped_column(String(20), nullable=False, default="PLANNED")
    therapeutic_area: Mapped[Optional[str]] = mapped_column(String(100))
    indication: Mapped[Optional[str]] = mapped_column(String(200))
    trial_start_date: Mapped[Optional[date]] = mapped_column(Date)
    planned_db_lock_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_db_lock_date: Mapped[Optional[date]] = mapped_column(Date)
    trial_close_date: Mapped[Optional[date]] = mapped_column(Date)
    trial_lead_name: Mapped[Optional[str]] = mapped_column(String(200))
    trial_lead_email: Mapped[Optional[str]] = mapped_column(String(200))
    ctms_trial_id: Mapped[Optional[str]] = mapped_column(String(100))
    last_ctms_sync: Mapped[Optional[datetime]] = mapped_column()
    next_confirmation_due: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())


class TrialSystemLink(Base):
    """Trial-system link table - many-to-many relationship."""

    __tablename__ = "trial_system_links"
    __table_args__ = (
        Index("idx_links_trial", "trial_id"),
        Index("idx_links_instance", "instance_id"),
        Index("idx_links_status", "assignment_status"),
        Index(
            "idx_links_unique_active",
            "trial_id",
            "instance_id",
            unique=True,
            postgresql_where=text("assignment_status NOT IN ('REPLACED', 'LOCKED')"),
        ),
        {"schema": "ctsr"},
    )

    link_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    trial_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    instance_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    assignment_status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE")
    criticality_code: Mapped[str] = mapped_column(String(10), nullable=False)
    criticality_override_reason: Mapped[Optional[str]] = mapped_column(String(500))
    usage_start_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=text("CURRENT_DATE"))
    usage_end_date: Mapped[Optional[date]] = mapped_column(Date)
    linked_by: Mapped[Optional[str]] = mapped_column(String(200))
    linked_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    unlinked_by: Mapped[Optional[str]] = mapped_column(String(200))
    unlinked_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())


class Confirmation(Base):
    """Confirmation table - periodic and DB lock confirmations."""

    __tablename__ = "confirmations"
    __table_args__ = (
        Index("idx_confirmations_trial", "trial_id"),
        Index("idx_confirmations_status", "confirmation_status"),
        Index(
            "idx_confirmations_due",
            "due_date",
            postgresql_where=text("confirmation_status = 'PENDING'"),
        ),
        {"schema": "ctsr"},
    )

    confirmation_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    trial_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    confirmation_type: Mapped[str] = mapped_column(String(20), nullable=False)
    confirmation_status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    confirmed_date: Mapped[Optional[date]] = mapped_column(Date)
    confirmed_by: Mapped[Optional[str]] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    systems_count: Mapped[Optional[int]] = mapped_column(Integer)
    validation_alerts_count: Mapped[Optional[int]] = mapped_column(Integer)
    export_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    export_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())


class LinkSnapshot(Base):
    """Link snapshot table - point-in-time captures at confirmation."""

    __tablename__ = "link_snapshots"
    __table_args__ = (
        Index("idx_snapshots_confirmation", "confirmation_id"),
        Index("idx_snapshots_link", "link_id"),
        {"schema": "ctsr"},
    )

    snapshot_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    confirmation_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    link_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    instance_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    instance_state: Mapped[dict] = mapped_column(JSONB, nullable=False)
    validation_status_at: Mapped[Optional[str]] = mapped_column(String(20))
    platform_version_at: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())


class UploadLog(Base):
    """Upload log table - vendor upload processing records."""

    __tablename__ = "upload_log"
    __table_args__ = (
        Index("idx_uploads_vendor", "vendor_code"),
        Index("idx_uploads_status", "processing_status"),
        Index("idx_uploads_created", "created_at"),
        {"schema": "ctsr"},
    )

    upload_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    vendor_code: Mapped[str] = mapped_column(String(50), nullable=False)
    upload_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_name: Mapped[Optional[str]] = mapped_column(String(500))
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    processing_status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    raw_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    schema_version: Mapped[Optional[str]] = mapped_column(String(10))
    instances_in_file: Mapped[Optional[int]] = mapped_column(Integer)
    instances_created: Mapped[int] = mapped_column(Integer, default=0)
    instances_updated: Mapped[int] = mapped_column(Integer, default=0)
    instances_unchanged: Mapped[int] = mapped_column(Integer, default=0)
    validation_errors: Mapped[Optional[dict]] = mapped_column(JSONB)
    processing_started_at: Mapped[Optional[datetime]] = mapped_column()
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column()
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())


class SystemInstanceAudit(Base):
    """System instance audit table - tracks all changes."""

    __tablename__ = "system_instances_audit"
    __table_args__ = (
        Index("idx_audit_instance", "instance_id"),
        Index("idx_audit_changed", "changed_at"),
        {"schema": "ctsr"},
    )

    audit_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    instance_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String(10), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    changed_by: Mapped[Optional[str]] = mapped_column(String(200))
    old_values: Mapped[Optional[dict]] = mapped_column(JSONB)
    new_values: Mapped[Optional[dict]] = mapped_column(JSONB)
