"""
GeoSDI ABM — Community Agent
=============================
Agen masyarakat lokal di sekitar WKP yang:
- Terima/tolak proyek berdasarkan benefit
- Respons terhadap kompensasi, job creation, CSR
- Bisa escalate ke protest kalau tidak puas
- Acceptance mempengaruhi investasi (investor lari dari konflik)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import random

from src.layer6_synthesis.agent_based.base import Agent, Environment
from src.shared.logger import get_logger

log = get_logger(__name__)


@dataclass
class CommunityAgent(Agent):
    """
    Agen masyarakat lokal (desa/kecamatan) di sekitar WKP.

    Atribut:
    - kode_wkp: kode WKP yang "dimiliki" agent (1 desa per WKP)
    - n_population: jumlah penduduk
    - initial_acceptance: tingkat penerimaan awal (0-1)
    - compensation_expectation_billion: ekspektasi kompensasi
    - benefit_received_billion: benefit yang sudah diterima (CSR, dll)
    """

    kode_wkp: str = ""
    n_population: int = 5000
    initial_acceptance: float = 0.5
    compensation_expectation_billion: float = 50.0
    benefit_received_billion: float = 0.0

    _current_acceptance: float = 0.0

    def __post_init__(self):
        super().__post_init__()
        if self._current_acceptance == 0.0:
            self._current_acceptance = self.initial_acceptance

    def perceive(self, environment: Environment) -> dict:
        """Community melihat WKP-nya dan benefit yang diterima."""
        obs = environment.get_observation(self)

        # Cari WKP agent
        target_wkp = None
        for w in obs.get("wkps_summary", []):
            if w["kode"] == self.kode_wkp:
                target_wkp = w
                break

        if not target_wkp:
            return {
                "has_target": False,
                "acceptance": self._current_acceptance,
            }

        # Hitung rasio benefit vs expectation
        benefit_ratio = self.benefit_received_billion / max(self.compensation_expectation_billion, 1)

        return {
            "has_target": True,
            "kode": target_wkp["kode"],
            "nama": target_wkp["nama"],
            "gdi": target_wkp["gdi_current"],
            "kapasitas": target_wkp["kapasitas_current"],
            "investasi_total": target_wkp.get("total_investment_billion", 0),
            "acceptance": self._current_acceptance,
            "benefit_ratio": round(benefit_ratio, 2),
            "n_population": self.n_population,
        }

    def decide(self, observation: dict) -> dict:
        """
        Community memutuskan:
        - Kalau investasi masuk, ekspektasi benefit naik → minta kompensasi
        - Kalau acceptance rendah → protest
        - Kalau benefit cukup → accept
        """
        if not observation.get("has_target"):
            return {"type": "wait", "reason": "no_target"}

        investasi = observation.get("investasi_total", 0)
        benefit_ratio = observation.get("benefit_ratio", 0)
        acceptance = observation.get("acceptance", 0.5)

        # Kalau investasi besar tapi benefit kecil → minta kompensasi
        if investasi > 100 and benefit_ratio < 0.5:
            # Ekspektasi kompensasi naik seiring investasi
            return {
                "type": "negotiate",
                "kode": observation["kode"],
                "ask_billion": min(investasi * 0.05, 100),  # 5% dari investasi
                "reason": f"Investasi {investasi}M, benefit kecil",
            }

        # Kalau acceptance < 0.3 → protest
        if acceptance < 0.3:
            return {
                "type": "protest",
                "kode": observation["kode"],
                "intensity": 0.3 + (0.3 - acceptance) * 2,
                "reason": "Acceptance sangat rendah",
            }

        # Kalau benefit_ratio > 0.8 → puas, tidak aksi
        if benefit_ratio > 0.8:
            return {"type": "wait", "reason": "satisfied"}

        # Default: minta CSR/mitra
        return {
            "type": "request_csr",
            "kode": observation["kode"],
            "amount_billion": 20.0,
            "reason": "Minta program CSR",
        }

    def act(self, decision: dict, environment: Environment) -> dict:
        """Eksekusi keputusan community."""
        action = decision["type"]

        if action == "wait":
            return {
                "action": "wait",
                "reason": decision.get("reason", ""),
                "acceptance": round(self._current_acceptance, 2),
            }

        if action == "negotiate":
            # Terima kompensasi → naikkan benefit
            amount = decision["ask_billion"]
            self.benefit_received_billion += amount
            self._current_acceptance = min(1.0, self._current_acceptance + 0.15)

            # Update environment (acceptance_score di WKP)
            for w in environment.wkps:
                if w.kode == decision["kode"]:
                    w.acceptance_score = min(1.0, w.acceptance_score + 0.1)
                    break

            return {
                "action": "negotiate",
                "kode": decision["kode"],
                "compensation_billion": amount,
                "new_acceptance": round(self._current_acceptance, 2),
            }

        if action == "protest":
            # Turunkan acceptance environment
            for w in environment.wkps:
                if w.kode == decision["kode"]:
                    w.acceptance_score = max(0.0, w.acceptance_score - 0.1)
                    w.media_sentiment = max(0.0, w.media_sentiment - 0.05)
                    break

            return {
                "action": "protest",
                "kode": decision["kode"],
                "intensity": decision["intensity"],
                "new_acceptance": round(self._current_acceptance, 2),
            }

        if action == "request_csr":
            amount = decision["amount_billion"]
            self.benefit_received_billion += amount
            self._current_acceptance = min(1.0, self._current_acceptance + 0.08)

            for w in environment.wkps:
                if w.kode == decision["kode"]:
                    w.acceptance_score = min(1.0, w.acceptance_score + 0.05)
                    break

            return {
                "action": "csr_received",
                "kode": decision["kode"],
                "amount_billion": amount,
                "new_acceptance": round(self._current_acceptance, 2),
            }

        return {"action": "unknown", "decision": decision}