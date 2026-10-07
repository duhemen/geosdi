"""
GeoSDI Network — Adjacency Matrix Builder
==========================================
Bangun adjacency matrix WKP berdasarkan:
1. Jarak geografis (haversine)
2. Kemiripan status/type
3. Kemiripan kapasitas

Adjacency = "siapa tetangga siapa" dalam network WKP.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import math

import numpy as np

from src.shared.database import get_cursor
from src.shared.logger import get_logger

log = get_logger(__name__)


# ============================================================
# Constants
# ============================================================
# Threshold default jarak (km) untuk koneksi antar-WKP
DEFAULT_DISTANCE_THRESHOLD_KM = 200.0

# Weight untuk tiap komponen adjacency
WEIGHT_DISTANCE = 0.6   # Jarak geografis
WEIGHT_STATUS = 0.2     # Kemiripan status
WEIGHT_CAPACITY = 0.2   # Kemiripan kapasitas


# ============================================================
# Data classes
# ============================================================
@dataclass
class WKPNode:
    """Node WKP dalam network."""
    id: int
    kode: str
    nama: str
    provinsi: str
    status: str
    kapasitas_mw: float
    gdi_mean: float
    lon: float
    lat: float
    type: str  # mature/developing/new/exploration


@dataclass
class AdjacencyMatrix:
    """Adjacency matrix WKP."""
    nodes: list[WKPNode]
    matrix: np.ndarray           # shape (n, n), weight 0-1
    distance_matrix: np.ndarray  # shape (n, n), jarak km
    threshold_km: float
    n_nodes: int


# ============================================================
# Helper: Haversine distance
# ============================================================
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Hitung jarak antara 2 titik di bumi (km).
    
    Formula: Haversine.
    """
    R = 6371.0  # Radius bumi (km)

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def _classify_type(status: str, tahun_operasi: Optional[int] = None) -> str:
    """Klasifikasi tipe WKP (sinkron dengan scenario.py)."""
    if status in ("Eksplorasi", "IPB Eksplorasi"):
        return "exploration"
    if status == "Belum Ada Pemegang IPB":
        return "new"
    if status == "Perencanaan":
        return "new"
    if status == "Dalam Survei":
        return "developing"
    if status == "Operasi":
        if tahun_operasi is None:
            return "mature"
        if tahun_operasi < 2000:
            return "mature"
        elif tahun_operasi < 2015:
            return "developing"
        else:
            return "new"
    return "new"


# ============================================================
# Load WKP dari DB
# ============================================================
def _load_wkp_nodes() -> list[WKPNode]:
    """Load semua WKP dengan GDI + koordinat."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                wa.id, wa.kode, wa.nama, wa.provinsi, wa.status,
                wa.tahun_operasi,
                COALESCE(wa.kapasitas_mw, 0) AS kapasitas_mw,
                gs.gdi_mean,
                ST_X(wa.geom)::float AS lon,
                ST_Y(wa.geom)::float AS lat
            FROM geosdi.work_areas wa
            JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id
            WHERE wa.geom IS NOT NULL
            ORDER BY wa.kode;
        """)
        rows = cur.fetchall()

    nodes = []
    for r in rows:
        nodes.append(WKPNode(
            id=r["id"],
            kode=r["kode"],
            nama=r["nama"],
            provinsi=r["provinsi"] or "",
            status=r["status"],
            kapasitas_mw=float(r["kapasitas_mw"] or 0),
            gdi_mean=float(r["gdi_mean"]),
            lon=float(r["lon"]),
            lat=float(r["lat"]),
            type=_classify_type(r["status"], r["tahun_operasi"]),
        ))

    log.info(f"Loaded {len(nodes)} WKP nodes for network analysis")
    return nodes


# ============================================================
# Build adjacency matrix
# ============================================================
def build_adjacency_matrix(
    distance_threshold_km: float = DEFAULT_DISTANCE_THRESHOLD_KM,
    weight_distance: float = WEIGHT_DISTANCE,
    weight_status: float = WEIGHT_STATUS,
    weight_capacity: float = WEIGHT_CAPACITY,
) -> AdjacencyMatrix:
    """
    Bangun adjacency matrix WKP.

    Weight = kombinasi:
    - Jarak geografis (semakin dekat → semakin kuat)
    - Kemiripan status/type
    - Kemiripan kapasitas

    Args:
        distance_threshold_km: Maks jarak untuk dianggap "tetangga" (default 200 km)
        weight_distance: Bobot komponen jarak (default 0.6)
        weight_status: Bobot komponen status (default 0.2)
        weight_capacity: Bobot komponen kapasitas (default 0.2)

    Returns:
        AdjacencyMatrix dengan node list + matrix.
    """
    nodes = _load_wkp_nodes()
    n = len(nodes)

    # Init matrix
    adj = np.zeros((n, n), dtype=np.float64)
    dist = np.zeros((n, n), dtype=np.float64)

    # Normalisasi kapasitas
    max_cap = max((nd.kapasitas_mw for nd in nodes), default=1.0) or 1.0

    # Build matrix
    for i in range(n):
        for j in range(n):
            if i == j:
                continue

            # Distance
            d_km = haversine_km(
                nodes[i].lat, nodes[i].lon,
                nodes[j].lat, nodes[j].lon,
            )
            dist[i, j] = d_km

            # Skip kalau terlalu jauh
            if d_km > distance_threshold_km:
                continue

            # Component 1: distance score (dekat → tinggi)
            # Normalisasi: 0 km → 1.0, threshold → 0.0
            dist_score = 1.0 - (d_km / distance_threshold_km)

            # Component 2: status similarity (sama type → 1.0)
            status_score = 1.0 if nodes[i].type == nodes[j].type else 0.3

            # Component 3: capacity similarity
            # 0 kalau beda ekstrim, 1 kalau mirip
            cap_i = nodes[i].kapasitas_mw / max_cap
            cap_j = nodes[j].kapasitas_mw / max_cap
            cap_diff = abs(cap_i - cap_j)
            cap_score = max(0.0, 1.0 - cap_diff * 2)  # penalti 2x

            # Combine
            weight = (
                weight_distance * dist_score
                + weight_status * status_score
                + weight_capacity * cap_score
            )

            adj[i, j] = max(0.0, min(1.0, weight))

    log.info(
        f"Built adjacency matrix: {n} nodes, "
        f"avg degree = {(adj > 0).sum() / n:.1f}"
    )

    return AdjacencyMatrix(
        nodes=nodes,
        matrix=adj,
        distance_matrix=dist,
        threshold_km=distance_threshold_km,
        n_nodes=n,
    )


# ============================================================
# Query: neighbors
# ============================================================
def get_neighbors(kode: str, min_weight: float = 0.3) -> list[dict]:
    """
    Dapatkan WKP tetangga (neighbors) dari WKP tertentu.

    Args:
        kode: Kode WKP (contoh: "WKP001")
        min_weight: Minimum adjacency weight untuk dianggap neighbor

    Returns:
        List tetangga dengan distance & weight.
    """
    adj = build_adjacency_matrix()

    # Find node index
    idx = None
    for i, node in enumerate(adj.nodes):
        if node.kode == kode:
            idx = i
            break

    if idx is None:
        raise ValueError(f"WKP {kode} tidak ditemukan")

    # Get neighbors
    source = adj.nodes[idx]
    neighbors = []

    for j, node in enumerate(adj.nodes):
        if j == idx:
            continue
        weight = adj.matrix[idx, j]
        if weight >= min_weight:
            neighbors.append({
                "kode": node.kode,
                "nama": node.nama,
                "provinsi": node.provinsi,
                "status": node.status,
                "type": node.type,
                "gdi_mean": node.gdi_mean,
                "kapasitas_mw": node.kapasitas_mw,
                "distance_km": round(adj.distance_matrix[idx, j], 2),
                "adjacency_weight": round(weight, 4),
            })

    # Sort by weight DESC
    neighbors.sort(key=lambda x: x["adjacency_weight"], reverse=True)

    return neighbors


# ============================================================
# Summary
# ============================================================
def get_adjacency_summary(
    distance_threshold_km: float = DEFAULT_DISTANCE_THRESHOLD_KM,
) -> dict:
    """Ringkasan adjacency matrix."""
    adj = build_adjacency_matrix(distance_threshold_km=distance_threshold_km)

    matrix = adj.matrix
    n = adj.n_nodes

    # Degree: berapa neighbor per WKP (weight > 0)
    degree_per_node = (matrix > 0).sum(axis=1)

    # Average
    avg_degree = float(degree_per_node.mean()) if n > 0 else 0
    max_degree = int(degree_per_node.max()) if n > 0 else 0
    min_degree = int(degree_per_node.min()) if n > 0 else 0

    # Density: berapa persen koneksi dari total possible
    max_edges = n * (n - 1)
    actual_edges = int((matrix > 0).sum())
    density = actual_edges / max_edges if max_edges > 0 else 0

    return {
        "n_nodes": n,
        "n_edges": actual_edges,
        "density": round(density, 4),
        "avg_degree": round(avg_degree, 2),
        "max_degree": max_degree,
        "min_degree": min_degree,
        "distance_threshold_km": distance_threshold_km,
        "is_connected": actual_edges > 0,
    }