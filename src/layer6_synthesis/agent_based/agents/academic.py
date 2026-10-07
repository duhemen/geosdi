"""
GeoSDI ABM — Academic Agent
============================
Agen akademisi (universitas, lembaga riset) yang:
- Riset potensi, reservoir, teknologi
- Publikasi, knowledge sharing
- Advokasi berbasis evidence
- Menyediakan tenaga ahli (SDM)
- Kolaborasi dengan operator & government

Contoh: ITB, UGM, BRIN, dll.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from src.layer6_synthesis.agent_based.base import Agent, Environment
from src.shared.logger import get_logger

log = get_logger(__name__)


@dataclass
class AcademicAgent(Agent):
    """
    Agen akademisi (universitas, lembaga riset).

    Atribut:
    - institution: nama universitas/lembaga
    - expertise: "geology" | "engineering" | "social" | "policy"
    - research_capacity: 0-1
    - publication_rate: 0-1
    """

    institution: str = "ITB"
    expertise: str = "geology"
    research_capacity: float = 0.8
    publication_rate: float = 0.6

    _research_count: int = 0
    _published_wkps: list = field(default_factory=list)

    def perceive(self, environment: Environment) -> dict:
        """Akademisi cari WKP yang butuh riset."""
        obs = environment.get_observation(self)

        # Prioritas riset:
        # 1. WKP eksplorasi (butuh geological survey)
        # 2. WKP dengan GDI rendah tapi potensi tinggi (butuh teknologi baru)
        # 3. WKP dengan data quality low
        candidates = []
        for w in obs.get("wkps_summary", []):
            research_priority = 0.0
            reason = None

            if w.get("type") == "exploration":
                research_priority += 0.5
                reason = "Eksplorasi butuh geological survey"

            if w["gdi_current"] < 78 and w["kapasitas_current"] > 50:
                research_priority += 0.3
                reason = reason or "GDI rendah tapi kapasitas besar"

            if w["media_sentiment"] < 0.5:
                research_priority += 0.2
                reason = reason or "Butuh studi social acceptance"

            if research_priority > 0.4:
                candidates.append({
                    "kode": w["kode"],
                    "nama": w["nama"],
                    "provinsi": w["provinsi"],
                    "gdi": w["gdi_current"],
                    "kapasitas": w["kapasitas_current"],
                    "type": w.get("type", "unknown"),
                    "research_priority": round(research_priority, 2),
                    "reason": reason,
                })

        candidates.sort(key=lambda x: x["research_priority"], reverse=True)

        return {
            "candidates": candidates[:5],
            "n_total_wkp": obs.get("n_wkp", 0),
        }

    def decide(self, observation: dict) -> dict:
        """Akademisi memutuskan WKP untuk riset."""
        candidates = observation.get("candidates", [])
        if not candidates:
            return {"type": "wait", "reason": "no_research_target"}

        top = candidates[0]
        return {
            "type": "conduct_research",
            "kode": top["kode"],
            "research_type": self.expertise,
            "priority": top["research_priority"],
            "reason": top["reason"],
        }

    def act(self, decision: dict, environment: Environment) -> dict:
        """Eksekusi riset akademisi."""
        if decision["type"] == "wait":
            return {"action": "wait", "reason": decision.get("reason", "")}

        kode = decision["kode"]

        # Riset meningkatkan pengetahuan → naikkan GDI sedikit
        gdi_gain = 0.5 * self.research_capacity

        for w in environment.wkps:
            if w.kode == kode:
                w.gdi_current = min(100, w.gdi_current + gdi_gain)
                break

        self._research_count += 1
        if kode not in self._published_wkps:
            self._published_wkps.append(kode)

        return {
            "action": "conduct_research",
            "kode": kode,
            "research_type": decision["research_type"],
            "gdi_gain": round(gdi_gain, 3),
            "total_research": self._research_count,
        }