-- SQL Schema Validation Script
-- Validates that all primary keys and foreign keys are properly defined

-- Check Primary Key Constraints
SELECT 
    table_name,
    constraint_name,
    constraint_type
FROM user_constraints 
WHERE constraint_type = 'P'
AND table_name IN (
    'CLAIM_CHANNELS',
    'STG_CLAIMS', 
    'STG_CLAIMSSERVICES',
    'SERVICE_ITEM_UPLOADS',
    'SERVICE_ITEM_TYPES'
)
ORDER BY table_name;

-- Check Foreign Key Constraints  
SELECT 
    table_name,
    constraint_name,
    r_constraint_name,
    constraint_type
FROM user_constraints 
WHERE constraint_type = 'R'
AND table_name IN (
    'STG_CLAIMS',
    'STG_CLAIMSSERVICES', 
    'SERVICE_ITEM_UPLOADS'
)
ORDER BY table_name;

-- Check Sequences
SELECT 
    sequence_name,
    last_number,
    increment_by
FROM user_sequences
WHERE sequence_name IN (
    'SQCLAIMCHANNELSID',
    'SQSTGCLAIMSID',
    'SQSTGCLAIMSSERVICEID', 
    'SQSERVICEITEMUPLOADSID',
    'SQSERVICE_ITEM_TYPESID'
)
ORDER BY sequence_name;

-- Validate Data Integrity
-- Check for duplicate primary keys
SELECT 'CLAIM_CHANNELS' as table_name, COUNT(*) as total_rows, COUNT(DISTINCT id) as unique_ids
FROM claim_channels
UNION ALL
SELECT 'STG_CLAIMS', COUNT(*), COUNT(DISTINCT id)
FROM stg_claims  
UNION ALL
SELECT 'STG_CLAIMSSERVICES', COUNT(*), COUNT(DISTINCT id)
FROM stg_claimsservices
UNION ALL
SELECT 'SERVICE_ITEM_UPLOADS', COUNT(*), COUNT(DISTINCT id)
FROM service_item_uploads
UNION ALL
SELECT 'SERVICE_ITEM_TYPES', COUNT(*), COUNT(DISTINCT id)
FROM service_item_types;

-- Check Foreign Key Integrity
-- Verify all foreign key references are valid
SELECT 'STG_CLAIMS -> CLAIM_CHANNELS' as relationship,
       COUNT(*) as total_rows,
       COUNT(CASE WHEN channelid IS NOT NULL THEN 1 END) as with_fk,
       COUNT(CASE WHEN channelid IS NULL THEN 1 END) as null_fk
FROM stg_claims
UNION ALL
SELECT 'STG_CLAIMSSERVICES -> STG_CLAIMS',
       COUNT(*),
       COUNT(CASE WHEN claimid IS NOT NULL THEN 1 END),
       COUNT(CASE WHEN claimid IS NULL THEN 1 END)
FROM stg_claimsservices
UNION ALL  
SELECT 'SERVICE_ITEM_UPLOADS -> SERVICE_ITEM_TYPES',
       COUNT(*),
       COUNT(CASE WHEN item_type IS NOT NULL THEN 1 END),
       COUNT(CASE WHEN item_type IS NULL THEN 1 END)
FROM service_item_uploads
UNION ALL
SELECT 'SERVICE_ITEM_UPLOADS -> CLAIM_CHANNELS', 
       COUNT(*),
       COUNT(CASE WHEN channel_id IS NOT NULL THEN 1 END),
       COUNT(CASE WHEN channel_id IS NULL THEN 1 END)
FROM service_item_uploads;

-- Test Sequence Functionality
-- Verify sequences are working correctly
SELECT 
    'CLAIM_CHANNELS' as table_name,
    MAX(id) as max_id,
    sqclaimchannelsid.nextval as next_sequence_value
FROM claim_channels
UNION ALL
SELECT 
    'STG_CLAIMS',
    MAX(id),
    sqstgclaimsid.nextval  
FROM stg_claims
UNION ALL
SELECT
    'STG_CLAIMSSERVICES', 
    MAX(id),
    sqstgclaimsserviceid.nextval
FROM stg_claimsservices
UNION ALL
SELECT
    'SERVICE_ITEM_UPLOADS',
    MAX(id), 
    sqserviceitemuploadsid.nextval
FROM service_item_uploads
UNION ALL
SELECT
    'SERVICE_ITEM_TYPES',
    MAX(id),
    sqservice_item_typesid.nextval  
FROM service_item_types;
