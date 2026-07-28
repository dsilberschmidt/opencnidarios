"""Write organism snapshots to disk.

No-op if adapter.export_full_state() returns None — supports any adapter
without isinstance checks.
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ruminant import Ruminant
    from .llm_adapter.base import LLMAdapter


def write_snapshot(
    r: "Ruminant",
    cause: str,  # "starvation" | "attacked" | "end_of_run" | "crash" | "checkpoint"
    run_id: str,
    tick: int,
    adapter: "LLMAdapter",
    organisms_dir: str,
) -> None:
    full_state = adapter.export_full_state(r.id)
    if full_state is None:
        return
    os.makedirs(organisms_dir, exist_ok=True)
    filename = f"{r.instance_id}_{r.id[:8]}_tick{tick:06d}.json"
    payload = {
        "id":                r.id,
        "instance_id":       r.instance_id,
        "forked_from":       r.forked_from,
        "run_id":            run_id,
        "tick":              tick,
        "cause":             cause,
        "adapter_type":      adapter.adapter_type,
        "x":                 r.x,
        "y":                 r.y,
        "energy_internal":   r.energy_internal,
        "age":               r.age,
        "constitution_text": r.constitution_text,
        "memory_text":       r.memory_text,
        "adapter_state":     full_state,
    }
    with open(os.path.join(organisms_dir, filename), "w") as f:
        json.dump(payload, f, indent=2)
