"""
GeoSDI Geothermal v2.0 - Centralized Logging
=============================================
Logging terstruktur: setiap log punya konteks (module, function, line).
Mendukung dua format: 'text' (human-readable) dan 'json' (machine-readable).

Philosophy: "A log is a story of what the system believed at a moment in time."
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.shared.config import get_settings


# ------------------------------------------------------------------
# Custom formatters
# ------------------------------------------------------------------
class TextFormatter(logging.Formatter):
    """Format: [TIMESTAMP] LEVEL  [module:line]  message"""

    COLORS = {
        "DEBUG": "\033[36m",     # cyan
        "INFO": "\033[32m",      # green
        "WARNING": "\033[33m",   # yellow
        "ERROR": "\033[31m",     # red
        "CRITICAL": "\033[35m",  # magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        level = record.levelname.ljust(8)
        color = self.COLORS.get(record.levelname, "")
        location = f"{record.module}:{record.lineno}"

        message = record.getMessage()

        # Tambahkan exception info jika ada
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)

        # Tambahkan extra fields jika ada
        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in logging.LogRecord.__dict__
            and k not in ("message", "asctime", "msg", "args")
            and not k.startswith("_")
        }
        if extras:
            extras_str = " | ".join(f"{k}={v}" for k, v in extras.items())
            message += f"  [{extras_str}]"

        return f"[{ts}] {color}{level}{self.RESET} [{location}] {message}"


class JsonFormatter(logging.Formatter):
    """Format: one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in logging.LogRecord.__dict__
            and k not in ("message", "asctime", "msg", "args")
            and not k.startswith("_")
        }
        if extras:
            payload["extra"] = extras

        return json.dumps(payload, default=str, ensure_ascii=False)


# ------------------------------------------------------------------
# Setup function
# ------------------------------------------------------------------
_LOGGER_INITIALIZED = False


def setup_logging(force: bool = False) -> None:
    """
    Setup root logger. Idempotent — panggil berkali-kali aman.
    """
    global _LOGGER_INITIALIZED
    if _LOGGER_INITIALIZED and not force:
        return

    settings = get_settings()

    # Pastikan folder logs ada
    settings.logs_path.mkdir(parents=True, exist_ok=True)

    # Pilih formatter
    formatter = JsonFormatter() if settings.log_format == "json" else TextFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File handler (rotating)
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        settings.logs_path / "geosdi.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # Root logger
    root = logging.getLogger()
    root.setLevel(settings.log_level)
    root.handlers.clear()
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    # Reduce noise dari library pihak ketiga
    for noisy in ("urllib3", "asyncio", "matplotlib", "botocore", "kafka"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _LOGGER_INITIALIZED = True

    logging.getLogger(__name__).info(
        "Logging initialized",
        extra={
            "env": settings.app_env,
            "level": settings.log_level,
            "format": settings.log_format,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """
    Ambil logger untuk modul tertentu.
    Panggil setup_logging() di entry point aplikasi.
    """
    if not _LOGGER_INITIALIZED:
        setup_logging()
    return logging.getLogger(name)


# ------------------------------------------------------------------
# Self-test
# ------------------------------------------------------------------
if __name__ == "__main__":
    setup_logging(force=True)
    log = get_logger(__name__)

    log.debug("Ini pesan DEBUG — biasanya tidak muncul di level INFO")
    log.info("Ini pesan INFO — normal")
    log.warning("Ini pesan WARNING — perlu perhatian")
    log.error("Ini pesan ERROR — ada masalah")

    # Contoh dengan extra context
    log.info(
        "Simulasi GDI selesai",
        extra={
            "node": "Kamojang",
            "gdi_mean": 78.3,
            "gdi_std": 6.1,
            "n_trials": 10000,
        },
    )

    # Contoh exception
    try:
        1 / 0
    except ZeroDivisionError:
        log.exception("Terjadi error saat pembagian")

    print(f"\n✅ Log file tersimpan di: {get_settings().logs_path / 'geosdi.log'}")