"""
GeoSDI Network Dynamics Engine
===============================
Analisis jaringan antar-WKP: adjacency, centrality, influence, cluster.

Prinsip:
- WKP tidak hidup sendiri — mereka saling mempengaruhi
- Spillover effect: WKP besar (mature) mempengaruhi WKP kecil (eksplorasi)
- Network effect = leverage untuk kebijakan
"""
from src.layer6_synthesis.network.adjacency import (
    build_adjacency_matrix,
    get_neighbors,
    get_adjacency_summary,
)
from src.layer6_synthesis.network.centrality import (
    compute_centrality,
    get_top_central_wkps,
    get_network_stats,
)
from src.layer6_synthesis.network.influence import (
    compute_influence_matrix,
    propagate_influence,
    simulate_network_intervention,
)
from src.layer6_synthesis.network.clusters import (
    detect_communities,
    get_cluster_summary,
)

__all__ = [
    # Adjacency
    "build_adjacency_matrix",
    "get_neighbors",
    "get_adjacency_summary",
    # Centrality
    "compute_centrality",
    "get_top_central_wkps",
    "get_network_stats",
    # Influence
    "compute_influence_matrix",
    "propagate_influence",
    "simulate_network_intervention",
    # Clusters
    "detect_communities",
    "get_cluster_summary",
]