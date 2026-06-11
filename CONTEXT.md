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

Conclusión: **el engine funciona** (ticks avanzan, hay nacimientos, muertes,
movimientos, absorciones), pero **la ecología no está balanceada**.

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

## Cambios propuestos para v0.2 (NO aplicados todavía)

Recalibración de parámetros en la config:

| parámetro              | v0.1 | v0.2 propuesto | razón                              |
|------------------------|------|----------------|------------------------------------|
| regen_rate             | 1    | 0.05           | mundo 20x más lento en regenerar   |
| base_metabolic_cost    | ausente (0) | 4.0  | quedarse quieto debe costar        |
| repro_threshold        | 40   | 60             | reproducirse requiere más energía  |
| repro_cost             | 2    | 20             | reproducirse debe ser caro         |
| child_e0               | 10   | 8              | hijos más vulnerables              |

Cambio de lógica en el engine (feeding):
- Que quedarse quieto sin emitir acción NO alimente al máximo, o que tenga
  penalidad. Hoy `None` entra en el feeding con `feed_cap` completo.

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

1. Refactor: config separada del código (`run.py` lee JSON).
2. Aplicar parámetros v0.2 en una branch, correr simulación, comparar con v0.1.
3. Arreglar la lógica de feeding (que `None` no alimente al máximo).
4. Cuando la ecología tenga dynamics reales → reemplazar DummyAdapter por
   un adapter de LLM real.

---

## Archivos clave del repo

- `src/world.py` — grid toroidal + energía + regeneración
- `src/engine.py` — loop de simulación (observar, generar, parsear, aplicar)
- `src/ruminant.py` — el organismo
- `src/llm_adapter/dummy.py` — adapter dummy actual
- `run.py` — entrypoint
- `Docs/02_planeta_v1_especificacion.md` — spec del mundo
- `Docs/04_parameters_v1.md` — parámetros
