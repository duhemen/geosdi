"""
GeoSDI — Digital Twin API
===========================
Endpoint untuk National GDI & Scenario Simulation.
"""
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from src.layer6_synthesis.digital_twin.aggregator import (
    get_national_gdi,
    get_health_score,
)
from src.layer6_synthesis.digital_twin.scenario import (
    Scenario,
    apply_scenario,
    run_preset,
    PRESET_SCENARIOS,
)
from src.layer6_synthesis.digital_twin.priority import (
    compute_priority_ranking,
    get_priority_summary,
)
from src.layer6_synthesis.digital_twin.budget import optimize_budget
from src.layer6_synthesis.digital_twin.executive import generate_executive_summary

router = APIRouter(prefix="/digital-twin", tags=["digital-twin"])


# ============================================================
# Schemas
# ============================================================
class ScenarioRequest(BaseModel):
    name: str = "Custom"
    delta_r: float = Field(0.0, ge=-0.5, le=0.5)
    delta_t: float = Field(0.0, ge=-0.5, le=0.5)
    delta_e: float = Field(0.0, ge=-0.5, le=0.5)
    delta_p: float = Field(0.0, ge=-0.5, le=0.5)
    delta_s: float = Field(0.0, ge=-0.5, le=0.5)
    delta_n: float = Field(0.0, ge=-0.5, le=0.5)
    delta_c: float = Field(0.0, ge=-0.5, le=0.5)
    delta_h: float = Field(0.0, ge=-0.5, le=0.5)
    filter_provinsi: str | None = None
    filter_status: str | None = None
    filter_type: str | None = None


class BudgetRequest(BaseModel):
    total_budget_billion: float = Field(..., gt=0, description="Total budget dalam miliar rupiah")


# ============================================================
# GET /national — National GDI
# ============================================================
@router.get("/national")
async def national_gdi():
    """National GDI aggregate."""
    n = get_national_gdi()
    health = get_health_score(n)

    return {
        "summary": {
            "total_wkp": n.total_wkp,
            "total_provinsi": n.total_provinsi,
            "total_operasi": n.total_operasi,
            "total_kapasitas_mw": n.total_kapasitas_mw,
        },
        "gdi": {
            "mean": n.gdi_mean,
            "std": n.gdi_std,
            "weighted": n.gdi_weighted,
        },
        "health": health,
        "by_status": n.by_status,
        "top_wkp": n.top_wkp,
        "bottom_wkp": n.bottom_wkp,
    }


# ============================================================
# GET /scenarios/presets — List preset scenarios
# ============================================================
@router.get("/scenarios/presets")
async def list_presets():
    """List semua preset scenario dengan info availability."""
    from src.shared.database import get_cursor

    # === Cek jumlah WKP per type (klasifikasi konsisten dengan classify_wkp_type) ===
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE wa.status IN ('Eksplorasi', 'IPB Eksplorasi')) AS exploration_count,
                COUNT(*) FILTER (WHERE wa.status = 'Operasi') AS mature_count,
                COUNT(*) FILTER (WHERE wa.status = 'Dalam Survei') AS developing_count,
                COUNT(*) FILTER (WHERE wa.status IN ('Perencanaan', 'Belum Ada Pemegang IPB')) AS new_count
            FROM geosdi.work_areas wa
            JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id
        """)
        counts = cur.fetchone()

    # Mapping type → jumlah WKP
    type_counts = {
        "exploration": counts["exploration_count"] or 0,
        "mature": counts["mature_count"] or 0,
        "developing": counts["developing_count"] or 0,
        "new": counts["new_count"] or 0,
    }

    presets = []
    for k, v in PRESET_SCENARIOS.items():
        available = True
        reason = None

        # Cek filter_type (kalau preset punya filter)
        if hasattr(v, 'filter_type') and v.filter_type:
            count = type_counts.get(v.filter_type, 0)
            if count == 0:
                available = False
                reason = f"Tidak ada WKP dengan tipe '{v.filter_type}' di database"

        presets.append({
            "key": k,
            "name": v.name,
            "available": available,
            "reason": reason,
        })

    return {
        "presets": presets,
        "type_counts": type_counts,  # ← Bonus: kirim juga count untuk debug
    }

# ============================================================
# GET /scenarios/preset/{name} — Run preset scenario
# ============================================================
@router.get("/scenarios/preset/{name}")
async def run_preset_scenario(name: str):
    """Jalankan preset scenario."""
    try:
        result = run_preset(name)
        return {
            "scenario_name": result.scenario_name,
            "baseline": {
                "gdi": result.baseline_gdi,
                "health": result.baseline_health,
            },
            "simulated": {
                "gdi": result.simulated_gdi,
                "health": result.simulated_health,
            },
            "delta": {
                "gdi": result.delta_gdi,
                "percent": result.delta_percent,
            },
            "wkp_summary": {
                "affected": result.wkp_affected,
                "improved": result.wkp_improved,
                "worsened": result.wkp_worsened,
                "unchanged": result.wkp_unchanged,
            },
            "by_type": getattr(result, "by_type", {}),
            "top_improvements": getattr(result, "top_improvements", []),
            "top_declines": getattr(result, "top_declines", []),
        }
    except ValueError as e:
        # Filter tidak match / preset tidak ada → 400
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch-all untuk debug — log traceback
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {str(e)}"
        )


# ============================================================
# POST /scenarios/custom — Custom scenario
# ============================================================
@router.post("/scenarios/custom")
async def run_custom_scenario(request: ScenarioRequest):
    """Jalankan custom scenario."""
    scenario = Scenario(
        name=request.name,
        delta_r=request.delta_r,
        delta_t=request.delta_t,
        delta_e=request.delta_e,
        delta_p=request.delta_p,
        delta_s=request.delta_s,
        delta_n=request.delta_n,
        delta_c=request.delta_c,
        delta_h=request.delta_h,
        filter_provinsi=request.filter_provinsi,
        filter_status=request.filter_status,
    )

    try:
        result = apply_scenario(scenario)
        return {
            "scenario_name": result.scenario_name,
            "baseline": {
                "gdi": result.baseline_gdi,
                "health": result.baseline_health,
            },
            "simulated": {
                "gdi": result.simulated_gdi,
                "health": result.simulated_health,
            },
            "delta": {
                "gdi": result.delta_gdi,
                "percent": result.delta_percent,
            },
            "wkp_summary": {
                "affected": result.wkp_affected,
                "improved": result.wkp_improved,
                "worsened": result.wkp_worsened,
                "unchanged": result.wkp_unchanged,
            },
            "by_type": getattr(result, "by_type", {}),
            "top_improvements": getattr(result, "top_improvements", []),
            "top_declines": getattr(result, "top_declines", []),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {str(e)}"
        )


# ============================================================
# GET /priority — Priority ranking
# ============================================================
@router.get("/priority")
async def priority_ranking(
    limit: int = Query(50, ge=1, le=200),
    level: str = Query(None, description="Filter by level: Critical/High/Medium/Low"),
):
    """Priority ranking semua WKP."""
    rankings = compute_priority_ranking()

    if level:
        rankings = [r for r in rankings if r.priority_level == level]

    rankings = rankings[:limit]

    return {
        "count": len(rankings),
        "rankings": [
            {
                "rank": r.priority_rank,
                "kode": r.kode,
                "nama": r.nama,
                "provinsi": r.provinsi,
                "gdi_current": r.gdi_current,
                "kapasitas_mw": r.kapasitas_mw,
                "priority_score": r.priority_score,
                "priority_level": r.priority_level,
                "intervention_type": r.intervention_type,
                "recommendation": r.recommendation,
                "scores": {
                    "impact": r.impact_score,
                    "urgency": r.urgency_score,
                    "effort": r.effort_score,
                    "confidence": r.confidence_score,
                },
            }
            for r in rankings
        ],
    }


# ============================================================
# GET /priority/summary — Priority summary
# ============================================================
@router.get("/priority/summary")
async def priority_summary():
    """Ringkasan prioritas."""
    return get_priority_summary()


# ============================================================
# POST /budget/optimize — Budget optimizer
# ============================================================
@router.post("/budget/optimize")
async def budget_optimize(request: BudgetRequest):
    """Optimize budget allocation dengan detail per WKP."""
    plan = optimize_budget(request.total_budget_billion)

    return {
        "budget": {
            "total": plan.total_budget_billion,
            "allocated": plan.allocated_billion,
            "remaining": plan.remaining_billion,
        },
        "summary": {
            "wkp_funded": plan.total_wkp_funded,
            "expected_gdi_gain_total": plan.total_expected_gdi_gain,
            "expected_mw_gain_total": plan.total_expected_mw_gain,
            "avg_gdi_gain_per_wkp": plan.avg_gdi_gain_per_wkp,
        },
        "impact": {
            "national_gdi_before": plan.national_gdi_before,
            "national_gdi_after": plan.national_gdi_after,
            "national_gdi_delta": plan.national_gdi_delta,
            "interpretation": (
                f"Dengan Rp {plan.allocated_billion:,.0f} miliar, "
                f"kita dapat meningkatkan {plan.total_wkp_funded} WKP dengan "
                f"rata-rata gain +{plan.avg_gdi_gain_per_wkp:.2f} GDI per WKP. "
                f"Dampak nasional: +{plan.national_gdi_delta:.2f} GDI "
                f"(karena hanya {plan.total_wkp_funded} dari total WKP yang diintervensi)."
            ),
        },
        "allocations": [
            {
                "kode": a.kode,
                "nama": a.nama,
                "provinsi": a.provinsi,
                "intervention_type": a.intervention_type,
                "priority_score": a.priority_score,
                "priority_level": a.priority_level,
                "gdi": {
                    "before": a.gdi_before,
                    "after": a.gdi_after,
                    "gain": a.gdi_gain,
                },
                "capacity": {
                    "before_mw": a.capacity_before_mw,
                    "after_mw": a.capacity_after_mw,
                    "gain_mw": a.capacity_gain_mw,
                },
                "cost_billion": a.cost_billion,
                "roi": a.roi,
                "rationale": a.rationale,
            }
            for a in plan.allocations
        ],
        "by_intervention": plan.by_intervention,
    }


# ============================================================
# GET /executive-summary — Executive summary
# ============================================================
@router.get("/executive-summary")
async def executive_summary():
    """Executive summary untuk decision maker."""
    return generate_executive_summary()