"""
GeoSDI API — Pydantic Schemas for Nodes (WKP)
==============================================
Schema untuk validasi input/output API.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================
# Base Schema
# ============================================================
class WorkAreaBase(BaseModel):
    """Base schema untuk Work Area."""
    kode: str = Field(..., description="Kode WKP (contoh: WKP001)")
    nama: str = Field(..., description="Nama WKP (contoh: Kamojang)")
    provinsi: str = Field(..., description="Provinsi lokasi WKP")
    status: str = Field(..., description="Status operasional")


# ============================================================
# Detail Schema
# ============================================================
class WorkAreaDetail(WorkAreaBase):
    """Detail WKP lengkap."""
    id: int
    kabupaten: Optional[str] = None
    kapasitas_mw: Optional[float] = None
    potensi_mw: Optional[float] = None
    tahun_operasi: Optional[int] = None
    luas_km2: Optional[float] = None
    keterangan: Optional[str] = None

    # Koordinat (dari PostGIS)
    latitude: Optional[float] = Field(None, description="Latitude (WGS84)")
    longitude: Optional[float] = Field(None, description="Longitude (WGS84)")

    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Data Quality (NEW in v2.2.0)
    data_quality: Optional[str] = Field(
        None,
        description="Kualitas data: verified | estimated | user_provided"
    )
    source: Optional[str] = Field(
        None,
        description="Sumber data: wikipedia | esdm | genesis | user_provided"
    )

    # Audit
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# Nearby Schema
# ============================================================
class WorkAreaNearby(WorkAreaBase):
    """WKP dalam radius tertentu."""
    id: int
    latitude: float
    longitude: float
    jarak_km: float = Field(..., description="Jarak dari titik pencarian (km)")


# ============================================================
# Stats Schema
# ============================================================
class StatsResponse(BaseModel):
    """Statistik agregat."""
    total_wkp: int
    total_provinsi: int
    total_operasi: int
    total_kapasitas_mw: float
    by_status: dict[str, int]
    by_provinsi: dict[str, int]


# ============================================================
# Pagination Schemas
# ============================================================
class PaginationMeta(BaseModel):
    """Metadata pagination."""
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedWorkAreas(BaseModel):
    """Response dengan pagination."""
    data: list[WorkAreaDetail]
    meta: PaginationMeta