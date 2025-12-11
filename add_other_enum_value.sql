-- Manual SQL script to add 'Other' to qualityclassenum
-- Run this if the Alembic migration doesn't work due to transaction issues

-- Method 1: Try adding directly (PostgreSQL 12+)
ALTER TYPE qualityclassenum ADD VALUE IF NOT EXISTS 'Other';

-- Method 2: If Method 1 fails, use this (works in transaction)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumlabel = 'Other' 
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'qualityclassenum')
    ) THEN
        ALTER TYPE qualityclassenum ADD VALUE 'Other';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        NULL;
    WHEN OTHERS THEN
        RAISE;
END $$;

-- Verify it was added
SELECT enumlabel 
FROM pg_enum 
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'qualityclassenum')
ORDER BY enumsortorder;

