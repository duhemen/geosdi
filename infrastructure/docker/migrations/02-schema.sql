-- ============================================================
-- GeoSDI Geothermal v2.0 — Schema Definition
-- ============================================================
-- File ini mendefinisikan struktur tabel untuk GeoSDI.
-- Dijalankan SETELAH 01-init.sql (yang buat schema + PostGIS).
--
-- Struktur:
--   geosdi.work_areas     — Wilayah Kerja Panas Bumi (WKP)
--   geosdi.wells          — Sumur (produksi, injeksi, eksplorasi)
--   geosdi.power_plants   — PLTP (Pembangkit Listrik Tenaga Panas Bumi)
--   geosdi.observations   — Observasi, event, survey, monitoring
--
-- Author: Emen & DeepSeek
-- Date: 2026-10-04
-- ============================================================

-- Set schema default
SET search_path TO geosdi, public;

-- ============================================================
-- TABLE 1: work_areas (Wilayah Kerja Panas Bumi)
-- ============================================================
-- Ini adalah tabel utama. Setiap WKP di Indonesia punya satu row.

CREATE TABLE IF NOT EXISTS geosdi.work_areas (
    -- Primary Key
    id              SERIAL PRIMARY KEY,

    -- Identifikasi
    kode            VARCHAR(20) UNIQUE NOT NULL,        -- ex: WKP001
    nama            VARCHAR(200) NOT NULL,              -- ex: Kamojang
    provinsi        VARCHAR(100) NOT NULL,
    kabupaten       VARCHAR(100),

    -- Status & Operasional
    status          VARCHAR(50) NOT NULL DEFAULT 'Unknown',
                    -- Nilai: Operasi, Eksplorasi, Konstruksi, Perencanaan, Non-Aktif
    kapasitas_mw    DECIMAL(10, 2),                     -- Kapasitas terpasang (MW)
    potensi_mw      DECIMAL(10, 2),                     -- Potensi total (MW)
    tahun_operasi   INTEGER,                            -- Tahun mulai operasi

    -- Geospasial
    geom            GEOMETRY(POINT, 4326),              -- Koordinat WGS84
    luas_km2        DECIMAL(10, 2),                     -- Luas area (km²)

    -- Metadata
    keterangan      TEXT,
    metadata        JSONB DEFAULT '{}'::jsonb,          -- Field dinamis

    -- Audit
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_status CHECK (
        status IN ('Operasi', 'Eksplorasi', 'Konstruksi', 'Perencanaan', 'Non-Aktif', 'Unknown')
    ),
    CONSTRAINT chk_kapasitas CHECK (kapasitas_mw IS NULL OR kapasitas_mw >= 0),
    CONSTRAINT chk_potensi CHECK (potensi_mw IS NULL OR potensi_mw >= 0)
);

-- Index untuk performa
CREATE INDEX IF NOT EXISTS idx_work_areas_geom ON geosdi.work_areas USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_work_areas_provinsi ON geosdi.work_areas (provinsi);
CREATE INDEX IF NOT EXISTS idx_work_areas_status ON geosdi.work_areas (status);
CREATE INDEX IF NOT EXISTS idx_work_areas_nama ON geosdi.work_areas (nama);
CREATE INDEX IF NOT EXISTS idx_work_areas_metadata ON geosdi.work_areas USING GIN (metadata);

-- Trigger untuk auto-update updated_at
CREATE OR REPLACE FUNCTION geosdi.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_work_areas_updated_at ON geosdi.work_areas;
CREATE TRIGGER trg_work_areas_updated_at
    BEFORE UPDATE ON geosdi.work_areas
    FOR EACH ROW
    EXECUTE FUNCTION geosdi.update_updated_at();

-- Komentar tabel
COMMENT ON TABLE geosdi.work_areas IS 'Wilayah Kerja Panas Bumi (WKP) di Indonesia';
COMMENT ON COLUMN geosdi.work_areas.geom IS 'Koordinat WGS84 (EPSG:4326)';
COMMENT ON COLUMN geosdi.work_areas.metadata IS 'Field tambahan (JSONB) untuk data yang fleksibel';

-- ============================================================
-- TABLE 2: wells (Sumur Geothermal)
-- ============================================================
-- Setiap WKP punya banyak sumur: produksi, injeksi, eksplorasi.

CREATE TABLE IF NOT EXISTS geosdi.wells (
    -- Primary Key
    id              SERIAL PRIMARY KEY,

    -- Foreign Key
    work_area_id    INTEGER NOT NULL REFERENCES geosdi.work_areas(id) ON DELETE CASCADE,

    -- Identifikasi
    kode            VARCHAR(50) UNIQUE NOT NULL,        -- ex: KMJ-01
    nama            VARCHAR(200),

    -- Tipe & Status
    tipe            VARCHAR(50) NOT NULL,
                    -- Nilai: Produksi, Injeksi, Eksplorasi, Monitoring
    status          VARCHAR(50) NOT NULL DEFAULT 'Unknown',
                    -- Nilai: Aktif, Non-Aktif, Dibatalkan, Drilling

    -- Data Teknis
    kedalaman_m     DECIMAL(10, 2),                     -- Kedalaman total (meter)
    temperatur_c    DECIMAL(6, 2),                      -- Temperatur reservoir (°C)
    tekanan_bar     DECIMAL(8, 2),                      -- Tekanan reservoir (bar)
    flow_rate_tph   DECIMAL(10, 2),                     -- Laju alir (ton/jam)

    -- Geospasial
    geom            GEOMETRY(POINT, 4326),

    -- Metadata
    keterangan      TEXT,
    metadata        JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_well_tipe CHECK (
        tipe IN ('Produksi', 'Injeksi', 'Eksplorasi', 'Monitoring')
    ),
    CONSTRAINT chk_well_status CHECK (
        status IN ('Aktif', 'Non-Aktif', 'Dibatalkan', 'Drilling', 'Unknown')
    )
);

CREATE INDEX IF NOT EXISTS idx_wells_work_area ON geosdi.wells (work_area_id);
CREATE INDEX IF NOT EXISTS idx_wells_geom ON geosdi.wells USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_wells_tipe ON geosdi.wells (tipe);
CREATE INDEX IF NOT EXISTS idx_wells_status ON geosdi.wells (status);

DROP TRIGGER IF EXISTS trg_wells_updated_at ON geosdi.wells;
CREATE TRIGGER trg_wells_updated_at
    BEFORE UPDATE ON geosdi.wells
    FOR EACH ROW
    EXECUTE FUNCTION geosdi.update_updated_at();

COMMENT ON TABLE geosdi.wells IS 'Sumur geothermal (produksi, injeksi, eksplorasi, monitoring)';

-- ============================================================
-- TABLE 3: power_plants (PLTP)
-- ============================================================
-- Pembangkit Listrik Tenaga Panas Bumi.

CREATE TABLE IF NOT EXISTS geosdi.power_plants (
    id              SERIAL PRIMARY KEY,
    work_area_id    INTEGER NOT NULL REFERENCES geosdi.work_areas(id) ON DELETE CASCADE,

    -- Identifikasi
    nama            VARCHAR(200) NOT NULL,              -- ex: PLTP Kamojang Unit 1
    kode            VARCHAR(50) UNIQUE,

    -- Kapasitas & Operasional
    kapasitas_mw    DECIMAL(10, 2) NOT NULL,
    tahun_operasi   INTEGER,
    status          VARCHAR(50) NOT NULL DEFAULT 'Operasi',
    operator        VARCHAR(200),                       -- ex: Pertamina Geothermal Energy

    -- Geospasial
    geom            GEOMETRY(POINT, 4326),

    -- Metadata
    keterangan      TEXT,
    metadata        JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_power_plants_work_area ON geosdi.power_plants (work_area_id);
CREATE INDEX IF NOT EXISTS idx_power_plants_geom ON geosdi.power_plants USING GIST (geom);

DROP TRIGGER IF EXISTS trg_power_plants_updated_at ON geosdi.power_plants;
CREATE TRIGGER trg_power_plants_updated_at
    BEFORE UPDATE ON geosdi.power_plants
    FOR EACH ROW
    EXECUTE FUNCTION geosdi.update_updated_at();

COMMENT ON TABLE geosdi.power_plants IS 'PLTP (Pembangkit Listrik Tenaga Panas Bumi)';

-- ============================================================
-- TABLE 4: observations (Observasi & Event)
-- ============================================================
-- Untuk menyimpan observasi, survey, event, berita, sensor reading, dll.

CREATE TABLE IF NOT EXISTS geosdi.observations (
    id              SERIAL PRIMARY KEY,
    work_area_id    INTEGER REFERENCES geosdi.work_areas(id) ON DELETE CASCADE,

    -- Klasifikasi
    tipe            VARCHAR(50) NOT NULL,
                    -- Nilai: Sensor, Survey, Berita, Event, Policy, Investment, Conflict
    kategori        VARCHAR(100),                       -- Sub-kategori

    -- Konten
    judul           VARCHAR(500) NOT NULL,
    konten          TEXT,
    sumber          VARCHAR(500),                       -- URL atau nama sumber

    -- Waktu
    observed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Nilai (untuk sensor/survey)
    nilai           DECIMAL(15, 4),
    satuan          VARCHAR(50),

    -- Geospasial (opsional)
    geom            GEOMETRY(POINT, 4326),

    -- Metadata
    metadata        JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_observations_work_area ON geosdi.observations (work_area_id);
CREATE INDEX IF NOT EXISTS idx_observations_tipe ON geosdi.observations (tipe);
CREATE INDEX IF NOT EXISTS idx_observations_time ON geosdi.observations (observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_observations_geom ON geosdi.observations USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_observations_metadata ON geosdi.observations USING GIN (metadata);

COMMENT ON TABLE geosdi.observations IS 'Observasi, event, survey, monitoring untuk WKP';

-- ============================================================
-- VIEWS (Opsional — untuk query yang sering dipakai)
-- ============================================================

-- View: Ringkasan WKP dengan jumlah sumur & PLTP
CREATE OR REPLACE VIEW geosdi.v_work_areas_summary AS
SELECT
    wa.id,
    wa.kode,
    wa.nama,
    wa.provinsi,
    wa.status,
    wa.kapasitas_mw,
    wa.potensi_mw,
    wa.tahun_operasi,
    wa.geom,
    COUNT(DISTINCT w.id) AS jumlah_sumur,
    COUNT(DISTINCT pp.id) AS jumlah_pltp,
    COALESCE(SUM(pp.kapasitas_mw), 0) AS total_kapasitas_pltp_mw
FROM geosdi.work_areas wa
LEFT JOIN geosdi.wells w ON w.work_area_id = wa.id
LEFT JOIN geosdi.power_plants pp ON pp.work_area_id = wa.id
GROUP BY wa.id;

COMMENT ON VIEW geosdi.v_work_areas_summary IS 'Ringkasan WKP dengan agregat sumur & PLTP';

-- ============================================================
-- INITIAL DATA (Opsional — kalau mau seed langsung)
-- ============================================================
-- Kita skip seed di sini. Akan dilakukan di Langkah 4 (migrasi data).

-- ============================================================
-- VERIFICATION
-- ============================================================
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'geosdi'
      AND table_type = 'BASE TABLE';

    RAISE NOTICE '============================================';
    RAISE NOTICE '✅ GeoSDI Schema Created';
    RAISE NOTICE '   Tables: %', table_count;
    RAISE NOTICE '   - work_areas';
    RAISE NOTICE '   - wells';
    RAISE NOTICE '   - power_plants';
    RAISE NOTICE '   - observations';
    RAISE NOTICE '   Views: 1 (v_work_areas_summary)';
    RAISE NOTICE '============================================';
END
$$;