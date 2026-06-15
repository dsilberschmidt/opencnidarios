# Commit: feat: engine — implement ATTACK action, remove passive absorption

Branch: experiment/v02-two-energy-sources
Fecha: 2026-06-15

## git log --oneline -3

```
2bee255 feat: engine — implement ATTACK action, remove passive absorption (step 8)
83d4e86 docs: VISION.md — nota de diseño: apertura del espacio de acción para LLMs reales
8ef8a45 docs: VISION.md — add future experiments section (LLMs reales)
```

## git diff HEAD~1 HEAD

```diff
diff --git a/runs/configs/v05_attack.json b/runs/configs/v05_attack.json
new file mode 100644
index 0000000..c235630
--- /dev/null
+++ b/runs/configs/v05_attack.json
@@ -0,0 +1,37 @@
+{
+  "meta": {
+    "name": "v05_attack",
+    "description": "First run with deliberate ATTACK action. Passive collision absorption removed. attack_efficiency=0.8. Based on v04b_long_run params; 10k ticks smoke test.",
+    "date": "2026-06-15"
+  },
+  "seed": 42,
+  "ticks": 10000,
+  "out_dir": "runs/2026-06-15_v05_attack",
+  "constitution": "You are a ruminant. Survive.",
+  "memory": "",
+  "adapter": {
+    "type": "dummy",
+    "p_action": 0.5
+  },
+  "world_energy_lo": 5,
+  "world_energy_hi": 20,
+  "params": {
+    "N": 32,
+    "e_max_internal": 100,
+    "regen_rate": 0,
+    "P0": 20,
+    "e_i0": 25,
+    "max_tokens": 50,
+    "token_cost": 0.05,
+    "move_cost": 0.5,
+    "feed_cap": 6,
+    "feed_eff": 1.0,
+    "base_metabolic_cost": 0.4,
+    "photo_energy": 4.0,
+    "attack_efficiency": 0.8,
+    "repro_threshold": 60,
+    "repro_cost": 4,
+    "child_e0": 10,
+    "P_max": 1000
+  }
+}
diff --git a/src/engine.py b/src/engine.py
index 7a0a028..468c4db 100644
--- a/src/engine.py
+++ b/src/engine.py
@@ -9,6 +9,7 @@ Spec references:
 
 from __future__ import annotations
 
+import random
 from collections import Counter
 from dataclasses import dataclass
 from typing import List, Dict, Any, Optional
@@ -21,7 +22,7 @@ class TickStats:
     births: int
     deaths: int
     moves: int
-    absorptions: int
+    attacks: int
     mean_internal_energy: float
 
 
@@ -67,7 +68,7 @@ class Engine:
     def step(self) -> TickStats:
         self.tick += 1
 
-        births = deaths = moves = absorptions = 0
+        births = deaths = moves = attacks = 0
 
         # 1) Observe + 2) Generate + 3) Parse actions (for all, before applying)
         outputs: Dict[int, Dict[str, Any]] = {}
@@ -136,13 +137,14 @@ class Engine:
             elif a == "PHOTOSYNTHESIZE":
                 feeding_delta = photo_energy
                 r.energy_internal += feeding_delta
-            discovered = self.llm.feedback(r.id, a, feeding_delta)
-            if discovered and self.logger is not None:
-                state = self.llm.get_organism_state(r.id)
-                self.logger.log_event(
-                    self.tick, "discovery", r.id,
-                    action=a, x=r.x, y=r.y, **state,
-                )
+            if a != "ATTACK":
+                discovered = self.llm.feedback(r.id, a, feeding_delta)
+                if discovered and self.logger is not None:
+                    state = self.llm.get_organism_state(r.id)
+                    self.logger.log_event(
+                        self.tick, "discovery", r.id,
+                        action=a, x=r.x, y=r.y, **state,
+                    )
 
         # 6.5) Metabolic drain — after feeding so an organism that eats on its last tick survives.
         base_metabolic_cost = float(self.p.get("base_metabolic_cost", 0.0))
@@ -190,26 +192,53 @@ class Engine:
 
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
+        for idx, r in enumerate(self.ruminants):
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
@@ -220,9 +249,10 @@ class Engine:
                 deaths += 1
                 if self.logger is not None:
                     state = self.llm.get_organism_state(r.id)
+                    cause = "attacked" if r.id in killed else "starvation"
                     self.logger.log_event(
                         self.tick, "death", r.id,
-                        age=r.age, x=r.x, y=r.y, **state,
+                        cause=cause, age=r.age, x=r.x, y=r.y, **state,
                     )
         self.ruminants = alive
 
@@ -241,7 +271,7 @@ class Engine:
             births=births,
             deaths=deaths,
             moves=moves,
-            absorptions=absorptions,
+            attacks=attacks,
             mean_internal_energy=float(mean_e),
         )
         if self.logger is not None:
```
