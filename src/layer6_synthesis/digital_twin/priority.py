"""
GeoSDI Digital Twin — Priority Ranking Engine
===============================================
Hitung prioritas intervensi untuk setiap WKP.

Priority = f(Impact, Urgency, Effort, Confidence)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.shared.database import get_cursor
from src.shared.logger import get_logger

log = get_logger(__name__)


@dataclass
class WKPPriority:
    """Priority score untuk satu WKP."""
    kode: str
    nama: str
    provinsi: str
    status: str

    # Metrics
    gdi_current: float
    gdi_status: str
    kapasitas_mw: float
    var_c: float  # conflict
    var_s: float  # social
    var_t: float  # technology

    # Scores (0-100)
    impact_score: float      # Potensi peningkatan GDI × kapasitas
    urgency_score: float     # Seberapa urgent (GDI rendah = urgent)
    effort_score: float      # Seberapa sulit intervensi
    confidence_score: float  # Seberapa yakin kita

    # Priority
    priority_score: float    # Composite
    priority_level: str      # Critical/High/Medium/Low
    priority_rank: int

    # Recommendation
    recommendation: str
    intervention_type: str   # "sosial", "teknis", "ekonomi", "komprehensif"


# ============================================================
# Scoring functions
# ============================================================
def calc_impact_score(gdi: float, kapasitas: float, status: str = "Unknown") -> float:
    """
    Impact = (potential improvement) × (kapasitas) × (strategic weight)
    
    Improvement:
    - WKP mature dengan kapasitas besar → incremental improvement (medium impact)
    - WKP eksplorasi dengan kapasitas 0 → transformational potential (high impact)
    - WKP developing → seimbang
    """
    # Potential improvement (0-100): makin rendah GDI, makin besar
    potential = 100 - gdi

    # Kapasitas normalized (max 400 MW)
    kapasitas_norm = min(kapasitas / 400 * 100, 100) if kapasitas else 0

    # Strategic weight by status
    # Eksplorasi = high risk high reward
    # Mature = safe incremental
    strategic_weights = {
        "Operasi": 0.7,        # sudah mature, incremental
        "Konstruksi": 1.0,     # momentum bagus, strategic
        "Eksplorasi": 1.3,     # potential besar, risky, high priority
        "Perencanaan": 1.1,    # awal, tapi belum tentu jadi
        "Non-Aktif": 0.5,      # dormant
    }
    strategic = strategic_weights.get(status, 0.8)

    # Impact composite
    # Untuk WKP eksplorasi (kapasitas 0), kita emphasize potential
    # Untuk WKP operasi (kapasitas besar), kita emphasize kapasitas
    if status == "Eksplorasi" or status == "Perencanaan":
        # Potential lebih penting
        base_impact = potential * 0.8 + kapasitas_norm * 0.2
    elif status == "Operasi":
        # Kapasitas + potential keduanya penting
        base_impact = potential * 0.4 + kapasitas_norm * 0.6
    else:
        # Developing = seimbang
        base_impact = potential * 0.6 + kapasitas_norm * 0.4

    impact = base_impact * strategic

    return round(impact, 2)

def calc_urgency_score(
    gdi: float,
    conflict: float,
    social: float = 0.5,
    status: str = "Unknown",
    has_history: bool = True,
) -> float:
    """
    Urgency = multi-factor urgency scoring.
    
    Faktor:
    1. GDI rendah → urgent (butuh perbaikan)
    2. Konflik tinggi → urgent (butuh intervensi)
    3. Social rendah → urgent (masyarakat tidak kooperatif)
    4. Status eksplorasi dengan momentum → urgent (jangan sampai kehilangan momentum)
    5. Data tidak lengkap → urgent (butuh perhatian data)
    """
    # Factor 1: GDI rendah
    gdi_urgency = max(0, 100 - gdi)

    # Factor 2: Konflik tinggi
    conflict_urgency = conflict * 100

    # Factor 3: Social rendah
    social_urgency = (1 - social) * 100

    # Factor 4: Strategic status
    # Eksplorasi dengan momentum → urgent
    # Operasi mature → tidak urgent
    status_urgency = {
        "Operasi": 30,       # mature, tidak urgent
        "Konstruksi": 70,    # momentum, urgent
        "Eksplorasi": 80,    # jangan sampai kehilangan momentum
        "Perencanaan": 60,   # awal, tapi belum eksekusi
        "Non-Aktif": 90,     # dormant, sangat urgent
        "Unknown": 50,
    }.get(status, 50)

    # Factor 5: Data confidence
    data_urgency = 80 if not has_history else 30

    # Composite
    urgency = (
        gdi_urgency * 0.35 +
        conflict_urgency * 0.20 +
        social_urgency * 0.15 +
        status_urgency * 0.15 +
        data_urgency * 0.15
    )

    return round(min(100, urgency), 2)

def calc_effort_score(conflict: float, social: float, tech: float) -> float:
    """
    Effort = seberapa sulit intervensi.
    
    Konflik tinggi + social rendah + tech rendah = effort tinggi.
    """
    # Konflik tinggi → effort tinggi
    conflict_effort = conflict * 100

    # Social rendah → effort tinggi (masyarakat tidak kooperatif)
    social_effort = (1 - social) * 100

    # Tech rendah → effort tinggi (butuh investasi besar)
    tech_effort = (1 - tech) * 100

    # Composite
    effort = conflict_effort * 0.4 + social_effort * 0.3 + tech_effort * 0.3

    return round(effort, 2)


def calc_confidence_score(has_history: bool, mape: float = 5.0) -> float:
    """
    Confidence = seberapa yakin kita dengan data WKP.
    
    WKP dengan history → confidence tinggi.
    MAPE rendah → confidence tinggi.
    """
    base = 70 if has_history else 40

    # MAPE adjustment (rendah = bagus)
    mape_adjustment = max(0, 30 - mape) * 0.5

    return round(min(100, base + mape_adjustment), 2)


def calc_priority_score(impact: float, urgency: float, effort: float, confidence: float) -> float:
    """
    Priority = f(Impact, Urgency, Effort, Confidence)
    
    Skala normalisasi baru:
    - Max Impact ~100
    - Max Urgency ~100
    - Max Confidence = 1
    - Min Effort = 1 (untuk maximize)
    
    Max realistic raw_score = 100 × 100 × 1 / 1 = 10,000
    Normalisasi ke 0-100 → divide by 100
    """
    numerator = impact * urgency * (confidence / 100)
    denominator = effort + 1
    raw_score = numerator / denominator

    # Normalisasi dengan skala yang benar
    # Max realistic raw_score ~ 2500 (impact 50 × urgency 50 / effort 1)
    score = min(100, (raw_score / 2500) * 100)

    return round(score, 2)

def classify_priority(score: float) -> str:
    """Klasifikasi priority score."""
    if score >= 40:
        return "Critical"
    elif score >= 25:
        return "High"
    elif score >= 15:
        return "Medium"
    else:
        return "Low"


def generate_recommendation(w: dict) -> tuple[str, str]:
    """
    Generate recommendation text & intervention type.
    
    Returns:
        (recommendation_text, intervention_type)
    """
    gdi = float(w["gdi_current"])
    conflict = float(w["var_c"])
    social = float(w["var_s"])
    tech = float(w["var_t"])
    kapasitas = float(w["kapasitas_mw"] or 0)

    # Klasifikasi intervensi
    if conflict > 0.5:
        return (
            f"Prioritas resolusi konflik sosial di sekitar WKP. "
            f"Konflik saat ini sangat tinggi ({conflict:.2f}). "
            f"Butuh pendekatan partisipatif dengan masyarakat.",
            "sosial"
        )
    elif social < 0.5:
        return (
            f"Perlu peningkatan social acceptance. "
            f"Program CSR & community engagement dianjurkan. "
            f"Social acceptance saat ini {social:.2f}.",
            "sosial"
        )
    elif tech < 0.5:
        return (
            f"Butuh investasi teknologi. WKP ini baru/eksplorasi "
            f"dengan technology readiness rendah ({tech:.2f}). "
            f"Butuh capital besar untuk pengembangan.",
            "teknis"
        )
    elif kapasitas > 200:
        return (
            f"WKP mature dengan kapasitas besar ({kapasitas:.0f} MW). "
            f"Optimalisasi operasional & maintenance dapat "
            f"meningkatkan output. Fokus pada efisiensi.",
            "ekonomi"
        )
    elif gdi < 60:
        return (
            f"WKP butuh intervensi komprehensif. GDI rendah ({gdi:.1f}) "
            f"menunjukkan masalah multidimensi. Butuh pendekatan "
            f"holistik dari semua aspek.",
            "komprehensif"
        )
    else:
        return (
            f"WKP dalam kondisi baik. Lanjutkan monitoring rutin. "
            f"Fokus pada perbaikan incremental.",
            "maintenance"
        )


# ============================================================
# Main: Compute priority rankings
# ============================================================
def compute_priority_ranking(limit: Optional[int] = None) -> list[WKPPriority]:
    """Hitung priority ranking untuk semua WKP."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                wa.kode, wa.nama, wa.provinsi, wa.status,
                COALESCE(wa.kapasitas_mw, 0) AS kapasitas_mw,
                gs.gdi_mean AS gdi_current,
                gs.status AS gdi_status,
                gs.var_c, gs.var_s, gs.var_t,
                CASE WHEN EXISTS (
                    SELECT 1 FROM geosdi.gdi_history gh
                    WHERE gh.work_area_id = wa.id
                ) THEN true ELSE false END AS has_history
            FROM geosdi.work_areas wa
            JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id
            ORDER BY wa.kode;
        """)
        wkps = cur.fetchall()

    results = []

    for w in wkps:
        gdi = float(w["gdi_current"])
        kapasitas = float(w["kapasitas_mw"] or 0)
        conflict = float(w["var_c"] or 0)
        social = float(w["var_s"] or 0)
        tech = float(w["var_t"] or 0)
        status = w["status"]
        has_history = w["has_history"]

        # Calc scores dengan formula baru
        impact = calc_impact_score(gdi, kapasitas, status)
        urgency = calc_urgency_score(gdi, conflict, social, status, has_history)
        effort = calc_effort_score(conflict, social, tech)
        confidence = calc_confidence_score(has_history)

        priority_score = calc_priority_score(impact, urgency, effort, confidence)
        priority_level = classify_priority(priority_score)

        # Recommendation
        recommendation, intervention_type = generate_recommendation(w)

        results.append(WKPPriority(
            kode=w["kode"],
            nama=w["nama"],
            provinsi=w["provinsi"],
            status=status,
            gdi_current=round(gdi, 2),
            gdi_status=w["gdi_status"],
            kapasitas_mw=kapasitas,
            var_c=round(conflict, 3),
            var_s=round(social, 3),
            var_t=round(tech, 3),
            impact_score=impact,
            urgency_score=urgency,
            effort_score=effort,
            confidence_score=confidence,
            priority_score=priority_score,
            priority_level=priority_level,
            priority_rank=0,
            recommendation=recommendation,
            intervention_type=intervention_type,
        ))

    # Sort by priority_score
    results.sort(key=lambda x: x.priority_score, reverse=True)

    # Set rank
    for i, r in enumerate(results):
        r.priority_rank = i + 1

    if limit:
        results = results[:limit]

    return results

def get_priority_summary() -> dict:
    """Ringkasan prioritas nasional."""
    rankings = compute_priority_ranking()

    # Hitung per level
    by_level = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    by_intervention = {}

    for r in rankings:
        by_level[r.priority_level] += 1
        by_intervention[r.intervention_type] = by_intervention.get(r.intervention_type, 0) + 1

    # Top 10
    top_10 = rankings[:10]

    return {
        "total_wkp": len(rankings),
        "by_level": by_level,
        "by_intervention": by_intervention,
        "top_10": [
            {
                "rank": r.priority_rank,
                "kode": r.kode,
                "nama": r.nama,
                "provinsi": r.provinsi,
                "priority_score": r.priority_score,
                "priority_level": r.priority_level,
                "intervention_type": r.intervention_type,
                "recommendation": r.recommendation,
            }
            for r in top_10
        ],
    }