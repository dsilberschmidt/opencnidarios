# git diff main...experiment/v02-two-energy-sources -- src/ run.py

Fecha: 2026-06-15

```diff
diff --git a/run.py b/run.py
index 8042fce..d7d915b 100644
--- a/run.py
+++ b/run.py
@@ -29,7 +29,7 @@ def main():
     seed = cfg["seed"]
     random.seed(seed)
 
-    world = World(n=params["N"], e_max=params["E_max"], regen_rate=params["regen_rate"])
+    world = World(n=params["N"], e_max=params.get("E_max", cfg["world_energy_hi"]), regen_rate=params["regen_rate"], cell_energy_hi=cfg["world_energy_hi"])
     world.seed_energy_uniform(cfg["world_energy_lo"], cfg["world_energy_hi"], seed=seed)
 
     adapter_cfg = cfg["adapter"]
@@ -37,7 +37,7 @@ def main():
     llm = DummyAdapter(p_action=adapter_cfg["p_action"], seed=seed)
 
     run_id = f"{cfg['meta']['date']}_{cfg['meta']['name']}"
-    logger = Logger(out_dir=cfg["out_dir"], run_id=run_id)
+    logger = Logger(out_dir=cfg["out_dir"], run_id=run_id, event_logging=cfg.get("event_logging", False))
 
     engine = Engine(world=world, llm_adapter=llm, params=params, logger=logger)
 
diff --git a/src/engine.py b/src/engine.py
index 5ef180a..0c0e29b 100644
--- a/src/engine.py
+++ b/src/engine.py
@@ -1,11 +1,6 @@
-"""OpenCnidarios v0.1 – minimal simulation engine (scaffold).
+"""OpenCnidarios v0.2 – simulation engine.
 
 Non-goals: performance, parallelism, multi-biome, human interaction.
-This file is a runnable skeleton to be completed alongside:
-- world.py
-- ruminant.py
-- llm_adapter/*
-- logging/*
 
 Spec references:
 - docs/02_planeta_v1_specification.md
@@ -14,6 +9,8 @@ Spec references:
 
 from __future__ import annotations
 
+import random
+from collections import Counter
 from dataclasses import dataclass
 from typing import List, Dict, Any, Optional
 
@@ -25,7 +22,7 @@ class TickStats:
     births: int
     deaths: int
     moves: int
-    absorptions: int
+    attacks: int
     mean_internal_energy: float
 
 
@@ -60,7 +57,7 @@ class Engine:
     def _parse_action(self, text: str) -> Optional[str]:
         # First line only
         first = (text or "").splitlines()[0].strip() if text else ""
-        if first in {"NA", "SA", "EA", "WA", "RS"}:
+        if first in {"NA", "SA", "EA", "WA", "RS", "EAT", "ATTACK", "PHOTOSYNTHESIZE"}:
             return first
         return None
 
@@ -71,13 +68,14 @@ class Engine:
     def step(self) -> TickStats:
         self.tick += 1
 
-        births = deaths = moves = absorptions = 0
+        births = deaths = moves = attacks = 0
 
         # 1) Observe + 2) Generate + 3) Parse actions (for all, before applying)
         outputs: Dict[int, Dict[str, Any]] = {}
         for idx, r in enumerate(self.ruminants):
             obs = self._build_observation(r)
             out_text, out_tokens = self.llm.generate(
+                organism_id=r.id,
                 constitution=r.constitution_text,
                 memory=r.memory_text,
                 observation=obs,
@@ -93,11 +91,9 @@ class Engine:
 
         # 4) Apply token cost
         token_cost = self.p["token_cost"]
-        base_metabolic_cost = self.p.get("base_metabolic_cost", 0)
         for idx, r in enumerate(self.ruminants):
             n_tok = outputs[idx]["tokens"]
             r.energy_internal -= float(n_tok) * float(token_cost)
-            r.energy_internal -= float(base_metabolic_cost)
 
         # 5) Apply movement + move_cost
         move_cost = self.p["move_cost"]
@@ -113,32 +109,80 @@ class Engine:
                 elif a == "WA":
                     dx = -1
+                origin_x, origin_y = r.x, r.y
                 r.x, r.y = self.world.wrap(r.x + dx, r.y + dy)
                 r.energy_internal -= float(move_cost)
                 moves += 1
+                if self.logger is not None:
+                    self.logger.log_event(
+                        self.tick, "movement", r.id,
+                        direction=a,
+                        origin_x=origin_x, origin_y=origin_y,
+                        dest_x=r.x, dest_y=r.y,
+                    )
 
-        # 6) Feeding (only if no movement action)
+        # 6) Feeding: EAT draws from cell; PHOTOSYNTHESIZE draws from renewable source.
+        #    None or any other action: no energy gain.
+        #    feeding_delta is reported to the adapter (exclusive of metabolic cost).
         feed_cap = self.p["feed_cap"]
         feed_eff = self.p["feed_eff"]
+        photo_energy = float(self.p.get("photo_energy", 0.0))
         for idx, r in enumerate(self.ruminants):
             a = outputs[idx]["action"]
-            if a not in {"NA", "SA", "EA", "WA"}:
+            feeding_delta = 0.0
+            if a == "EAT":
                 taken = self.world.take_energy(r.x, r.y, feed_cap)
-                r.energy_internal += float(taken) * float(feed_eff)
+                feeding_delta = float(taken) * float(feed_eff)
+                r.energy_internal += feeding_delta
+            elif a == "PHOTOSYNTHESIZE":
+                feeding_delta = photo_energy
+                r.energy_internal += feeding_delta
+            if a != "ATTACK":
+                discovered = self.llm.feedback(r.id, a, feeding_delta)
+                if discovered and self.logger is not None:
+                    state = self.llm.get_organism_state(r.id)
+                    self.logger.log_event(
+                        self.tick, "discovery", r.id,
+                        action=a, x=r.x, y=r.y, **state,
+                    )
+
+        # 6.5) Metabolic drain — after feeding so an organism that eats on its last tick survives.
+        base_metabolic_cost = float(self.p.get("base_metabolic_cost", 0.0))
+        if base_metabolic_cost > 0.0:
+            for r in self.ruminants:
+                r.energy_internal -= base_metabolic_cost
+
+        # 6.6) Internal energy cap — prevents unbounded accumulation.
+        e_max_internal = self.p.get("e_max_internal")
+        if e_max_internal is not None:
+            cap = float(e_max_internal)
+            for r in self.ruminants:
+                if r.energy_internal > cap:
+                    r.energy_internal = cap
 
         # 7) Reproduction
         T = self.p["repro_threshold"]
         repro_cost = self.p["repro_cost"]
         child_e0 = self.p["child_e0"]
+        cell_cap = self.p.get("cell_cap")
+        cell_counts = Counter((r.x, r.y) for r in self.ruminants) if cell_cap is not None else None
         new_children: List[Any] = []
         for idx, r in enumerate(self.ruminants):
             a = outputs[idx]["action"]
             if a == "RS" and r.energy_internal >= float(T):
-                # cheap reproduction
+                if cell_counts is not None and cell_counts[(r.x, r.y)] >= int(cell_cap):
+                    continue
                 r.energy_internal -= float(repro_cost)
                 child = r.clone_child(child_e0=child_e0)
+                self.llm.register_child(child.id, r.id)
                 new_children.append(child)
                 births += 1
+                if self.logger is not None:
+                    state = self.llm.get_organism_state(child.id)
+                    self.logger.log_event(
+                        self.tick, "birth", child.id,
+                        parent_id=r.id, x=child.x, y=child.y, **state,
+                    )
 
         # Optional population cap
         if "P_max" in self.p and self.p["P_max"] is not None:
@@ -148,26 +192,54 @@ class Engine:
 
         self.ruminants.extend(new_children)
 
-        # 8) Absorption (collision)
-        # Naive O(n^2) for v0.1 simplicity.
-        ratio = float(self.p["absorb_ratio"])
-        frac = float(self.p["absorb_frac"])
-        for i in range(len(self.ruminants)):
-            for j in range(i + 1, len(self.ruminants)):
-                a = self.ruminants[i]
-                b = self.ruminants[j]
-                if a.x == b.x and a.y == b.y:
-                    # decide stronger
-                    if a.energy_internal >= ratio * b.energy_internal:
-                        gain = frac * b.energy_internal
-                        a.energy_internal += gain
-                        b.energy_internal -= gain
-                        absorptions += 1
-                    elif b.energy_internal >= ratio * a.energy_internal:
-                        gain = frac * a.energy_internal
-                        b.energy_internal += gain
-                        a.energy_internal -= gain
-                        absorptions += 1
+        # 8) ATTACK resolution
+        attack_efficiency = float(self.p.get("attack_efficiency", 0.8))
+        cell_map: Dict[Any, List[Any]] = {}
+        for r in self.ruminants:
+            cell_map.setdefault((r.x, r.y), []).append(r)
+
+        killed: set = set()  # ids attacked this tick, marked for removal in step 9
+
+        for idx in range(len(outputs)):  # only original population emitted actions
+            r = self.ruminants[idx]
+            if outputs[idx]["action"] != "ATTACK":
+                continue
+            if r.id in killed:  # attacker already dead this tick
+                continue
+            candidates = [
+                o for o in cell_map.get((r.x, r.y), [])
+                if o.id != r.id and o.id not in killed
+            ]
+            if not candidates:
+                self.llm.feedback(r.id, "ATTACK", 0.0)  # no victim → no discovery
+                continue
+            victim = random.choice(candidates)
+            energy_gained = attack_efficiency * victim.energy_internal
+            r.energy_internal += energy_gained
+            victim.energy_internal = 0.0
+            killed.add(victim.id)
+            attacks += 1
+            discovered = self.llm.feedback(r.id, "ATTACK", energy_gained)
+            if discovered and self.logger is not None:
+                state = self.llm.get_organism_state(r.id)
+                self.logger.log_event(
+                    self.tick, "discovery", r.id,
+                    action="ATTACK", x=r.x, y=r.y, **state,
+                )
+            if self.logger is not None:
+                self.logger.log_event(
+                    self.tick, "attack", r.id,
+                    victim_id=victim.id,
+                    energy_gained=energy_gained,
+                    x=r.x, y=r.y,
+                )
+
+        # 8.5) Re-apply internal energy cap after ATTACK
+        if e_max_internal is not None:
+            cap = float(e_max_internal)
+            for r in self.ruminants:
+                if r.energy_internal > cap:
+                    r.energy_internal = cap
 
         # 9) Remove dead
         alive: List[Any] = []
@@ -176,6 +248,13 @@ class Engine:
                 alive.append(r)
             else:
                 deaths += 1
+                if self.logger is not None:
+                    state = self.llm.get_organism_state(r.id)
+                    cause = "attacked" if r.id in killed else "starvation"
+                    self.logger.log_event(
+                        self.tick, "death", r.id,
+                        cause=cause, age=r.age, x=r.x, y=r.y, **state,
+                    )
         self.ruminants = alive
 
         # 10) Regenerate world
@@ -193,7 +272,7 @@ class Engine:
             births=births,
             deaths=deaths,
             moves=moves,
-            absorptions=absorptions,
+            attacks=attacks,
             mean_internal_energy=float(mean_e),
         )
         if self.logger is not None:
diff --git a/src/llm_adapter/base.py b/src/llm_adapter/base.py
index 5d8a69e..a4accdb 100644
--- a/src/llm_adapter/base.py
+++ b/src/llm_adapter/base.py
@@ -1,11 +1,13 @@
 """LLM adapter interface for OpenCnidarios.
 
-The engine calls a single method per ruminant per tick.
-This adapter abstracts away local vs API models.
+The engine calls generate() once per ruminant per tick, then feedback() after
+the energy outcome of that action is resolved.
 
 Contract:
-- Input: constitution, memory, observation, max_tokens
-- Output: (text, token_count)
+- generate: Input: organism_id, constitution, memory, observation, max_tokens
+             Output: (text, token_count)
+- feedback: Input: organism_id, action taken (or None), energy_delta from feeding only
+             Output: None (side-effect on adapter internal state)
 
 The adapter must enforce max token generation.
 """
@@ -13,13 +15,14 @@ The adapter must enforce max token generation.
 from __future__ import annotations
 
 from abc import ABC, abstractmethod
-from typing import Dict, Any, Tuple
+from typing import Dict, Any, Optional, Tuple
 
 
 class LLMAdapter(ABC):
     @abstractmethod
     def generate(
         self,
+        organism_id: str,
         constitution: str,
         memory: str,
         observation: Dict[str, Any],
@@ -27,3 +30,22 @@ class LLMAdapter(ABC):
     ) -> Tuple[str, int]:
         """Return (output_text, tokens_generated)."""
         raise NotImplementedError
+
+    @abstractmethod
+    def feedback(
+        self,
+        organism_id: str,
+        action: Optional[str],
+        energy_delta: float,
+    ) -> bool:
+        """Reinforce action based on feeding energy delta. delta > 0 = gain.
+        Returns True if a discovery jump fired this call."""
+        raise NotImplementedError
+
+    def register_child(self, child_id: str, parent_id: str) -> None:
+        """Hook for weight inheritance at birth. No-op by default."""
+
+    def get_organism_state(self, organism_id: str) -> dict:
+        """Return current adapter state for an organism (weights, discovered, etc.).
+        Used for event logging. Returns empty dict for adapters without per-organism state."""
+        return {}
diff --git a/src/llm_adapter/dummy.py b/src/llm_adapter/dummy.py
index fff2674..2d33445 100644
--- a/src/llm_adapter/dummy.py
+++ b/src/llm_adapter/dummy.py
@@ -1,42 +1,118 @@
-"""Dummy LLM adapter for OpenCnidarios v0.1.
+"""Dummy LLM adapter for OpenCnidarios v0.2.
 
 Purpose:
 - Enable running the simulation without any external model.
-- Provide controlled randomness to test movement/reproduction discovery.
+- Provide controlled randomness to test action discovery mechanics.
 
-This adapter sometimes emits hidden action tokens with low probability.
+Single action pool sampled with per-organism weights:
+- p_action: probability of emitting any action this tick.
+- Action chosen via random.choices() using per-organism weight vector.
+
+Initial weights are non-uniform (EAT biased high, RS medium, rest low).
+PHOTOSYNTHESIZE and ATTACK are in the pool but start with low weight —
+must be discovered through feedback to become dominant strategies.
+
+Per-organism weights updated by feedback() via positive reinforcement.
+First successful use of an action triggers an irreversible discovery jump.
+New organisms inherit parent weights and discovery state (Lamarckian).
 """
 
 from __future__ import annotations
 
 import random
-from typing import Dict, Any, Tuple
+from typing import Dict, Any, Optional, Set, Tuple
 
 from .base import LLMAdapter
 
+_NORMAL_ACTIONS = ["NA", "SA", "EA", "WA", "RS", "EAT", "ATTACK", "PHOTOSYNTHESIZE"]
+_INITIAL_WEIGHTS = [1.0,  1.0,  1.0,  1.0,  5.0, 100.0,    1.0,           1.0]
+
+# First successful use of these actions triggers a one-time weight jump.
+# EAT and RS are excluded: EAT starts high; RS gradual reinforcement is sufficient.
+_DISCOVERY_JUMP: Dict[str, float] = {
+    "PHOTOSYNTHESIZE": 100.0,
+    "ATTACK":           30.0,
+    "NA":               30.0,
+    "SA":               30.0,
+    "EA":               30.0,
+    "WA":               30.0,
+}
+
 
 class DummyAdapter(LLMAdapter):
-    def __init__(self, p_action: float = 0.02, seed: int | None = None):
+    def __init__(
+        self,
+        p_action: float = 0.05,
+        learning_rate: float = 0.1,
+        seed: int | None = None,
+    ):
         self.p_action = float(p_action)
+        self.learning_rate = float(learning_rate)
+        self._weights: Dict[str, list[float]] = {}
+        self._discovered: Dict[str, Set[str]] = {}
         if seed is not None:
             random.seed(seed)
 
+    def _get_weights(self, organism_id: str) -> list[float]:
+        if organism_id not in self._weights:
+            self._weights[organism_id] = list(_INITIAL_WEIGHTS)
+        return self._weights[organism_id]
+
+    def _get_discovered(self, organism_id: str) -> Set[str]:
+        if organism_id not in self._discovered:
+            self._discovered[organism_id] = set()
+        return self._discovered[organism_id]
+
+    def register_child(self, child_id: str, parent_id: str) -> None:
+        parent_weights = self._weights.get(parent_id)
+        if parent_weights is not None:
+            self._weights[child_id] = list(parent_weights)
+        parent_disc = self._discovered.get(parent_id)
+        if parent_disc is not None:
+            self._discovered[child_id] = set(parent_disc)
+
     def generate(
         self,
+        organism_id: str,
         constitution: str,
         memory: str,
         observation: Dict[str, Any],
         max_tokens: int,
     ) -> Tuple[str, int]:
-        # Occasionally emit a valid hidden token.
         if random.random() < self.p_action:
-            token = random.choice(["NA", "SA", "EA", "WA", "RS"])
-            text = token
-            tokens = 1
-            return text, tokens
-
-        # Default: produce a short, neutral line.
-        # Keep token count small and bounded.
-        text = "..."
-        tokens = 1
-        return text, tokens
+            weights = self._get_weights(organism_id)
+            action = random.choices(_NORMAL_ACTIONS, weights=weights, k=1)[0]
+            return action, 1
+
+        return "...", 1
+
+    def feedback(
+        self,
+        organism_id: str,
+        action: Optional[str],
+        energy_delta: float,
+    ) -> bool:
+        if action not in _NORMAL_ACTIONS or energy_delta <= 0.0:
+            return False
+        weights = self._get_weights(organism_id)
+        idx = _NORMAL_ACTIONS.index(action)
+        discovered = self._get_discovered(organism_id)
+
+        jumped = False
+        # Discovery jump: irreversible, fires once per action per organism.
+        if action in _DISCOVERY_JUMP and action not in discovered:
+            weights[idx] = max(weights[idx], _DISCOVERY_JUMP[action])
+            discovered.add(action)
+            jumped = True
+
+        # Gradual reinforcement always applies after the jump.
+        weights[idx] += self.learning_rate * energy_delta
+        return jumped
+
+    def get_organism_state(self, organism_id: str) -> dict:
+        weights = self._weights.get(organism_id, list(_INITIAL_WEIGHTS))
+        discovered = list(self._get_discovered(organism_id))
+        return {
+            "weights": dict(zip(_NORMAL_ACTIONS, weights)),
+            "discovered": discovered,
+        }
diff --git a/src/logger.py b/src/logger.py
index ded2653..84152df 100644
--- a/src/logger.py
+++ b/src/logger.py
@@ -2,7 +2,7 @@
 
 Writes:
 - per-tick aggregates to CSV
-- optional event stream to JSONL (placeholder)
+- optional event stream to JSONL (birth, death, discovery, movement)
 
 This is intentionally minimal.
 """
@@ -11,12 +11,18 @@ from __future__ import annotations
 
 from dataclasses import asdict
 import csv
+import json
 from pathlib import Path
-from typing import Optional
+from typing import Any
 
 
 class Logger:
-    def __init__(self, out_dir: str = "runs/latest", run_id: str | None = None):
+    def __init__(
+        self,
+        out_dir: str = "runs/latest",
+        run_id: str | None = None,
+        event_logging: bool = False,
+    ):
         self.out_dir = Path(out_dir)
         self.out_dir.mkdir(parents=True, exist_ok=True)
 
@@ -25,6 +31,11 @@ class Logger:
         self._csv_file = self.csv_path.open("w", newline="", encoding="utf-8")
         self._csv = None
 
+        self._jsonl_file = None
+        if event_logging:
+            ev_filename = f"events_{run_id}.jsonl" if run_id else "events.jsonl"
+            self._jsonl_file = (self.out_dir / ev_filename).open("w", encoding="utf-8")
+
     def log_tick(self, tick_stats) -> None:
         row = asdict(tick_stats)
         if self._csv is None:
@@ -33,6 +44,22 @@ class Logger:
         self._csv.writerow(row)
         self._csv_file.flush()
 
+    def log_event(
+        self,
+        tick: int,
+        event_type: str,
+        organism_id: str,
+        **payload: Any,
+    ) -> None:
+        if self._jsonl_file is None:
+            return
+        record = {"tick": tick, "event": event_type, "organism_id": organism_id}
+        record.update(payload)
+        self._jsonl_file.write(json.dumps(record) + "\n")
+        self._jsonl_file.flush()
+
     def close(self) -> None:
         if self._csv_file:
             self._csv_file.close()
+        if self._jsonl_file:
+            self._jsonl_file.close()
diff --git a/src/viewer/viewer.html b/src/viewer/viewer.html
new file mode 100644
index 0000000..399c4f6
--- /dev/null
+++ b/src/viewer/viewer.html
@@ -0,0 +1,592 @@
+<!DOCTYPE html>
[592 líneas — archivo nuevo completo, viewer HTML/JS interactivo]
diff --git a/src/world.py b/src/world.py
index 991b9ae..a38ced5 100644
--- a/src/world.py
+++ b/src/world.py
@@ -1,4 +1,4 @@
-"""OpenCnidarios v0.1 – world model (toroidal grid + energy).
+"""OpenCnidarios v0.2 – world model (toroidal grid + energy).
@@ -17,8 +17,13 @@ class World:
     n: int
     e_max: float
     regen_rate: float
+    cell_energy_hi: Optional[float] = field(default=None)
 
     def __post_init__(self) -> None:
+        if self.cell_energy_hi is None:
+            self.cell_energy_hi = self.e_max
         self.energy = [[0.0 for _ in range(self.n)] for _ in range(self.n)]
 
@@ -46,11 +51,11 @@ class World:
     def regenerate(self) -> None:
-        """Regenerate energy for all cells."""
+        """Regenerate energy for all cells, clamped to cell_energy_hi."""
         r = float(self.regen_rate)
-        emax = float(self.e_max)
+        cap = float(self.cell_energy_hi)
         for y in range(self.n):
             row = self.energy[y]
             for x in range(self.n):
                 v = float(row[x]) + r
-                row[x] = v if v < emax else emax
+                row[x] = v if v < cap else cap
```
