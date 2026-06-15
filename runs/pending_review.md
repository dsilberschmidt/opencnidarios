# Fix: engine — ATTACK parsing and step 8 index bounds; enable event_logging in v05_attack

Branch: experiment/v02-two-energy-sources
Fecha: 2026-06-15

## git log --oneline -3

```
c34144b fix: engine — ATTACK parsing and step 8 index bounds; enable event_logging in v05_attack
2f507e7 docs: pending_review.md — log y diff del commit ATTACK
2bee255 feat: engine — implement ATTACK action, remove passive absorption (step 8)
```

## git diff HEAD~1 HEAD

```diff
diff --git a/runs/configs/v05_attack.json b/runs/configs/v05_attack.json
index c235630..ffcb70f 100644
--- a/runs/configs/v05_attack.json
+++ b/runs/configs/v05_attack.json
@@ -13,6 +13,7 @@
     "type": "dummy",
     "p_action": 0.5
   },
+  "event_logging": true,
   "world_energy_lo": 5,
   "world_energy_hi": 20,
   "params": {
diff --git a/src/engine.py b/src/engine.py
index 468c4db..0c0e29b 100644
--- a/src/engine.py
+++ b/src/engine.py
@@ -57,7 +57,7 @@ class Engine:
     def _parse_action(self, text: str) -> Optional[str]:
         # First line only
         first = (text or "").splitlines()[0].strip() if text else ""
-        if first in {"NA", "SA", "EA", "WA", "RS", "EAT", "PHOTOSYNTHESIZE"}:
+        if first in {"NA", "SA", "EA", "WA", "RS", "EAT", "ATTACK", "PHOTOSYNTHESIZE"}:
             return first
         return None
 
@@ -200,7 +200,8 @@ class Engine:
 
         killed: set = set()  # ids attacked this tick, marked for removal in step 9
 
-        for idx, r in enumerate(self.ruminants):
+        for idx in range(len(outputs)):  # only original population emitted actions
+            r = self.ruminants[idx]
             if outputs[idx]["action"] != "ATTACK":
                 continue
             if r.id in killed:  # attacker already dead this tick
```

---

## Contexto de los bugs

**Bug 1 — ATTACK nunca parseado** (`src/engine.py:60`):
`_parse_action()` tenía un set cerrado que omitía "ATTACK". El DummyAdapter emitía
el token, pero el parser lo descartaba como `None`; step 8 nunca lo veía.
Consecuencia: en la primera corrida de v05 (bug activo) — 0 eventos "attack",
0 muertes por depredación, población llegó a P_max=1000 sin presión depredadora.

**Bug 2 — KeyError en step 8** (`src/engine.py:203`):
Step 7 (reproducción) agrega hijos a `self.ruminants` antes de step 8.
`enumerate(self.ruminants)` generaba índices más allá del rango de `outputs`
(que solo tiene entradas para la población original del tick). Fix: iterar
`range(len(outputs))` explícitamente.

**event_logging faltante** (`runs/configs/v05_attack.json`):
El campo no estaba en el config; se agregó antes de la corrida válida.

---

## Resultados de la corrida válida (post-fix)

| tick  | población | energía media |
|-------|-----------|---------------|
|     1 |        20 |         26.65 |
|  1000 |       120 |         85.12 |
|  5000 |       250 |         96.24 |
| 10000 |       244 |         97.08 |

| evento     | count |
|------------|-------|
| attack     | 5.493 |
| birth      | 5.724 |
| death      | 5.500 |
| discovery  |   475 |
| movement   | 4.985 |

| causa      | count | %     |
|------------|-------|-------|
| attacked   | 5.493 | 99.9% |
| starvation |     7 |  0.1% |
