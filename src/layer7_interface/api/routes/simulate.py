"""
GeoSDI — Simulation Routes
===========================
Endpoint untuk simulasi intervensi kebijakan.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.shared.database import get_cursor
from src.shared.logger import get_logger
from src.layer5_inference.analytics.gdi_model import compute_gdi, GDIWeights

log = get_logger(__name__)
router = APIRouter(prefix="/simulate", tags=["simulate"])


class SimulationRequest(BaseModel):
    """Request untuk simulasi intervensi."""
    kode: str

    # Variabel yang diubah (None = tidak diubah)
    R: Optional[float] = Field(None, ge=0, le=1, description="Reservoir 0-1")
    T: Optional[float] = Field(None, ge=0, le=1, description="Technology 0-1")
    E: Optional[float] = Field(None, ge=0, le=1, description="Economic 0-1")
    P: Optional[float] = Field(None, ge=0, le=1, description="Policy 0-1")
    S: Optional[float] = Field(None, ge=0, le=1, description="Social 0-1")
    N: Optional[float] = Field(None, ge=0, le=1, description="Environmental 0-1")
    C: Optional[float] = Field(None, ge=0, le=1, description="Conflict 0-1")
    H: Optional[float] = Field(None, ge=0, le=1, description="Historical 0-1")


class SimulationResponse(BaseModel):
    """Response simulasi."""
    kode: str
    nama: str

    # GDI saat ini (baseline)
    baseline_mean: float
    baseline_status: str

    # GDI setelah intervensi
    simulated_mean: float
    simulated_std: float
    simulated_ci_lower: float
    simulated_ci_upper: float
    simulated_status: str

    # Perubahan
    delta: float
    delta_percent: float

    # Info
    variables_changed: dict
    scenario_name: str


@router.post("", response_model=SimulationResponse)
async def simulate(request: SimulationRequest):
    """
    Simulasi intervensi pada satu WKP.
    User bisa mengubah variabel dan lihat dampak ke GDI.
    """
    # 1. Ambil data GDI & variabel saat ini dari DB
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                wa.kode, wa.nama,
                g.gdi_mean, g.status,
                g.var_r, g.var_t, g.var_e, g.var_p,
                g.var_s, g.var_n, g.var_c, g.var_h
            FROM geosdi.gdi_scores g
            JOIN geosdi.work_areas wa ON wa.id = g.work_area_id
            WHERE wa.kode = %s
            ORDER BY g.computed_at DESC
            LIMIT 1;
        """, (request.kode,))
        row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail=f"WKP '{request.kode}' tidak ditemukan")

    # 2. Baseline: hitung ulang dengan variabel lama
    baseline_vars = {
        "R": float(row["var_r"] or 0),
        "T": float(row["var_t"] or 0),
        "E": float(row["var_e"] or 0),
        "P": float(row["var_p"] or 0),
        "S": float(row["var_s"] or 0),
        "N": float(row["var_n"] or 0),
        "C": float(row["var_c"] or 0),
        "H": float(row["var_h"] or 0),
    }
    baseline = compute_gdi(
        kode=row["kode"],
        nama=row["nama"],
        variables=baseline_vars,
        seed=42,
    )

    # 3. Apply intervensi
    new_vars = baseline_vars.copy()
    variables_changed = {}

    for var_name in ["R", "T", "E", "P", "S", "N", "C", "H"]:
        value = getattr(request, var_name)
        if value is not None:
            variables_changed[var_name] = {
                "old": baseline_vars[var_name],
                "new": value,
                "delta": round(value - baseline_vars[var_name], 3),
            }
            new_vars[var_name] = value

    # 4. Hitung GDI baru
    simulated = compute_gdi(
        kode=row["kode"],
        nama=row["nama"],
        variables=new_vars,
        seed=43,  # seed berbeda untuk variasi
    )

    # 5. Hitung delta
    delta = simulated.mean - baseline.mean
    delta_percent = (delta / baseline.mean * 100) if baseline.mean > 0 else 0

    # 6. Buat deskripsi skenario
    if variables_changed:
        parts = [f"{k}={v['delta']:+.2f}" for k, v in variables_changed.items()]
        scenario_name = "Intervensi: " + ", ".join(parts)
    else:
        scenario_name = "Tanpa perubahan"

    return SimulationResponse(
        kode=row["kode"],
        nama=row["nama"],
        baseline_mean=baseline.mean,
        baseline_status=baseline.status,
        simulated_mean=simulated.mean,
        simulated_std=simulated.std,
        simulated_ci_lower=simulated.ci_lower,
        simulated_ci_upper=simulated.ci_upper,
        simulated_status=simulated.status,
        delta=round(delta, 2),
        delta_percent=round(delta_percent, 1),
        variables_changed=variables_changed,
        scenario_name=scenario_name,
    )