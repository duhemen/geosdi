"""
GeoSDI ABM — Operator Agent
============================
Agen operator PLTP yang:
- Maintain kapasitas existing
- Upgrade teknologi (efficiency)
- Expand kapasitas
- Fokus WKP "mature" dengan GDI tinggi
"""
from __future__ import annotations

from dataclasses import dataclass, field

from src.layer6_synthesis.agent_based.base import Agent, Environment
from src.shared.logger import get_logger

log = get_logger(__name__)


@dataclass
class OperatorAgent(Agent):
    """
    Agen operator PLTP (Pertamina Geothermal, dll).

    Atribut:
    - kode_wkp: kode WKP yang dioperasikan
    - opex_budget_billion: budget operasional tahunan
    - tech_readiness: 0-1 (kesiapan teknologi)
    - maintenance_interval: steps antara maintenance
    - efficiency: 0-1 (efisiensi operasi)
    """

    kode_wkp: str = ""
    opex_budget_billion: float = 500.0
    tech_readiness: float = 0.7
    maintenance_interval: int = 3
    efficiency: float = 0.85

    _last_maintenance_step: int = 0
    _upgrade_count: int = 0

    def perceive(self, environment: Environment) -> dict:
        """Operator melihat WKP-nya dan status teknis."""
        obs = environment.get_observation(self)

        target = None
        for w in obs.get("wkps_summary", []):
            if w["kode"] == self.kode_wkp:
                target = w
                break

        if not target:
            return {"has_target": False}

        # Cek "umur" sejak maintenance terakhir
        current_step = len(self.memory)
        steps_since_maint = current_step - self._last_maintenance_step

        return {
            "has_target": True,
            "kode": target["kode"],
            "nama": target["nama"],
            "gdi": target["gdi_current"],
            "kapasitas": target["kapasitas_current"],
            "tech_readiness": self.tech_readiness,
            "efficiency": self.efficiency,
            "budget": self.opex_budget_billion,
            "steps_since_maintenance": steps_since_maint,
            "upgrade_count": self._upgrade_count,
        }

    def decide(self, observation: dict) -> dict:
        """Operator memutuskan: maintenance, upgrade, atau wait."""
        if not observation.get("has_target"):
            return {"type": "wait", "reason": "no_target"}

        budget = observation.get("budget", 0)
        steps_since_maint = observation.get("steps_since_maintenance", 0)
        tech = observation.get("tech_readiness", 0.7)
        kapasitas = observation.get("kapasitas", 0)

        # Prioritas 1: maintenance kalau sudah waktunya
        if steps_since_maint >= self.maintenance_interval and budget >= 50:
            return {
                "type": "maintain",
                "cost_billion": 50.0,
                "reason": f"Maintenance rutin (interval {self.maintenance_interval})",
            }

        # Prioritas 2: upgrade tech kalau tech_readiness rendah
        if tech < 0.6 and budget >= 100:
            return {
                "type": "upgrade",
                "cost_billion": 100.0,
                "reason": f"Tech readiness rendah ({tech:.2f})",
            }

        # Prioritas 3: expand kapasitas kalau mature & budget besar
        if kapasitas > 100 and budget >= 200 and tech >= 0.7:
            return {
                "type": "expand",
                "capacity_target_mw": 50.0,
                "cost_billion": 200.0,
                "reason": f"Ekspansi kapasitas (current {kapasitas:.0f} MW)",
            }

        return {"type": "wait", "reason": "no_priority_action"}

    def act(self, decision: dict, environment: Environment) -> dict:
        """Eksekusi keputusan operator."""
        action = decision["type"]

        if action == "wait":
            return {
                "action": "wait",
                "reason": decision.get("reason", ""),
                "budget": self.opex_budget_billion,
            }

        cost = decision.get("cost_billion", 0)
        if cost > self.opex_budget_billion:
            return {"action": "rejected", "reason": "insufficient_budget"}

        self.opex_budget_billion -= cost

        if action == "maintain":
            # Maintenance restores efficiency
            self.efficiency = min(1.0, self.efficiency + 0.05)
            self._last_maintenance_step = len(self.memory)

            return {
                "action": "maintain",
                "cost_billion": cost,
                "new_efficiency": round(self.efficiency, 3),
                "budget_remaining": round(self.opex_budget_billion, 2),
            }

        if action == "upgrade":
            self.tech_readiness = min(1.0, self.tech_readiness + 0.15)
            self._upgrade_count += 1

            # Upgrade juga naikkan GDI WKP
            for w in environment.wkps:
                if w.kode == self.kode_wkp:
                    w.gdi_current = min(100, w.gdi_current + 1.5)
                    break

            return {
                "action": "upgrade",
                "cost_billion": cost,
                "new_tech_readiness": round(self.tech_readiness, 3),
                "gdi_gain": 1.5,
                "budget_remaining": round(self.opex_budget_billion, 2),
            }

        if action == "expand":
            cap_target = decision["capacity_target_mw"]

            for w in environment.wkps:
                if w.kode == self.kode_wkp:
                    w.kapasitas_current += cap_target
                    w.gdi_current = min(100, w.gdi_current + 2.0)
                    break

            return {
                "action": "expand",
                "cost_billion": cost,
                "capacity_added_mw": cap_target,
                "gdi_gain": 2.0,
                "budget_remaining": round(self.opex_budget_billion, 2),
            }

        return {"action": "unknown"}