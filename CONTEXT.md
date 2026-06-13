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

## Estado actual (al 2026-04-30 — diagnóstico recalculado 2026-06-11)

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

**DummyAdapter:** split `p_action` (acciones descritas: EAT, MOVE, RS) / `p_hidden` (PHOTOSYNTHESIZE).

**`feedback()` y pesos dinámicos por organismo (implementado 2026-06-13):**
- `LLMAdapter.generate()` recibe `organism_id: str` como primer parámetro.
- `LLMAdapter.feedback(organism_id, action, energy_delta)` — abstracto; delta es exclusivo del feeding (no incluye costo metabólico).
- `LLMAdapter.register_child(child_id, parent_id)` — concreto no-op en base; sobreescrito en DummyAdapter para herencia lamarckiana de pesos.
- `DummyAdapter` mantiene `_weights: Dict[str, list[float]]` por organismo. `generate()` usa `random.choices()` ponderado. Reinforcement positivo puro: `weight[action] += learning_rate * delta`.
- El engine llama `feedback()` tras el step 6 (feeding) y `register_child()` tras `clone_child()`.
- Corrida de verificación: sin errores; extinción en tick 142 (problema de balance preexistente, no regresión).

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
| `p_hidden` (DummyAdapter) | ausente | 0.01 |

### Pendiente (balance)

Primera corrida v02: extinción en tick 100 (antes de implementar `feedback()`).
Segunda corrida (con `feedback()` activo): extinción en tick 142. Misma causa raíz:
`EAT` es 1 de 6 acciones en `_NORMAL_ACTIONS` → se emite el 0.83% de los ticks,
no el 5% asumido en el diseño. Balance real: −0.38 u/tick.
Fix pendiente: bajar `base_metabolic_cost` o darle a `EAT` su propia probabilidad.

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

## Próximos pasos (en orden)

1. **Calibrar balance v02** ← próximo paso: fix del desbalance EAT/metabolic para evitar
   extinción con DummyAdapter.
2. ~~**Agregar `feedback()`** al adapter~~ — **completado 2026-06-13.**
3. ~~**Pesos dinámicos por organismo**~~ — **completado junto con feedback().**
4. **Implementar ATTACK**: acción deliberada que reemplaza la absorción pasiva.
   El organismo emite ATTACK; el engine resuelve la pelea y transfiere energía.
   La absorción por colisión (step 8) se elimina.
5. **Reemplazar DummyAdapter** por adapter de LLM real cuando la ecología tenga
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
