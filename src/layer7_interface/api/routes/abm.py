"""
GeoSDI — Agent-Based Modeling API
===================================
Endpoint untuk menjalankan ABM simulation via API.
"""
from typing import Optional, Literal
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.layer6_synthesis.agent_based import (
    WKPEnvironment,
    InvestorAgent,
    GovernmentAgent,
    CommunityAgent,
    OperatorAgent,
    MediaAgent,
    NGOAgent,
    AcademicAgent,
    Simulation,
)
from src.shared.logger import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/abm", tags=["abm"])


# ============================================================
# Schemas
# ============================================================
class AgentConfig(BaseModel):
    """Konfigurasi 1 agen."""
    type: str = Field(..., description="investor/government/community/operator/media/ngo/academic")
    id: str = Field(..., description="Unique ID")
    name: str = Field(..., description="Nama agen")
    params: dict = Field(default_factory=dict, description="Parameter spesifik agen")


class ABMSimulationRequest(BaseModel):
    """Request untuk jalankan ABM simulation."""
    name: str = Field("Custom Simulation", description="Nama simulation")
    max_steps: int = Field(15, ge=1, le=100)
    seed: int = Field(42, description="Random seed")
    agents: list[AgentConfig] = Field(..., description="Daftar agen")


class AgentDefaults(BaseModel):
    """Default config untuk 1 tipe agen."""
    type: str
    label: str
    icon: str
    default_params: dict
    description: str


# ============================================================
# Preset scenarios
# ============================================================
PRESET_SCENARIOS = {
    "balanced": {
        "name": "🎯 Balanced — Semua Stakeholder",
        "description": "Investor agresif + Government balanced + NGO moderat",
        "agents": [
            {"type": "investor", "id": "inv-1", "name": "PLN Geothermal",
             "params": {"budget_billion": 5000, "risk_tolerance": 0.7}},
            {"type": "government", "id": "gov-1", "name": "ESDM",
             "params": {"annual_budget_billion": 3000, "policy_orientation": "balanced"}},
            {"type": "operator", "id": "op-1", "name": "Operator Salak",
             "params": {"kode_wkp": "WKP001", "opex_budget_billion": 500}},
            {"type": "community", "id": "com-1", "name": "Warga Salak",
             "params": {"kode_wkp": "WKP001", "n_population": 10000, "initial_acceptance": 0.6}},
            {"type": "media", "id": "med-1", "name": "GeoSDI News",
             "params": {"editorial_orientation": "neutral", "reach": 0.7}},
            {"type": "ngo", "id": "ngo-1", "name": "WALHI",
             "params": {"focus": "both", "reach": 0.7, "advocacy_power": 0.8}},
            {"type": "academic", "id": "aca-1", "name": "ITB Research",
             "params": {"institution": "ITB", "expertise": "geology", "research_capacity": 0.8}},
        ],
    },
    "growth": {
        "name": "📈 Growth — Pro-Industri",
        "description": "Investor agresif + Government pro-growth + NGO lemah",
        "agents": [
            {"type": "investor", "id": "inv-1", "name": "PLN Geothermal",
             "params": {"budget_billion": 8000, "risk_tolerance": 0.9}},
            {"type": "government", "id": "gov-1", "name": "ESDM",
             "params": {"annual_budget_billion": 5000, "policy_orientation": "growth"}},
            {"type": "media", "id": "med-1", "name": "Media Pro-Industri",
             "params": {"editorial_orientation": "pro_industry", "reach": 0.8}},
            {"type": "ngo", "id": "ngo-1", "name": "NGO Moderat",
             "params": {"focus": "environment", "reach": 0.5, "advocacy_power": 0.3}},
        ],
    },
    "equity": {
        "name": "⚖️ Equity — Pemerataan",
        "description": "Government pro-equity + NGO kuat + Community aktif",
        "agents": [
            {"type": "investor", "id": "inv-1", "name": "Investor Konservatif",
             "params": {"budget_billion": 3000, "risk_tolerance": 0.3}},
            {"type": "government", "id": "gov-1", "name": "ESDM",
             "params": {"annual_budget_billion": 4000, "policy_orientation": "equity"}},
            {"type": "community", "id": "com-1", "name": "Warga Salak",
             "params": {"kode_wkp": "WKP001", "n_population": 10000, "initial_acceptance": 0.4}},
            {"type": "ngo", "id": "ngo-1", "name": "WALHI",
             "params": {"focus": "both", "reach": 0.9, "advocacy_power": 0.9}},
            {"type": "media", "id": "med-1", "name": "Media Pro-Lingkungan",
             "params": {"editorial_orientation": "pro_environment", "reach": 0.7}},
        ],
    },
}


# ============================================================
# Agent metadata
# ============================================================
AGENT_METADATA = {
    "investor": {
        "label": "Investor",
        "icon": "🏢",
        "description": "Mencari ROI tinggi, budget constraint, hindari konflik",
        "default_params": {
            "budget_billion": 5000,
            "risk_tolerance": 0.5,
            "min_gdi_threshold": 80.0,
        },
    },
    "government": {
        "label": "Pemerintah",
        "icon": "🏛️",
        "description": "Alokasi subsidi, kebijakan fiskal, pemerataan",
        "default_params": {
            "annual_budget_billion": 3000,
            "policy_orientation": "balanced",
            "subsidy_per_wkp_billion": 150.0,
        },
    },
    "community": {
        "label": "Masyarakat",
        "icon": "👥",
        "description": "Penerimaan/penolakan, minta kompensasi",
        "default_params": {
            "kode_wkp": "WKP001",
            "n_population": 5000,
            "initial_acceptance": 0.5,
            "compensation_expectation_billion": 50.0,
        },
    },
    "operator": {
        "label": "Operator PLTP",
        "icon": "⚡",
        "description": "Maintenance, upgrade teknologi, ekspansi kapasitas",
        "default_params": {
            "kode_wkp": "WKP001",
            "opex_budget_billion": 500.0,
            "tech_readiness": 0.7,
            "maintenance_interval": 3,
        },
    },
    "media": {
        "label": "Media",
        "icon": "📰",
        "description": "Framing isu, amplification, opini publik",
        "default_params": {
            "outlet": "GeoSDI News",
            "editorial_orientation": "neutral",
            "reach": 0.6,
            "viral_factor": 0.4,
        },
    },
    "ngo": {
        "label": "NGO",
        "icon": "🌿",
        "description": "Advokasi lingkungan, check and balance",
        "default_params": {
            "ngo_name": "WALHI",
            "focus": "both",
            "reach": 0.6,
            "advocacy_power": 0.7,
        },
    },
    "academic": {
        "label": "Akademisi",
        "icon": "🎓",
        "description": "Riset, knowledge sharing, SDM expert",
        "default_params": {
            "institution": "ITB",
            "expertise": "geology",
            "research_capacity": 0.8,
            "publication_rate": 0.6,
        },
    },
}


# ============================================================
# Agent factory
# ============================================================
def create_agent(config: AgentConfig):
    """Buat agent dari config."""
    agent_type = config.type
    params = config.params

    if agent_type == "investor":
        return InvestorAgent(
            id=config.id, name=config.name,
            budget_billion=params.get("budget_billion", 5000),
            risk_tolerance=params.get("risk_tolerance", 0.5),
            min_gdi_threshold=params.get("min_gdi_threshold", 80.0),
        )
    elif agent_type == "government":
        return GovernmentAgent(
            id=config.id, name=config.name,
            annual_budget_billion=params.get("annual_budget_billion", 3000),
            policy_orientation=params.get("policy_orientation", "balanced"),
            subsidy_per_wkp_billion=params.get("subsidy_per_wkp_billion", 150.0),
        )
    elif agent_type == "community":
        return CommunityAgent(
            id=config.id, name=config.name,
            kode_wkp=params.get("kode_wkp", "WKP001"),
            n_population=params.get("n_population", 5000),
            initial_acceptance=params.get("initial_acceptance", 0.5),
            compensation_expectation_billion=params.get("compensation_expectation_billion", 50.0),
        )
    elif agent_type == "operator":
        return OperatorAgent(
            id=config.id, name=config.name,
            kode_wkp=params.get("kode_wkp", "WKP001"),
            opex_budget_billion=params.get("opex_budget_billion", 500),
            tech_readiness=params.get("tech_readiness", 0.7),
            maintenance_interval=params.get("maintenance_interval", 3),
        )
    elif agent_type == "media":
        return MediaAgent(
            id=config.id, name=config.name,
            outlet=params.get("outlet", "GeoSDI News"),
            editorial_orientation=params.get("editorial_orientation", "neutral"),
            reach=params.get("reach", 0.6),
            viral_factor=params.get("viral_factor", 0.4),
        )
    elif agent_type == "ngo":
        return NGOAgent(
            id=config.id, name=config.name,
            ngo_name=params.get("ngo_name", "WALHI"),
            focus=params.get("focus", "both"),
            reach=params.get("reach", 0.6),
            advocacy_power=params.get("advocacy_power", 0.7),
        )
    elif agent_type == "academic":
        return AcademicAgent(
            id=config.id, name=config.name,
            institution=params.get("institution", "ITB"),
            expertise=params.get("expertise", "geology"),
            research_capacity=params.get("research_capacity", 0.8),
            publication_rate=params.get("publication_rate", 0.6),
        )
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")


# ============================================================
# GET /agents — List agent metadata
# ============================================================
@router.get("/agents")
async def list_agents():
    """List tipe agen yang tersedia + default config."""
    return {
        "agents": [
            {
                "type": k,
                "label": v["label"],
                "icon": v["icon"],
                "description": v["description"],
                "default_params": v["default_params"],
            }
            for k, v in AGENT_METADATA.items()
        ]
    }


# ============================================================
# GET /scenarios — List preset scenarios
# ============================================================
@router.get("/scenarios")
async def list_scenarios():
    """List preset ABM scenarios."""
    return {
        "scenarios": [
            {
                "key": k,
                "name": v["name"],
                "description": v["description"],
                "n_agents": len(v["agents"]),
            }
            for k, v in PRESET_SCENARIOS.items()
        ]
    }


# ============================================================
# POST /simulate — Run simulation
# ============================================================
@router.post("/simulate")
async def run_simulation(request: ABMSimulationRequest):
    """
    Jalankan ABM simulation dengan config agen.
    """
    try:
        # Build environment
        env = WKPEnvironment.from_database()

        # Build simulation
        sim = Simulation(
            name=request.name,
            environment=env,
            max_steps=request.max_steps,
            seed=request.seed,
        )

        # Add agents
        for agent_config in request.agents:
            try:
                agent = create_agent(agent_config)
                sim.add_agent(agent)
            except Exception as e:
                log.error(f"Failed to create agent {agent_config.id}: {e}")
                raise ValueError(f"Agen '{agent_config.name}' gagal dibuat: {e}")

        # Run simulation
        summary = sim.run()

        # Build detailed response
        initial_gdi = summary["initial_environment"]["gdi_national"]
        final_gdi = summary["final_environment"]["gdi_national"]
        delta_gdi = round(final_gdi - initial_gdi, 2)

        return {
            "name": summary["name"],
            "n_steps": summary["n_steps"],
            "n_agents": summary["n_agents"],
            "environment": {
                "initial": summary["initial_environment"],
                "final": summary["final_environment"],
                "delta": {
                    "gdi_national": delta_gdi,
                    "gdi_percent": round((delta_gdi / initial_gdi * 100), 2) if initial_gdi > 0 else 0,
                },
            },
            "agents": summary["agent_states"],
            "n_events": len(env.event_log),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


# ============================================================
# GET /scenario/{key}/run — Run preset scenario
# ============================================================
@router.get("/scenario/{key}/run")
async def run_preset_scenario(
    key: str,
    max_steps: int = Query(15, ge=1, le=50),
):
    """Jalankan preset scenario."""
    if key not in PRESET_SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{key}' tidak ditemukan")

    preset = PRESET_SCENARIOS[key]

    # Build agents dari config
    agents = []
    for a in preset["agents"]:
        agents.append(AgentConfig(
            type=a["type"],
            id=a["id"],
            name=a["name"],
            params=a["params"],
        ))

    request = ABMSimulationRequest(
        name=preset["name"],
        max_steps=max_steps,
        seed=42,
        agents=agents,
    )

    return await run_simulation(request)