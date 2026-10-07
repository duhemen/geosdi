"""
GeoSDI Network — Centrality Analysis
=====================================
Hitung centrality WKP dalam network:
- Degree: berapa banyak tetangga
- Betweenness: seberapa sering jadi "jembatan" antar WKP
- Closeness: seberapa dekat ke semua WKP lain
- PageRank: prestise berdasarkan network (Google algorithm)
- Eigenvector: prestise berdasarkan koneksi ke node penting

Centrality = "WKP mana yang paling pusat dalam network?"
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import networkx as nx

from src.layer6_synthesis.network.adjacency import (
    build_adjacency_matrix,
    AdjacencyMatrix,
)
from src.shared.logger import get_logger

log = get_logger(__name__)


# ============================================================
# Data classes
# ============================================================
@dataclass
class CentralityResult:
    """Hasil centrality per WKP."""
    kode: str
    nama: str
    provinsi: str
    status: str
    type: str
    gdi_mean: float
    kapasitas_mw: float

    # Centrality metrics
    degree: float              # jumlah tetangga (weighted)
    degree_normalized: float   # degree / (n-1)
    betweenness: float         # 0-1
    closeness: float           # 0-1
    pagerank: float            # > 0, biasanya < 1
    eigenvector: float         # 0-1


@dataclass
class NetworkStats:
    """Statistik network."""
    n_nodes: int
    n_edges: int
    density: float
    avg_degree: float
    avg_clustering: float
    is_connected: bool
    n_components: int
    largest_component_size: int


# ============================================================
# Build NetworkX graph dari adjacency
# ============================================================
def _build_nx_graph(adj: AdjacencyMatrix) -> nx.Graph:
    """Konversi AdjacencyMatrix ke NetworkX Graph."""
    G = nx.Graph()

    # Add nodes
    for node in adj.nodes:
        G.add_node(
            node.kode,
            nama=node.nama,
            provinsi=node.provinsi,
            status=node.status,
            type=node.type,
            gdi_mean=node.gdi_mean,
            kapasitas_mw=node.kapasitas_mw,
        )

    # Add edges dengan weight
    n = adj.n_nodes
    for i in range(n):
        for j in range(i + 1, n):
            w = adj.matrix[i, j]
            if w > 0:
                G.add_edge(
                    adj.nodes[i].kode,
                    adj.nodes[j].kode,
                    weight=float(w),
                )

    return G


# ============================================================
# Compute centrality
# ============================================================
def compute_centrality() -> list[CentralityResult]:
    """
    Hitung semua centrality metrics untuk setiap WKP.

    Returns:
        List CentralityResult, sorted by PageRank DESC.
    """
    adj = build_adjacency_matrix()
    G = _build_nx_graph(adj)

    n = G.number_of_nodes()
    if n == 0:
        return []

    # --- Compute centrality metrics ---
    # Degree (weighted)
    degree = dict(G.degree(weight="weight"))
    degree_norm = {k: v / (n - 1) if n > 1 else 0 for k, v in degree.items()}

    # Betweenness
    betweenness = nx.betweenness_centrality(G, weight="weight")

    # Closeness
    closeness = nx.closeness_centrality(G, distance="weight")

    # PageRank
    pagerank = nx.pagerank(G, weight="weight", alpha=0.85)

    # Eigenvector
    try:
        eigenvector = nx.eigenvector_centrality(G, weight="weight", max_iter=1000)
    except nx.PowerIterationFailedConvergence:
        log.warning("Eigenvector centrality did not converge, using uniform")
        eigenvector = {k: 0.0 for k in G.nodes()}

    # --- Build result ---
    results = []
    for node in adj.nodes:
        k = node.kode
        results.append(CentralityResult(
            kode=k,
            nama=node.nama,
            provinsi=node.provinsi,
            status=node.status,
            type=node.type,
            gdi_mean=node.gdi_mean,
            kapasitas_mw=node.kapasitas_mw,
            degree=round(float(degree.get(k, 0)), 4),
            degree_normalized=round(float(degree_norm.get(k, 0)), 4),
            betweenness=round(float(betweenness.get(k, 0)), 4),
            closeness=round(float(closeness.get(k, 0)), 4),
            pagerank=round(float(pagerank.get(k, 0)), 6),
            eigenvector=round(float(eigenvector.get(k, 0)), 4),
        ))

    results.sort(key=lambda r: r.pagerank, reverse=True)

    log.info(f"Computed centrality for {len(results)} WKP")
    return results


# ============================================================
# Top-N central WKP
# ============================================================
def get_top_central_wkps(
    metric: str = "pagerank",
    limit: int = 10,
) -> list[dict]:
    """
    Top-N WKP paling sentral.

    Args:
        metric: "degree" | "betweenness" | "closeness" | "pagerank" | "eigenvector"
        limit: jumlah top WKP

    Returns:
        List dict WKP top.
    """
    valid_metrics = {"degree", "betweenness", "closeness", "pagerank", "eigenvector"}
    if metric not in valid_metrics:
        raise ValueError(f"Metric harus salah satu dari {valid_metrics}")

    results = compute_centrality()
    results.sort(key=lambda r: getattr(r, metric), reverse=True)

    top = results[:limit]

    return [
        {
            "rank": i + 1,
            "kode": r.kode,
            "nama": r.nama,
            "provinsi": r.provinsi,
            "status": r.status,
            "type": r.type,
            "gdi_mean": r.gdi_mean,
            "kapasitas_mw": r.kapasitas_mw,
            "metric": metric,
            "value": getattr(r, metric),
            "degree": r.degree,
            "betweenness": r.betweenness,
            "closeness": r.closeness,
            "pagerank": r.pagerank,
            "eigenvector": r.eigenvector,
        }
        for i, r in enumerate(top)
    ]


# ============================================================
# Network stats
# ============================================================
def get_network_stats() -> dict:
    """Statistik network lengkap."""
    adj = build_adjacency_matrix()
    G = _build_nx_graph(adj)

    n = G.number_of_nodes()
    m = G.number_of_edges()
    density = nx.density(G)

    # Clustering coefficient
    avg_clustering = nx.average_clustering(G, weight="weight")

    # Components
    components = list(nx.connected_components(G))
    n_components = len(components)
    largest = max(len(c) for c in components) if components else 0

    is_connected = nx.is_connected(G) if n > 0 else False

    return {
        "n_nodes": n,
        "n_edges": m,
        "density": round(density, 4),
        "avg_degree": round(2 * m / n, 2) if n > 0 else 0,
        "avg_clustering": round(avg_clustering, 4),
        "is_connected": is_connected,
        "n_components": n_components,
        "largest_component_size": largest,
    }