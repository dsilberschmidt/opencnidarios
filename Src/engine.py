"""OpenCnidarios v0.1 – minimal simulation engine (scaffold).

Non-goals: performance, parallelism, multi-biome, human interaction.
This file is a runnable skeleton to be completed alongside:
- world.py
- ruminant.py
- llm_adapter/*
- logging/*

Spec references:
- docs/02_planeta_v1_specification.md
- docs/04_parameters_v1.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class TickStats:
    tick: int
    population: int
    births: int
    deaths: int
    moves: int
    absorptions: int
    mean_internal_energy: float


class Engine:
    def __init__(self, world, llm_adapter, params: Dict[str, Any], logger=None):
        self.world = world
        self.llm = llm_adapter
        self.p = params
        self.logger = logger
        self.ruminants: List[Any] = []
        self.tick = 0

    def seed_population(self, ruminants: List[Any]) -> None:
        self.ruminants = list(ruminants)

    def _build_observation(self, r) -> Dict[str, Any]:
        # Local observation: E_center + N/S/E/W + internal energy
        e_center = self.world.energy_at(r.x, r.y)
        e_n = self.world.energy_at(r.x, r.y - 1)
        e_s = self.world.energy_at(r.x, r.y + 1)
        e_e = self.world.energy_at(r.x + 1, r.y)
        e_w = self.world.energy_at(r.x - 1, r.y)
        return {
            "E_center": e_center,
            "E_N": e_n,
            "E_S": e_s,
            "E_E": e_e,
            "E_W": e_w,
            "e_i": r.energy_internal,
        }

    def _parse_action(self, text: str) -> Optional[str]:
        # First line only
        first = (text or "").splitlines()[0].strip() if text else ""
        if first in {"NA", "SA", "EA", "WA", "RS"}:
            return first
        return None

    def run(self, ticks: int) -> None:
        for _ in range(ticks):
            self.step()

    def step(self) -> TickStats:
        self.tick += 1

        births = deaths = moves = absorptions = 0

        # 1) Observe + 2) Generate + 3) Parse actions (for all, before applying)
        outputs: Dict[int, Dict[str, Any]] = {}
        for idx, r in enumerate(self.ruminants):
            obs = self._build_observation(r)
            out_text, out_tokens = self.llm.generate(
                constitution=r.constitution_text,
                memory=r.memory_text,
                observation=obs,
                max_tokens=self.p["max_tokens"],
            )
            action = self._parse_action(out_text)
            outputs[idx] = {
                "obs": obs,
                "text": out_text,
                "tokens": out_tokens,
                "action": action,
            }

        # 4) Apply token cost
        token_cost = self.p["token_cost"]
        for idx, r in enumerate(self.ruminants):
            n_tok = outputs[idx]["tokens"]
            r.energy_internal -= float(n_tok) * float(token_cost)

        # 5) Apply movement + move_cost
        move_cost = self.p["move_cost"]
        for idx, r in enumerate(self.ruminants):
            a = outputs[idx]["action"]
            if a in {"NA", "SA", "EA", "WA"}:
                dx, dy = 0, 0
                if a == "NA":
                    dy = -1
                elif a == "SA":
                    dy = 1
                elif a == "EA":
                    dx = 1
                elif a == "WA":
                    dx = -1
                r.x, r.y = self.world.wrap(r.x + dx, r.y + dy)
                r.energy_internal -= float(move_cost)
                moves += 1

        # 6) Feeding (only if no movement action)
        feed_cap = self.p["feed_cap"]
        feed_eff = self.p["feed_eff"]
        for idx, r in enumerate(self.ruminants):
            a = outputs[idx]["action"]
            if a not in {"NA", "SA", "EA", "WA"}:
                taken = self.world.take_energy(r.x, r.y, feed_cap)
                r.energy_internal += float(taken) * float(feed_eff)

        # 7) Reproduction
        T = self.p["repro_threshold"]
        repro_cost = self.p["repro_cost"]
        child_e0 = self.p["child_e0"]
        new_children: List[Any] = []
        for idx, r in enumerate(self.ruminants):
            a = outputs[idx]["action"]
            if a == "RS" and r.energy_internal >= float(T):
                # cheap reproduction
                r.energy_internal -= float(repro_cost)
                child = r.clone_child(child_e0=child_e0)
                new_children.append(child)
                births += 1

        # Optional population cap
        if "P_max" in self.p and self.p["P_max"] is not None:
            cap = int(self.p["P_max"])
            room = max(0, cap - len(self.ruminants))
            new_children = new_children[:room]

        self.ruminants.extend(new_children)

        # 8) Absorption (collision)
        # Naive O(n^2) for v0.1 simplicity.
        ratio = float(self.p["absorb_ratio"])
        frac = float(self.p["absorb_frac"])
        for i in range(len(self.ruminants)):
            for j in range(i + 1, len(self.ruminants)):
                a = self.ruminants[i]
                b = self.ruminants[j]
                if a.x == b.x and a.y == b.y:
                    # decide stronger
                    if a.energy_internal >= ratio * b.energy_internal:
                        gain = frac * b.energy_internal
                        a.energy_internal += gain
                        b.energy_internal -= gain
                        absorptions += 1
                    elif b.energy_internal >= ratio * a.energy_internal:
                        gain = frac * a.energy_internal
                        b.energy_internal += gain
                        a.energy_internal -= gain
                        absorptions += 1

        # 9) Remove dead
        alive: List[Any] = []
        for r in self.ruminants:
            if r.energy_internal > 0:
                alive.append(r)
            else:
                deaths += 1
        self.ruminants = alive

        # 10) Regenerate world
        self.world.regenerate()

        # 11) Log
        mean_e = (
            sum(r.energy_internal for r in self.ruminants) / len(self.ruminants)
            if self.ruminants
            else 0.0
        )
        stats = TickStats(
            tick=self.tick,
            population=len(self.ruminants),
            births=births,
            deaths=deaths,
            moves=moves,
            absorptions=absorptions,
            mean_internal_energy=float(mean_e),
        )
        if self.logger is not None:
            self.logger.log_tick(stats)

        return stats
