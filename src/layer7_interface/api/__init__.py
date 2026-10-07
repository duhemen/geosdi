"""GeoSDI API Routes Package."""
from src.layer7_interface.api.routes import (
    nodes,
    spatial,
    gdi,
    simulate,
    insights,
    digital_twin,
    admin,
    network,
    abm,
    events,
)

__all__ = [
    "nodes",
    "spatial",
    "gdi",
    "simulate",
    "insights",
    "digital_twin",
    "admin",
    "network",
    "abm",
    "events",
]