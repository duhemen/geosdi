"""
GeoSDI ABM — WKP Environment
=============================
Environment untuk ABM: representasi WKP + agregat nasional.

State utama:
- WKP list dengan GDI, kapasitas, status
- Agregat: GDI nasional, total investasi, dsb.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.shared.database import get_cursor
from src.shared.logger import get_logger
from src.layer6_synthesis.agent_based.base import Environment, Agent

log = get_logger(__name__)


# ============================================================
# WKP Data Container
# ============================================================
@dataclass
class WKPState:
    """State WKP dalam environment."""
    id: int
    kode: str
    nama: str
    provinsi: str
    status: str
    gdi_mean: float
    kapasitas_mw: float
    type: str

    # Dinamis (berubah selama simulation)
    gdi_current: float = 0.0
    kapasitas_current: float = 0.0
    total_investment_billion: float = 0.0    # dalam miliar Rp
    acceptance_score: float = 0.5             # 0-1 (masyarakat)
    media_sentiment: float = 0.5              # 0-1 (media)
    gov_support: float = 0.5                  # 0-1 (pemerintah)

    def __post_init__(self):
        # Inisialisasi current = baseline
        if self.gdi_current == 0.0:
            self.gdi_current = self.gdi_mean
        if self.kapasitas_current == 0.0:
            self.kapasitas_current = self.kapasitas_mw


# ============================================================
# WKP Environment
# ============================================================
@dataclass
class WKPEnvironment(Environment):
    """
    Environment berbasis WKP.

    Menyimpan:
    - Daftar WKP dengan state dinamis
    - Agregat nasional (GDI nasional, total investasi)
    - Event log (aksi apa yang terjadi)
    """

    wkps: list[WKPState] = field(default_factory=list)
    total_investment_billion: float = 0.0
    event_log: list = field(default_factory=list)

    @classmethod
    def from_database(cls, name: str = "GeoSDI WKP Environment") -> "WKPEnvironment":
        """
        Build environment dari database.
        Query semua WKP dengan GDI + status.
        """
        with get_cursor() as cur:
            cur.execute("""
                SELECT
                    wa.id, wa.kode, wa.nama, wa.provinsi, wa.status,
                    wa.tahun_operasi,
                    COALESCE(wa.kapasitas_mw, 0) AS kapasitas_mw,
                    gs.gdi_mean
                FROM geosdi.work_areas wa
                JOIN geosdi.gdi_scores gs ON gs.work_area_id = wa.id
                WHERE wa.geom IS NOT NULL
                ORDER BY wa.kode;
            """)
            rows = cur.fetchall()

        def _classify(status: str, tahun: Optional[int]) -> str:
            if status in ("Eksplorasi", "IPB Eksplorasi"):
                return "exploration"
            if status == "Dalam Survei":
                return "developing"
            if status == "Operasi":
                if tahun is None or tahun < 2000:
                    return "mature"
                return "developing"
            return "new"

        wkps = []
        for r in rows:
            wkps.append(WKPState(
                id=r["id"],
                kode=r["kode"],
                nama=r["nama"],
                provinsi=r["provinsi"] or "",
                status=r["status"],
                gdi_mean=float(r["gdi_mean"]),
                kapasitas_mw=float(r["kapasitas_mw"] or 0),
                type=_classify(r["status"], r["tahun_operasi"]),
                # Init acceptance dari type
                acceptance_score=0.7 if r["status"] == "Operasi" else 0.5,
                media_sentiment=0.6,
                gov_support=0.7 if r["status"] == "Operasi" else 0.5,
            ))

        env = cls(
            id="wkp-env-1",
            name=name,
            state={},
            wkps=wkps,
        )

        log.info(f"WKPEnvironment initialized with {len(wkps)} WKP")

        return env

    def get_observation(self, agent: Agent) -> dict:
        """
        Return observasi environment untuk agen.

        Setiap tipe agen dapat "penglihatan" berbeda.
        """
        # Default: return aggregate info
        return {
            "n_wkp": len(self.wkps),
            "gdi_national": self._get_gdi_national(),
            "total_capacity_mw": sum(w.kapasitas_current for w in self.wkps),
            "total_investment_billion": self.total_investment_billion,
            "wkps_summary": [
                {
                    "kode": w.kode,
                    "nama": w.nama,
                    "provinsi": w.provinsi,
                    "type": w.type,
                    "gdi_current": w.gdi_current,
                    "kapasitas_current": w.kapasitas_current,
                    "total_investment_billion": w.total_investment_billion,
                    "acceptance_score": w.acceptance_score,
                    "media_sentiment": w.media_sentiment,
                    "gov_support": w.gov_support,
                }
                for w in self.wkps
            ],
        }

    def apply_action(self, agent: Agent, action: dict) -> dict:
        """
        Apply aksi agen ke environment.

        Aksi bisa:
        - invest_wkp: tambah kapasitas + GDI WKP tertentu
        - change_policy: ubah gov_support semua WKP
        - media_campaign: ubah media_sentiment
        - community_engagement: ubah acceptance_score
        """
        action_type = action.get("type", "unknown")
        result = {"action_type": action_type, "agent": agent.id, "changes": []}

        if action_type == "invest_wkp":
            kode = action.get("kode")
            amount = action.get("amount", 0.0)

            for w in self.wkps:
                if w.kode == kode:
                    # Investasi menambah kapasitas & GDI
                    gdi_gain = amount * 0.05  # 100 M → +5 GDI
                    capacity_gain = amount * 0.2  # 100 M → +20 MW

                    w.total_investment_billion += amount
                    w.gdi_current = min(100, w.gdi_current + gdi_gain)
                    w.kapasitas_current += capacity_gain

                    self.total_investment_billion += amount

                    result["changes"].append({
                        "kode": kode,
                        "gdi_gain": round(gdi_gain, 2),
                        "capacity_gain_mw": round(capacity_gain, 1),
                        "amount_billion": amount,
                    })
                    break

        elif action_type == "change_policy":
            delta = action.get("delta", 0.0)
            for w in self.wkps:
                w.gov_support = max(0.0, min(1.0, w.gov_support + delta))
            result["changes"].append({"gov_support_delta": delta, "n_wkp": len(self.wkps)})

        elif action_type == "media_campaign":
            delta = action.get("delta", 0.0)
            for w in self.wkps:
                w.media_sentiment = max(0.0, min(1.0, w.media_sentiment + delta))
            result["changes"].append({"media_delta": delta, "n_wkp": len(self.wkps)})

        elif action_type == "community_engagement":
            kode = action.get("kode")
            delta = action.get("delta", 0.0)
            for w in self.wkps:
                if w.kode == kode:
                    w.acceptance_score = max(0.0, min(1.0, w.acceptance_score + delta))
                    result["changes"].append({"kode": kode, "acceptance_delta": delta})
                    break

        elif action_type == "wait":
            result["changes"].append({"note": "Agent decided to wait"})

        # Log event
        self.event_log.append({
            "step": len(self.event_log),
            "agent": agent.id,
            "action": action_type,
            "result": result,
        })

        return result

    def get_state(self) -> dict:
        """Return state environment."""
        return {
            "n_wkp": len(self.wkps),
            "gdi_national": round(self._get_gdi_national(), 2),
            "total_capacity_mw": round(sum(w.kapasitas_current for w in self.wkps), 2),
            "total_investment_billion": round(self.total_investment_billion, 2),
            "n_events": len(self.event_log),
        }

    def _get_gdi_national(self) -> float:
        """Rata-rata GDI nasional."""
        if not self.wkps:
            return 0.0
        return sum(w.gdi_current for w in self.wkps) / len(self.wkps)