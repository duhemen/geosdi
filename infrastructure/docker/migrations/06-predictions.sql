-- ============================================================
-- GeoSDI: Predictions & Insights
-- ============================================================
-- Menyimpan hasil prediksi GDI & insight otomatis.
-- ============================================================

SET search_path TO geosdi, public;

-- ============================================================
-- TABLE: gdi_predictions
-- ============================================================
CREATE TABLE IF NOT EXISTS geosdi.gdi_predictions (
    id                  SERIAL PRIMARY KEY,
    work_area_id        INTEGER NOT NULL REFERENCES geosdi.work_areas(id) ON DELETE CASCADE,

    -- Metadata prediksi
    predicted_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    horizon_months      INTEGER NOT NULL,
    method              VARCHAR(50) DEFAULT 'Holt Linear Trend',

    -- Hasil prediksi
    last_observed       DECIMAL(5, 2) NOT NULL,
    trend_slope         DECIMAL(6, 4) NOT NULL,
    prediction_status   VARCHAR(20) NOT NULL,  -- Naik/Stabil/Turun
    mape                DECIMAL(5, 2),

    -- Nilai prediksi akhir (bulan ke-horizon)
    predicted_final     DECIMAL(5, 2),

    -- Delta
    delta_total         DECIMAL(5, 2),

    -- Kategori dampak
    impact_level        VARCHAR(20),  -- Positive/Neutral/Negative
    priority            VARCHAR(20),  -- Low/Medium/High/Critical

    -- Narasi manusia
    narrative           TEXT,         -- "GDI diprediksi turun..."

    -- Metadata
    metadata            JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_gdi_predictions_work_area ON geosdi.gdi_predictions (work_area_id);
CREATE INDEX IF NOT EXISTS idx_gdi_predictions_status ON geosdi.gdi_predictions (prediction_status);
CREATE INDEX IF NOT EXISTS idx_gdi_predictions_priority ON geosdi.gdi_predictions (priority);

COMMENT ON TABLE geosdi.gdi_predictions IS 'Hasil prediksi GDI per WKP';

-- ============================================================
-- TABLE: insights_daily
-- ============================================================
CREATE TABLE IF NOT EXISTS geosdi.insights_daily (
    id                  SERIAL PRIMARY KEY,

    insight_date        DATE NOT NULL DEFAULT CURRENT_DATE,
    insight_type        VARCHAR(50) NOT NULL,   -- trend/alert/recommendation/summary

    -- Konten
    title               VARCHAR(200) NOT NULL,
    body                TEXT NOT NULL,          -- Narasi lengkap
    icon                VARCHAR(50),            -- emoji/icon

    -- Konteks
    related_wkp         VARCHAR(20),            -- Kalau spesifik ke WKP
    severity            VARCHAR(20),            -- info/warning/critical

    -- Metadata
    metadata            JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_insights_daily_date ON geosdi.insights_daily (insight_date DESC);
CREATE INDEX IF NOT EXISTS idx_insights_daily_type ON geosdi.insights_daily (insight_type);

COMMENT ON TABLE geosdi.insights_daily IS 'Insight harian yang auto-generated';

-- ============================================================
-- TABLE: alerts
-- ============================================================
CREATE TABLE IF NOT EXISTS geosdi.alerts (
    id                  SERIAL PRIMARY KEY,
    work_area_id        INTEGER REFERENCES geosdi.work_areas(id) ON DELETE CASCADE,

    alert_type          VARCHAR(50) NOT NULL,   -- declining_gdi/high_conflict/low_confidence
    severity            VARCHAR(20) NOT NULL,   -- info/warning/critical

    title               VARCHAR(200) NOT NULL,
    message             TEXT NOT NULL,

    -- Trigger info
    trigger_value       DECIMAL(10, 4),
    threshold_value     DECIMAL(10, 4),

    -- Status
    status              VARCHAR(20) DEFAULT 'active',  -- active/acknowledged/resolved
    acknowledged_at     TIMESTAMPTZ,

    -- Audit
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_work_area ON geosdi.alerts (work_area_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON geosdi.alerts (status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON geosdi.alerts (severity);

COMMENT ON TABLE geosdi.alerts IS 'Alert otomatis untuk kondisi yang butuh perhatian';

-- ============================================================
-- VIEW: v_wkp_health_report
-- ============================================================
DROP VIEW IF EXISTS geosdi.v_wkp_health_report;

CREATE OR REPLACE VIEW geosdi.v_wkp_health_report AS
SELECT
    wa.kode,
    wa.nama,
    wa.provinsi,
    wa.status AS status_operasi,

    -- GDI saat ini
    g.gdi_mean AS gdi_current,
    g.status AS gdi_status,

    -- Prediksi
    p.trend_slope,
    p.prediction_status,
    p.predicted_final,
    p.delta_total,
    p.impact_level,
    p.priority,
    p.mape,
    p.narrative,

    -- Human-readable summary
    CASE
        WHEN p.prediction_status = 'Turun' AND p.trend_slope < -0.2 THEN '⚠️ PERHATIAN: Penurunan signifikan diprediksi'
        WHEN p.prediction_status = 'Turun' THEN '📉 Penurunan ringan diprediksi'
        WHEN p.prediction_status = 'Naik' THEN '📈 Peningkatan diprediksi'
        ELSE '➡️ Kondisi diprediksi stabil'
    END AS summary_human,

    -- Rekomendasi
    CASE
        WHEN p.priority = 'Critical' THEN 'Intervensi segera diperlukan'
        WHEN p.priority = 'High' THEN 'Monitoring ketat + intervensi direncanakan'
        WHEN p.priority = 'Medium' THEN 'Monitoring rutin'
        ELSE 'Tidak ada tindakan khusus'
    END AS recommendation,

    -- Metadata
    p.predicted_at

FROM geosdi.work_areas wa
LEFT JOIN geosdi.gdi_scores g ON g.work_area_id = wa.id
LEFT JOIN LATERAL (
    SELECT * FROM geosdi.gdi_predictions
    WHERE work_area_id = wa.id
    ORDER BY predicted_at DESC
    LIMIT 1
) p ON true;

COMMENT ON VIEW geosdi.v_wkp_health_report IS 'Health report per WKP dengan narasi manusia';

DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE '✅ Predictions & Insights Tables Created';
    RAISE NOTICE '   - gdi_predictions';
    RAISE NOTICE '   - insights_daily';
    RAISE NOTICE '   - alerts';
    RAISE NOTICE '   - v_wkp_health_report (view)';
    RAISE NOTICE '============================================';
END
$$;