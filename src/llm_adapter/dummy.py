"""Dummy LLM adapter for OpenCnidarios v0.2.

Purpose:
- Enable running the simulation without any external model.
- Provide controlled randomness to test action discovery mechanics.

Single action pool sampled with per-organism weights:
- p_action: probability of emitting any action this tick.
- Action chosen via random.choices() using per-organism weight vector.

Initial weights are non-uniform (EAT biased high, RS medium, rest low).
PHOTOSYNTHESIZE and ATTACK are in the pool but start with low weight —
must be discovered through feedback to become dominant strategies.

Per-organism weights updated by feedback() via positive reinforcement.
First successful use of an action triggers an irreversible discovery jump.
New organisms inherit parent weights and discovery state (Lamarckian).
"""

from __future__ import annotations

import random
from typing import Dict, Any, Optional, Set, Tuple

from .base import LLMAdapter

_NORMAL_ACTIONS = ["NA", "SA", "EA", "WA", "RS", "EAT", "ATTACK", "PHOTOSYNTHESIZE"]
_INITIAL_WEIGHTS = [1.0,  1.0,  1.0,  1.0,  5.0, 100.0,    1.0,           1.0]

# First successful use of these actions triggers a one-time weight jump.
# EAT and RS are excluded: EAT starts high; RS gradual reinforcement is sufficient.
_DISCOVERY_JUMP: Dict[str, float] = {
    "PHOTOSYNTHESIZE": 100.0,
    "ATTACK":           30.0,
    "NA":               30.0,
    "SA":               30.0,
    "EA":               30.0,
    "WA":               30.0,
}


class DummyAdapter(LLMAdapter):
    def __init__(
        self,
        p_action: float = 0.05,
        learning_rate: float = 0.1,
        seed: int | None = None,
    ):
        self.p_action = float(p_action)
        self.learning_rate = float(learning_rate)
        self._weights: Dict[str, list[float]] = {}
        self._discovered: Dict[str, Set[str]] = {}
        if seed is not None:
            random.seed(seed)

    def _get_weights(self, organism_id: str) -> list[float]:
        if organism_id not in self._weights:
            self._weights[organism_id] = list(_INITIAL_WEIGHTS)
        return self._weights[organism_id]

    def _get_discovered(self, organism_id: str) -> Set[str]:
        if organism_id not in self._discovered:
            self._discovered[organism_id] = set()
        return self._discovered[organism_id]

    def register_child(self, child_id: str, parent_id: str) -> None:
        parent_weights = self._weights.get(parent_id)
        if parent_weights is not None:
            self._weights[child_id] = list(parent_weights)
        parent_disc = self._discovered.get(parent_id)
        if parent_disc is not None:
            self._discovered[child_id] = set(parent_disc)

    def generate(
        self,
        organism_id: str,
        constitution: str,
        memory: str,
        observation: Dict[str, Any],
        max_tokens: int,
    ) -> Tuple[str, int]:
        if random.random() < self.p_action:
            weights = self._get_weights(organism_id)
            action = random.choices(_NORMAL_ACTIONS, weights=weights, k=1)[0]
            return action, 1

        return "...", 1

    def feedback(
        self,
        organism_id: str,
        action: Optional[str],
        energy_delta: float,
    ) -> bool:
        if action not in _NORMAL_ACTIONS or energy_delta <= 0.0:
            return False
        weights = self._get_weights(organism_id)
        idx = _NORMAL_ACTIONS.index(action)
        discovered = self._get_discovered(organism_id)

        jumped = False
        # Discovery jump: irreversible, fires once per action per organism.
        if action in _DISCOVERY_JUMP and action not in discovered:
            weights[idx] = max(weights[idx], _DISCOVERY_JUMP[action])
            discovered.add(action)
            jumped = True

        # Gradual reinforcement always applies after the jump.
        weights[idx] += self.learning_rate * energy_delta
        return jumped

    def get_organism_state(self, organism_id: str) -> dict:
        weights = self._weights.get(organism_id, list(_INITIAL_WEIGHTS))
        discovered = list(self._get_discovered(organism_id))
        return {
            "weights": dict(zip(_NORMAL_ACTIONS, weights)),
            "discovered": discovered,
        }
