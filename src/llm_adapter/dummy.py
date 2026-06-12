"""Dummy LLM adapter for OpenCnidarios v0.2.

Purpose:
- Enable running the simulation without any external model.
- Provide controlled randomness to test action discovery mechanics.

Two independent action pools:
- p_hidden: probability of emitting the hidden action PHOTOSYNTHESIZE (renewable energy,
  not described to organisms — must be discovered by accident or reasoning).
- p_action: probability of emitting a random action from the described space
  (NA/SA/EA/WA for movement, RS for reproduction, EAT for chemotrophy).

p_hidden is checked first; if it fires, no normal action is emitted that tick.
"""

from __future__ import annotations

import random
from typing import Dict, Any, Tuple

from .base import LLMAdapter

_NORMAL_ACTIONS = ["NA", "SA", "EA", "WA", "RS", "EAT"]
_HIDDEN_ACTION = "PHOTOSYNTHESIZE"


class DummyAdapter(LLMAdapter):
    def __init__(
        self,
        p_action: float = 0.05,
        p_hidden: float = 0.0,
        seed: int | None = None,
    ):
        self.p_action = float(p_action)
        self.p_hidden = float(p_hidden)
        if seed is not None:
            random.seed(seed)

    def generate(
        self,
        constitution: str,
        memory: str,
        observation: Dict[str, Any],
        max_tokens: int,
    ) -> Tuple[str, int]:
        # Hidden action checked first — exclusive with normal actions.
        if random.random() < self.p_hidden:
            return _HIDDEN_ACTION, 1

        # Occasionally emit a described action token.
        if random.random() < self.p_action:
            return random.choice(_NORMAL_ACTIONS), 1

        # Default: idle.
        return "...", 1
