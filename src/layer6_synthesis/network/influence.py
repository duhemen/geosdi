"""
GeoSDI Network — Influence Model
=================================
Model propagasi pengaruh antar-WKP:
- Influence matrix: seberapa besar WKP A mempengaruhi WKP B
- Propagate: kalau WKP A naik +X, WKP B naik berapa?
- Simulate intervention: intervensi di WKP tertentu, efek ke seluruh network

Influence = "kalau saya ubah 1 WKP, apa dampaknya ke WKP lain?"
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from src.layer6_synthesis.network.adjacency import (
    build_adjacency_matrix,
    AdjacencyMatrix,
)
from src.layer6_synthesis.network.centrality import compute_centrality
from src.shared.logger import get_logger

log = get_logger(__name__)


# ============================================================
# Constants
# ============================================================
# Faktor atenuasi: berapa persen influence yang "sampai" ke tetangga
DEFAULT_DECAY = 0.30   # 30% influence tiap hop
# Batas maksimum propagasi (jumlah hop)
DEFAULT_MAX_HOPS = 2
# Threshold minimum influence untuk dianggap signifikan
DEFAULT_MIN_INFLUENCE = 0.01


# ============================================================
# Data classes
# ============================================================
@dataclass
class InfluenceEdge:
    """Edge pengaruh dari WKP A ke WKP B."""
    source_kode: str
    target_kode: str
    source_name: str
    target_name: str
    weight: float             # adjacency weight
    influence: float          # actual influence (0-1)


@dataclass
class InterventionResult:
    """Hasil simulasi intervensi."""
    source_kode: str
    source_name: str
    delta_gdi: float          # perubahan GDI di source
    affected_wkps: list[dict]  # WKP yang terpengaruh
    total_network_effect: float  # total efek network
    n_affected: int
    max_hop: int


# ============================================================
# Influence matrix
# ============================================================
def compute_influence_matrix(
    decay: float = DEFAULT_DECAY,
    max_hops: int = DEFAULT_MAX_HOPS,
) -> dict:
    """
    Hitung influence matrix antar-WKP.

    Influence dari A ke B = adjacency_weight(A,B) × decay
    Untuk jarak multi-hop, influence = product of decays along path.

    Args:
        decay: faktor atenuasi per hop
        max_hops: maksimum jumlah hop untuk propagasi

    Returns:
        Dict dengan source → list of {target, influence, hop}.
    """
    adj = build_adjacency_matrix()
    n = adj.n_nodes

    influence_data = {}

    for i in range(n):
        source = adj.nodes[i]
        visited = {i: 1.0}  # {node_idx: influence_ratio}
        frontier = {i: 1.0}

        # BFS untuk propagasi multi-hop
        for hop in range(1, max_hops + 1):
            next_frontier = {}
            for node_idx, src_influence in frontier.items():
                for j in range(n):
                    if j in visited:
                        continue
                    w = adj.matrix[node_idx, j]
                    if w <= 0:
                        continue
                    propagated = src_influence * w * decay
                    if propagated >= DEFAULT_MIN_INFLUENCE:
                        if j not in visited or visited[j] < propagated:
                            visited[j] = propagated
                            next_frontier[j] = propagated
            frontier = next_frontier
            if not frontier:
                break

        # Build edges
        edges = []
        for j, inf in visited.items():
            if j == i:
                continue
            target = adj.nodes[j]
            edges.append({
                "target_kode": target.kode,
                "target_name": target.nama,
                "influence": round(float(inf), 4),
                "adjacency_weight": round(float(adj.matrix[i, j]), 4),
            })

        edges.sort(key=lambda e: e["influence"], reverse=True)

        influence_data[source.kode] = {
            "source_kode": source.kode,
            "source_name": source.nama,
            "source_type": source.type,
            "source_gdi": source.gdi_mean,
            "edges": edges,
            "n_edges": len(edges),
        }

    log.info(f"Computed influence matrix for {n} WKP")
    return influence_data


# ============================================================
# Propagate influence
# ============================================================
def propagate_influence(
    source_kode: str,
    delta_gdi: float,
    decay: float = DEFAULT_DECAY,
    max_hops: int = DEFAULT_MAX_HOPS,
) -> InterventionResult:
    """
    Propagasi influence dari 1 WKP ke tetangganya.

    Args:
        source_kode: WKP yang diintervensi
        delta_gdi: perubahan GDI di source (contoh: +5.0)
        decay: faktor atenuasi per hop
        max_hops: maksimum hop

    Returns:
        InterventionResult dengan semua WKP terpengaruh.
    """
    adj = build_adjacency_matrix()

    # Find source index
    source_idx = None
    for i, node in enumerate(adj.nodes):
        if node.kode == source_kode:
            source_idx = i
            break

    if source_idx is None:
        raise ValueError(f"WKP {source_kode} tidak ditemukan")

    source_node = adj.nodes[source_idx]

    # BFS propagate
    visited = {source_idx: 1.0}
    frontier = {source_idx: 1.0}

    for hop in range(1, max_hops + 1):
        next_frontier = {}
        for node_idx, src_influence in frontier.items():
            for j in range(adj.n_nodes):
                if j in visited:
                    continue
                w = adj.matrix[node_idx, j]
                if w <= 0:
                    continue
                propagated = src_influence * w * decay
                if propagated >= DEFAULT_MIN_INFLUENCE:
                    visited[j] = propagated
                    next_frontier[j] = propagated
        frontier = next_frontier
        if not frontier:
            break

    # Build affected list
    affected = []
    for j, inf in visited.items():
        if j == source_idx:
            continue
        node = adj.nodes[j]
        affected.append({
            "kode": node.kode,
            "nama": node.nama,
            "provinsi": node.provinsi,
            "type": node.type,
            "gdi_before": node.gdi_mean,
            "delta_gdi": round(delta_gdi * inf, 4),
            "influence_ratio": round(inf, 4),
        })

    affected.sort(key=lambda a: a["delta_gdi"], reverse=True)

    total_effect = sum(a["delta_gdi"] for a in affected)

    return InterventionResult(
        source_kode=source_node.kode,
        source_name=source_node.nama,
        delta_gdi=delta_gdi,
        affected_wkps=affected,
        total_network_effect=round(total_effect, 4),
        n_affected=len(affected),
        max_hop=max_hops,
    )


# ============================================================
# Simulate network intervention
# ============================================================
def simulate_network_intervention(
    delta_gdi_per_wkp: float,
    filter_type: Optional[str] = None,
    decay: float = DEFAULT_DECAY,
    max_hops: int = DEFAULT_MAX_HOPS,
) -> dict:
    """
    Simulasi intervensi ke seluruh network.

    Args:
        delta_gdi_per_wkp: perubahan GDI langsung (di source WKP)
        filter_type: kalau diisi, hanya apply ke WKP type tertentu
        decay, max_hops: parameter propagasi

    Returns:
        Hasil simulasi lengkap dengan agregat.
    """
    adj = build_adjacency_matrix()

    # Filter sources
    sources = []
    for node in adj.nodes:
        if filter_type and node.type != filter_type:
            continue
        sources.append(node)

    if not sources:
        return {
            "delta_per_wkp": delta_gdi_per_wkp,
            "filter_type": filter_type,
            "n_sources": 0,
            "total_network_effect": 0.0,
            "results": [],
        }

    # Simulasi per source
    results = []
    total_effect = 0.0

    for src in sources:
        r = propagate_influence(
            source_kode=src.kode,
            delta_gdi=delta_gdi_per_wkp,
            decay=decay,
            max_hops=max_hops,
        )
        results.append({
            "source_kode": src.kode,
            "source_name": src.nama,
            "delta_direct": delta_gdi_per_wkp,
            "delta_network": r.total_network_effect,
            "n_affected": r.n_affected,
        })
        total_effect += r.total_network_effect

    # Aggregate
    return {
        "delta_per_wkp": delta_gdi_per_wkp,
        "filter_type": filter_type,
        "n_sources": len(sources),
        "total_direct_effect": round(delta_gdi_per_wkp * len(sources), 4),
        "total_network_effect": round(total_effect, 4),
        "grand_total": round(delta_gdi_per_wkp * len(sources) + total_effect, 4),
        "avg_network_per_source": round(total_effect / len(sources), 4),
        "results": results,
    }