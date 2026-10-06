-- ============================================================
-- GeoSDI: Add data quality column
-- ============================================================
-- Menambahkan kolom untuk tracking kualitas data WKP.
-- Nilai: 'verified' | 'estimated' | 'user_provided'
-- ============================================================

SET search_path TO geosdi, public;

-- Tambah kolom data_quality ke work_areas
ALTER TABLE geosdi.work_areas
ADD COLUMN IF NOT EXISTS data_quality VARCHAR(20) DEFAULT 'user_provided';

-- Set default untuk WKP yang sudah ada (dari Wikipedia = verified)
UPDATE geosdi.work_areas
SET data_quality = 'verified'
WHERE data_quality = 'user_provided' AND kode LIKE 'WKP%';

-- Tambah index
CREATE INDEX IF NOT EXISTS idx_work_areas_data_quality
ON geosdi.work_areas (data_quality);

-- Tambah kolom source
ALTER TABLE geosdi.work_areas
ADD COLUMN IF NOT EXISTS source VARCHAR(50) DEFAULT 'user_provided';

-- Set source untuk WKP Wikipedia
UPDATE geosdi.work_areas
SET source = 'wikipedia'
WHERE source = 'user_provided' AND kode LIKE 'WKP%';

DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE '[OK] Data Quality Columns Added';
    RAISE NOTICE '   - data_quality (verified/estimated/user_provided)';
    RAISE NOTICE '   - source (wikipedia/esdm/genesis/user_provided)';
    RAISE NOTICE '============================================';
END
$$;