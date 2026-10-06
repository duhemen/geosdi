-- ============================================================
-- GeoSDI: Economic Covariates
-- ============================================================
-- Menyimpan data makroekonomi untuk prediksi.
-- Sumber: BPS (inflasi), BI (kurs), PLN (tarif).
-- ============================================================

SET search_path TO geosdi, public;

-- Tabel inflasi bulanan
CREATE TABLE IF NOT EXISTS geosdi.econ_inflation (
    id              SERIAL PRIMARY KEY,
    period_month    DATE NOT NULL UNIQUE,
    inflation_pct   DECIMAL(6, 2) NOT NULL,
    source          VARCHAR(50) DEFAULT 'BPS',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_econ_inflation_period
    ON geosdi.econ_inflation (period_month DESC);

-- Tabel kurs USD/IDR harian
CREATE TABLE IF NOT EXISTS geosdi.econ_exchange_rate (
    id              SERIAL PRIMARY KEY,
    period_date     DATE NOT NULL UNIQUE,
    rate_idr_usd    DECIMAL(10, 2) NOT NULL,
    source          VARCHAR(50) DEFAULT 'BI-JISDOR',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_econ_exchange_period
    ON geosdi.econ_exchange_rate (period_date DESC);

-- Tabel tarif listrik (snapshot)
CREATE TABLE IF NOT EXISTS geosdi.econ_electricity_tariff (
    id              SERIAL PRIMARY KEY,
    golongan        VARCHAR(50) NOT NULL,
    daya_va         VARCHAR(50),
    tarif_rp_kwh    DECIMAL(10, 2) NOT NULL,
    effective_date  DATE NOT NULL,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_econ_tariff_date
    ON geosdi.econ_electricity_tariff (effective_date DESC);

-- Tabel event politik/ekonomi
CREATE TABLE IF NOT EXISTS geosdi.econ_events (
    id              SERIAL PRIMARY KEY,
    event_date      DATE NOT NULL,
    event_type      VARCHAR(50) NOT NULL,
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    impact_level    VARCHAR(20),
    source          VARCHAR(100),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_econ_events_date
    ON geosdi.econ_events (event_date DESC);

DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE '[OK] Economic Covariates Tables Created';
    RAISE NOTICE '   - econ_inflation';
    RAISE NOTICE '   - econ_exchange_rate';
    RAISE NOTICE '   - econ_electricity_tariff';
    RAISE NOTICE '   - econ_events';
    RAISE NOTICE '============================================';
END
$$;