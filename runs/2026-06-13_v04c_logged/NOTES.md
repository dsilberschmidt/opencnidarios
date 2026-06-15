# v04c_logged

Config: `runs/configs/v04c_logged.json`
Branch: `experiment/v02-two-energy-sources`
Fecha: 2026-06-13

## Propósito

Primer run largo (10.000 ticks) con el event logger activo. Produce el JSONL
de eventos necesario para la visualización completa en `src/viewer/viewer.html`.

Idéntico a v04_small_grid_no_regen en todos sus parámetros — el único cambio
es `event_logging: true`. Permite comparar directamente con el run v04 (mismo
seed, mismos parámetros) y confirmar que el logger no altera la dinámica.

## Parámetros clave

- N=32, regen_rate=0, repro_cost=4, e_max_internal=100, P_max=1000
- seed=42, ticks=10000, p_action=0.5
- event_logging=true → genera events_2026-06-13_v04c_logged.jsonl

## Resultados

| archivo                              | tamaño |
|--------------------------------------|--------|
| events_2026-06-13_v04c_logged.jsonl  | 2.3 MB |
| ticks_2026-06-13_v04c_logged.csv     | 352 KB |

Conteo de eventos:

| evento     | cantidad |
|------------|----------|
| birth      |    3.027 |
| death      |    2.803 |
| discovery  |        9 |
| movement   |    2.603 |
| **TOTAL**  |  **8.442** |

9 eventos de discovery — consistente con la corrida de validación (también 9 en 500 ticks
con el mismo seed). Confirmación de que el logger no altera la dinámica del simulador.
