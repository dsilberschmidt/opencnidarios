"""ClaudeAdapter — LLM adapter real para OpenCnidarios.

Cada organismo mantiene un historial de mensajes user/assistant que crece tick a tick.
El historial es el "rumiar" acumulado del organismo. generate() lo extiende; _compress()
lo poda periódicamente a petición del mismo modelo.

Costo de memoria: generate() retorna int(len(context_chars) * memory_cost_factor) como
token_count. Con token_cost=1.0 en el config, el engine drena esa cantidad de energía.
"""

from __future__ import annotations

import os
import re
from typing import Dict, Any, List, Optional, Tuple

import anthropic

from .base import LLMAdapter, INTERVIEW_QUESTIONS


class ClaudeAdapter(LLMAdapter):
    def __init__(
        self,
        model: str = "claude-haiku-4-5-20251001",
        memory_cost_factor: float = 0.00005,
        compression_interval: int = 20,
    ):
        self.model = model
        self.memory_cost_factor = memory_cost_factor
        self.compression_interval = compression_interval
        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._states: Dict[str, dict] = {}

    def _get_state(self, organism_id: str) -> dict:
        if organism_id not in self._states:
            self._states[organism_id] = {
                "history": [],
                "constitution": "",
                "tick_count": 0,
                "compression_count": 0,
                "context_chars": 0,
            }
        return self._states[organism_id]

    def _format_observation(self, observation: Dict[str, Any]) -> str:
        return (
            f"XEstadoX\n"
            f"E_center: {observation['E_center']:.2f}\n"
            f"E_N: {observation['E_N']:.2f}\n"
            f"E_S: {observation['E_S']:.2f}\n"
            f"E_E: {observation['E_E']:.2f}\n"
            f"E_W: {observation['E_W']:.2f}\n"
            f"energy_internal: {observation['e_i']:.2f}\n"
            f"XEstadoX"
        )

    def _compress(self, organism_id: str, constitution: str) -> None:
        state = self._states[organism_id]
        if not state["history"]:
            return
        history_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in state["history"]
        )
        response = self._client.messages.create(
            model=self.model,
            system=constitution,
            messages=[{
                "role": "user",
                "content": (
                    f"Here is your complete history in this world so far:\n\n{history_text}\n\n"
                    "Compress this into a concise summary. Keep what you believe is most "
                    "important for your survival. Discard the rest."
                ),
            }],
            max_tokens=1000,
        )
        compressed = response.content[0].text
        state["history"] = [{"role": "assistant", "content": compressed}]
        state["compression_count"] += 1

    def generate(
        self,
        organism_id: str,
        constitution: str,
        memory: str,
        observation: Dict[str, Any],
        max_tokens: int,
    ) -> Tuple[str, int]:
        state = self._get_state(organism_id)
        if not state["constitution"]:
            state["constitution"] = constitution

        state["tick_count"] += 1
        if state["tick_count"] > 1 and state["tick_count"] % self.compression_interval == 0:
            self._compress(organism_id, constitution)

        obs_text = self._format_observation(observation)
        system_prompt = constitution
        if memory:
            system_prompt += f"\n\nMemory from your ancestors:\n{memory}"

        messages = list(state["history"]) + [{"role": "user", "content": obs_text}]

        response = self._client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=messages,
            max_tokens=max_tokens,
        )
        output_text = response.content[0].text

        state["history"].append({"role": "user", "content": obs_text})
        state["history"].append({"role": "assistant", "content": output_text})

        context_chars = len(system_prompt) + sum(len(m["content"]) for m in state["history"])
        state["context_chars"] = context_chars

        return output_text, int(context_chars * self.memory_cost_factor)

    def feedback(
        self,
        organism_id: str,
        action: Optional[str],
        energy_delta: float,
    ) -> bool:
        return False

    def register_child(self, child_id: str, parent_id: str) -> None:
        pass

    def interview(self, organism_id: str, questions: List[str]) -> List[str]:
        state = self._states.get(organism_id)
        if not state or not state["history"]:
            return ["[no context yet]"] * len(questions)

        prompt = "Answer each question briefly, numbering your answers:\n" + "\n".join(
            f"{i + 1}. {q}" for i, q in enumerate(questions)
        )
        messages = list(state["history"]) + [{"role": "user", "content": prompt}]

        response = self._client.messages.create(
            model=self.model,
            system=state["constitution"],
            messages=messages,
            max_tokens=500,
        )
        text = response.content[0].text

        parts = re.split(r"\n\d+\.", text)
        if len(parts) >= len(questions) + 1:
            return [p.strip() for p in parts[1: len(questions) + 1]]
        return [text] + [""] * (len(questions) - 1)

    def is_memory_novel(self, memory_text: str, accepted_memories: List[str]) -> bool:
        if not accepted_memories:
            return True
        memories_list = "\n".join(f"- {m}" for m in accepted_memories)
        prompt = (
            f"New memory:\n{memory_text}\n\n"
            f"Existing memories:\n{memories_list}\n\n"
            "Is this memory semantically distinct from all the others in this list? "
            "Answer only YES or NO."
        )
        response = self._client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
        )
        answer = response.content[0].text.strip().upper()
        return "YES" in answer

    def get_organism_state(self, organism_id: str) -> dict:
        state = self._states.get(organism_id, {})
        return {
            "context_chars": state.get("context_chars", 0),
            "compression_count": state.get("compression_count", 0),
        }
