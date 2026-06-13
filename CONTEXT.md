# OpenCnidarios — Contexto del proyecto

> Este archivo es la "memoria" del proyecto para cualquier asistente LLM.
> Vive en el repositorio y se mantiene actualizado a mano.
> Si lo leés al empezar una sesión, tenés todo el contexto necesario.

---

## Qué es OpenCnidarios

Un framework de evolución digital donde **LLMs son los organismos**.

- Grid 2D toroidal (los bordes se conectan: salir por la derecha = entrar por la izquierda).
- Sin objetivos explícitos, sin recompensas externas.
- Los organismos ("ruminantes") deben descubrir las acciones disponibles por
  correlación empírica con el entorno — no se les dice qué pueden hacer.
- Modelo evolutivo darwiniano-lamarckiano con herencia casi total.

La idea central: forzar al LLM a hacer algo parecido a exploración científica
genuina dentro de su contexto, en lugar de seguir instrucciones explícitas.

---

## Estado actual (al 2026-04-30 — actualizado 2026-06-13)

**Primera simulación completada — smoke test con DummyAdapter v0.1.**

Setup de la corrida:
- Engine: OpenCnidarios v0.1 scaffold
- Adapter: DummyAdapter (no es un LLM real todavía; emite acciones al azar)
- Grid: 32×32 toroidal
- Población inicial: 20
- Ticks: 500
- Probabilidad de acción oculta: 0.02

Resultado:
- La corrida terminó sin errores y produjo `ticks.csv`.
- Población subió de 20 a 37.
- Energía interna media subió de ~24 (tick 1) a ~563 (tick 500).

Conclusión: **el engine funciona** y la ecología tiene presión real. Primera corrida
v02 produjo extinción en tick 100 por desbalance de parámetros (ver branch).
La lógica de dos fuentes de energía está implementada y validada mecánicamente.

---

## Problema identificado: acumulación descontrolada de energía

La energía media crece casi monotónicamente sin ninguna presión real.
Diagnóstico de las tres causas raíz:

> _Nota 2026-06-11: números verificados contra `runs/configs/v01_smoke_test.json`
> (diff vacío contra el ticks.csv archivado). El CONTEXT.md original calculaba con
> regen\_rate=0.2 y feed\_cap=2.0; el run real usó regen\_rate=1 y feed\_cap=5._

### 1. La regeneración del mundo es demasiado generosa
`regenerate()` suma `regen_rate` como valor absoluto a cada celda.
Con `regen_rate = 1` y un grid de 32×32 = 1024 celdas, entran
**~1024 unidades de energía por tick** al sistema. Con 20-37 ruminantes
comiendo máximo 5.0 cada uno, el consumo máximo teórico es 37 × 5 = 185
por tick — siempre sobra comida por un factor de ~5.5×.

### 2. Comer es gratis aunque no se haga nada
En el paso de feeding del engine, la condición alimenta también cuando la
acción es `None`. Como DummyAdapter emite acción válida solo el 2% del tiempo,
el 98% de los ticks cada ruminante come sin "decidir" comer.

### 3. Reproducirse es casi gratis
`repro_cost = 2` contra `repro_threshold = 40`. Reproducirse no genera
ninguna presión: quedás casi en el threshold de nuevo. Además los nacimientos
ocurren por emisión aleatoria de `RS`, no por comportamiento aprendido.

---

## Estado de la branch `experiment/v02-two-energy-sources`

### Implementado

**Dos fuentes de energía activas (ninguna pasiva — todas requieren acción explícita):**
- `EAT` — quimiotrofía: acción descrita; extrae energía de la celda (finita, agotable). Fácil de descubrir.
- `PHOTOSYNTHESIZE` — fotosíntesis: acción oculta (no descrita al organismo); da `photo_energy` sin agotar celda. Difícil de descubrir.
- `None` y cualquier otra acción: no alimentan.

**Base metabolic cost:** se drena **después** del feeding. Un organismo que come en su tick crítico puede sobrevivir.

**`cell_energy_hi` en `World`:** cap de celda separado del cap de organismo (`E_max`). `regenerate()` clampea a `world_energy_hi`.

**DummyAdapter:** pool unificado con pesos iniciales no uniformes. `p_action` = probabilidad de emitir cualquier acción. PHOTOSYNTHESIZE y ATTACK están en el pool desde el inicio con peso bajo — deben descubrirse vía feedback.

**`feedback()`, pesos dinámicos y salto de descubrimiento (implementado 2026-06-13):**
- `LLMAdapter.generate()` recibe `organism_id: str` como primer parámetro.
- `LLMAdapter.feedback(organism_id, action, energy_delta)` — abstracto; delta es exclusivo del feeding (no incluye costo metabólico).
- `LLMAdapter.register_child(child_id, parent_id)` — concreto no-op en base; sobreescrito en DummyAdapter para herencia lamarckiana.
- `DummyAdapter._weights`: pesos iniciales no uniformes: `EAT=100, RS=5, NA/SA/EA/WA/ATTACK/PHOTOSYNTHESIZE=1`. `generate()` usa `random.choices()` ponderado.
- `DummyAdapter._discovered`: set por organismo. Primera acción exitosa dispara un salto irreversible de peso (`PHOTOSYNTHESIZE→100`, `ATTACK/movimientos→30`). EAT y RS sin salto.
- Herencia lamarckiana: `register_child()` copia tanto `_weights` como `_discovered`.
- El engine llama `feedback()` tras el step 6 (feeding) y `register_child()` tras `clone_child()`.
- Corrida de verificación: sin errores; extinción en tick 136 (problema de balance preexistente, no regresión).

**Parámetros v02:**

| parámetro | v01 | v02 |
|---|---|---|
| `regen_rate` | 1 | 0.1 |
| `base_metabolic_cost` | 0 | 0.4 |
| `photo_energy` | ausente | 4.0 |
| `repro_threshold` | 40 | 60 |
| `repro_cost` | 2 | 20 |
| `feed_cap` | 5 | 6 |
| `e_i0` | 20 | 25 |
| `E_max` | 50 | 100 |
| `p_action` (DummyAdapter) | 0.02 | 0.05 |
| `p_hidden` (DummyAdapter) | ausente | eliminado (pool unificado) |

### Corridas realizadas en esta branch

| run | config base | ticks | resultado |
|---|---|---|---|
| v02 smoke (pre-feedback) | v02 | 500 | extinción tick 100 |
| v02 + feedback | v02 | 500 | extinción tick 142 |
| v02 p_action=0.5 | v02 | 10000 | supervivencia completa |
| v02 regen_rate=0 | v02 | 10000 | supervivencia completa |
| v04 | v04 | 10000 | supervivencia completa, pop 20→244 |
| v04b_long_run | v04b | 100000 | supervivencia completa, pop converge ~440 |

**Run p_action=0.5, 10000 ticks** (`runs/2026-06-13_p_action_0.5_10000ticks/`):
Población sobrevivió los 10.000 ticks. Creció de 20 a ~93, alcanzó cap P_max=100.
Energía media creció de ~27 a ~10.611 (~1 u/tick lineal sostenida, sin meseta).
Misma dinámica de acumulación que v01, pero con población estable. PHOTOSYNTHESIZE
no confirmable sin logging de acciones.

**Run regen_rate=0, 10000 ticks** (`runs/2026-06-13_regen_rate_0/`):
Población sobrevivió los 10.000 ticks sin regeneración del mundo. Die-off en tick
~200 cuando las celdas se agotaron; recuperación sostenida y crecimiento hasta ~93.
Con cero regeneración, la única fuente de energía disponible tras el agotamiento es
PHOTOSYNTHESIZE. Energía creció a ~8.843 al tick 10.000. **Evidencia fuerte de que
PHOTOSYNTHESIZE fue descubierto y propagado vía herencia lamarckiana**: los
organismos que lo descubrieron sobrevivieron el die-off y transmitieron el peso
saltado (100) a su descendencia. Requiere logging de pesos para confirmación directa.

### Run v03_spatial_pressure (2026-06-13)

Config: `runs/configs/v03_spatial_pressure.json` — N=128, P_max=1000, cell_cap=5.
Población llegó a 110 al tick 10.000, muy por debajo del cap de 1000. Grid 128×128
(16.384 celdas) es demasiado grande para la población actual: los organismos quedan
dispersos y cell_cap=5 nunca se activó. La presión espacial no mordió.
Energía media al tick 10.000: ~8.556. Acumulación sin meseta persiste.

### Run v04_small_grid_no_regen (2026-06-13)

Config: `runs/configs/v04_small_grid_no_regen.json` — N=32, regen_rate=0, repro_cost=4,
e_max_internal=100, P_max=1000.

Cambios de diseño respecto a v03:
- `e_max_internal=100` implementado en engine (step 6.6): clamp de `energy_internal`
  después del metabolismo. `E_max` era un parámetro muerto; reemplazado por este.
- `run.py`: fix `KeyError` al leer `E_max` — ahora usa `.get("E_max", world_energy_hi)`.
- `regen_rate=0`: sin regeneración, PHOTOSYNTHESIZE es la única fuente renovable.
- `repro_cost`: 20 → 4, para permitir crecimiento poblacional bajo restricción energética.

Resultados (10.000 ticks):

| tick  | pop | energía media |
|-------|-----|---------------|
|     1 |  20 |         26.65 |
|  1000 |  23 |         94.54 |
|  3000 |  82 |         96.51 |
|  6000 | 166 |         94.38 |
| 10000 | 244 |         94.14 |

Energía satura en ~94-96 desde tick 1000: `e_max_internal` funciona, acumulación
descontrolada eliminada. Arranque lento (20→23 en los primeros 1000 ticks): probable
die-off mientras se agotan las celdas, seguido de crecimiento sostenido vía
PHOTOSYNTHESIZE (evidencia indirecta; requiere logger para confirmar).

### Run v04b_long_run (2026-06-13)

Config: `runs/configs/v04b_long_run.json` — idéntico a v04, ticks=100000.
Output: `runs/2026-06-13_v04b_long_run/`

Propósito: ver si la población alcanza densidad suficiente para que ATTACK tenga
sentido ecológico.

Resultados (100.000 ticks):

| tick   | pop | energía media |
|--------|-----|---------------|
|      1 |  20 |         26.65 |
|  10000 | 244 |         94.14 |
|  25000 | 359 |         96.08 |
|  50000 | 404 |         97.92 |
|  75000 | 427 |         98.35 |
| 100000 | 439 |         99.11 |

La población crece pero desacelera marcadamente y converge en torno a ~440,
muy por debajo de P_max=1000. Densidad al tick 100k: 439/1024 ≈ 0.43 org/celda.
ATTACK tiene sentido mecánico pero el impacto ecológico sería moderado a esta
densidad. El equilibrio lo determinan la dinámica interna (repro_cost, absorción
pasiva, metabolismo), no el cap poblacional. Energía media satura en ~99,
confirmando PHOTOSYNTHESIZE como fuente dominante de toda la población.

### Problema identificado: feedback de movimiento no funciona

`feedback()` mide únicamente el delta inmediato de energía del feeding. Moverse
no produce `energy_delta` directo, por lo que el salto de descubrimiento de
movimiento (NA/SA/EA/WA → 30) nunca dispara. El beneficio del movimiento es
indirecto (llegar a una celda con más energía) pero el contrato actual de
`feedback()` no captura esa causalidad diferida. Requiere rediseño.

### Reglas del mundo v02

- Grid: 32×32 toroidal, metabolismo basal siempre activo
- **Tres fuentes de energía** (ninguna gratis, todas hay que descubrirlas):
  1. **EAT** — quimiotrofía: fácil (acción descrita), finita
  2. **PHOTOSYNTHESIZE** — fotosíntesis: difícil (acción oculta), renovable
  3. **ATTACK** — depredación: no implementada aún; reemplazará la absorción
     pasiva por colisión (step 8 del engine actual)
- Absorción pasiva por colisión: **aún activa** en el engine; se eliminará cuando
  se implemente ATTACK deliberado

---

## Decisiones de arquitectura tomadas

### Regla de versionado de configs (adoptada en v03)

v02 acumuló múltiples cambios de diseño sin generar un config nuevo (pesos no
uniformes, salto de descubrimiento, experimentos con regen_rate=0 y p_action=0.5).
A partir de v03, cada cambio de diseño significativo genera un archivo de config
nuevo. El config anterior queda como registro histórico. Los experimentos puntuales
(como regen_rate=0) se archivan en `runs/` pero no generan un config versionado a
menos que sean adoptados como base.

### Configuración separada del código
Para evitar el antipatrón `run_v1.py`, `run_v2.py`, etc., los parámetros van
en archivos de config (JSON), no hardcodeados en `run.py`. Un solo `run.py`
recibe el config por argumento:

```bash
python run.py --config runs/configs/v02_balanced_ecology.json
```

Estructura propuesta:
```
runs/
  configs/
    v01_smoke_test.json
    v02_balanced_ecology.json
  latest/
    ticks.csv
```

Cada config documenta el experimento (nombre, fecha, descripción, params).
El historial de experimentos queda en git, no en nombres de archivo.

---

## Forma de trabajo (importante — enfoque ultraconservador)

- **Nunca tocar `main` directamente.** Cada round de cambios va en su propia branch:
  `git checkout -b experiment/v02-balanced-ecology`
- Si el experimento sale bien → PR a main. Si sale mal → se tira la branch,
  main queda intacto.
- Antes de cualquier cambio: repo limpio, todo commiteado y pusheado.
- Este `CONTEXT.md` se actualiza cuando se toman decisiones importantes.
  El conocimiento del proyecto vive en el repo, no en conversaciones de chat.

---

## Próximos pasos (en orden) — actualizado 2026-06-13

1. ~~**Config v04**~~: completado. v04 y v04b corridos. `e_max_internal` implementado.
   Población converge a ~440/1024 celdas (0.43 org/celda) a los 100k ticks.
2. **Rediseñar feedback de movimiento**: si el organismo se mueve a una celda con
   energía disponible, `feedback()` recibe un delta positivo proporcional a la
   energía de la celda destino. El engine debe pasar esta información al adapter.
3. **Logger por organismo**: registrar acciones emitidas, pesos actuales y
   `_discovered` set por tick. Necesario para confirmar empíricamente el
   descubrimiento de PHOTOSYNTHESIZE y diagnosticar el comportamiento emergente.
4. **Visualizador del mundo**: película tick a tick — posición de organismos,
   energía por celda, nacimientos, muertes.
5. **Implementar ATTACK**: acción deliberada que reemplaza la absorción pasiva.
   El organismo emite ATTACK; el engine resuelve la pelea y transfiere energía.
   La absorción por colisión (step 8 del engine) se elimina.
6. **Reemplazar DummyAdapter** por adapter de LLM real cuando la ecología tenga
   dinámicas estables.

---

## Archivos clave del repo

- `src/world.py` — grid toroidal + energía + regeneración
- `src/engine.py` — loop de simulación (observar, generar, parsear, aplicar)
- `src/ruminant.py` — el organismo
- `src/llm_adapter/dummy.py` — adapter dummy actual
- `run.py` — entrypoint
- `Docs/02_planeta_v1_especificacion.md` — spec del mundo
- `Docs/04_parameters_v1.md` — parámetros
