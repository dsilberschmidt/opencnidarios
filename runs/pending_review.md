# git diff main...experiment/v02-two-energy-sources --stat

Fecha: 2026-06-15

```
 .gitignore                                         |     2 +
 CONTEXT.md                                         |   274 +-
 VISION.md                                          |    76 +-
 run.py                                             |     4 +-
 runs/2026-06-13_p_action_0.5_10000ticks/NOTES.md   |    57 +
 .../ticks_2026-06-12_v02_two_energy_sources.csv    | 10001 +++++++++++++++++++
 runs/2026-06-13_regen_rate_0/NOTES.md              |    67 +
 .../ticks_2026-06-12_v02_two_energy_sources.csv    | 10001 +++++++++++++++++++
 runs/2026-06-13_v04b_long_run/NOTES.md             |    45 +
 runs/2026-06-13_v04c_logged/NOTES.md               |    40 +
 .../events_2026-06-13_v04c_logged.jsonl            |  8442 ++++++++++++++++
 .../ticks_2026-06-13_v04c_logged.csv               | 10001 +++++++++++++++++++
 runs/2026-06-15_v05_attack/NOTES.md                |    91 +
 runs/SESSION_START.md                              |     9 +
 runs/configs/v02_two_energy_sources.json           |    38 +
 runs/configs/v03_spatial_pressure.json             |    39 +
 runs/configs/v04_small_grid_no_regen.json          |    38 +
 runs/configs/v04b_long_run.json                    |    38 +
 runs/configs/v04c_logged.json                      |    39 +
 runs/configs/v05_attack.json                       |    38 +
 runs/pending_review.md                             |    10 +
 .../events_2026-06-13_tmp_validation.jsonl         |   165 +
 .../ticks_2026-06-13_tmp_validation.csv            |   501 +
 src/engine.py                                      |   151 +-
 src/llm_adapter/base.py                            |    32 +-
 src/llm_adapter/dummy.py                           |   108 +-
 src/logger.py                                      |    33 +-
 src/viewer/viewer.html                             |   592 ++
 src/world.py                                       |    17 +-
 29 files changed, 40851 insertions(+), 98 deletions(-)
```

## Nota

El volumen de líneas (+40851) se explica principalmente por tres archivos de datos
de corridas ya commiteados (dos ticks_*.csv de 10001 líneas c/u, más el ticks del
v04c_logged). El código fuente neto es mucho más acotado:

| archivo fuente | delta |
|---|---|
| src/engine.py | +151/-? |
| src/llm_adapter/dummy.py | +108/-? |
| src/llm_adapter/base.py | +32/-? |
| src/logger.py | +33/-? |
| src/viewer/viewer.html | +592 (nuevo) |
| src/world.py | +17/-? |
| run.py | +4/-? |
