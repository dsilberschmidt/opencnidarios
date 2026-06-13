# Confirmación: CONTEXT.md actualizado y pusheado

Commit: e92774e
Branch: experiment/v02-two-energy-sources
Fecha: 2026-06-13

## Qué se actualizó

### 1. Run v03_spatial_pressure
Población llegó a 110 al tick 10.000, muy por debajo de P_max=1000. Grid 128×128
demasiado grande: cell_cap=5 no se activó. Energía media ~8.556, acumulación sin
meseta persiste.

### 2. Problema identificado: feedback de movimiento
feedback() mide solo delta inmediato de feeding. Movimiento no produce energy_delta
directo → salto de descubrimiento para NA/SA/EA/WA nunca dispara. El beneficio del
movimiento es indirecto (celda destino con energía) pero el contrato actual no lo
captura.

### 3. Próximos pasos reemplazados
1. Config v04: 32×32, e_max_internal=100, repro_cost=4, regen_rate=0.
2. Rediseñar feedback de movimiento: delta proporcional a energía de celda destino.
3. Logger por organismo: acciones, pesos, discovered por tick.
4. Visualizador del mundo: película tick a tick.
5. Implementar ATTACK.
6. Reemplazar DummyAdapter por LLM real.

## Estado
CONTEXT.md commiteado y pusheado. Branch al día.

---

# Run v04_small_grid_no_regen

Config: `runs/configs/v04_small_grid_no_regen.json`
Branch: `experiment/v02-two-energy-sources`
Fecha: 2026-06-13

Parámetros clave: N=32, regen_rate=0, repro_cost=4, e_max_internal=100, P_max=1000, p_action=0.5

## Resultados

| tick  | población | energía media |
|-------|-----------|---------------|
|     1 |        20 |         26.65 |
|  1000 |        23 |         94.54 |
|  3000 |        82 |         96.51 |
|  6000 |       166 |         94.38 |
| 10000 |       244 |         94.14 |

## Observaciones

- **`e_max_internal` funciona**: la energía media satura cerca de 94-96 a partir del tick 1000. La acumulación descontrolada que afectó a v01-v03 está controlada.
- **Supervivencia completa**: sin extinción en 10.000 ticks.
- **Crecimiento poblacional sostenido**: 20 → 244, bien por debajo de P_max=1000. `repro_cost=4` permite crecer bajo restricción energética real.
- **Crecimiento lento al inicio**: de tick 1 a tick 1000 la población apenas sube (20→23). Probable die-off inicial mientras las celdas se agotan y los organismos que no descubrieron PHOTOSYNTHESIZE mueren, seguido de recuperación y crecimiento desde tick ~1000 en adelante.
- **PHOTOSYNTHESIZE**: con `regen_rate=0` es la única fuente renovable. El crecimiento sostenido después del die-off inicial es evidencia indirecta de descubrimiento, igual que en el run `regen_rate=0` anterior. Requiere logger por organismo para confirmación directa.

---

# Commit v04

Branch: `experiment/v02-two-energy-sources`
Fecha: 2026-06-13

## Archivos commiteados

- `runs/configs/v04_small_grid_no_regen.json` — config nueva
- `src/engine.py` — step 6.6: clamp `energy_internal` a `e_max_internal`
- `run.py` — fix `KeyError: 'E_max'` para configs sin ese campo
- `runs/pending_review.md` — este archivo

## Estado

Commiteado y pusheado. Branch al día.
