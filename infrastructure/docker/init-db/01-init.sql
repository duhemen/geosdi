-- ============================================================
-- GeoSDI Geothermal v2.0 — Database Initialization
-- ============================================================
-- File ini dijalankan OTOMATIS saat PostgreSQL container
-- pertama kali dibuat (hanya sekali).
--
-- Tugasnya:
-- 1. Aktifkan extension PostGIS (untuk data spasial)
-- 2. Buat schema `geosdi` (namespace terpisah)
-- 3. Setup user permissions
-- ============================================================

-- ----------------------------------------
-- 1. Enable Extensions
-- ----------------------------------------
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- Untuk fuzzy search

-- Cek versi PostGIS
SELECT PostGIS_Version();

-- ----------------------------------------
-- 2. Buat Schema `geosdi`
-- ----------------------------------------
-- Schema = "folder" dalam database
-- Semua tabel GeoSDI akan tinggal di sini
CREATE SCHEMA IF NOT EXISTS geosdi;

-- Set default search path
SET search_path TO geosdi, public;

-- ----------------------------------------
-- 3. Info
-- ----------------------------------------
DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE '✅ GeoSDI Database Initialized';
    RAISE NOTICE '   PostgreSQL: %', version();
    RAISE NOTICE '   PostGIS: %', PostGIS_Version();
    RAISE NOTICE '   Schema geosdi: READY';
    RAISE NOTICE '============================================';
END
$$;