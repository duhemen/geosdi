"""
GeoSDI — Network Dynamics API
==============================
Endpoint untuk network analysis: adjacency, centrality, influence, communities.
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from src.layer6_synthesis.network import (
    get_adjacency_summary,
    get_neighbors,
    compute_centrality,
    get_top_central_wkps,
    get_network_stats,
    propagate_influence,
    simulate_network_intervention,
    detect_communities,
    get_cluster_summary,
)
from src.shared.logger import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/network", tags=["network"])


# ============================================================
# Schemas
# ============================================================
class PropagationRequest(BaseModel):
    """Request untuk influence propagation."""
    source_kode: str = Field(..., description="Kode WKP sumber (contoh: WKP001)")
    delta_gdi: float = Field(..., description="Perubahan GDI di source (contoh: 5.0)")
    decay: float = Field(0.30, ge=0.0, le=1.0, description="Faktor atenuasi per hop")
    max_hops: int = Field(2, ge=1, le=5, description="Maksimum hop propagasi")


class NetworkInterventionRequest(BaseModel):
    """Request untuk simulasi intervensi network."""
    delta_gdi_per_wkp: float = Field(..., description="Perubahan GDI per WKP source")
    filter_type: Optional[str] = Field(
        None,
        description="Filter tipe WKP: mature/developing/new/exploration",
    )
    decay: float = Field(0.30, ge=0.0, le=1.0)
    max_hops: int = Field(2, ge=1, le=5)


# ============================================================
# GET /stats — Network statistics
# ============================================================
@router.get("/stats")
async def network_stats():
    """Statistik network lengkap."""
    adj_summary = get_adjacency_summary()
    net_stats = get_network_stats()

    return {
        "adjacency": adj_summary,
        "network": net_stats,
    }


# ============================================================
# GET /centrality — Centrality ranking
# ============================================================
@router.get("/centrality")
async def centrality(
    metric: str = Query(
        "pagerank",
        description="Metric: degree | betweenness | closeness | pagerank | eigenvector",
    ),
    limit: int = Query(10, ge=1, le=100),
):
    """Top-N WKP berdasarkan centrality metric."""
    try:
        results = get_top_central_wkps(metric=metric, limit=limit)
        return {
            "metric": metric,
            "count": len(results),
            "rankings": results,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# GET /communities — Community detection
# ============================================================
@router.get("/communities")
async def communities(
    algorithm: str = Query(
        "louvain",
        description="Algorithm: louvain | label_propagation | greedy",
    ),
    include_wkps: bool = Query(False, description="Include WKP detail per komunitas"),
):
    """Deteksi komunitas WKP."""
    try:
        if include_wkps:
            return detect_communities(algorithm=algorithm)
        else:
            return get_cluster_summary(algorithm=algorithm)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# GET /neighbors/{kode} — Neighbors of WKP
# ============================================================
@router.get("/neighbors/{kode}")
async def neighbors(
    kode: str,
    min_weight: float = Query(0.3, ge=0.0, le=1.0),
):
    """WKP tetangga dari WKP tertentu."""
    try:
        result = get_neighbors(kode=kode, min_weight=min_weight)
        return {
            "source_kode": kode,
            "count": len(result),
            "neighbors": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================
# POST /propagate — Influence propagation
# ============================================================
@router.post("/propagate")
async def propagate(request: PropagationRequest):
    """
    Propagasi influence dari 1 WKP ke tetangga.

    Contoh: Kalau WKP001 naik +5 GDI, WKP tetangga naik berapa?
    """
    try:
        result = propagate_influence(
            source_kode=request.source_kode,
            delta_gdi=request.delta_gdi,
            decay=request.decay,
            max_hops=request.max_hops,
        )

        return {
            "source": {
                "kode": result.source_kode,
                "nama": result.source_name,
                "delta_direct": result.delta_gdi,
            },
            "summary": {
                "n_affected": result.n_affected,
                "total_network_effect": result.total_network_effect,
                "grand_total": round(result.delta_gdi + result.total_network_effect, 4),
                "max_hop": result.max_hop,
            },
            "affected_wkps": result.affected_wkps,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================
# POST /simulate — Network-wide intervention
# ============================================================
@router.post("/simulate")
async def simulate(request: NetworkInterventionRequest):
    """
    Simulasi intervensi ke seluruh network.

    Contoh: Kalau semua WKP mature naik +3 GDI, efek network total berapa?
    """
    try:
        result = simulate_network_intervention(
            delta_gdi_per_wkp=request.delta_gdi_per_wkp,
            filter_type=request.filter_type,
            decay=request.decay,
            max_hops=request.max_hops,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# GET /graph — Graph data untuk visualisasi
# ============================================================
@router.get("/graph")
async def graph_data(
    min_weight: float = Query(0.2, ge=0.0, le=1.0, description="Min edge weight untuk ditampilkan"),
    include_communities: bool = Query(True),
):
    """
    Graph data (nodes + edges) untuk visualisasi network.

    Output kompatibel dengan vis.js Network.
    """
    from src.layer6_synthesis.network import build_adjacency_matrix, compute_centrality

    adj = build_adjacency_matrix()

    # Compute centrality untuk node size
    centrality_map = {}
    try:
        for c in compute_centrality():
            centrality_map[c.kode] = c
    except Exception:
        pass

    # Community map
    community_map = {}
    if include_communities:
        try:
            comm_result = detect_communities()
            for comm in comm_result.get("communities", []):
                for wkp in comm.get("wkps", []):
                    community_map[wkp["kode"]] = comm["id"]
        except Exception:
            pass

    # Type color mapping
    type_colors = {
        "mature": "#10b981",       # green
        "developing": "#3b82f6",   # blue
        "new": "#f59e0b",          # amber
        "exploration": "#8b5cf6",  # purple
    }

    # Build nodes
    nodes = []
    for node in adj.nodes:
        c = centrality_map.get(node.kode)
        # Node size: berdasarkan degree centrality
        size = 15 + (c.degree * 3 if c else 0)

        nodes.append({
            "id": node.kode,
            "label": node.kode,
            "title": f"{node.kode} — {node.nama}",
            "nama": node.nama,
            "provinsi": node.provinsi,
            "status": node.status,
            "type": node.type,
            "gdi_mean": node.gdi_mean,
            "kapasitas_mw": node.kapasitas_mw,
            "size": round(size, 2),
            "color": type_colors.get(node.type, "#64748b"),
            "community": community_map.get(node.kode),
            "centrality": {
                "degree": c.degree if c else 0,
                "pagerank": c.pagerank if c else 0,
                "betweenness": c.betweenness if c else 0,
            } if c else None,
        })

    # Build edges
    edges = []
    n = adj.n_nodes
    for i in range(n):
        for j in range(i + 1, n):
            w = adj.matrix[i, j]
            if w >= min_weight:
                edges.append({
                    "from": adj.nodes[i].kode,
                    "to": adj.nodes[j].kode,
                    "value": round(float(w), 4),
                    "title": f"Weight: {w:.3f}",
                    "distance_km": round(adj.distance_matrix[i, j], 2),
                })

    return {
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "n_nodes": len(nodes),
            "n_edges": len(edges),
            "min_weight": min_weight,
            "type_colors": type_colors,
        },
    }



# ============================================================
# GET /export — Export network ke GraphML / JSON
# ============================================================
@router.get("/export")
async def export_network(
    format: str = Query("graphml", description="Format: graphml | json"),
    min_weight: float = Query(0.3, ge=0.0, le=1.0),
):
    """
    Export network dalam format GraphML (untuk Gephi) atau JSON.
    """
    from fastapi.responses import Response, JSONResponse
    from src.layer6_synthesis.network import build_adjacency_matrix, compute_centrality
    import networkx as nx
    import io

    adj = build_adjacency_matrix()

    # Centrality map
    cent_map = {}
    try:
        for c in compute_centrality():
            cent_map[c.kode] = c
    except Exception:
        pass

    if format == "json":
        # Build JSON
        nodes = []
        for node in adj.nodes:
            c = cent_map.get(node.kode)
            nodes.append({
                "id": node.kode,
                "nama": node.nama,
                "provinsi": node.provinsi,
                "status": node.status,
                "type": node.type,
                "gdi_mean": node.gdi_mean,
                "kapasitas_mw": node.kapasitas_mw,
                "degree": c.degree if c else 0,
                "pagerank": c.pagerank if c else 0,
                "betweenness": c.betweenness if c else 0,
                "closeness": c.closeness if c else 0,
                "eigenvector": c.eigenvector if c else 0,
            })

        edges = []
        n = adj.n_nodes
        for i in range(n):
            for j in range(i + 1, n):
                w = adj.matrix[i, j]
                if w >= min_weight:
                    edges.append({
                        "source": adj.nodes[i].kode,
                        "target": adj.nodes[j].kode,
                        "weight": round(float(w), 4),
                        "distance_km": round(adj.distance_matrix[i, j], 2),
                    })

        return JSONResponse(content={
            "metadata": {
                "n_nodes": len(nodes),
                "n_edges": len(edges),
                "min_weight": min_weight,
                "generated_at": __import__("datetime").datetime.now().isoformat(),
            },
            "nodes": nodes,
            "edges": edges,
        })

    # Build NetworkX graph untuk GraphML export
    G = nx.Graph()
    for node in adj.nodes:
        c = cent_map.get(node.kode)
        G.add_node(
            node.kode,
            label=f"{node.kode} — {node.nama}",
            nama=node.nama,
            provinsi=node.provinsi,
            status=node.status,
            type=node.type,
            gdi_mean=float(node.gdi_mean),
            kapasitas_mw=float(node.kapasitas_mw),
            degree=float(c.degree) if c else 0.0,
            pagerank=float(c.pagerank) if c else 0.0,
            betweenness=float(c.betweenness) if c else 0.0,
        )

    n = adj.n_nodes
    for i in range(n):
        for j in range(i + 1, n):
            w = adj.matrix[i, j]
            if w >= min_weight:
                G.add_edge(
                    adj.nodes[i].kode,
                    adj.nodes[j].kode,
                    weight=float(w),
                    distance_km=float(adj.distance_matrix[i, j]),
                )

    # Write GraphML ke buffer
    buffer = io.BytesIO()
    nx.write_graphml(G, buffer)
    buffer.seek(0)

    return Response(
        content=buffer.read(),
        media_type="application/xml",
        headers={
            "Content-Disposition": f'attachment; filename="geosdi-network.graphml"',
        },
    )

# ============================================================
# GET /history — GDI history untuk time-lapse animation
# ============================================================
@router.get("/history")
async def network_history():
    """
    GDI history untuk 18 WKP (24 bulan) untuk animasi time-lapse.
    """
    from src.shared.database import get_cursor

    with get_cursor() as cur:
        cur.execute("""
            SELECT
                wa.kode,
                gh.year,
                gh.month,
                gh.gdi_mean,
                gh.recorded_at
            FROM geosdi.gdi_history gh
            JOIN geosdi.work_areas wa ON wa.id = gh.work_area_id
            ORDER BY wa.kode, gh.year, gh.month;
        """)
        rows = cur.fetchall()

    # Build: { kode: [{year, month, gdi_mean}, ...] }
    history = {}
    for r in rows:
        kode = r["kode"]
        if kode not in history:
            history[kode] = []
        history[kode].append({
            "year": r["year"],
            "month": r["month"],
            "gdi_mean": float(r["gdi_mean"]),
            "recorded_at": r["recorded_at"].isoformat() if r["recorded_at"] else None,
        })

    # Sort each series by year, month
    for kode in history:
        history[kode].sort(key=lambda x: (x["year"], x["month"]))

    return {
        "n_wkp": len(history),
        "n_months": 24,
        "history": history,
    }