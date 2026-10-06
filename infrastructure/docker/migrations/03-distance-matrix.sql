-- ============================================================
-- GeoSDI: Distance Matrix antar WKP
-- ============================================================
-- Menghitung jarak antar semua pasangan WKP menggunakan PostGIS.
-- Hasil: 6×6 matrix (diri sendiri = 0 km).
--
-- Author: Emen & DeepSeek
-- Date: 2026-10-04
-- ============================================================

SET search_path TO geosdi, public;

-- Drop view kalau sudah ada (idempotent)
DROP VIEW IF EXISTS geosdi.v_wkp_distance_matrix;

-- Buat view untuk distance matrix
CREATE OR REPLACE VIEW geosdi.v_wkp_distance_matrix AS
SELECT
    a.kode AS from_kode,
    a.nama AS from_nama,
    b.kode AS to_kode,
    b.nama AS to_nama,
    ROUND(
        (ST_Distance(a.geom::geography, b.geom::geography) / 1000.0)::numeric
    , 2) AS jarak_km
FROM geosdi.work_areas a
CROSS JOIN geosdi.work_areas b
ORDER BY a.kode, b.kode;

COMMENT ON VIEW geosdi.v_wkp_distance_matrix IS
'Matriks jarak antar WKP (km) menggunakan PostGIS ST_Distance';

-- Verifikasi
DO $$
DECLARE
    cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO cnt FROM geosdi.v_wkp_distance_matrix;
    RAISE NOTICE '============================================';
    RAISE NOTICE '✅ Distance Matrix View Created';
    RAISE NOTICE '   Total rows: %', cnt;
    RAISE NOTICE '   Expected: % (% WKP^2)', 36, 6;
    RAISE NOTICE '============================================';
END
$$;