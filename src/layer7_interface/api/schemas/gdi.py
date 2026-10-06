"""Schemas untuk GDI API."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class GDIResponse(BaseModel):
    """Response GDI untuk satu WKP."""
    kode: str
    nama: str
    provinsi: str

    # Distribusi
    gdi_mean: float
    gdi_std: float
    gdi_median: float
    gdi_ci_lower: float
    gdi_ci_upper: float
    status: str

    # Variabel
    variables: dict[str, float]

    # Kontribusi
    contributions: dict[str, Any]

    # Meta
    model_version: str
    computed_at: datetime


class GDIListResponse(BaseModel):
    """Response list GDI."""
    data: list[GDIResponse]
    total: int