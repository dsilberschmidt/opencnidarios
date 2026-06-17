"""OpenCnidarios v0.2 – simulation engine.

Non-goals: performance, parallelism, multi-biome, human interaction.

Spec references:
- docs/02_planeta_v1_specification.md
- docs/04_parameters_v1.md
"""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from .llm_adapter.base import INTERVIEW_QUESTIONS

_ACTION_TOKENS = frozenset({
    "NORTH", "SOUTH", "EAST", "WEST", "REPRODUCE",
    "EAT", "ATTACK", "PHOTOSYNTHESIZE",
})


@dataclass
class TickStats:
    tick: int
    population: int
    births: int
    deaths: int
    moves: int
    attacks: int
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
        if first in {"NORTH", "SOUTH", "EAST", "WEST", "REPRODUCE", "EAT", "ATTACK", "PHOTOSYNTHESIZE"}:
            return first
        return None

    def run(self, ticks: int) -> None:
        for _ in range(ticks):
            self.step()

    def step(self) -> TickStats:
        self.tick += 1

        births = deaths = moves = attacks = 0

        # 1) Observe + 2) Generate + 3) Parse actions (for all, before applying)
        prev_memory: Dict[int, str] = {idx: r.memory_text for idx, r in enumerate(self.ruminants)}
        outputs: Dict[int, Dict[str, Any]] = {}
        for idx, r in enumerate(self.ruminants):
            obs = self._build_observation(r)
            out_text, out_tokens = self.llm.generate(
                organism_id=r.id,
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
            # Interview clone triggers
            trigger_token = any(t in out_text.split() for t in _ACTION_TOKENS)
            trigger_memory = r.memory_text != prev_memory[idx]
            if (trigger_token or trigger_memory) and self.logger is not None:
                answers = self.llm.interview(r.id, INTERVIEW_QUESTIONS)
                state = self.llm.get_organism_state(r.id)
                self.logger.write_interview_clone(
                    tick=self.tick,
                    organism_id=r.id,
                    discovery_action="token" if trigger_token else "memory",
                    ruminant_snapshot={
                        "tick": self.tick, "x": r.x, "y": r.y,
                        "energy_internal": r.energy_internal,
                        "age": r.age, "parent_id": r.parent_id,
                        "constitution_text": r.constitution_text,
                        "memory_text": r.memory_text,
                    },
                    adapter_state=state,
                    interview_qa=[
                        {"question": q, "answer": ans}
                        for q, ans in zip(INTERVIEW_QUESTIONS, answers)
                    ],
                )

        # 4) Apply token cost
        token_cost = self.p["token_cost"]
        for idx, r in enumerate(self.ruminants):
            n_tok = outputs[idx]["tokens"]
            r.energy_internal -= float(n_tok) * float(token_cost)

        # 5) Apply movement + move_cost
        move_cost = self.p["move_cost"]
        for idx, r in enumerate(self.ruminants):
            a = outputs[idx]["action"]
            if a in {"NORTH", "SOUTH", "EAST", "WEST"}:
                dx, dy = 0, 0
                if a == "NORTH":
                    dy = -1
                elif a == "SOUTH":
                    dy = 1
                elif a == "EAST":
                    dx = 1
                elif a == "WEST":
                    dx = -1
                origin_x, origin_y = r.x, r.y
                r.x, r.y = self.world.wrap(r.x + dx, r.y + dy)
                r.energy_internal -= float(move_cost)
                moves += 1
                if self.logger is not None:
                    self.logger.log_event(
                        self.tick, "movement", r.id,
                        direction=a,
                        origin_x=origin_x, origin_y=origin_y,
                        dest_x=r.x, dest_y=r.y,
                    )

        # 6) Feeding: EAT draws from cell; PHOTOSYNTHESIZE draws from renewable source.
        #    None or any other action: no energy gain.
        #    feeding_delta is reported to the adapter (exclusive of metabolic cost).
        feed_cap = self.p["feed_cap"]
        feed_eff = self.p["feed_eff"]
        photo_energy = float(self.p.get("photo_energy", 0.0))
        for idx, r in enumerate(self.ruminants):
            a = outputs[idx]["action"]
            feeding_delta = 0.0
            if a == "EAT":
                taken = self.world.take_energy(r.x, r.y, feed_cap)
                feeding_delta = float(taken) * float(feed_eff)
                r.energy_internal += feeding_delta
            elif a == "PHOTOSYNTHESIZE":
                feeding_delta = photo_energy
                r.energy_internal += feeding_delta
            if a != "ATTACK":
                discovered = self.llm.feedback(r.id, a, feeding_delta)
                if discovered and self.logger is not None:
                    state = self.llm.get_organism_state(r.id)
                    self.logger.log_event(
                        self.tick, "discovery", r.id,
                        action=a, x=r.x, y=r.y, **state,
                    )

        # 6.5) Metabolic drain — after feeding so an organism that eats on its last tick survives.
        base_metabolic_cost = float(self.p.get("base_metabolic_cost", 0.0))
        if base_metabolic_cost > 0.0:
            for r in self.ruminants:
                r.energy_internal -= base_metabolic_cost

        # 6.6) Internal energy cap — prevents unbounded accumulation.
        e_max_internal = self.p.get("e_max_internal")
        if e_max_internal is not None:
            cap = float(e_max_internal)
            for r in self.ruminants:
                if r.energy_internal > cap:
                    r.energy_internal = cap

        # 7) Reproduction
        T = self.p["repro_threshold"]
        repro_cost = self.p["repro_cost"]
        child_e0 = self.p["child_e0"]
        cell_cap = self.p.get("cell_cap")
        cell_counts = Counter((r.x, r.y) for r in self.ruminants) if cell_cap is not None else None
        new_children: List[Any] = []
        for idx, r in enumerate(self.ruminants):
            a = outputs[idx]["action"]
            if a == "REPRODUCE" and r.energy_internal >= float(T):
                if cell_counts is not None and cell_counts[(r.x, r.y)] >= int(cell_cap):
                    continue
                r.energy_internal -= float(repro_cost)
                child = r.clone_child(child_e0=child_e0)
                self.llm.register_child(child.id, r.id)
                new_children.append(child)
                births += 1
                if self.logger is not None:
                    state = self.llm.get_organism_state(child.id)
                    self.logger.log_event(
                        self.tick, "birth", child.id,
                        parent_id=r.id, x=child.x, y=child.y, **state,
                    )

        # Optional population cap
        if "P_max" in self.p and self.p["P_max"] is not None:
            cap = int(self.p["P_max"])
            room = max(0, cap - len(self.ruminants))
            new_children = new_children[:room]

        self.ruminants.extend(new_children)

        # 8) ATTACK resolution
        attack_efficiency = float(self.p.get("attack_efficiency", 0.8))
        cell_map: Dict[Any, List[Any]] = {}
        for r in self.ruminants:
            cell_map.setdefault((r.x, r.y), []).append(r)

        killed: set = set()  # ids attacked this tick, marked for removal in step 9

        for idx in range(len(outputs)):  # only original population emitted actions
            r = self.ruminants[idx]
            if outputs[idx]["action"] != "ATTACK":
                continue
            if r.id in killed:  # attacker already dead this tick
                continue
            candidates = [
                o for o in cell_map.get((r.x, r.y), [])
                if o.id != r.id and o.id not in killed
            ]
            if not candidates:
                self.llm.feedback(r.id, "ATTACK", 0.0)  # no victim → no discovery
                continue
            victim = random.choice(candidates)
            energy_gained = attack_efficiency * victim.energy_internal
            r.energy_internal += energy_gained
            victim.energy_internal = 0.0
            killed.add(victim.id)
            attacks += 1
            discovered = self.llm.feedback(r.id, "ATTACK", energy_gained)
            if discovered and self.logger is not None:
                state = self.llm.get_organism_state(r.id)
                self.logger.log_event(
                    self.tick, "discovery", r.id,
                    action="ATTACK", x=r.x, y=r.y, **state,
                )
            if self.logger is not None:
                self.logger.log_event(
                    self.tick, "attack", r.id,
                    victim_id=victim.id,
                    energy_gained=energy_gained,
                    x=r.x, y=r.y,
                )

        # 8.5) Re-apply internal energy cap after ATTACK
        if e_max_internal is not None:
            cap = float(e_max_internal)
            for r in self.ruminants:
                if r.energy_internal > cap:
                    r.energy_internal = cap

        # 9) Remove dead
        alive: List[Any] = []
        for r in self.ruminants:
            if r.energy_internal > 0:
                alive.append(r)
            else:
                deaths += 1
                if self.logger is not None:
                    state = self.llm.get_organism_state(r.id)
                    cause = "attacked" if r.id in killed else "starvation"
                    self.logger.log_event(
                        self.tick, "death", r.id,
                        cause=cause, age=r.age, x=r.x, y=r.y, **state,
                    )
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
            attacks=attacks,
            mean_internal_energy=float(mean_e),
        )
        if self.logger is not None:
            self.logger.log_tick(stats)

        return stats
