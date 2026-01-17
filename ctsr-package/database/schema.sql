-- =============================================================================
-- Clinical Trial Systems Register (CTSR) - PostgreSQL Schema
-- =============================================================================
-- Target: Azure Database for PostgreSQL Flexible Server (v15+)
-- Version: 1.1
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- Schema
-- =============================================================================
CREATE SCHEMA IF NOT EXISTS ctsr;
SET search_path TO ctsr, public;

-- =============================================================================
-- Lookup Tables
-- =============================================================================

CREATE TABLE lkp_system_category (
    category_code       VARCHAR(20) PRIMARY KEY,
    category_name       VARCHAR(100) NOT NULL,
    description         VARCHAR(500),
    default_criticality VARCHAR(10) NOT NULL DEFAULT 'STD',
    sort_order          INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE lkp_validation_status (
    status_code         VARCHAR(20) PRIMARY KEY,
    status_name         VARCHAR(100) NOT NULL,
    description         VARCHAR(500),
    requires_attention  BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order          INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE lkp_criticality (
    criticality_code    VARCHAR(10) PRIMARY KEY,
    criticality_name    VARCHAR(50) NOT NULL,
    description         VARCHAR(500),
    sort_order          INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE
);

-- =============================================================================
-- Core Tables
-- =============================================================================

-- Vendors (platform owners, service providers, internal)
CREATE TABLE vendors (
    vendor_id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_code         VARCHAR(50) NOT NULL UNIQUE,
    vendor_name         VARCHAR(200) NOT NULL,
    vendor_type         VARCHAR(20) NOT NULL CHECK (vendor_type IN (
                            'CRO', 'FSP', 'TECH_VENDOR', 'CENTRAL_LAB', 
                            'IMAGING', 'ECG_VENDOR', 'BIOANALYTICAL', 
                            'LOGISTICS', 'SPECIALTY', 'INTERNAL')),
    contact_name        VARCHAR(200),
    contact_email       VARCHAR(200),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(200),
    updated_by          VARCHAR(200)
);

CREATE INDEX idx_vendors_code ON vendors(vendor_code);
CREATE INDEX idx_vendors_type ON vendors(vendor_type) WHERE is_active = TRUE;

-- System Instances (the catalog)
CREATE TABLE system_instances (
    instance_id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    instance_code           VARCHAR(100) NOT NULL UNIQUE,
    platform_vendor_id      UUID REFERENCES vendors(vendor_id),
    service_provider_id     UUID REFERENCES vendors(vendor_id),
    category_code           VARCHAR(20) NOT NULL REFERENCES lkp_system_category(category_code),
    platform_name           VARCHAR(200) NOT NULL,
    platform_version        VARCHAR(50),
    instance_name           VARCHAR(200),
    instance_environment    VARCHAR(20) DEFAULT 'PRODUCTION' CHECK (instance_environment IN (
                                'PRODUCTION', 'VALIDATION', 'UAT', 'DEV')),
    validation_status_code  VARCHAR(20) NOT NULL REFERENCES lkp_validation_status(status_code),
    validation_date         DATE,
    validation_expiry       DATE,
    validation_evidence_link VARCHAR(500),
    hosting_model           VARCHAR(20) CHECK (hosting_model IN (
                                'SAAS', 'SAAS_ST', 'PAAS', 'IAAS', 'ON_PREM', 'HYBRID')),
    data_hosting_region     VARCHAR(20) CHECK (data_hosting_region IN (
                                'EU', 'US', 'CHINA', 'APAC_OTHER', 'UK', 'GLOBAL_DISTRIBUTED')),
    description             TEXT,
    supported_studies       TEXT[],
    interfaces              JSONB,
    part11_compliant        BOOLEAN,
    annex11_compliant       BOOLEAN,
    soc2_certified          BOOLEAN,
    iso27001_certified      BOOLEAN,
    last_major_change_date  DATE,
    last_major_change_desc  VARCHAR(500),
    next_planned_change_date DATE,
    next_planned_change_desc VARCHAR(500),
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by              VARCHAR(200),
    updated_by              VARCHAR(200)
);

CREATE INDEX idx_instances_code ON system_instances(instance_code);
CREATE INDEX idx_instances_category ON system_instances(category_code) WHERE is_active = TRUE;
CREATE INDEX idx_instances_validation ON system_instances(validation_status_code) WHERE is_active = TRUE;
CREATE INDEX idx_instances_platform_vendor ON system_instances(platform_vendor_id);
CREATE INDEX idx_instances_service_provider ON system_instances(service_provider_id);
CREATE INDEX idx_instances_hosting_region ON system_instances(data_hosting_region) WHERE is_active = TRUE;

-- Trials (synced from CTMS)
CREATE TABLE trials (
    trial_id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    protocol_number         VARCHAR(50) NOT NULL UNIQUE,
    trial_title             VARCHAR(500) NOT NULL,
    trial_phase             VARCHAR(20),
    trial_status            VARCHAR(20) NOT NULL DEFAULT 'PLANNED' CHECK (trial_status IN (
                                'PLANNED', 'ACTIVE', 'DB_LOCKED', 'CLOSED')),
    therapeutic_area        VARCHAR(100),
    indication              VARCHAR(200),
    trial_start_date        DATE,
    planned_db_lock_date    DATE,
    actual_db_lock_date     DATE,
    trial_close_date        DATE,
    trial_lead_name         VARCHAR(200),
    trial_lead_email        VARCHAR(200),
    ctms_trial_id           VARCHAR(100),
    last_ctms_sync          TIMESTAMPTZ,
    next_confirmation_due   DATE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_trials_protocol ON trials(protocol_number);
CREATE INDEX idx_trials_status ON trials(trial_status);
CREATE INDEX idx_trials_lead ON trials(trial_lead_email);
CREATE INDEX idx_trials_confirmation_due ON trials(next_confirmation_due) 
    WHERE trial_status = 'ACTIVE';

-- Trial-System Links
CREATE TABLE trial_system_links (
    link_id                     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trial_id                    UUID NOT NULL REFERENCES trials(trial_id),
    instance_id                 UUID NOT NULL REFERENCES system_instances(instance_id),
    assignment_status           VARCHAR(30) NOT NULL DEFAULT 'ACTIVE' CHECK (assignment_status IN (
                                    'ACTIVE', 'CONFIRMED', 'PENDING_CONFIRMATION', 'REPLACED', 'LOCKED')),
    criticality_code            VARCHAR(10) NOT NULL REFERENCES lkp_criticality(criticality_code),
    criticality_override_reason VARCHAR(500),
    usage_start_date            DATE NOT NULL DEFAULT CURRENT_DATE,
    usage_end_date              DATE,
    linked_by                   VARCHAR(200),
    linked_at                   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    unlinked_by                 VARCHAR(200),
    unlinked_at                 TIMESTAMPTZ,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_links_trial ON trial_system_links(trial_id);
CREATE INDEX idx_links_instance ON trial_system_links(instance_id);
CREATE INDEX idx_links_status ON trial_system_links(assignment_status);

-- Ensure only one active link per trial+instance combination
CREATE UNIQUE INDEX idx_links_unique_active 
    ON trial_system_links(trial_id, instance_id) 
    WHERE assignment_status NOT IN ('REPLACED', 'LOCKED');

-- Confirmations
CREATE TABLE confirmations (
    confirmation_id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trial_id                UUID NOT NULL REFERENCES trials(trial_id),
    confirmation_type       VARCHAR(20) NOT NULL CHECK (confirmation_type IN ('PERIODIC', 'DB_LOCK')),
    confirmation_status     VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (confirmation_status IN (
                                'PENDING', 'COMPLETED', 'OVERDUE')),
    due_date                DATE,
    confirmed_date          DATE,
    confirmed_by            VARCHAR(200),
    notes                   TEXT,
    systems_count           INTEGER,
    validation_alerts_count INTEGER,
    export_generated        BOOLEAN DEFAULT FALSE,
    export_id               UUID,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_confirmations_trial ON confirmations(trial_id);
CREATE INDEX idx_confirmations_status ON confirmations(confirmation_status);
CREATE INDEX idx_confirmations_due ON confirmations(due_date) WHERE confirmation_status = 'PENDING';

-- Link Snapshots (point-in-time capture at confirmation)
CREATE TABLE link_snapshots (
    snapshot_id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    confirmation_id         UUID NOT NULL REFERENCES confirmations(confirmation_id),
    link_id                 UUID NOT NULL REFERENCES trial_system_links(link_id),
    instance_id             UUID NOT NULL REFERENCES system_instances(instance_id),
    instance_state          JSONB NOT NULL,
    validation_status_at    VARCHAR(20),
    platform_version_at     VARCHAR(50),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_snapshots_confirmation ON link_snapshots(confirmation_id);
CREATE INDEX idx_snapshots_link ON link_snapshots(link_id);

-- Upload Log
CREATE TABLE upload_log (
    upload_id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_code             VARCHAR(50) NOT NULL,
    upload_type             VARCHAR(20) NOT NULL CHECK (upload_type IN ('FULL', 'INCREMENTAL')),
    file_name               VARCHAR(500),
    file_size_bytes         BIGINT,
    processing_status       VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (processing_status IN (
                                'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    raw_json                JSONB,
    schema_version          VARCHAR(10),
    instances_in_file       INTEGER,
    instances_created       INTEGER DEFAULT 0,
    instances_updated       INTEGER DEFAULT 0,
    instances_unchanged     INTEGER DEFAULT 0,
    validation_errors       JSONB,
    processing_started_at   TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    error_message           TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_uploads_vendor ON upload_log(vendor_code);
CREATE INDEX idx_uploads_status ON upload_log(processing_status);
CREATE INDEX idx_uploads_created ON upload_log(created_at DESC);

-- =============================================================================
-- Audit Table for System Instances
-- =============================================================================

CREATE TABLE system_instances_audit (
    audit_id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    instance_id             UUID NOT NULL,
    action                  VARCHAR(10) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    changed_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    changed_by              VARCHAR(200),
    old_values              JSONB,
    new_values              JSONB
);

CREATE INDEX idx_audit_instance ON system_instances_audit(instance_id);
CREATE INDEX idx_audit_changed ON system_instances_audit(changed_at DESC);

-- Audit trigger function
CREATE OR REPLACE FUNCTION fn_audit_system_instances()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO system_instances_audit (instance_id, action, changed_by, new_values)
        VALUES (NEW.instance_id, 'INSERT', NEW.created_by, to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO system_instances_audit (instance_id, action, changed_by, old_values, new_values)
        VALUES (NEW.instance_id, 'UPDATE', NEW.updated_by, to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO system_instances_audit (instance_id, action, old_values)
        VALUES (OLD.instance_id, 'DELETE', to_jsonb(OLD));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_system_instances
AFTER INSERT OR UPDATE OR DELETE ON system_instances
FOR EACH ROW EXECUTE FUNCTION fn_audit_system_instances();

-- =============================================================================
-- Useful Views
-- =============================================================================

-- System instances with vendor names
CREATE VIEW v_system_instances AS
SELECT 
    si.*,
    pv.vendor_name AS platform_vendor_name,
    pv.vendor_code AS platform_vendor_code,
    sp.vendor_name AS service_provider_name,
    sp.vendor_code AS service_provider_code,
    sc.category_name,
    sc.default_criticality,
    vs.status_name AS validation_status_name,
    vs.requires_attention AS validation_requires_attention
FROM system_instances si
LEFT JOIN vendors pv ON si.platform_vendor_id = pv.vendor_id
LEFT JOIN vendors sp ON si.service_provider_id = sp.vendor_id
LEFT JOIN lkp_system_category sc ON si.category_code = sc.category_code
LEFT JOIN lkp_validation_status vs ON si.validation_status_code = vs.status_code;

-- Trial systems with full details
CREATE VIEW v_trial_systems AS
SELECT 
    tsl.*,
    t.protocol_number,
    t.trial_title,
    t.trial_status,
    si.instance_code,
    si.platform_name,
    si.platform_version,
    si.category_code,
    si.validation_status_code,
    si.data_hosting_region,
    lc.criticality_name
FROM trial_system_links tsl
JOIN trials t ON tsl.trial_id = t.trial_id
JOIN system_instances si ON tsl.instance_id = si.instance_id
LEFT JOIN lkp_criticality lc ON tsl.criticality_code = lc.criticality_code;

-- Trials with confirmation status
CREATE VIEW v_trials_confirmation_status AS
SELECT 
    t.*,
    CASE 
        WHEN t.next_confirmation_due < CURRENT_DATE THEN 'OVERDUE'
        WHEN t.next_confirmation_due <= CURRENT_DATE + INTERVAL '14 days' THEN 'DUE_SOON'
        ELSE 'OK'
    END AS confirmation_status,
    (SELECT COUNT(*) FROM trial_system_links tsl 
     WHERE tsl.trial_id = t.trial_id AND tsl.assignment_status NOT IN ('REPLACED', 'LOCKED')) AS active_systems_count
FROM trials t
WHERE t.trial_status = 'ACTIVE';

-- =============================================================================
-- Seed Data
-- =============================================================================

-- System Categories
INSERT INTO lkp_system_category (category_code, category_name, description, default_criticality, sort_order) VALUES
('EDC', 'Electronic Data Capture', 'Primary clinical data collection systems', 'CRIT', 1),
('eCOA', 'Electronic Clinical Outcome Assessment', 'Patient-reported outcomes, ePRO, eClinRO', 'CRIT', 2),
('eDIARY', 'Electronic Patient Diary', 'Patient diary applications', 'CRIT', 3),
('eSOURCE', 'eSource / Direct Data Capture', 'Direct capture from EHR/EMR', 'CRIT', 4),
('IRT', 'Interactive Response Technology', 'Randomization and trial supply (RTSM/IWRS)', 'CRIT', 5),
('CTMS', 'Clinical Trial Management System', 'Trial operations management', 'MAJ', 6),
('TMF', 'Trial Master File', 'Electronic TMF systems', 'MAJ', 7),
('SITE', 'Site Management / Feasibility', 'Site selection and management', 'STD', 8),
('SAFETY', 'Safety Database / Pharmacovigilance', 'Adverse event and safety reporting', 'CRIT', 9),
('SAE_REPORT', 'SAE Collection & Reporting', 'Serious adverse event collection', 'CRIT', 10),
('LAB', 'Central Laboratory LIMS', 'Laboratory information management', 'CRIT', 11),
('BIOBANK', 'Biomarker / Sample Management', 'Biological sample tracking', 'MAJ', 12),
('ECG', 'Central ECG Processing', 'Electrocardiogram analysis', 'CRIT', 13),
('IMG', 'Medical Imaging / Central Read', 'Imaging and radiology review', 'CRIT', 14),
('PK', 'Pharmacokinetic Data Management', 'PK/PD analysis systems', 'MAJ', 15),
('CODING', 'Medical Coding', 'MedDRA, WHODrug coding', 'MAJ', 16),
('STAT', 'Statistical Analysis Environment', 'SAS, R, statistical platforms', 'MAJ', 17),
('SUB', 'Regulatory Submissions', 'eCTD and submission systems', 'STD', 18),
('TELE', 'Telemedicine / Virtual Visits', 'Remote visit platforms', 'MAJ', 19),
('eCONSENT', 'Electronic Informed Consent', 'eConsent platforms', 'CRIT', 20),
('DHT', 'Digital Health Technology', 'Wearables and sensors', 'MAJ', 21),
('RPM', 'Remote Patient Monitoring', 'Remote monitoring platforms', 'MAJ', 22),
('DTP', 'Direct-to-Patient Portal', 'Patient portals and drug delivery', 'MAJ', 23),
('IDMC', 'Data Monitoring Committee', 'IDMC/DSMB platforms', 'MAJ', 24),
('ADJUD', 'Endpoint Adjudication', 'Clinical endpoint adjudication', 'MAJ', 25),
('TRAIN', 'Training Management', 'GCP and protocol training', 'STD', 26),
('ARCHIVE', 'Long-term Data Archive', 'Data archival systems', 'STD', 27),
('INTEG', 'Integration Platform', 'Data integration and ETL', 'STD', 28),
('OTHER', 'Other', 'Other system types', 'STD', 99);

-- Validation Statuses
INSERT INTO lkp_validation_status (status_code, status_name, description, requires_attention, sort_order) VALUES
('VALIDATED', 'Validated', 'System is validated and current', FALSE, 1),
('VAL_PLANNED', 'Validation Planned', 'Validation is scheduled', FALSE, 2),
('VAL_IN_PROGRESS', 'Validation In Progress', 'Validation activities ongoing', FALSE, 3),
('VAL_EXPIRED', 'Validation Expired', 'Validation has expired, re-assessment needed', TRUE, 4),
('NOT_VALIDATED', 'Not Validated', 'System has not been validated', TRUE, 5),
('DECOMMISSIONED', 'Decommissioned', 'System is no longer in use', FALSE, 6);

-- Criticality Levels
INSERT INTO lkp_criticality (criticality_code, criticality_name, description, sort_order) VALUES
('CRIT', 'Critical', 'Direct impact on participant safety and/or primary endpoint data integrity', 1),
('MAJ', 'Major', 'Impact on secondary endpoints, regulatory compliance, or trial operations', 2),
('STD', 'Standard', 'Supporting functions with indirect impact on trial quality', 3);

-- =============================================================================
-- Sample Data (Optional - for development/testing)
-- =============================================================================

-- Sample Vendors
INSERT INTO vendors (vendor_code, vendor_name, vendor_type, contact_email) VALUES
('MEDIDATA', 'Medidata Solutions', 'TECH_VENDOR', 'support@medidata.com'),
('VEEVA', 'Veeva Systems', 'TECH_VENDOR', 'support@veeva.com'),
('ICON_CRO', 'ICON plc', 'CRO', 'ctsr@iconplc.com'),
('IQVIA_CRO', 'IQVIA', 'CRO', 'ctsr@iqvia.com'),
('LABCORP', 'LabCorp Drug Development', 'CENTRAL_LAB', 'ctsr@labcorp.com'),
('CLARIO', 'Clario', 'TECH_VENDOR', 'support@clario.com'),
('INTERNAL', 'Internal (Novo Nordisk)', 'INTERNAL', 'rnd-it@novonordisk.com');
