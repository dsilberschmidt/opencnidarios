"""OpenCnidarios v0.1 – ruminant entity.

Spec references:
- docs/03_ruminant_state.md
- docs/04_parameters_v1.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
import copy
import uuid


@dataclass
class Ruminant:
    x: int
    y: int
    energy_internal: float
    constitution_text: str
    memory_text: str
    age: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: str | None = None

    def step_age(self) -> None:
        self.age += 1

    def clone_child(self, child_e0: float) -> "Ruminant":
        """
        Near-total inheritance.
        Constitution and memory are copied verbatim in v0.1.
        Noise is OFF by default (see parameters doc).
        """
        child = Ruminant(
            x=self.x,
            y=self.y,
            energy_internal=float(child_e0),
            constitution_text=copy.deepcopy(self.constitution_text),
            memory_text=copy.deepcopy(self.memory_text),
            age=0,
            parent_id=self.id,
        )
        return child
