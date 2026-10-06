-- ============================================================
-- GeoSDI: GDI History (Time Series)
-- ============================================================
-- Menyimpan history GDI per WKP per bulan.
-- ============================================================

SET search_path TO geosdi, public;

CREATE TABLE IF NOT EXISTS geosdi.gdi_history (
    id                  SERIAL PRIMARY KEY,
    work_area_id        INTEGER NOT NULL REFERENCES geosdi.work_areas(id) ON DELETE CASCADE,

    -- Waktu
    recorded_at         DATE NOT NULL,
    year                INTEGER NOT NULL,
    month               INTEGER NOT NULL,

    -- GDI
    gdi_mean            DECIMAL(5, 2) NOT NULL,
    gdi_std             DECIMAL(5, 2),

    -- Variabel
    var_r               DECIMAL(4, 3),
    var_t               DECIMAL(4, 3),
    var_e               DECIMAL(4, 3),
    var_p               DECIMAL(4, 3),
    var_s               DECIMAL(4, 3),
    var_n               DECIMAL(4, 3),
    var_c               DECIMAL(4, 3),
    var_h               DECIMAL(4, 3),

    -- Meta
    model_version       VARCHAR(20) DEFAULT 'v1.0',
    notes               TEXT,

    -- Audit
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique per WKP per bulan
    CONSTRAINT uq_gdi_history_unique UNIQUE (work_area_id, year, month)
);

CREATE INDEX IF NOT EXISTS idx_gdi_history_work_area ON geosdi.gdi_history (work_area_id);
CREATE INDEX IF NOT EXISTS idx_gdi_history_date ON geosdi.gdi_history (recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_gdi_history_year_month ON geosdi.gdi_history (year, month);

COMMENT ON TABLE geosdi.gdi_history IS 'Time series GDI per WKP per bulan';

DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE '✅ GDI History Table Created';
    RAISE NOTICE '============================================';
END
$$;