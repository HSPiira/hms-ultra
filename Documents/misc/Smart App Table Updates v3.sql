-- Smart App Table Updates v3.sql
-- HMS Database Schema Updates for Claims Intake and Upload Tracking
-- This file contains the SQL schema for the new claims intake and tracking system

-- =============================================================================
-- SEQUENCES FOR PRIMARY KEYS
-- =============================================================================

-- Channel sequence for notification channels
CREATE SEQUENCE IF NOT EXISTS seq_channels START WITH 1 INCREMENT BY 1;

-- Staging claims sequence for claim intake tracking
CREATE SEQUENCE IF NOT EXISTS seq_staging_claims START WITH 1 INCREMENT BY 1;

-- Services sequence for service management
CREATE SEQUENCE IF NOT EXISTS seq_services START WITH 1 INCREMENT BY 1;

-- Uploads sequence for file upload tracking
CREATE SEQUENCE IF NOT EXISTS seq_uploads START WITH 1 INCREMENT BY 1;

-- Item types sequence for claim item categorization
CREATE SEQUENCE IF NOT EXISTS seq_item_types START WITH 1 INCREMENT BY 1;

-- =============================================================================
-- NOTIFICATION CHANNELS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS notification_channels (
    id BIGINT PRIMARY KEY DEFAULT nextval('seq_channels'),
    channel_name VARCHAR(100) NOT NULL UNIQUE,
    channel_type VARCHAR(50) NOT NULL CHECK (channel_type IN ('EMAIL', 'SMS', 'PUSH', 'IN_APP')),
    is_active BOOLEAN DEFAULT TRUE,
    configuration JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- STAGING CLAIMS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS staging_claims (
    id BIGINT PRIMARY KEY DEFAULT nextval('seq_staging_claims'),
    claim_number VARCHAR(100) NOT NULL UNIQUE,
    member_id VARCHAR(50) NOT NULL,
    hospital_id VARCHAR(50) NOT NULL,
    service_date DATE NOT NULL,
    claim_amount DECIMAL(15,2) NOT NULL CHECK (claim_amount >= 0),
    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    upload_id BIGINT,
    processing_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- =============================================================================
-- SERVICES TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS services (
    id BIGINT PRIMARY KEY DEFAULT nextval('seq_services'),
    service_code VARCHAR(50) NOT NULL UNIQUE,
    service_name VARCHAR(200) NOT NULL,
    service_category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- UPLOADS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS uploads (
    id BIGINT PRIMARY KEY DEFAULT nextval('seq_uploads'),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL CHECK (file_size > 0),
    file_type VARCHAR(100) NOT NULL,
    upload_path VARCHAR(500) NOT NULL,
    upload_status VARCHAR(50) DEFAULT 'PENDING' CHECK (upload_status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    uploaded_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- =============================================================================
-- ITEM TYPES TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS item_types (
    id BIGINT PRIMARY KEY DEFAULT nextval('seq_item_types'),
    type_code VARCHAR(50) NOT NULL UNIQUE,
    type_name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- FOREIGN KEY CONSTRAINTS
-- =============================================================================

-- Add foreign key constraint for staging_claims.upload_id
ALTER TABLE staging_claims 
ADD CONSTRAINT fk_staging_claims_upload 
FOREIGN KEY (upload_id) REFERENCES uploads(id) ON DELETE SET NULL;

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Index on staging_claims for common queries
CREATE INDEX IF NOT EXISTS idx_staging_claims_member_id ON staging_claims(member_id);
CREATE INDEX IF NOT EXISTS idx_staging_claims_hospital_id ON staging_claims(hospital_id);
CREATE INDEX IF NOT EXISTS idx_staging_claims_status ON staging_claims(status);
CREATE INDEX IF NOT EXISTS idx_staging_claims_service_date ON staging_claims(service_date);

-- Index on uploads for file management
CREATE INDEX IF NOT EXISTS idx_uploads_status ON uploads(upload_status);
CREATE INDEX IF NOT EXISTS idx_uploads_uploaded_by ON uploads(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_uploads_created_at ON uploads(created_at);

-- Index on services for lookup performance
CREATE INDEX IF NOT EXISTS idx_services_code ON services(service_code);
CREATE INDEX IF NOT EXISTS idx_services_active ON services(is_active);

-- Index on item_types for categorization
CREATE INDEX IF NOT EXISTS idx_item_types_code ON item_types(type_code);
CREATE INDEX IF NOT EXISTS idx_item_types_active ON item_types(is_active);

-- =============================================================================
-- SEED DATA
-- =============================================================================

-- Insert default notification channels
INSERT INTO notification_channels (channel_name, channel_type, is_active, configuration) VALUES
('Email Channel', 'EMAIL', TRUE, '{"smtp_server": "localhost", "port": 587}'),
('SMS Channel', 'SMS', TRUE, '{"provider": "twilio", "api_key": "placeholder"}'),
('Push Channel', 'PUSH', TRUE, '{"provider": "fcm", "api_key": "placeholder"}')
ON CONFLICT (channel_name) DO NOTHING;

-- Insert default services
INSERT INTO services (service_code, service_name, service_category, is_active, description) VALUES
('CONSULTATION', 'Medical Consultation', 'OUTPATIENT', TRUE, 'General medical consultation services'),
('LABORATORY', 'Laboratory Tests', 'DIAGNOSTIC', TRUE, 'Various laboratory diagnostic tests'),
('RADIOLOGY', 'Radiology Services', 'DIAGNOSTIC', TRUE, 'X-ray, MRI, CT scan services'),
('SURGERY', 'Surgical Procedures', 'INPATIENT', TRUE, 'Various surgical procedures'),
('EMERGENCY', 'Emergency Services', 'EMERGENCY', TRUE, 'Emergency medical services')
ON CONFLICT (service_code) DO NOTHING;

-- Insert default item types
INSERT INTO item_types (type_code, type_name, category, is_active, description) VALUES
('MEDICATION', 'Medications', 'PHARMACY', TRUE, 'Prescription and over-the-counter medications'),
('PROCEDURE', 'Medical Procedures', 'MEDICAL', TRUE, 'Medical procedures and treatments'),
('DIAGNOSTIC', 'Diagnostic Tests', 'DIAGNOSTIC', TRUE, 'Laboratory and diagnostic tests'),
('CONSULTATION', 'Consultation Fees', 'SERVICE', TRUE, 'Medical consultation fees'),
('EMERGENCY', 'Emergency Services', 'EMERGENCY', TRUE, 'Emergency medical services')
ON CONFLICT (type_code) DO NOTHING;

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_notification_channels_updated_at 
    BEFORE UPDATE ON notification_channels 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_staging_claims_updated_at 
    BEFORE UPDATE ON staging_claims 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_services_updated_at 
    BEFORE UPDATE ON services 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_item_types_updated_at 
    BEFORE UPDATE ON item_types 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- View for active notification channels
CREATE OR REPLACE VIEW active_notification_channels AS
SELECT id, channel_name, channel_type, configuration
FROM notification_channels 
WHERE is_active = TRUE;

-- View for pending staging claims
CREATE OR REPLACE VIEW pending_staging_claims AS
SELECT 
    sc.id,
    sc.claim_number,
    sc.member_id,
    sc.hospital_id,
    sc.service_date,
    sc.claim_amount,
    sc.status,
    sc.created_at,
    u.filename as upload_filename
FROM staging_claims sc
LEFT JOIN uploads u ON sc.upload_id = u.id
WHERE sc.status = 'PENDING';

-- View for claim processing statistics
CREATE OR REPLACE VIEW claim_processing_stats AS
SELECT 
    status,
    COUNT(*) as claim_count,
    SUM(claim_amount) as total_amount,
    AVG(claim_amount) as average_amount
FROM staging_claims 
GROUP BY status;

-- =============================================================================
-- SAMPLE DATA FOR TESTING
-- =============================================================================

-- Insert sample staging claims
INSERT INTO staging_claims (claim_number, member_id, hospital_id, service_date, claim_amount, status) VALUES
('CLM-2024-001', 'MEM-001', 'HOSP-001', '2024-01-15', 1500.00, 'PENDING'),
('CLM-2024-002', 'MEM-002', 'HOSP-002', '2024-01-16', 2300.50, 'PROCESSING'),
('CLM-2024-003', 'MEM-003', 'HOSP-001', '2024-01-17', 850.75, 'COMPLETED')
ON CONFLICT (claim_number) DO NOTHING;

-- Insert sample uploads
INSERT INTO uploads (filename, original_filename, file_size, file_type, upload_path, upload_status, uploaded_by) VALUES
('claim_001.pdf', 'claim_001.pdf', 1024000, 'application/pdf', '/uploads/claims/claim_001.pdf', 'COMPLETED', 'admin'),
('claim_002.pdf', 'claim_002.pdf', 2048000, 'application/pdf', '/uploads/claims/claim_002.pdf', 'PROCESSING', 'user1'),
('claim_003.pdf', 'claim_003.pdf', 1536000, 'application/pdf', '/uploads/claims/claim_003.pdf', 'PENDING', 'user2')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- COMMENTS AND DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE notification_channels IS 'Stores notification channel configurations for the HMS system';
COMMENT ON TABLE staging_claims IS 'Temporary storage for claims during intake and processing';
COMMENT ON TABLE services IS 'Master list of medical services available in the system';
COMMENT ON TABLE uploads IS 'Tracks file uploads and their processing status';
COMMENT ON TABLE item_types IS 'Categorization of claim items and services';

COMMENT ON COLUMN staging_claims.claim_number IS 'Unique identifier for the claim';
COMMENT ON COLUMN staging_claims.status IS 'Current processing status of the claim';
COMMENT ON COLUMN uploads.upload_status IS 'Current status of the file upload and processing';

-- =============================================================================
-- GRANTS AND PERMISSIONS (if needed)
-- =============================================================================

-- Example grants (adjust based on your security requirements)
-- GRANT SELECT, INSERT, UPDATE ON staging_claims TO hms_user;
-- GRANT SELECT ON services TO hms_user;
-- GRANT SELECT ON item_types TO hms_user;
