-- ============================================================
-- GeoSDI: Expand status constraint
-- ============================================================
-- Menambahkan status baru sesuai kategori Genesis ESDM.
-- ============================================================

SET search_path TO geosdi, public;

-- Drop constraint lama
ALTER TABLE geosdi.work_areas
DROP CONSTRAINT IF EXISTS chk_status;

-- Add constraint baru dengan 8 kategori Genesis + existing
ALTER TABLE geosdi.work_areas
ADD CONSTRAINT chk_status CHECK (
    status IN (
        -- Kategori existing
        'Operasi',
        'Eksplorasi',
        'Konstruksi',
        'Perencanaan',
        'Non-Aktif',
        'Unknown',
        -- Kategori Genesis ESDM (baru)
        'Dalam Survei',
        'Penawaran/Lelang',
        'IPB Eksplorasi',
        'IPB Eksploitasi',
        'IPB Produksi',
        'Kuasa Pengusahaan',
        'Belum Ada Pemegang IPB'
    )
);

DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE '[OK] Status Constraint Expanded';
    RAISE NOTICE '   6 existing + 7 new statuses';
    RAISE NOTICE '============================================';
END
$$;