"""
GeoSDI ABM — Base Classes
==========================
Base classes untuk Agent-Based Modeling:
- Agent: abstraksi agen (investor, pemerintah, masyarakat, dll)
- Environment: abstraksi lingkungan (WKP, region, dll)
- Simulation: orchestrator yang jalankan semua agen
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
import random

from src.shared.logger import get_logger

log = get_logger(__name__)


# ============================================================
# Agent — Base Class
# ============================================================
@dataclass
class Agent(ABC):
    """
    Base class untuk semua agen dalam ABM.

    Setiap agen punya:
    - id: identifier unik
    - name: nama agen (human-readable)
    - state: dict state internal agen
    - memory: history aksi
    """

    id: str
    name: str
    state: dict = field(default_factory=dict)
    memory: list = field(default_factory=list)

    # Config
    seed: Optional[int] = None

    def __post_init__(self):
        if self.seed is not None:
            self._rng = random.Random(self.seed)
        else:
            self._rng = random.Random()

    @abstractmethod
    def perceive(self, environment: "Environment") -> dict:
        """
        Agen mengamati environment → return observasi.

        Contoh: Investor melihat GDI, ROI, risk dari WKP.
        """
        pass

    @abstractmethod
    def decide(self, observation: dict) -> dict:
        """
        Agen memutuskan aksi berdasarkan observasi.

        Contoh: Investor memutuskan "invest" atau "wait".
        """
        pass

    @abstractmethod
    def act(self, decision: dict, environment: "Environment") -> dict:
        """
        Agen melakukan aksi → return hasil aksi.

        Contoh: Investor invest → tambah kapasitas WKP.
        """
        pass

    def step(self, environment: "Environment") -> dict:
        """
        Satu siklus: perceive → decide → act.

        Return: dict hasil aksi.
        """
        observation = self.perceive(environment)
        decision = self.decide(observation)
        result = self.act(decision, environment)

        # Simpan ke memory
        self.memory.append({
            "step": len(self.memory),
            "observation": observation,
            "decision": decision,
            "result": result,
        })

        return result

    def get_state(self) -> dict:
        """Return state agen untuk serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state,
            "memory_size": len(self.memory),
        }


# ============================================================
# Environment — Base Class
# ============================================================
@dataclass
class Environment(ABC):
    """
    Base class untuk environment dalam ABM.

    Environment adalah "dunia" di mana agen beroperasi.
    Untuk GeoSDI: WKP + agregat nasional.
    """

    id: str
    name: str
    state: dict = field(default_factory=dict)

    @abstractmethod
    def get_observation(self, agent: Agent) -> dict:
        """
        Return observasi untuk agen tertentu.

        Setiap agen bisa dapat observasi berbeda (tergantung "penglihatan").
        """
        pass

    @abstractmethod
    def apply_action(self, agent: Agent, action: dict) -> dict:
        """
        Apply aksi agen ke environment.

        Return: perubahan yang terjadi.
        """
        pass

    @abstractmethod
    def get_state(self) -> dict:
        """Return state environment untuk serialization."""
        pass


# ============================================================
# Simulation — Orchestrator
# ============================================================
@dataclass
class Simulation:
    """
    Orchestrator ABM: jalankan semua agen selama N step.

    Setiap step:
    1. Semua agen observe environment
    2. Semua agen decide
    3. Semua agen act (update environment)
    4. Log state
    """

    name: str
    environment: Environment
    agents: list[Agent] = field(default_factory=list)
    max_steps: int = 10
    seed: Optional[int] = None

    # History
    history: list = field(default_factory=list)

    def __post_init__(self):
        if self.seed is not None:
            random.seed(self.seed)

    def add_agent(self, agent: Agent) -> None:
        """Tambah agen ke simulation."""
        self.agents.append(agent)

    def step(self) -> dict:
        """Jalankan 1 step: semua agen bertindak."""
        results = []

        # Shuffle agents (biar tidak ada ordering bias)
        shuffled = self.agents.copy()
        random.shuffle(shuffled)

        for agent in shuffled:
            result = agent.step(self.environment)
            results.append({
                "agent_id": agent.id,
                "agent_name": agent.name,
                "result": result,
            })

        # Snapshot state
        snapshot = {
            "step": len(self.history),
            "environment": self.environment.get_state(),
            "actions": results,
        }
        self.history.append(snapshot)

        return snapshot

    def run(self, max_steps: Optional[int] = None) -> dict:
        """
        Jalankan simulation untuk N step.

        Return: summary akhir.
        """
        n = max_steps or self.max_steps

        log.info(f"ABM Simulation '{self.name}' started: {len(self.agents)} agents, {n} steps")

        for step_idx in range(n):
            self.step()

        log.info(f"ABM Simulation '{self.name}' completed: {n} steps")

        return self.get_summary()

    def get_summary(self) -> dict:
        """Ringkasan hasil simulation."""
        if not self.history:
            return {"name": self.name, "steps": 0}

        final = self.history[-1]
        initial = self.history[0] if self.history else final

        return {
            "name": self.name,
            "n_agents": len(self.agents),
            "n_steps": len(self.history),
            "final_environment": final["environment"],
            "initial_environment": initial["environment"],
            "agent_states": [a.get_state() for a in self.agents],
        }