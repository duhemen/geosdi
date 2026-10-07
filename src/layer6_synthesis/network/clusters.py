"""
GeoSDI Network — Community Detection
=====================================
Deteksi komunitas WKP dalam network:
- Louvain algorithm (modularity optimization)
- Label propagation
- Cluster summary per komunitas

Cluster = "kelompok WKP yang saling terhubung erat"
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from collections import defaultdict

import networkx as nx
import networkx.algorithms.community as nx_comm

from src.layer6_synthesis.network.adjacency import (
    build_adjacency_matrix,
    AdjacencyMatrix,
)
from src.layer6_synthesis.network.centrality import _build_nx_graph
from src.shared.logger import get_logger

log = get_logger(__name__)


# ============================================================
# Data classes
# ============================================================
@dataclass
class Community:
    """Komunitas WKP."""
    id: int
    size: int
    wkps: list[dict]
    avg_gdi: float
    total_kapasitas_mw: float
    dominant_provinsi: str
    dominant_type: str
    provinces: list[str]


# ============================================================
# Detect communities
# ============================================================
def detect_communities(
    algorithm: str = "louvain",
    seed: int = 42,
) -> dict:
    """
    Deteksi komunitas WKP.

    Args:
        algorithm: "louvain" | "label_propagation" | "greedy"
        seed: random seed untuk reproducibility

    Returns:
        Dict dengan communities + metadata.
    """
    adj = build_adjacency_matrix()
    G = _build_nx_graph(adj)

    if G.number_of_nodes() == 0:
        return {"algorithm": algorithm, "communities": [], "n_communities": 0}

    # --- Run algorithm ---
    if algorithm == "louvain":
        # Louvain butuh node weights (bukan edge)
        try:
            communities_raw = list(
                nx_comm.louvain_communities(G, weight="weight", seed=seed)
            )
        except Exception as e:
            log.warning(f"Louvain failed: {e}, fallback to greedy")
            communities_raw = list(
                nx_comm.greedy_modularity_communities(G, weight="weight")
            )
    elif algorithm == "label_propagation":
        communities_raw = list(
            nx_comm.label_propagation_communities(G)
        )
    elif algorithm == "greedy":
        communities_raw = list(
            nx_comm.greedy_modularity_communities(G, weight="weight")
        )
    else:
        raise ValueError(
            f"Algorithm '{algorithm}' tidak dikenal. "
            "Pilih: louvain | label_propagation | greedy"
        )

    # --- Build community objects ---
    communities = []
    for cid, nodes_set in enumerate(communities_raw):
        wkp_list = []
        gdi_values = []
        kapasitas_total = 0.0
        provinces = defaultdict(int)
        types = defaultdict(int)

        for kode in nodes_set:
            node_data = G.nodes[kode]
            wkp_list.append({
                "kode": kode,
                "nama": node_data.get("nama", ""),
                "provinsi": node_data.get("provinsi", ""),
                "status": node_data.get("status", ""),
                "type": node_data.get("type", ""),
                "gdi_mean": node_data.get("gdi_mean", 0),
                "kapasitas_mw": node_data.get("kapasitas_mw", 0),
            })
            gdi_values.append(node_data.get("gdi_mean", 0))
            kapasitas_total += node_data.get("kapasitas_mw", 0)
            provinces[node_data.get("provinsi", "")] += 1
            types[node_data.get("type", "")] += 1

        wkp_list.sort(key=lambda w: w["gdi_mean"], reverse=True)

        avg_gdi = sum(gdi_values) / len(gdi_values) if gdi_values else 0
        dominant_prov = max(provinces.items(), key=lambda x: x[1])[0] if provinces else ""
        dominant_type = max(types.items(), key=lambda x: x[1])[0] if types else ""

        communities.append(Community(
            id=cid,
            size=len(nodes_set),
            wkps=wkp_list,
            avg_gdi=round(avg_gdi, 2),
            total_kapasitas_mw=round(kapasitas_total, 2),
            dominant_provinsi=dominant_prov,
            dominant_type=dominant_type,
            provinces=sorted(provinces.keys()),
        ))

    # Sort by size DESC
    communities.sort(key=lambda c: c.size, reverse=True)

    # Compute modularity
    try:
        modularity = nx_comm.modularity(G, communities_raw, weight="weight")
    except Exception:
        modularity = 0.0

    log.info(
        f"Detected {len(communities)} communities "
        f"using {algorithm} (modularity={modularity:.4f})"
    )

    return {
        "algorithm": algorithm,
        "n_communities": len(communities),
        "modularity": round(modularity, 4),
        "communities": [
            {
                "id": c.id,
                "size": c.size,
                "avg_gdi": c.avg_gdi,
                "total_kapasitas_mw": c.total_kapasitas_mw,
                "dominant_provinsi": c.dominant_provinsi,
                "dominant_type": c.dominant_type,
                "provinces": c.provinces,
                "wkps": c.wkps,
            }
            for c in communities
        ],
    }


# ============================================================
# Cluster summary
# ============================================================
def get_cluster_summary(
    algorithm: str = "louvain",
) -> dict:
    """Ringkasan komunitas (tanpa detail WKP)."""
    result = detect_communities(algorithm=algorithm)

    return {
        "algorithm": result["algorithm"],
        "n_communities": result["n_communities"],
        "modularity": result["modularity"],
        "communities": [
            {
                "id": c["id"],
                "size": c["size"],
                "avg_gdi": c["avg_gdi"],
                "total_kapasitas_mw": c["total_kapasitas_mw"],
                "dominant_provinsi": c["dominant_provinsi"],
                "dominant_type": c["dominant_type"],
                "provinces": c["provinces"],
            }
            for c in result["communities"]
        ],
    }