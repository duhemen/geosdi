-- ============================================================
-- GeoSDI: GDI Scores Table
-- ============================================================
-- Menyimpan skor GDI per WKP dengan distribusi probabilistik.
-- ============================================================

SET search_path TO geosdi, public;

-- Table untuk GDI Scores
CREATE TABLE IF NOT EXISTS geosdi.gdi_scores (
    id                  SERIAL PRIMARY KEY,
    work_area_id        INTEGER NOT NULL REFERENCES geosdi.work_areas(id) ON DELETE CASCADE,

    -- Distribusi GDI
    gdi_mean            DECIMAL(5, 2) NOT NULL,
    gdi_std             DECIMAL(5, 2),
    gdi_median          DECIMAL(5, 2),
    gdi_ci_lower        DECIMAL(5, 2),
    gdi_ci_upper        DECIMAL(5, 2),

    -- Kategori
    status              VARCHAR(20) NOT NULL,

    -- Variabel (0-1)
    var_r               DECIMAL(4, 3),  -- Reservoir
    var_t               DECIMAL(4, 3),  -- Technology
    var_e               DECIMAL(4, 3),  -- Economic
    var_p               DECIMAL(4, 3),  -- Policy
    var_s               DECIMAL(4, 3),  -- Social
    var_n               DECIMAL(4, 3),  -- Environmental
    var_c               DECIMAL(4, 3),  -- Conflict
    var_h               DECIMAL(4, 3),  -- Historical

    -- Kontribusi (JSONB untuk flexibility)
    contributions       JSONB,
    weights_used        JSONB,

    -- Meta
    n_samples           INTEGER,
    model_version       VARCHAR(20) DEFAULT 'v1.0',

    -- Audit
    computed_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraint
    CONSTRAINT chk_gdi_status CHECK (
        status IN ('Kritis', 'Rentan', 'Berkembang', 'Stabil', 'Optimal')
    ),
    CONSTRAINT chk_gdi_mean CHECK (gdi_mean >= 0 AND gdi_mean <= 100)
);

CREATE INDEX IF NOT EXISTS idx_gdi_scores_work_area ON geosdi.gdi_scores (work_area_id);
CREATE INDEX IF NOT EXISTS idx_gdi_scores_mean ON geosdi.gdi_scores (gdi_mean DESC);
CREATE INDEX IF NOT EXISTS idx_gdi_scores_status ON geosdi.gdi_scores (status);

COMMENT ON TABLE geosdi.gdi_scores IS 'Skor GDI (Geothermal Development Index) per WKP';

DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE '✅ GDI Scores Table Created';
    RAISE NOTICE '============================================';
END
$$;