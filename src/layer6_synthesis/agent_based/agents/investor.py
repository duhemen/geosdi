"""
GeoSDI ABM — Investor Agent
============================
Agen investor yang:
- Mencari WKP dengan ROI tinggi (GDI × kapasitas)
- Punya budget terbatas
- Menghindari WKP dengan konflik/acceptance rendah
- Decision: invest atau wait
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.layer6_synthesis.agent_based.base import Agent, Environment
from src.shared.logger import get_logger

log = get_logger(__name__)


@dataclass
class InvestorAgent(Agent):
    """
    Agen investor geothermal.

    Atribut:
    - budget_billion: total budget (miliar Rp)
    - risk_tolerance: 0-1 (0=konservatif, 1=agresif)
    - min_roi_threshold: minimum GDI untuk invest
    - invested_wkps: list WKP yang sudah diinvestasi
    """

    budget_billion: float = 5000.0
    risk_tolerance: float = 0.5
    min_gdi_threshold: float = 80.0

    invested_wkps: list = field(default_factory=list)

    def perceive(self, environment: Environment) -> dict:
        """
        Investor melihat WKP dengan filter:
        - GDI > threshold
        - Acceptance > 0.5 (masyarakat tidak menolak)
        - Media sentiment > 0.4
        """
        obs = environment.get_observation(self)

        candidates = []
        for w in obs.get("wkps_summary", []):
            # Filter
            if w["gdi_current"] < self.min_gdi_threshold:
                continue
            if w["acceptance_score"] < 0.5:
                continue
            if w["media_sentiment"] < 0.4:
                continue

            # Hitung ROI score: GDI × kapasitas / (1 + risk)
            roi_score = w["gdi_current"] * (1 + w["kapasitas_current"] / 100)
            roi_score *= (0.5 + self.risk_tolerance)
            roi_score *= (1 + w["acceptance_score"] * 0.3)  # social bonus
            roi_score *= (1 + w["gov_support"] * 0.2)  # policy bonus

            candidates.append({
                "kode": w["kode"],
                "nama": w["nama"],
                "provinsi": w["provinsi"],
                "gdi": w["gdi_current"],
                "kapasitas": w["kapasitas_current"],
                "roi_score": round(roi_score, 2),
                "acceptance": w["acceptance_score"],
                "gov_support": w["gov_support"],
            })

        # Sort by ROI
        candidates.sort(key=lambda x: x["roi_score"], reverse=True)

        return {
            "budget_remaining": self.budget_billion,
            "candidates": candidates[:10],  # top 10
            "n_total_wkp": obs.get("n_wkp", 0),
            "gdi_national": obs.get("gdi_national", 0),
        }

    def decide(self, observation: dict) -> dict:
        """
        Investor memutuskan:
        - Kalau budget habis → wait
        - Kalau ada candidate → invest ke top 1
        - Kalau tidak ada → wait
        """
        candidates = observation.get("candidates", [])
        budget = observation.get("budget_remaining", 0)

        if budget < 100:  # minimal invest 100 M
            return {"type": "wait", "reason": "budget_exhausted"}

        if not candidates:
            return {"type": "wait", "reason": "no_candidates"}

        # Pilih top 1
        target = candidates[0]

        # Tentukan amount (10-30% dari budget, sesuai risk tolerance)
        amount_pct = 0.10 + self.risk_tolerance * 0.20  # 10-30%
        amount = min(budget * amount_pct, 500.0)  # max 500 M per investment

        return {
            "type": "invest_wkp",
            "kode": target["kode"],
            "amount": round(amount, 2),
            "expected_roi": target["roi_score"],
            "reason": f"ROI {target['roi_score']} di {target['kode']}",
        }

    def act(self, decision: dict, environment: Environment) -> dict:
        """
        Eksekusi keputusan investasi.
        """
        if decision["type"] == "wait":
            return {
                "action": "wait",
                "reason": decision.get("reason", ""),
                "budget_remaining": self.budget_billion,
            }

        # Invest
        amount = decision["amount"]
        kode = decision["kode"]

        if amount > self.budget_billion:
            return {
                "action": "rejected",
                "reason": "insufficient_budget",
                "budget_remaining": self.budget_billion,
            }

        # Apply ke environment
        result = environment.apply_action(self, {
            "type": "invest_wkp",
            "kode": kode,
            "amount": amount,
        })

        # Update state
        self.budget_billion -= amount
        self.invested_wkps.append({
            "kode": kode,
            "amount": amount,
            "step": len(self.memory),
        })

        return {
            "action": "invest",
            "kode": kode,
            "amount": amount,
            "budget_remaining": round(self.budget_billion, 2),
            "environment_changes": result["changes"],
        }