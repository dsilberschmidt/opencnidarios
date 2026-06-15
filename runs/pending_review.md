# Pre-PR checklist — experiment/v02-two-energy-sources

Fecha: 2026-06-15

---

## git status

```
On branch experiment/v02-two-energy-sources
Your branch is ahead of 'origin/experiment/v02-two-energy-sources' by 10 commits.

Untracked files (no commiteados, no bloqueantes):
  runs/2026-06-13_v04b_long_run/ticks_2026-06-13_v04b_long_run.csv
  runs/2026-06-15_v05_attack/events_2026-06-15_v05_attack.jsonl
  runs/2026-06-15_v05_attack/ticks_2026-06-15_v05_attack.csv

nothing added to commit but untracked files present
```

## git log main..experiment/v02-two-energy-sources --oneline

```
c2dbc2c docs: pending_review.md — log y stat del commit CONTEXT.md
e29185c docs: CONTEXT.md — ATTACK completado, v05_attack results, próximos pasos LLM real
1c854b4 docs: pending_review.md — log y stat del commit NOTES.md
2220e19 docs: v05_attack/NOTES.md — propósito, bugs corregidos y resultados del run
2529aa2 docs: pending_review.md — confirmación fix commiteado
f765230 docs: pending_review.md — actualizar log post-fix
c34144b fix: engine — ATTACK parsing and step 8 index bounds; enable event_logging in v05_attack
2f507e7 docs: pending_review.md — log y diff del commit ATTACK
2bee255 feat: engine — implement ATTACK action, remove passive absorption (step 8)
83d4e86 docs: VISION.md — nota de diseño: apertura del espacio de acción para LLMs reales
```

10 commits por encima de main, todos los de esta sesión.

---

## Diagnóstico

**Cambios sin commitear:** ninguno. Working tree limpio (solo archivos untracked de
datos de corridas — CSV y JSONL — que no forman parte del código).

**Branch pusheada:** NO. La branch está 10 commits por delante de
`origin/experiment/v02-two-energy-sources`. Hay que hacer `git push` antes del PR.

**Archivos untracked:** los tres CSV/JSONL de datos de corrida no están en `.gitignore`
pero tampoco commiteados. Decidir antes del PR si se incluyen o se agregan a `.gitignore`.
Los NOTES.md de cada corrida sí están commiteados y son suficientes como registro.

---

## Acción requerida antes del PR

1. `git push` para subir los 10 commits a origin.
2. Decidir qué hacer con los archivos untracked de datos (ignorar o commitear).
3. Crear el PR a main.
