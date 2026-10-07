"""
GeoSDI Digital Twin — Enhanced Scenario Simulator
==================================================
Simulasi skenario kebijakan dengan model yang lebih realistis.

Enhancements:
1. Sensitivity per WKP (saturasi di GDI tinggi)
2. Interaction effects (konflik, social)
3. WKP type awareness (mature/developing/new)
4. Time delay (investasi butuh waktu)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.shared.database import get_cursor
from src.shared.logger import get_logger
from src.layer5_inference.analytics.gdi_model import compute_gdi

log = get_logger(__name__)


# ============================================================
# WKP Type Classification
# ============================================================
def classify_wkp_type(tahun_operasi: Optional[int], status: str) -> str:
    """
    Klasifikasi WKP berdasarkan maturity.

    Returns:
        "mature" | "developing" | "new" | "exploration"

    Mapping status:
    - Operasi + tahun < 2000     → mature
    - Operasi + tahun 2000-2014  → developing
    - Operasi + tahun >= 2015    → new
    - Operasi + tahun NULL       → mature (asumsi WKP tua)
    - IPB Eksplorasi             → exploration
    - Dalam Survei               → developing
    - Perencanaan                → new
    - Belum Ada Pemegang IPB     → new
    - Eksplorasi (literal)       → exploration (backward compat)
    """
    # === Status eksplisit (prioritas tertinggi) ===
    if status in ("Eksplorasi", "IPB Eksplorasi"):
        return "exploration"
    if status == "Belum Ada Pemegang IPB":
        return "new"
    if status == "Perencanaan":
        return "new"
    if status == "Dalam Survei":
        return "developing"

    # === Status Operasi — klasifikasi by tahun ===
    if status == "Operasi":
        if tahun_operasi is None:
            return "mature"
        if tahun_operasi < 2000:
            return "mature"
        elif tahun_operasi < 2015:
            return "developing"
        else:
            return "new"

    # Fallback
    return "new"


def get_type_sensitivity(wkp_type: str) -> float:
    """
    Sensitivity multiplier berdasarkan tipe WKP.
    
    - Mature: respons kecil (sudah optimal)
    - Developing: respons sedang
    - New: respons besar
    - Exploration: respons paling besar
    """
    return {
        "mature": 0.5,       # hanya 50% dari delta
        "developing": 0.8,   # 80%
        "new": 1.0,          # 100%
        "exploration": 1.2,  # 120% (lebih volatile)
    }.get(wkp_type, 1.0)


# ============================================================
# Data classes
# ============================================================
@dataclass
class Scenario:
    """Skenario perubahan variabel (delta, bukan absolut)."""
    name: str = "Custom Scenario"

    # Delta untuk setiap variabel (-0.5 to +0.5)
    delta_r: float = 0.0
    delta_t: float = 0.0
    delta_e: float = 0.0
    delta_p: float = 0.0
    delta_s: float = 0.0
    delta_n: float = 0.0
    delta_c: float = 0.0
    delta_h: float = 0.0

    # Filter WKP yang terpengaruh (opsional)
    filter_provinsi: Optional[str] = None
    filter_status: Optional[str] = None
    filter_type: Optional[str] = None  # mature/developing/new/exploration

    # === NETWORK-AWARE (BARU) ===
    enable_network: bool = False       # Aktifkan network propagation?
    network_decay: float = 0.30        # Atenuasi per hop
    network_max_hops: int = 2          # Maksimum hop propagasi

    # Tuning options
    enable_time_delay: bool = True      # apply 40% untuk 1 tahun
    enable_sensitivity: bool = True     # apply sensitivity per WKP
    enable_interactions: bool = True    # apply interaction effects
    enable_type_awareness: bool = True  # apply type-based sensitivity

    # Time delay factor
    time_delay_factor: float = 0.4      # 40% dalam 1 tahun


@dataclass
class ScenarioResult:
    """Hasil simulasi skenario."""
    scenario_name: str

    # Baseline
    baseline_gdi: float
    baseline_health: float

    # Simulated
    simulated_gdi: float
    simulated_health: float

    # Delta
    delta_gdi: float
    delta_percent: float

    # Breakdown
    wkp_affected: int
    wkp_improved: int
    wkp_worsened: int
    wkp_unchanged: int

    # Top movers
    top_improvements: list[dict]
    top_declines: list[dict]

        # Type breakdown
    by_type: dict[str, dict]

    # === NETWORK-AWARE (BARU) ===
    network_enabled: bool = False
    network_effect: float = 0.0          # Total efek network
    n_network_affected: int = 0          # Berapa WKP kena efek network
    network_top_affected: list[dict] = None  # Top WKP yang kena network effect


# ============================================================
# Core: Apply scenario dengan enhancements
# ============================================================
def apply_scenario(scenario: Scenario) -> ScenarioResult:
    """
    Apply scenario dengan 4 enhancements.
    
    Enhanced logic:
    1. Sensitivity per WKP (saturasi)
    2. Interaction effects (konflik, social)
    3. WKP type awareness
    4. Time delay
    """
    with get_cursor() as cur:
        # Build WHERE clause
        where = []
        params = []

        if scenario.filter_provinsi:
            where.append("wa.provinsi = %s")
            params.append(scenario.filter_provinsi)
        if scenario.filter_status:
            where.append("wa.status = %s")
            params.append(scenario.filter_status)

        where_sql = "WHERE " + " AND ".join(where) if where else ""

        # Ambil WKP dengan info lengkap
        cur.execute(f"""
            SELECT
                wa.id, wa.kode, wa.nama, wa.provinsi, wa.status,
                wa.tahun_operasi,
                gs.gdi_mean AS baseline_gdi,
                gs.var_r, gs.var_t, gs.var_e, gs.var_p,
                gs.var_s, gs.var_n, gs.var_c, gs.var_h
            FROM geosdi.work_areas wa
            JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id
            {where_sql}
            ORDER BY wa.kode;
        """, params)
        wkps = cur.fetchall()

    if not wkps:
        raise ValueError("Tidak ada WKP yang cocok dengan filter")

    # Baseline
    baseline_gdis = [float(w["baseline_gdi"]) for w in wkps]
    baseline_avg = sum(baseline_gdis) / len(baseline_gdis)

    # Apply scenario dengan enhancements
    results = []
    improved = 0
    worsened = 0
    unchanged = 0

    by_type = {
        "mature": {"count": 0, "improved": 0, "worsened": 0, "avg_delta": 0.0, "total_delta": 0.0},
        "developing": {"count": 0, "improved": 0, "worsened": 0, "avg_delta": 0.0, "total_delta": 0.0},
        "new": {"count": 0, "improved": 0, "worsened": 0, "avg_delta": 0.0, "total_delta": 0.0},
        "exploration": {"count": 0, "improved": 0, "worsened": 0, "avg_delta": 0.0, "total_delta": 0.0},
    }

    for w in wkps:
        baseline_gdi = float(w["baseline_gdi"])
        baseline_c = float(w["var_c"] or 0)
        baseline_s = float(w["var_s"] or 0)

        # Klasifikasi WKP type
        wkp_type = classify_wkp_type(w["tahun_operasi"], w["status"])

        # Filter by type (kalau ada)
        if scenario.filter_type and wkp_type != scenario.filter_type:
            continue

        # === Enhancement #1: Sensitivity per WKP ===
        if scenario.enable_sensitivity:
            # WKP dengan GDI tinggi → sensitivity rendah (saturasi)
            sensitivity = (100 - baseline_gdi) / 100
            # Clamp: minimal 10% (biar tidak nol)
            sensitivity = max(0.1, sensitivity)
        else:
            sensitivity = 1.0

        # === Enhancement #3: Type Awareness ===
        if scenario.enable_type_awareness:
            type_multiplier = get_type_sensitivity(wkp_type)
        else:
            type_multiplier = 1.0

        # === Enhancement #4: Time Delay ===
        if scenario.enable_time_delay:
            time_multiplier = scenario.time_delay_factor
        else:
            time_multiplier = 1.0

        # Kombinasi multiplier
        combined_multiplier = sensitivity * type_multiplier * time_multiplier

        # === Enhancement #2: Interaction Effects ===
        # Konflik tinggi mengurangi efektivitas investasi (T, E)
        if scenario.enable_interactions:
            conflict_penalty = max(0.3, 1 - baseline_c * 0.7)  # max 70% penalty
            social_bonus = 0.5 + baseline_s * 0.5  # 50-100% untuk P
        else:
            conflict_penalty = 1.0
            social_bonus = 1.0

        # Apply delta dengan interaction
        def clamp(v, delta):
            return max(0, min(1, float(v or 0) + delta))

        new_vars = {
            "R": clamp(w["var_r"], scenario.delta_r * combined_multiplier),
            "T": clamp(w["var_t"], scenario.delta_t * combined_multiplier * conflict_penalty),
            "E": clamp(w["var_e"], scenario.delta_e * combined_multiplier * conflict_penalty),
            "P": clamp(w["var_p"], scenario.delta_p * combined_multiplier * social_bonus),
            "S": clamp(w["var_s"], scenario.delta_s * combined_multiplier),
            "N": clamp(w["var_n"], scenario.delta_n * combined_multiplier),
            "C": clamp(w["var_c"], scenario.delta_c * combined_multiplier),
            "H": clamp(w["var_h"], scenario.delta_h * combined_multiplier),
        }

        # Compute new GDI
        result = compute_gdi(
            kode=w["kode"],
            nama=w["nama"],
            variables=new_vars,
            seed=hash(w["kode"]) % 10000,
        )

        delta = result.mean - baseline_gdi

        if delta > 0.3:
            improved += 1
        elif delta < -0.3:
            worsened += 1
        else:
            unchanged += 1

        # Update type stats
        by_type[wkp_type]["count"] += 1
        by_type[wkp_type]["total_delta"] += delta
        if delta > 0.3:
            by_type[wkp_type]["improved"] += 1
        elif delta < -0.3:
            by_type[wkp_type]["worsened"] += 1

        results.append({
            "kode": w["kode"],
            "nama": w["nama"],
            "provinsi": w["provinsi"],
            "wkp_type": wkp_type,
            "baseline_gdi": round(baseline_gdi, 2),
            "simulated_gdi": round(result.mean, 2),
            "delta": round(delta, 2),
            "status": result.status,
            "multiplier": round(combined_multiplier, 3),
        })

    # Hitung avg delta per type
        # Hitung avg delta per type
    for t, data in by_type.items():
        if data["count"] > 0:
            data["avg_delta"] = round(data["total_delta"] / data["count"], 2)
        data["total_delta"] = round(data["total_delta"], 2)

    # === FIX: Guard: kalau tidak ada WKP yang match filter ===
    if not results:
        filter_desc = []
        if scenario.filter_type:
            filter_desc.append(f"type={scenario.filter_type}")
        if scenario.filter_status:
            filter_desc.append(f"status={scenario.filter_status}")
        if scenario.filter_provinsi:
            filter_desc.append(f"provinsi={scenario.filter_provinsi}")
        filter_str = ", ".join(filter_desc) if filter_desc else "tidak ada"

        raise ValueError(
            f"Tidak ada WKP yang cocok dengan filter ({filter_str}). "
            f"Preset ini tidak dapat dijalankan untuk dataset saat ini."
        )

        # === NETWORK-AWARE PROPAGATION ===
    network_effect = 0.0
    n_network_affected = 0
    network_top_affected = []

    if scenario.enable_network:
        try:
            from src.layer6_synthesis.network import build_adjacency_matrix

            adj_matrix = build_adjacency_matrix()
            n_net = adj_matrix.n_nodes

            # Build map: kode → node index
            kode_to_idx = {node.kode: i for i, node in enumerate(adj_matrix.nodes)}

            # Delta per WKP dari scenario
            delta_map = {r["kode"]: r["delta"] for r in results}

            # Propagate via network
            network_deltas = {}  # { kode: total_network_delta }

            for source_kode, source_delta in delta_map.items():
                if source_delta == 0:
                    continue

                src_idx = kode_to_idx.get(source_kode)
                if src_idx is None:
                    continue

                # BFS propagate
                visited = {src_idx: 1.0}
                frontier = {src_idx: 1.0}

                for hop in range(1, scenario.network_max_hops + 1):
                    next_frontier = {}
                    for node_idx, src_inf in frontier.items():
                        for j in range(n_net):
                            if j in visited:
                                continue
                            w = adj_matrix.matrix[node_idx, j]
                            if w <= 0:
                                continue
                            propagated = src_inf * w * scenario.network_decay
                            if propagated >= 0.01:
                                visited[j] = propagated
                                next_frontier[j] = propagated
                    frontier = next_frontier
                    if not frontier:
                        break

                # Akumulasi delta ke network_deltas
                for j, inf in visited.items():
                    if j == src_idx:
                        continue
                    target_kode = adj_matrix.nodes[j].kode
                    network_deltas[target_kode] = network_deltas.get(target_kode, 0.0) + source_delta * inf

            # Apply network delta ke results
            for r in results:
                net_delta = network_deltas.get(r["kode"], 0.0)
                r["network_delta"] = round(net_delta, 4)
                r["simulated_gdi_with_network"] = round(r["simulated_gdi"] + net_delta, 2)

            # Stats
            network_effect = sum(network_deltas.values())
            n_network_affected = len(network_deltas)

            # Top network affected
            sorted_net = sorted(network_deltas.items(), key=lambda x: x[1], reverse=True)[:10]
            network_top_affected = [
                {
                    "kode": kode,
                    "nama": next((n.nama for n in adj_matrix.nodes if n.kode == kode), ""),
                    "delta_network": round(delta, 4),
                }
                for kode, delta in sorted_net
            ]

            log.info(
                f"Network-aware propagation: {n_network_affected} WKP affected, "
                f"total network effect = {network_effect:.3f}"
            )
        except Exception as e:
            log.warning(f"Network propagation failed: {e}")

    # Simulated stats
    simulated_gdis = [r["simulated_gdi"] for r in results]
    simulated_avg = sum(simulated_gdis) / len(simulated_gdis)

    # Kalau network enabled, pakai simulated_gdi_with_network untuk avg
    if scenario.enable_network:
        simulated_with_net = [r.get("simulated_gdi_with_network", r["simulated_gdi"]) for r in results]
        simulated_avg_final = sum(simulated_with_net) / len(simulated_with_net)
    else:
        simulated_avg_final = simulated_avg

    # Simulated stats
    simulated_gdis = [r["simulated_gdi"] for r in results]
    simulated_avg = sum(simulated_gdis) / len(simulated_gdis)

    # Top movers
    sorted_results = sorted(results, key=lambda r: r["delta"], reverse=True)
    top_improvements = sorted_results[:5]
    top_declines = sorted_results[-5:][::-1]

    delta_gdi = simulated_avg_final - baseline_avg
    delta_pct = (delta_gdi / baseline_avg * 100) if baseline_avg > 0 else 0

    return ScenarioResult(
        scenario_name=scenario.name,
        baseline_gdi=round(baseline_avg, 2),
        baseline_health=round(baseline_avg, 2),
        simulated_gdi=round(simulated_avg_final, 2),
        simulated_health=round(simulated_avg_final, 2),
        delta_gdi=round(delta_gdi, 2),
        delta_percent=round(delta_pct, 2),
        wkp_affected=len(results),
        wkp_improved=improved,
        wkp_worsened=worsened,
        wkp_unchanged=unchanged,
        top_improvements=top_improvements,
        top_declines=top_declines,
        by_type=by_type,
        network_enabled=scenario.enable_network,
        network_effect=round(network_effect, 4),
        n_network_affected=n_network_affected,
        network_top_affected=network_top_affected or [],
    )


# ============================================================
# Preset Scenarios
# ============================================================
PRESET_SCENARIOS = {
    "optimistic": Scenario(
        name="📈 Optimistic — Investasi & Kebijakan",
        delta_t=0.15,
        delta_e=0.15,
        delta_p=0.10,
        delta_c=-0.10,
    ),
    "pessimistic": Scenario(
        name="📉 Pessimistic — Krisis Ekonomi & Konflik",
        delta_e=-0.15,
        delta_p=-0.10,
        delta_c=0.20,
    ),
    "social_first": Scenario(
        name="👥 Social First — Pemberdayaan Masyarakat",
        delta_s=0.20,
        delta_c=-0.15,
    ),
    "tech_first": Scenario(
        name="⚙️ Tech First — Investasi Teknologi",
        delta_t=0.25,
        delta_e=0.10,
    ),
    "baseline": Scenario(
        name="➡️ Baseline — Tanpa Perubahan",
    ),
    "mature_only": Scenario(
        name="🎯 Mature Only — Fokus WKP Mature",
        delta_t=0.20,
        delta_e=0.15,
        delta_c=-0.15,
        filter_type="mature",
    ),
    "exploration_only": Scenario(
        name="🔍 Exploration Only — Fokus Eksplorasi",
        delta_t=0.20,
        delta_e=0.20,
        delta_c=-0.10,
        filter_type="exploration",
    ),
}


def run_preset(name: str) -> ScenarioResult:
    """Jalankan preset scenario."""
    if name not in PRESET_SCENARIOS:
        raise ValueError(f"Preset '{name}' tidak ditemukan")
    return apply_scenario(PRESET_SCENARIOS[name])