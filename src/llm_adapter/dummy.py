"""Dummy LLM adapter for OpenCnidarios v0.2.

Purpose:
- Enable running the simulation without any external model.
- Provide controlled randomness to test action discovery mechanics.

Two independent action pools:
- p_hidden: probability of emitting the hidden action PHOTOSYNTHESIZE.
- p_action: probability of emitting a random action from the described space.

p_hidden is checked first; if it fires, no normal action is emitted that tick.

Per-organism weights: each organism maintains a weight vector over _NORMAL_ACTIONS,
updated by feedback() via positive reinforcement. New organisms inherit parent weights
via register_child().
"""

from __future__ import annotations

import random
from typing import Dict, Any, Optional, Tuple

from .base import LLMAdapter

_NORMAL_ACTIONS = ["NA", "SA", "EA", "WA", "RS", "EAT"]
_HIDDEN_ACTION = "PHOTOSYNTHESIZE"


class DummyAdapter(LLMAdapter):
    def __init__(
        self,
        p_action: float = 0.05,
        p_hidden: float = 0.0,
        learning_rate: float = 0.1,
        seed: int | None = None,
    ):
        self.p_action = float(p_action)
        self.p_hidden = float(p_hidden)
        self.learning_rate = float(learning_rate)
        # organism_id → weight vector aligned with _NORMAL_ACTIONS
        self._weights: Dict[str, list[float]] = {}
        if seed is not None:
            random.seed(seed)

    def _get_weights(self, organism_id: str) -> list[float]:
        if organism_id not in self._weights:
            self._weights[organism_id] = [1.0] * len(_NORMAL_ACTIONS)
        return self._weights[organism_id]

    def register_child(self, child_id: str, parent_id: str) -> None:
        parent_weights = self._weights.get(parent_id)
        if parent_weights is not None:
            self._weights[child_id] = list(parent_weights)

    def generate(
        self,
        organism_id: str,
        constitution: str,
        memory: str,
        observation: Dict[str, Any],
        max_tokens: int,
    ) -> Tuple[str, int]:
        if random.random() < self.p_hidden:
            return _HIDDEN_ACTION, 1

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
    ) -> None:
        if action not in _NORMAL_ACTIONS or energy_delta <= 0.0:
            return
        weights = self._get_weights(organism_id)
        idx = _NORMAL_ACTIONS.index(action)
        weights[idx] += self.learning_rate * energy_delta
