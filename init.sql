-- HMS Ultra Database Initialization Script
-- PostgreSQL initialization for HMS Ultra application
-- This script runs when the PostgreSQL container starts for the first time

-- =============================================================================
-- DATABASE INITIALIZATION
-- =============================================================================

-- Create the database if it doesn't exist (this is handled by POSTGRES_DB env var)
-- The database 'hms_ultra' will be created automatically by PostgreSQL

-- =============================================================================
-- EXTENSIONS
-- =============================================================================

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm extension for text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable unaccent extension for text search without accents
CREATE EXTENSION IF NOT EXISTS unaccent;

-- =============================================================================
-- CUSTOM FUNCTIONS
-- =============================================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =============================================================================
-- INITIAL DATA
-- =============================================================================

-- Create initial admin user (password will be set by Django management commands)
-- This is just a placeholder - actual user creation should be done via Django

-- =============================================================================
-- PERMISSIONS
-- =============================================================================

-- Grant necessary permissions to the database user
-- These permissions will be granted to the user specified in POSTGRES_USER

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON DATABASE hms_ultra IS 'HMS Ultra Healthcare Management System Database';
COMMENT ON EXTENSION "uuid-ossp" IS 'UUID generation functions';
COMMENT ON EXTENSION pg_trgm IS 'Text similarity measurement and index searching based on trigrams';
COMMENT ON EXTENSION unaccent IS 'Text search dictionary that removes accents';
