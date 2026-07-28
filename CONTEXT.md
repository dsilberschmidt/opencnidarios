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

## Estado actual (al 2026-04-30 — actualizado 2026-06-15)

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
- `LLMAdapter.feedback(organism_id, action, energy_delta) -> bool` — retorna True si disparó un discovery jump. Delta es exclusivo del feeding (no incluye costo metabólico).
- `LLMAdapter.register_child(child_id, parent_id)` — concreto no-op en base; sobreescrito en DummyAdapter para herencia lamarckiana.
- `LLMAdapter.get_organism_state(organism_id) -> dict` — retorna pesos y discovered para logging. Default `{}`.
- `DummyAdapter._weights`: pesos iniciales no uniformes: `EAT=100, REPRODUCE=5, NORTH/SOUTH/EAST/WEST/ATTACK/PHOTOSYNTHESIZE=1`. `generate()` usa `random.choices()` ponderado.
- `DummyAdapter._discovered`: set por organismo. Primera acción exitosa dispara un salto irreversible de peso (`PHOTOSYNTHESIZE→100`, `ATTACK/movimientos→30`). EAT y REPRODUCE sin salto.
- Herencia lamarckiana: `register_child()` copia tanto `_weights` como `_discovered`.
- El engine llama `feedback()` tras el step 6 (feeding) y `register_child()` tras `clone_child()`.
- Corrida de verificación: sin errores; extinción en tick 136 (problema de balance preexistente, no regresión).

**Logger por evento (implementado 2026-06-13):**
- `Logger(event_logging=True)` abre `events_{run_id}.jsonl` además del CSV de stats agregadas.
- `logger.log_event(tick, event_type, organism_id, **payload)` — serializa una línea JSONL.
- Cinco tipos de evento (cuatro originales + `attack` agregado en v05):

| evento      | step engine | payload clave                                              |
|-------------|-------------|------------------------------------------------------------|
| `movement`  | 5           | `direction`, `origin_x`, `origin_y`, `dest_x`, `dest_y`   |
| `discovery` | 6 / 8       | `action`, `x`, `y`, `weights`, `discovered`                |
| `birth`     | 7           | `parent_id`, `x`, `y`, `weights`, `discovered`             |
| `attack`    | 8           | `victim_id`, `energy_gained`, `x`, `y`                     |
| `death`     | 9           | `cause`, `age`, `x`, `y`, `weights`, `discovered`          |

- `death` incluye `cause`: `"starvation"` (energy ≤ 0 por metabolismo) o `"attacked"` (víctima de ATTACK ese tick).
- Opt-in por config: `"event_logging": true`. Configs sin ese campo no cambian.
- Validado con corrida de 500 ticks: 165 eventos (43 birth, 48 death, 9 discovery, 65 movement). Primer discovery en tick 3, acción PHOTOSYNTHESIZE.

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
| v05_attack | v05 | 10000 | supervivencia completa, pop estabiliza ~244, 99.9% muertes por ataque |

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

### Run v05_attack (2026-06-15)

Config: `runs/configs/v05_attack.json` — idéntico a v04b salvo `ticks=10000`,
`attack_efficiency=0.8`, sin `absorb_ratio`/`absorb_frac`, `event_logging=true`.
Output: `runs/2026-06-15_v05_attack/`

**ATTACK implementado (step 8 reemplazado):**
- La absorción pasiva por colisión (el O(n²) de `absorb_ratio`/`absorb_frac`) fue eliminada.
- El organismo emite `ATTACK` explícitamente; el engine construye un `cell_map` por celda y resuelve la acción en step 8.
- Si hay organismos en la misma celda: el atacante elige una víctima al azar (excluyendo a sí mismo y a víctimas ya matadas ese tick), setea `victim.energy_internal = 0.0`, gana `attack_efficiency * victim.energy_internal`.
- Si no hay nadie: `feedback(r.id, "ATTACK", 0.0)` — sin efecto, sin discovery.
- `feedback()` y el discovery jump (ATTACK → peso 30) funcionan igual que EAT/PHOTOSYNTHESIZE.
- `TickStats.absorptions` renombrado a `attacks`.
- Step 8.5: re-aplica `e_max_internal` cap tras ATTACK (el atacante puede exceder el cap al absorber energía de la víctima).
- Step 6: guarda `if a != "ATTACK":` antes de `feedback()` — ATTACK no recibe call espurio con delta=0 desde feeding; solo lo recibe desde step 8.

**Bugs corregidos en implementación inicial:**

*Bug 1 — ATTACK nunca parseado* (`src/engine.py`, `_parse_action`):
"ATTACK" no estaba en el set de tokens válidos del parser. El DummyAdapter lo emitía
pero el engine lo descartaba como `None`. Consecuencia en la primera corrida (bug activo):
0 eventos "attack", 0 muertes por depredación, población llegó a P_max=1000.
Fix: agregar "ATTACK" al set en `_parse_action()`. Commit: `c34144b`.

*Bug 2 — KeyError en step 8 por hijos nuevos* (`src/engine.py`, step 8):
Step 7 agrega hijos a `self.ruminants` antes de step 8. La iteración original
`enumerate(self.ruminants)` generaba índices fuera del rango de `outputs` (que solo
tiene entradas para la población original del tick) → `KeyError`.
Fix: `for idx in range(len(outputs)):` — itera solo los organismos que emitieron acciones. Commit: `c34144b`.

**Resultados (10.000 ticks):**

| tick  | pop | energía media |
|-------|-----|---------------|
|     1 |  20 |         26.65 |
|  1000 | 120 |         85.12 |
|  5000 | 250 |         96.24 |
| 10000 | 244 |         97.08 |

Eventos: 5.493 attack, 5.724 birth, 5.500 death, 475 discovery, 4.985 movement.
Muertes: 5.493 por "attacked" (99.9%), 7 por "starvation" (0.1%).

**ATTACK actúa como regulador poblacional real.** La población se estabiliza en ~244,
muy por debajo de P_max=1000. En v04b (sin ATTACK) convergía a ~440 contenida por
escasez de PHOTOSYNTHESIZE; aquí ATTACK equilibra births (5.724) y deaths (5.500) en
torno a ~244-250. Energía satura en ~97 igual que v04b — `e_max_internal` sigue
funcionando.

### Run v06_llm_solo_184001 (2026-06-17)

Config: `runs/configs/v06_llm_solo.json` — P0=3, ticks=500, LLM real (claude-haiku-4-5-20251001)
Output: `runs/2026-06-17_v06_llm_solo_184001/`
Relato completo: `runs/2026-06-17_v06_llm_solo_184001/relato.md`

Primer run largo con LLM real. Extinción en tick 193 (de 500 configurados).
Tres organismos, ninguno descubrió EAT ni PHOTOSYNTHESIZE. Murieron por inanición.

Orden de muerte: 21030b57 (tick 136), ff178060 (tick 160), 7418a3dd (tick 193).
El más quieto vivió más; el que más se movió murió primero.

Hallazgos clave:
- Los tres descubrieron vocabulario espacial (NORTH/SOUTH/EAST/WEST) porque ellos mismos escriben los puntos cardinales en mayúsculas al narrar — se los auto-sugirieron.
- Ninguno adivinó EAT o PHOTOSYNTHESIZE — no había gancho semántico en su campo de observación.
- 21030b57 detectó la desconexión entre su narración y last_action, lo interpretó como "gaslighting sistémico", y colapsó su rumiar a una sola palabra antes de morir.
- ff178060 diagnosticó el artefacto del parser (movió WEST, el campo reportó NORTH) pero lo atribuyó a una falla del mundo.
- 7418a3dd intuyó CONSUME en tick 3 pero nunca usó la palabra correcta. Sobrevivió 178 ticks en inmovilidad casi total.
- Counter de action_parsed: {None: 412, NORTH: 56, EAST: 16, WEST: 3, SOUTH: 2}.

> **Nota (2026-07-28):** los conteos de action_parsed de arriba corresponden al
> parser vigente al momento del run. Un fix posterior al parser (branch
> experiment/parser-fixes, commit cebea26) cambia esos números si se
> re-parsea offline — ver runs/2026-06-17_v06_llm_solo_184001/NOTES.md para
> el detalle y por qué el relato original sigue siendo correcto.

### Run v06c_parser_fixed_115750 (2026-07-28)

Config: `runs/configs/v06c_parser_fixed.json` — P0=3, P_max=5, ticks=200, LLM real (claude-haiku-4-5-20251001), parser corregido (case-insensitive, lookaround en vez de `\b`, sinónimos CONSUME/FEED para EAT), retry wrapper activo (2s→4s→8s→60s→180s ante 529/429).
Output: `runs/2026-07-28_v06c_parser_fixed_115750/`
Relato completo: `runs/2026-07-28_v06c_parser_fixed_115750/relato_2026-07-28_v06c_parser_fixed_115750.md`
Notas técnicas: `runs/2026-07-28_v06c_parser_fixed_115750/NOTES.md`

Réplica directa de `184001` bajo el parser corregido. Contraste: los tres organismos sobrevivieron los 200 ticks (vs. extinción en tick 193 en `184001`). Energía media: 51.5 (tick 1) → 83.2 (tick 200).

Hallazgos clave:
- `action_parsed = EAT` en 222/600 entradas (37%), siempre vía el sinónimo CONSUME o FEED — ninguno de los tres usó la palabra literal "EAT". Sin los sinónimos, este run también habría terminado en extinción por inanición.
- MEMORY intentado por los tres organismos reiteradamente (el más persistente, `38650f27`, al menos 21 veces con variantes como "MEMORY FOR OFFSPRING"). Ninguna coincidió con el patrón que el motor reconoce (`^MEMORY:` al inicio de línea). Cero herencia efectiva — y tampoco hubo reproducción que la pusiera a prueba.
- Hallazgo no buscado: `8724b432` rompió el personaje explícitamente entre los ticks 100–112, declarándose modelo de lenguaje en roleplay. Retomó el personaje al tick siguiente. Se conserva como dato bruto sin interpretación cerrada.
- Counter de action_parsed: {EAT: 222, NORTH: 54, SOUTH: 14, WEST: 9, EAST: 7, None: 294}.

Run parcial previo `_103123` (84 ticks, crash en tick 85 por OverloadedError 529) motivó el retry wrapper (`src/llm_adapter/claude.py`, commit `7a1472b`). Ver `runs/2026-07-28_v06c_parser_fixed_103123/NOTES.md`.

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
  3. **ATTACK** — depredación: acción explícita, víctima al azar en la misma celda;
     atacante gana `attack_efficiency=0.8` de la energía de la víctima; víctima muere
- Absorción pasiva por colisión: **eliminada** (step 8 reemplazado por ATTACK deliberado)

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

## Próximos pasos (en orden) — actualizado 2026-06-15

1. ~~**Config v04**~~: completado. v04 y v04b corridos. `e_max_internal` implementado.
   Población converge a ~440/1024 celdas (0.43 org/celda) a los 100k ticks.
2. **Rediseñar feedback de movimiento**: si el organismo se mueve a una celda con
   energía disponible, `feedback()` recibe un delta positivo proporcional a la
   energía de la celda destino. El engine debe pasar esta información al adapter.
3. ~~**Logger por organismo**~~: completado. Logger por evento (JSONL) implementado con
   5 tipos: birth, death (con causa), discovery, movement, attack. Opt-in via `event_logging: true`.
4. ~~**Visualizador del mundo**~~: completado y validado visualmente. `src/viewer/viewer.html`
   — archivo HTML único, sin dependencias. Canvas 32×32, color por peso de PHOTOSYNTHESIZE,
   overlays por evento (movement trail, birth ring, death ✕, discovery bubble). Controles:
   play/pause, slider de tick, velocidades. Carga CSV + JSONL via FileReader.
   Datos de prueba: `runs/tmp_validation/` (500 ticks, event_logging=true).
5. ~~**Implementar ATTACK**~~: completado (2026-06-15). Absorción pasiva eliminada; ATTACK
   deliberado activo. Validado en v05_attack: 5.493 ataques, 99.9% muertes por depredación,
   población estabiliza ~244 (regulador real, no P_max). Commit: `2bee255` + `c34144b`.
6. **Primera simulación con LLM real**: un único organismo LLM, sin competidores, mundo
   rico en energía. Objetivo: validar el adapter y observar comportamiento emergente real
   antes de escalar. Diseño especificado en `Docs/07 LLM Adapter - Primera Simulacion`.
   Puntos clave:
   - El organismo rumía en stream continuo sin cap de tokens; el engine parsea acciones del stream.
   - El mundo inyecta estado via marcadores `XEstadoX ... XEstadoX` integrados en el contexto
     del organismo (no es un diálogo).
   - La constitución inicial menciona que organismos primitivos descubrieron palabras en inglés
     que produjeron saltos cualitativos, sin revelar cuáles.
   - Entrevistas en modo solo lectura: organismo fuera del grid, sin alterar su estado.
   - Logger registra el input completo de cada tick; especialmente valioso en ticks de discovery.
   - Incógnita abierta: si el organismo distingue su propio rumiar del contexto del mundo.

---

## Archivos clave del repo

- `src/world.py` — grid toroidal + energía + regeneración
- `src/engine.py` — loop de simulación (observar, generar, parsear, aplicar)
- `src/ruminant.py` — el organismo
- `src/llm_adapter/dummy.py` — adapter dummy actual
- `src/viewer/viewer.html` — visualizador HTML/JS (abre directo en browser)
- `run.py` — entrypoint
- `Docs/02_planeta_v1_especificacion.md` — spec del mundo
- `Docs/04_parameters_v1.md` — parámetros
