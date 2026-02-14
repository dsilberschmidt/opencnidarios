"""LLM adapter interface for OpenCnidarios.

The engine calls a single method per ruminant per tick.
This adapter abstracts away local vs API models.

Contract:
- Input: constitution, memory, observation, max_tokens
- Output: (text, token_count)

The adapter must enforce max token generation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple


class LLMAdapter(ABC):
    @abstractmethod
    def generate(
        self,
        constitution: str,
        memory: str,
        observation: Dict[str, Any],
        max_tokens: int,
    ) -> Tuple[str, int]:
        """Return (output_text, tokens_generated)."""
        raise NotImplementedError
