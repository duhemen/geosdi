"""
GeoSDI ABM — Government Agent
==============================
Agen pemerintah yang:
- Alokasikan subsidi ke WKP prioritas
- Ubah kebijakan (insentif fiskal, regulasi)
- Fokus WKP dengan GDI rendah (untuk pemerataan)
- Respons acceptance sosial & media sentiment
"""
from __future__ import annotations

from dataclasses import dataclass, field

from src.layer6_synthesis.agent_based.base import Agent, Environment
from src.shared.logger import get_logger

log = get_logger(__name__)


@dataclass
class GovernmentAgent(Agent):
    """
    Agen pemerintah (Kementerian ESDM).

    Atribut:
    - annual_budget_billion: budget tahunan untuk subsidi
    - policy_orientation: "growth" | "equity" | "balanced"
      - growth: fokus WKP dengan GDI tinggi (fast ROI)
      - equity: fokus WKP dengan GDI rendah (pemerataan)
      - balanced: kompromi
    - subsidy_per_wkp_billion: standar subsidi per WKP
    """

    annual_budget_billion: float = 3000.0
    policy_orientation: str = "balanced"
    subsidy_per_wkp_billion: float = 150.0

    subsidized_wkps: list = field(default_factory=list)

    def perceive(self, environment: Environment) -> dict:
        """
        Government melihat semua WKP, dengan prioritas sesuai orientasi.
        """
        obs = environment.get_observation(self)
        wkps = obs.get("wkps_summary", [])

        # Skor prioritas sesuai orientasi
        scored = []
        for w in wkps:
            if self.policy_orientation == "growth":
                # Prioritas: GDI tinggi
                priority = w["gdi_current"]
            elif self.policy_orientation == "equity":
                # Prioritas: GDI rendah (pemerataan)
                priority = 100 - w["gdi_current"]
            else:  # balanced
                # Prioritas: GDI menengah + acceptance tinggi
                priority = 50 + w["acceptance_score"] * 30 - abs(w["gdi_current"] - 80) * 0.5

            # Bonus kalau acceptance tinggi
            priority += w["acceptance_score"] * 10

            scored.append({
                "kode": w["kode"],
                "nama": w["nama"],
                "provinsi": w["provinsi"],
                "gdi": w["gdi_current"],
                "acceptance": w["acceptance_score"],
                "gov_support": w["gov_support"],
                "priority": round(priority, 2),
            })

        scored.sort(key=lambda x: x["priority"], reverse=True)

        return {
            "budget_remaining": self.annual_budget_billion,
            "orientation": self.policy_orientation,
            "candidates": scored[:15],
            "gdi_national": obs.get("gdi_national", 0),
        }

    def decide(self, observation: dict) -> dict:
        """Government memutuskan: subsidi ke WKP prioritas #1."""
        budget = observation.get("budget_remaining", 0)
        candidates = observation.get("candidates", [])

        if budget < self.subsidy_per_wkp_billion:
            return {"type": "wait", "reason": "budget_exhausted"}

        if not candidates:
            return {"type": "wait", "reason": "no_candidates"}

        target = candidates[0]
        subsidy = self.subsidy_per_wkp_billion

        return {
            "type": "give_subsidy",
            "kode": target["kode"],
            "amount": subsidy,
            "priority_score": target["priority"],
            "reason": f"Subsidi ke {target['kode']} (priority={target['priority']})",
        }

    def act(self, decision: dict, environment: Environment) -> dict:
        """Eksekusi keputusan subsidi."""
        if decision["type"] == "wait":
            return {
                "action": "wait",
                "reason": decision.get("reason", ""),
                "budget_remaining": self.annual_budget_billion,
            }

        amount = decision["amount"]
        kode = decision["kode"]

        if amount > self.annual_budget_billion:
            return {"action": "rejected", "reason": "insufficient_budget"}

        # Apply investasi via environment
        result = environment.apply_action(self, {
            "type": "invest_wkp",
            "kode": kode,
            "amount": amount,
        })

        # Bonus: subsidi juga naikkan gov_support
        for w in environment.wkps:
            if w.kode == kode:
                w.gov_support = min(1.0, w.gov_support + 0.1)
                break

        self.annual_budget_billion -= amount
        self.subsidized_wkps.append({"kode": kode, "amount": amount})

        return {
            "action": "subsidy",
            "kode": kode,
            "amount": amount,
            "budget_remaining": round(self.annual_budget_billion, 2),
            "environment_changes": result["changes"],
        }