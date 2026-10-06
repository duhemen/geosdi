"""
GeoSDI Digital Twin — Budget Allocation Optimizer
==================================================
Alokasi anggaran optimal berdasarkan priority ranking.

Strategi: Greedy allocation — alokasi dana ke WKP dengan ROI tertinggi dulu.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.shared.database import get_cursor
from src.layer6_synthesis.digital_twin.priority import (
    compute_priority_ranking,
    WKPPriority,
)

# Estimasi biaya intervensi per tipe (dalam miliar rupiah)
INTERVENTION_COSTS = {
    "sosial": 500,         # Rp 500 miliar (program CSR, community engagement)
    "teknis": 5000,        # Rp 5 triliun (eksplorasi, pemboran)
    "ekonomi": 1500,       # Rp 1.5 triliun (optimalisasi)
    "komprehensif": 3000,  # Rp 3 triliun (multi-aspek)
    "maintenance": 200,    # Rp 200 miliar (monitoring)
}

# Estimasi dampak GDI per intervensi (dalam poin)
INTERVENTION_IMPACTS = {
    "sosial": 3.0,
    "teknis": 5.0,
    "ekonomi": 2.5,
    "komprehensif": 4.0,
    "maintenance": 0.5,
}


@dataclass
class Allocation:
    kode: str
    nama: str
    provinsi: str
    intervention_type: str
    priority_score: float
    priority_level: str

    # GDI
    gdi_before: float
    gdi_after: float
    gdi_gain: float

    # Kapasitas
    capacity_before_mw: float
    capacity_after_mw: float
    capacity_gain_mw: float

    # Biaya & ROI
    cost_billion: float
    roi: float  # GDI gain per miliar Rp

    # Justifikasi
    rationale: str

@dataclass
class BudgetPlan:
    total_budget_billion: float
    allocated_billion: float
    remaining_billion: float

    # Allocations
    allocations: list[Allocation]
    total_wkp_funded: int
    total_expected_gdi_gain: float
    total_expected_mw_gain: float

    # Impact estimate
    national_gdi_before: float
    national_gdi_after: float
    national_gdi_delta: float

    # Per WKP impact
    avg_gdi_gain_per_wkp: float

    # Summary
    by_intervention: dict[str, dict]


def optimize_budget(total_budget_billion: float) -> BudgetPlan:
    """
    Alokasi anggaran optimal dengan greedy algorithm.
    
    Sorting: by ROI (expected_gain × priority / cost)
    """
    rankings = compute_priority_ranking()

    # Hitung ROI untuk setiap WKP
    candidates = []
    for w in rankings:
        cost = INTERVENTION_COSTS.get(w.intervention_type, 1000)
        base_gain = INTERVENTION_IMPACTS.get(w.intervention_type, 2.0)

        # Adjust gain by priority score
        adjusted_gain = base_gain * (w.priority_score / 30)  # normalize by priority

        # ROI: gain per miliar
        roi = adjusted_gain / cost * 1000

        # Adjust ROI by confidence
        roi = roi * (w.confidence_score / 100)

        # Estimated MW gain (rough)
        mw_gain = 0
        if w.intervention_type == "teknis":
            mw_gain = 50  # new capacity
        elif w.intervention_type == "ekonomi":
            mw_gain = w.kapasitas_mw * 0.05  # 5% improvement
        elif w.intervention_type == "komprehensif":
            mw_gain = 30

        candidates.append({
            "wkp": w,
            "cost": cost,
            "gain": adjusted_gain,
            "roi": roi,
            "mw_gain": mw_gain,
        })

    # Sort by ROI
    candidates.sort(key=lambda c: c["roi"], reverse=True)

    # Allocate
    allocated = 0
    allocations = []
    total_gain = 0
    total_mw_gain = 0

    for c in candidates:
        if allocated + c["cost"] > total_budget_billion:
            continue

        allocated += c["cost"]
        w = c["wkp"]
        gain = c["gain"]

        allocations.append(Allocation(
            kode=w.kode,
            nama=w.nama,
            provinsi=w.provinsi,
            intervention_type=w.intervention_type,
            priority_score=w.priority_score,
            priority_level=w.priority_level,
            gdi_before=w.gdi_current,
            gdi_after=round(w.gdi_current + gain, 2),
            gdi_gain=round(gain, 2),
            capacity_before_mw=w.kapasitas_mw,
            capacity_after_mw=round(w.kapasitas_mw + c["mw_gain"], 1),
            capacity_gain_mw=round(c["mw_gain"], 1),
            cost_billion=c["cost"],
            roi=round(c["roi"], 2),
            rationale=w.recommendation,
        ))

        total_gain += gain
        total_mw_gain += c["mw_gain"]

        if allocated >= total_budget_billion:
            break

    # National impact
    with get_cursor() as cur:
        cur.execute("SELECT AVG(gdi_mean) AS avg_gdi, COUNT(*) AS cnt FROM geosdi.gdi_scores;")
        row = cur.fetchone()
        national_before = float(row["avg_gdi"] or 0)
        total_wkp = row["cnt"]

    # Correct national impact calculation
    # Only the funded WKP change
    national_after = national_before + (total_gain / total_wkp)

    # By intervention
    by_intervention = {}
    for a in allocations:
        if a.intervention_type not in by_intervention:
            by_intervention[a.intervention_type] = {
                "count": 0,
                "total_cost": 0,
                "total_gain": 0,
                "total_mw": 0,
            }
        by_intervention[a.intervention_type]["count"] += 1
        by_intervention[a.intervention_type]["total_cost"] += a.cost_billion
        by_intervention[a.intervention_type]["total_gain"] += a.gdi_gain
        by_intervention[a.intervention_type]["total_mw"] += a.capacity_gain_mw

    avg_gain_per_wkp = total_gain / len(allocations) if allocations else 0

    return BudgetPlan(
        total_budget_billion=total_budget_billion,
        allocated_billion=allocated,
        remaining_billion=total_budget_billion - allocated,
        allocations=allocations,
        total_wkp_funded=len(allocations),
        total_expected_gdi_gain=round(total_gain, 2),
        total_expected_mw_gain=round(total_mw_gain, 1),
        national_gdi_before=round(national_before, 2),
        national_gdi_after=round(national_after, 2),
        national_gdi_delta=round(national_after - national_before, 2),
        avg_gdi_gain_per_wkp=round(avg_gain_per_wkp, 2),
        by_intervention=by_intervention,
    )