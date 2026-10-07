"""
GeoSDI ABM — Media Agent
========================
Agen media yang:
- Frame isu (positif/negatif)
- Investigasi isu konflik/environmental
- Amplifikasi sentiment (viral effects)
- Mempengaruhi acceptance & investor decision
"""
from __future__ import annotations

from dataclasses import dataclass, field

from src.layer6_synthesis.agent_based.base import Agent, Environment
from src.shared.logger import get_logger

log = get_logger(__name__)


@dataclass
class MediaAgent(Agent):
    """
    Agen media (media nasional + lokal).

    Atribut:
    - outlet: nama media
    - editorial_orientation: "neutral" | "pro_industry" | "pro_environment"
    - reach: 0-1 (jangkauan audiens)
    - viral_factor: 0-1 (potensi viral)
    """

    outlet: str = "GeoSDI News"
    editorial_orientation: str = "neutral"
    reach: float = 0.6
    viral_factor: float = 0.4

    covered_wkps: list = field(default_factory=list)

    def perceive(self, environment: Environment) -> dict:
        """
        Media mencari "story" — WKP dengan cerita menarik:
        - GDI rendah + acceptance rendah (krisis)
        - GDI tinggi + investasi besar (sukses)
        - Konflik/protest
        """
        obs = environment.get_observation(self)

        stories = []
        for w in obs.get("wkps_summary", []):
            # Skor "newsworthiness"
            newsworthiness = 0.0

            # Story 1: Krisis (GDI rendah + acceptance rendah)
            if w["gdi_current"] < 78 and w["acceptance_score"] < 0.5:
                newsworthiness += 0.4

            # Story 2: Sukses (GDI tinggi + investasi besar)
            if w["gdi_current"] > 85 and w.get("total_investment_billion", 0) > 100:
                newsworthiness += 0.3

            # Story 3: Protest signifikan
            if w["acceptance_score"] < 0.4:
                newsworthiness += 0.3

            # Story 4: Media sentiment sudah negatif → amplify
            if w["media_sentiment"] < 0.4:
                newsworthiness += 0.2

            # Sesuaikan orientasi
            if self.editorial_orientation == "pro_environment":
                if w["media_sentiment"] < 0.5:
                    newsworthiness += 0.2
            elif self.editorial_orientation == "pro_industry":
                if w["gdi_current"] > 80:
                    newsworthiness += 0.2

            if newsworthiness > 0.3:
                stories.append({
                    "kode": w["kode"],
                    "nama": w["nama"],
                    "gdi": w["gdi_current"],
                    "acceptance": w["acceptance_score"],
                    "media_sentiment": w["media_sentiment"],
                    "newsworthiness": round(newsworthiness, 2),
                })

        stories.sort(key=lambda x: x["newsworthiness"], reverse=True)

        return {
            "stories": stories[:5],
            "n_total_wkp": obs.get("n_wkp", 0),
        }

    def decide(self, observation: dict) -> dict:
        """Media memutuskan story mana yang akan di-cover."""
        stories = observation.get("stories", [])
        if not stories:
            return {"type": "wait", "reason": "no_story"}

        top = stories[0]

        # Tentukan tone berdasarkan orientasi + konteks WKP
        if self.editorial_orientation == "pro_environment":
            # Fokus environmental issues
            tone = "negative" if top["acceptance"] < 0.5 else "neutral"
        elif self.editorial_orientation == "pro_industry":
            # Fokus success stories
            tone = "positive" if top["gdi"] > 80 else "neutral"
        else:
            # Neutral: report apa adanya
            if top["acceptance"] < 0.4:
                tone = "negative"
            elif top["gdi"] > 85:
                tone = "positive"
            else:
                tone = "neutral"

        return {
            "type": "cover_story",
            "kode": top["kode"],
            "tone": tone,
            "impact": round(top["newsworthiness"] * self.reach * (1 + self.viral_factor), 2),
            "reason": f"Story {top['kode']} newsworthy",
        }

    def act(self, decision: dict, environment: Environment) -> dict:
        """Eksekusi peliputan media."""
        action = decision["type"]

        if action == "wait":
            return {"action": "wait", "reason": decision.get("reason", "")}

        kode = decision["kode"]
        tone = decision["tone"]
        impact = decision["impact"]

        # Apply ke environment
        for w in environment.wkps:
            if w.kode == kode:
                if tone == "positive":
                    w.media_sentiment = min(1.0, w.media_sentiment + 0.05 * impact)
                    w.acceptance_score = min(1.0, w.acceptance_score + 0.02 * impact)
                elif tone == "negative":
                    w.media_sentiment = max(0.0, w.media_sentiment - 0.08 * impact)
                    w.acceptance_score = max(0.0, w.acceptance_score - 0.04 * impact)
                # neutral: no change
                break

        self.covered_wkps.append({"kode": kode, "tone": tone, "impact": impact})

        return {
            "action": "cover_story",
            "kode": kode,
            "tone": tone,
            "impact": round(impact, 3),
            "media_sentiment_updated": True,
        }