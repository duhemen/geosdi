"""
GeoSDI Geothermal v2.0 - Central Configuration
================================================
Membaca konfigurasi dari .env dan menyediakannya sebagai objek Python.
Semua layer lain mengimpor dari sini — single source of truth.

Philosophy: "Configuration is a contract between the system and its environment."
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# ------------------------------------------------------------------
# Root path — asumsi file ini ada di src/shared/config.py
# ------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Settings GeoSDI Geothermal.
    Dibaca dari .env, di-override oleh environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --------------------------------------------------------------
    # Application
    # --------------------------------------------------------------
    app_name: str = "GeoSDI-Geothermal"
    app_env: Literal["development", "staging", "production"] = "development"
    app_version: str = "2.0.0"
    debug: bool = True

    # --------------------------------------------------------------
    # PostgreSQL + PostGIS
    # --------------------------------------------------------------
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "geosdi"
    postgres_user: str = "geosdi"
    postgres_password: str = Field(default="", repr=False)

    @property
    def postgres_url(self) -> str:
        """SQLAlchemy connection URL."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def postgres_url_safe(self) -> str:
        """Connection URL tanpa password — untuk logging."""
        return (
            f"postgresql://{self.postgres_user}:***"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # --------------------------------------------------------------
    # TimescaleDB
    # --------------------------------------------------------------
    timescale_host: str = "localhost"
    timescale_port: int = 5433
    timescale_db: str = "geosdi_timeseries"
    timescale_user: str = "geosdi"
    timescale_password: str = Field(default="", repr=False)

    # --------------------------------------------------------------
    # Neo4j
    # --------------------------------------------------------------
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = Field(default="", repr=False)

    # --------------------------------------------------------------
    # MinIO
    # --------------------------------------------------------------
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = Field(default="", repr=False)
    minio_bucket: str = "geosdi-data"

    # --------------------------------------------------------------
    # Kafka
    # --------------------------------------------------------------
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "geosdi-consumer"

    # --------------------------------------------------------------
    # API
    # --------------------------------------------------------------
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_secret_key: str = Field(default="", repr=False)
    api_cors_origins: str = "http://localhost:3000,http://localhost:8000"

    # --------------------------------------------------------------
    # Session (Web Auth)
    # --------------------------------------------------------------
    session_secret: str = Field(default="", repr=False)
    session_cookie_name: str = "geosdi_session"
    session_max_age: int = 60 * 60 * 8  # 8 jam dalam detik
    session_https_only: bool = False   # set True di production

    @property
    def api_cors_origins_list(self) -> list[str]:
        """Parse CORS origins string menjadi list."""
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]

    # --------------------------------------------------------------
    # Logging
    # --------------------------------------------------------------
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "text"] = "text"

    # --------------------------------------------------------------
    # Paths
    # --------------------------------------------------------------
    data_raw_path: Path = ROOT_DIR / "data" / "raw"
    data_processed_path: Path = ROOT_DIR / "data" / "processed"
    logs_path: Path = ROOT_DIR / "logs"

    @field_validator("data_raw_path", "data_processed_path", "logs_path", mode="before")
    @classmethod
    def _coerce_path(cls, v):
        return Path(v) if v else v

    # --------------------------------------------------------------
    # Validation
    # --------------------------------------------------------------
    @field_validator("api_secret_key", "postgres_password", "neo4j_password")
    @classmethod
    def _not_empty_in_prod(cls, v, info):
        # Validasi hanya dilakukan jika app_env sudah diketahui
        # (Pydantic v2 tidak menjamin urutan; kita lakukan di runtime)
        return v

    def validate_production(self) -> list[str]:
        """Cek konfigurasi wajib untuk production. Return list error."""
        errors: list[str] = []
        if self.app_env == "production":
            if not self.postgres_password:
                errors.append("POSTGRES_PASSWORD wajib di production")
            if not self.neo4j_password:
                errors.append("NEO4J_PASSWORD wajib di production")
            if not self.api_secret_key or len(self.api_secret_key) < 32:
                errors.append("API_SECRET_KEY minimal 32 karakter di production")
            if self.debug:
                errors.append("DEBUG harus false di production")
        return errors


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Singleton — settings dibaca sekali, di-cache.
    Gunakan ini di seluruh aplikasi.
    """
    return Settings()


# ------------------------------------------------------------------
# Quick self-test (jalankan file ini langsung untuk cek)
# ------------------------------------------------------------------
if __name__ == "__main__":
    s = get_settings()
    print("=" * 60)
    print(f"GeoSDI Configuration — {s.app_name} v{s.app_version}")
    print("=" * 60)
    print(f"Environment    : {s.app_env}")
    print(f"Debug mode     : {s.debug}")
    print(f"PostgreSQL     : {s.postgres_url_safe}")
    print(f"Neo4j URI      : {s.neo4j_uri}")
    print(f"API Address    : http://{s.api_host}:{s.api_port}")
    print(f"CORS Origins   : {s.api_cors_origins_list}")
    print(f"Log Level      : {s.log_level}")
    print(f"Data Raw Path  : {s.data_raw_path}")
    print(f"Logs Path      : {s.logs_path}")
    print("-" * 60)

    errors = s.validate_production()
    if errors:
        print("⚠️  Production warnings:")
        for e in errors:
            print(f"   - {e}")
    else:
        print("✅ Configuration valid.")
    print("=" * 60)