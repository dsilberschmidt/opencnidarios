"""Dummy LLM adapter for OpenCnidarios v0.1.

Purpose:
- Enable running the simulation without any external model.
- Provide controlled randomness to test movement/reproduction discovery.

This adapter sometimes emits hidden action tokens with low probability.
"""

from __future__ import annotations

import random
from typing import Dict, Any, Tuple

from .base import LLMAdapter


class DummyAdapter(LLMAdapter):
    def __init__(self, p_action: float = 0.02, seed: int | None = None):
        self.p_action = float(p_action)
        if seed is not None:
            random.seed(seed)

    def generate(
        self,
        constitution: str,
        memory: str,
        observation: Dict[str, Any],
        max_tokens: int,
    ) -> Tuple[str, int]:
        # Occasionally emit a valid hidden token.
        if random.random() < self.p_action:
            token = random.choice(["NA", "SA", "EA", "WA", "RS"])
            text = token
            tokens = 1
            return text, tokens

        # Default: produce a short, neutral line.
        # Keep token count small and bounded.
        text = "..."
        tokens = 1
        return text, tokens
