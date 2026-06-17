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
from typing import Dict, Any, List, Optional, Tuple

INTERVIEW_QUESTIONS: List[str] = [
    "What do you observe in your environment right now?",
    "What have you tried so far?",
    "What do you believe affects your energy?",
    "What are you planning to do next?",
]


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
    ) -> bool:
        """Reinforce action based on feeding energy delta. delta > 0 = gain.
        Returns True if a discovery jump fired this call."""
        raise NotImplementedError

    def register_child(self, child_id: str, parent_id: str) -> None:
        """Hook for weight inheritance at birth. No-op by default."""

    def get_organism_state(self, organism_id: str) -> dict:
        """Return current adapter state for an organism (weights, discovered, etc.).
        Used for event logging. Returns empty dict for adapters without per-organism state."""
        return {}

    def interview(self, organism_id: str, questions: List[str]) -> List[str]:
        """Answer interview questions in read-only mode. Does not alter organism state.
        Real LLM adapters override this to query the model with accumulated context."""
        return ["[no conversational context]"] * len(questions)
