-- ============================================================
-- GeoSDI: Audit Log Table
-- ============================================================
-- Mencatat setiap perubahan data untuk audit trail.
-- ============================================================

SET search_path TO geosdi, public;

CREATE TABLE IF NOT EXISTS geosdi.audit_log (
    id              SERIAL PRIMARY KEY,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    action          VARCHAR(20) NOT NULL,
    entity          VARCHAR(50) NOT NULL,
    entity_id       INTEGER,
    entity_key      VARCHAR(50),
    user_ip         VARCHAR(50),
    user_agent      TEXT,
    before_data     JSONB,
    after_data      JSONB,
    notes           TEXT,
    success         BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp
    ON geosdi.audit_log (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_audit_log_entity
    ON geosdi.audit_log (entity, entity_id);

CREATE INDEX IF NOT EXISTS idx_audit_log_action
    ON geosdi.audit_log (action);

COMMENT ON TABLE geosdi.audit_log IS 'Audit trail untuk semua perubahan data';

DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE '[OK] Audit Log Table Created';
    RAISE NOTICE '============================================';
END
$$;