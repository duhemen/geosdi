"""
GeoSDI ABM — NGO Agent
=======================
Agen NGO (Non-Governmental Organization) yang:
- Advokasi lingkungan & hak masyarakat
- Monitor environmental impact
- Kampanye publik (media, petition, lobby)
- Bisa jadi "check and balance" untuk investor & pemerintah
- Respons terhadap pelanggaran lingkungan / social injustice

Contoh: WALHI, Greenpeace, ICEL, dll.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from src.layer6_synthesis.agent_based.base import Agent, Environment
from src.shared.logger import get_logger

log = get_logger(__name__)


@dataclass
class NGOAgent(Agent):
    """
    Agen NGO (environmental/social advocacy).

    Atribut:
    - ngo_name: nama NGO
    - focus: "environment" | "social" | "both"
    - reach: 0-1 (jangkauan advokasi)
    - advocacy_power: 0-1 (kekuatan advokasi)
    - key_wkps: WKP fokus pantauan
    - alliance_with_community: bool
    """

    ngo_name: str = "WALHI"
    focus: str = "both"  # environment | social | both
    reach: float = 0.6
    advocacy_power: float = 0.7
    key_wkps: list = field(default_factory=list)
    alliance_with_community: bool = True

    _campaigns_count: int = 0
    _alerted_wkps: list = field(default_factory=list)

    def perceive(self, environment: Environment) -> dict:
        """
        NGO monitor WKP untuk:
        - Environmental issues (kapasitas tinggi + media negatif)
        - Social issues (acceptance rendah + community miskin benefit)
        - Governance issues (investasi besar tanpa transparency)
        """
        obs = environment.get_observation(self)

        issues = []
        for w in obs.get("wkps_summary", []):
            issue_score = 0.0
            issue_type = None

            # Environmental issue
            if self.focus in ("environment", "both"):
                # Kapasitas tinggi tapi environmental care rendah
                env_concern = w["media_sentiment"] < 0.6 and w["kapasitas_current"] > 50
                if env_concern:
                    issue_score += 0.4
                    issue_type = "environment"

            # Social issue
            if self.focus in ("social", "both"):
                # Acceptance rendah meski sudah ada investasi
                social_concern = w["acceptance_score"] < 0.5
                if social_concern:
                    issue_score += 0.5
                    issue_type = "social" if issue_type is None else "both"

            # Governance issue
            # Investasi besar tapi GDI masih rendah → kemungkinan mismanagement
            investasi = w.get("total_investment_billion", 0)
            if investasi > 200 and w["gdi_current"] < 82:
                issue_score += 0.3
                issue_type = "governance" if issue_type is None else "both"

            # Bonus kalau WKP ada di key_wkps (fokus NGO)
            if w["kode"] in self.key_wkps:
                issue_score += 0.2

            if issue_score > 0.4:
                issues.append({
                    "kode": w["kode"],
                    "nama": w["nama"],
                    "provinsi": w["provinsi"],
                    "gdi": w["gdi_current"],
                    "kapasitas": w["kapasitas_current"],
                    "acceptance": w["acceptance_score"],
                    "media_sentiment": w["media_sentiment"],
                    "investasi_total": investasi,
                    "issue_score": round(issue_score, 2),
                    "issue_type": issue_type,
                })

        issues.sort(key=lambda x: x["issue_score"], reverse=True)

        return {
            "issues": issues[:5],
            "n_total_wkp": obs.get("n_wkp", 0),
            "gdi_national": obs.get("gdi_national", 0),
        }

    def decide(self, observation: dict) -> dict:
        """
        NGO memutuskan aksi:
        - Advocacy campaign (media, petition)
        - Public statement
        - Lobby pemerintah
        - Direct dialogue dengan community
        """
        issues = observation.get("issues", [])
        if not issues:
            return {"type": "wait", "reason": "no_issues"}

        top = issues[0]

        # Tentukan aksi berdasarkan severity
        if top["issue_score"] > 0.8:
            action = "advocacy_campaign"  # Skala besar
        elif top["issue_score"] > 0.6:
            action = "public_statement"   # Skala menengah
        else:
            action = "monitor"            # Skala kecil

        return {
            "type": action,
            "kode": top["kode"],
            "issue_type": top["issue_type"],
            "intensity": top["issue_score"],
            "reason": f"{top['issue_type']} issue di {top['kode']} (score {top['issue_score']})",
        }

    def act(self, decision: dict, environment: Environment) -> dict:
        """Eksekusi aksi NGO."""
        action = decision["type"]

        if action in ("wait", "monitor"):
            return {
                "action": action,
                "reason": decision.get("reason", ""),
            }

        kode = decision["kode"]
        intensity = decision["intensity"]
        issue_type = decision["issue_type"]

        # Impact: NGO advocacy menurunkan media sentiment & acceptance
        # (karena NGO expose masalah → publik mulai kritikal)
        impact_factor = self.reach * self.advocacy_power * intensity

        for w in environment.wkps:
            if w.kode == kode:
                if action == "advocacy_campaign":
                    w.media_sentiment = max(0.0, w.media_sentiment - 0.10 * impact_factor)
                    w.acceptance_score = max(0.0, w.acceptance_score - 0.05 * impact_factor)
                    w.gov_support = max(0.0, w.gov_support - 0.03 * impact_factor)
                elif action == "public_statement":
                    w.media_sentiment = max(0.0, w.media_sentiment - 0.05 * impact_factor)
                    w.acceptance_score = max(0.0, w.acceptance_score - 0.02 * impact_factor)
                break

        self._campaigns_count += 1
        if kode not in self._alerted_wkps:
            self._alerted_wkps.append(kode)

        return {
            "action": action,
            "kode": kode,
            "issue_type": issue_type,
            "intensity": round(intensity, 3),
            "impact_factor": round(impact_factor, 3),
            "media_sentiment_delta": -0.10 * impact_factor if action == "advocacy_campaign" else -0.05 * impact_factor,
            "total_campaigns": self._campaigns_count,
        }