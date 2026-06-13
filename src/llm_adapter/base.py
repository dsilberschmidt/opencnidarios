"""LLM adapter interface for OpenCnidarios.

The engine calls generate() once per ruminant per tick, then feedback() after
the energy outcome of that action is resolved.

Contract:
- generate: Input: organism_id, constitution, memory, observation, max_tokens
             Output: (text, token_count)
- feedback: Input: organism_id, action taken (or None), energy_delta from feeding only
             Output: None (side-effect on adapter internal state)

The adapter must enforce max token generation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple


class LLMAdapter(ABC):
    @abstractmethod
    def generate(
        self,
        organism_id: str,
        constitution: str,
        memory: str,
        observation: Dict[str, Any],
        max_tokens: int,
    ) -> Tuple[str, int]:
        """Return (output_text, tokens_generated)."""
        raise NotImplementedError

    @abstractmethod
    def feedback(
        self,
        organism_id: str,
        action: Optional[str],
        energy_delta: float,
    ) -> None:
        """Reinforce action based on feeding energy delta. delta > 0 = gain."""
        raise NotImplementedError

    def register_child(self, child_id: str, parent_id: str) -> None:
        """Hook for weight inheritance at birth. No-op by default."""
