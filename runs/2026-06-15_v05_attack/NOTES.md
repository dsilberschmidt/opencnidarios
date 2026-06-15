# Run v05_attack — notas

Config: `runs/configs/v05_attack.json`
Branch: experiment/v02-two-energy-sources
Fecha: 2026-06-15
Seed: 42 | Grid: 32×32 | Ticks: 10.000 | P0: 20 | P_max: 1.000
attack_efficiency: 0.8 | regen_rate: 0 | p_action: 0.5

---

## Propósito

Primera corrida con ATTACK como acción deliberada activa. La absorción pasiva por
colisión (step 8 original del engine) fue eliminada; en su lugar el organismo emite
ATTACK explícitamente, elige una víctima al azar en su celda, la mata y absorbe
`attack_efficiency * victim.energy_internal`. Si no hay víctima, no hay efecto ni
discovery.

Objetivo del smoke test: verificar que la mecánica funciona, que los eventos se
loguean correctamente, y que ATTACK actúa como regulador poblacional real.

---

## Bugs corregidos antes de esta corrida (post-fix)

Dos bugs descubiertos al intentar correr v05 por primera vez:

**Bug 1 — ATTACK nunca parseado** (`src/engine.py`, `_parse_action`):
El set de tokens válidos no incluía "ATTACK". El DummyAdapter emitía el token pero
el parser lo descartaba como `None`; step 8 nunca lo procesaba.
Consecuencia en la corrida bugueada: 0 eventos "attack", 0 muertes por depredación,
población llegó a P_max=1.000 sin ninguna presión depredadora.
Fix: agregar "ATTACK" al set en `_parse_action()`.

**Bug 2 — KeyError en step 8** (`src/engine.py`, iterador de step 8):
Step 7 (reproducción) agrega hijos a `self.ruminants` antes de que corra step 8.
La iteración `enumerate(self.ruminants)` generaba índices más allá del rango de
`outputs` (que solo contiene la población original del tick) → `KeyError: 19`.
Fix: `for idx in range(len(outputs)):` en lugar de `enumerate(self.ruminants)`.

Ambos fixes commiteados en `c34144b`.

---

## Resultados

### Población y energía media

| tick  | población | energía media |
|-------|-----------|---------------|
|     1 |        20 |         26.65 |
|  1000 |       120 |         85.12 |
|  5000 |       250 |         96.24 |
| 10000 |       244 |         97.08 |

### Eventos por tipo

| evento    | count |
|-----------|-------|
| attack    | 5.493 |
| birth     | 5.724 |
| death     | 5.500 |
| discovery |   475 |
| movement  | 4.985 |

### Muertes por causa

| causa      | count | %     |
|------------|-------|-------|
| attacked   | 5.493 | 99.9% |
| starvation |     7 |  0.1% |

---

## Observaciones

**ATTACK es la causa dominante de muerte (99.9%).** La mecánica funciona: la
depredación reemplazó casi completamente la inanición como causa de muerte.

**Población estabilizada en ~244, muy por debajo de P_max=1.000.** En v04b (sin
ATTACK) la población llegaba a ~440 y era contenida por escasez de PHOTOSYNTHESIZE.
Aquí ATTACK actúa como regulador: births (5.724) y deaths por ataque (5.493) se
equilibran en torno a ~244-250 organismos. El crecimiento neto (224 = 5724 - 5500)
concuerda con el delta poblacional 20→244.

**Energía media satura en ~97.** `e_max_internal=100` sigue funcionando; la
presión de ATTACK no afecta el cap energético de los sobrevivientes.

**475 discovery events.** Con ATTACK activo y parseado, los organismos pueden
descubrir la acción y recibir el jump de peso (→30). Contrasta con la corrida
bugueada (13 discoveries, ninguno de ATTACK).
