-- ========================================
-- PRE-MIGRATION 004 BACKUP
-- Created: 2025-10-04
-- Purpose: Backup existing data before video_projects migration
-- ========================================

-- IMPORTANT: Run these queries to backup data before migration 004
-- These can be used to restore if migration fails

-- Backup folders table
CREATE TABLE IF NOT EXISTS folders_backup_20251004 AS
SELECT * FROM folders;

-- Backup folder_links table
CREATE TABLE IF NOT EXISTS folder_links_backup_20251004 AS
SELECT * FROM folder_links;

-- Backup urls table (just in case)
CREATE TABLE IF NOT EXISTS urls_backup_20251004 AS
SELECT * FROM urls;

-- Backup clicks table (just in case)
CREATE TABLE IF NOT EXISTS clicks_backup_20251004 AS
SELECT * FROM clicks;

-- Verification queries
DO $$
BEGIN
    RAISE NOTICE '✅ Backup completed successfully!';
    RAISE NOTICE 'Folders backed up: %', (SELECT COUNT(*) FROM folders_backup_20251004);
    RAISE NOTICE 'Folder links backed up: %', (SELECT COUNT(*) FROM folder_links_backup_20251004);
    RAISE NOTICE 'URLs backed up: %', (SELECT COUNT(*) FROM urls_backup_20251004);
    RAISE NOTICE 'Clicks backed up: %', (SELECT COUNT(*) FROM clicks_backup_20251004);
END $$;

-- ========================================
-- ROLLBACK PROCEDURE (if needed)
-- ========================================

/*
-- To rollback migration 004, run:

-- 1. Drop new tables
DROP TABLE IF EXISTS project_links CASCADE;
DROP TABLE IF EXISTS video_projects CASCADE;

-- 2. Restore folders and folder_links
TRUNCATE folders CASCADE;
INSERT INTO folders SELECT * FROM folders_backup_20251004;

TRUNCATE folder_links CASCADE;
INSERT INTO folder_links SELECT * FROM folder_links_backup_20251004;

-- 3. Verify restoration
SELECT COUNT(*) FROM folders; -- Should match backup count
SELECT COUNT(*) FROM folder_links; -- Should match backup count
*/
