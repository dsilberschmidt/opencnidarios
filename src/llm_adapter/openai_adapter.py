"""OpenAIAdapter — LLM adapter OpenAI para OpenCnidarios."""

from __future__ import annotations

import os
import re
import time
from typing import Dict, Any, List, Optional, Tuple

import openai

from .base import LLMAdapter, INTERVIEW_QUESTIONS

_RETRY_DELAYS = (2, 4, 8, 60, 180)


class OpenAIAdapter(LLMAdapter):
    adapter_type = "openai"
    supports_token_cost_metric = True

    def __init__(
        self,
        model: str = "gpt-5.4-mini",
        memory_cost_factor: float = 0.00005,
        compression_interval: int = 20,
        cost_metric: str = "chars",
    ):
        self.model = model
        self.memory_cost_factor = memory_cost_factor
        self.compression_interval = compression_interval
        self.cost_metric = cost_metric
        self._client = openai.OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            max_retries=0,
        )
        self._states: Dict[str, dict] = {}

    def _api_call(self, fn):
        for delay in _RETRY_DELAYS:
            try:
                return fn()
            except (openai.RateLimitError, openai.InternalServerError,
                    openai.APIConnectionError, openai.APITimeoutError):
                time.sleep(delay)
        return fn()

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
            f"last_action: {observation['last_action']}\n"
            f"XEstadoX"
        )

    def _compress(self, organism_id: str, constitution: str) -> None:
        state = self._states[organism_id]
        if not state["history"]:
            return
        history_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in state["history"]
        )
        messages = [
            {"role": "system", "content": constitution},
            {"role": "user", "content": (
                f"Here is your complete history in this world so far:\n\n{history_text}\n\n"
                "Compress this into a concise summary. Keep what you believe is most "
                "important for your survival. Discard the rest."
            )},
        ]
        response = self._api_call(lambda: self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_completion_tokens=1000,
        ))
        compressed = response.choices[0].message.content
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

        messages = (
            [{"role": "system", "content": system_prompt}]
            + list(state["history"])
            + [{"role": "user", "content": obs_text}]
        )

        response = self._api_call(lambda: self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_completion_tokens=max_tokens,
        ))
        output_text = response.choices[0].message.content

        state["history"].append({"role": "user", "content": obs_text})
        state["history"].append({"role": "assistant", "content": output_text})

        context_chars = len(system_prompt) + sum(len(m["content"]) for m in state["history"])
        state["context_chars"] = context_chars

        if self.cost_metric == "tokens":
            token_count = response.usage.completion_tokens
        else:
            token_count = int(context_chars * self.memory_cost_factor)

        return output_text, token_count

    def feedback(self, organism_id: str, action: Optional[str], energy_delta: float) -> bool:
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
        messages = (
            [{"role": "system", "content": state["constitution"]}]
            + list(state["history"])
            + [{"role": "user", "content": prompt}]
        )
        response = self._api_call(lambda: self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_completion_tokens=500,
        ))
        text = response.choices[0].message.content

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
        response = self._api_call(lambda: self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=10,
        ))
        answer = response.choices[0].message.content.strip().upper()
        return "YES" in answer

    def export_full_state(self, organism_id: str) -> dict | None:
        state = self._states.get(organism_id)
        if state is None:
            return None
        return {
            "history":           list(state["history"]),
            "constitution":      state["constitution"],
            "tick_count":        state["tick_count"],
            "compression_count": state["compression_count"],
            "context_chars":     state["context_chars"],
        }

    def get_organism_state(self, organism_id: str) -> dict:
        state = self._states.get(organism_id, {})
        return {
            "context_chars": state.get("context_chars", 0),
            "compression_count": state.get("compression_count", 0),
        }
