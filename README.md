# OpenCnidarios

> Three ruminants were born equal, with the same phrase etched into their memory:
> *"the primitive organisms of this world discovered that certain words in English
> produced qualitative leaps in their ability to persist."* Each one read the same
> environment and began narrating to itself what to do.
>
> One decided to move toward "CENTER" — but the world doesn't understand that
> word, only the one the organism had already used a line earlier to describe the
> field: "NORTH". From then on, every time the organism thought it was deciding
> something, the world handed it back a different action. It read this as
> betrayal: *"this is systemic gaslighting,"* it wrote. It died 136 cycles later,
> having never eaten, crossing the map toward the east.
>
> Another discovered almost by accident that "staying still" seemed to be a valid
> strategy, and spent 178 of its 193 life cycles nearly motionless, sensing that it
> should "consume the current location" without ever landing on the exact word. It
> was the one that lived the longest.
>
> None of the three ever found the word that feeds. All three died of starvation.
> (The full chronicle, with fragments of their own words, is in
> [`runs/2026-06-17_v06_llm_solo_184001/relato_2026-06-17_v06_llm_solo_184001.md`](runs/2026-06-17_v06_llm_solo_184001/relato_2026-06-17_v06_llm_solo_184001.md).)

---

## 1. What it is

OpenCnidarios is an experiment where the organisms of a digital ecosystem are
language models (LLMs): each one lives by narrating itself, and from that
self-conversation come its actions, its survival, and — if it manages to
reproduce — what it passes on to its offspring.

## 2. Why it's interesting

An organism is never told what it can do. There are no goals, no points, no
explicit rewards: there's a closed world with energy hidden in different places,
and the only rule is that whoever fails to get energy dies. To survive, the
organism has to do something resembling genuine science: observe its
environment, formulate hypotheses about what actions exist, test them, and learn
from the consequences — all of this inside its own text, with no one explaining
the rules to it.

That turns every run into a real experiment with an open question: what emerges
when a language model is subjected to evolution and selection, instead of
following instructions? The answers, so far, have been different from what was
expected — both when the "organism" is a random action generator (a control) and
when it's a real LLM.

## 3. What's happened so far

The project has moved forward in two stages: first, the world's ecology was
validated with a control adapter (`DummyAdapter`, which emits random actions —
useful for testing that the engine works before spending on real LLMs). Then,
the first run with a real LLM.

### Stage 1 — five iterations with control organisms (v01 to v05)

Each version changed one rule of the world and was run to see what happened:

- **Die-off and recovery.** Without energy regeneration in the environment, the
  population collapsed once the available resources ran out — and then recovered
  and kept growing. The only possible explanation was that some organisms had
  found a source of energy that doesn't depend on the environment.
- **Photosynthesis discovered and inherited.** That alternative source — a
  hidden action, never explained to the organisms — was found through pure
  trial-and-error exploration, and spread to offspring: the children of those who
  discovered it inherited the tendency to use it (Lamarckian inheritance: what's
  learned in life is passed on, not just what's genetic).
- **Predation as a population regulator.** By enabling the option to attack
  another organism and absorb its energy, the population stopped growing without
  limit and stabilized on its own around ~244 individuals — well below the
  maximum allowed limit (1000). 99.9% of deaths became predation, not
  starvation: the dynamic between hunters and prey ended up regulating the
  population better than any limit imposed from outside.

### Stage 2 — first run with a real LLM (v06)

The first time the organisms were real language models (Claude Haiku) instead of
random generators. Three organisms, with no competition among them, in a world
with abundant energy. None survived: total extinction at cycle 193 of 500
planned, and none discovered the actions that feed (neither "EAT" nor
"PHOTOSYNTHESIZE"). The full account of that run — with literal fragments of
what each organism told itself before dying — is above and in
[`relato_2026-06-17_v06_llm_solo_184001.md`](runs/2026-06-17_v06_llm_solo_184001/relato_2026-06-17_v06_llm_solo_184001.md).

A notable finding from that run: the organisms did discover the movement
vocabulary (NORTH/SOUTH/EAST/WEST) — but not because the world taught it to
them, but because they themselves wrote the cardinal points in uppercase while
narrating their own environment, and the engine ended up interpreting that as
their decision. They self-suggested a word that then behaved as if it were a
valid action. There was no equivalent shortcut for "eating," and none of them
found one.

## 4. How it works technically

- **The world:** a toroidal 2D grid (the edges wrap around to each other) with
  energy distributed per cell, which regenerates at a configurable rate.
- **The organism ("ruminant"):** each cycle, it receives its local environment —
  energy in its cell and in the four neighboring cells, its own internal energy,
  its last recognized action — injected into its context between
  `XEstadoX ... XEstadoX` markers. It responds with free text (its
  "rumination"); the engine searches within that text, by priority, for whole
  words matching valid actions (moving in a direction, eating, photosynthesizing,
  attacking, reproducing). Whatever it doesn't recognize, it discards.
- **No instruction manual:** actions are never explained to the organism. It has
  to infer them by correlating what it writes with what changes in its next
  state.
- **Three energy sources, none free:** chemotrophy (`EAT`, depletes the cell,
  easy to infer because it's described), photosynthesis (`PHOTOSYNTHESIZE`,
  doesn't deplete, hidden — no one tells the organism it exists), and predation
  (`ATTACK`, kills another organism in the same cell and absorbs its energy).
- **Lamarckian inheritance:** when reproducing, the organism passes on to its
  offspring what it learned in life (not just a fixed starting constitution).
- **Two interchangeable adapters:** `DummyAdapter` (random actions, used to
  validate the ecology without spending on LLMs) and `ClaudeAdapter` (organisms
  that are real calls to a Claude model, with their own conversation history as
  memory).
- **Per-event logging:** every birth, death (with cause), discovery, movement,
  and attack is logged in a JSONL, plus aggregated statistics per cycle in CSV.
- **Viewer:** `src/viewer/viewer.html`, a self-contained HTML file (no
  dependencies or server) that loads a run's CSV and JSONL and plays back the
  simulation on a canvas, with play/pause and speed controls.

More detailed technical documentation lives in `Docs/`, and the full log of
decisions and runs is in [`CONTEXT.md`](CONTEXT.md). The project's vision and
philosophy is in [`VISION.md`](VISION.md).

## 5. How to run it

```bash
pip install -r requirements.txt

# Control run (no cost, no real LLM)
python run.py --config runs/configs/v05_attack.json

# Run with a real LLM (requires ANTHROPIC_API_KEY in the environment)
export ANTHROPIC_API_KEY=...
python run.py --config runs/configs/v06_llm_solo.json --ticks 500
```

Each config in `runs/configs/` documents an experiment (parameters, adapter,
date). The results of each run end up in `runs/<date>_<name>/`: a CSV of
aggregated statistics, a JSONL of events, and, if the run used a real LLM, also
the interview and "rumination" log of each organism.

To see a run that's already been done, open `src/viewer/viewer.html` directly in
the browser and load the corresponding CSV and JSONL from `runs/`.

---

## History

The original concept ("Cnidarios 0.1", July 2025) was a proposal aimed at an
institutional setting. OpenCnidarios is the open, reproducible evolution of that
idea. The historical documents are in `History/2025-07 Cnidarios-0.1/`.

---

# OpenCnidarios

> Tres rumiantes nacieron iguales, con la misma frase grabada en la memoria: *"los
> organismos primitivos de este mundo descubrieron que ciertas palabras en inglés
> producían saltos cualitativos en su capacidad de persistir"*. Cada uno leyó el
> mismo entorno y empezó a narrarse a sí mismo qué hacer.
>
> Uno decidió moverse hacia el "CENTER" — pero el mundo no entiende esa palabra, solo
> entiende la que el organismo ya había usado una línea antes para describir el
> campo: "NORTH". A partir de ahí, cada vez que el organismo creía decidir algo, el
> mundo le devolvía una acción distinta. Lo interpretó como traición: *"esto es
> gaslighting a nivel sistémico"*, escribió. Murió 136 ciclos después, sin haber
> comido nunca, atravesando el mapa hacia el este.
>
> Otro descubrió casi por accidente que "quedarse quieto" parecía ser una estrategia
> válida, y pasó 178 de sus 193 ciclos de vida casi inmóvil, intuyendo que debía
> "consumir la ubicación actual" sin nunca dar con la palabra exacta. Fue el que más
> vivió.
>
> Ninguno de los tres encontró jamás la palabra que alimenta. Los tres murieron de
> inanición. (La crónica completa, con fragmentos de sus propias palabras, está en
> [`runs/2026-06-17_v06_llm_solo_184001/relato_2026-06-17_v06_llm_solo_184001.md`](runs/2026-06-17_v06_llm_solo_184001/relato_2026-06-17_v06_llm_solo_184001.md).)

---

## 1. Qué es

OpenCnidarios es un experimento donde los organismos de un ecosistema digital son
modelos de lenguaje (LLMs): cada uno vive narrándose a sí mismo, y de esa
autoconversación salen sus acciones, su supervivencia y, si llega a reproducirse,
lo que transmite a su descendencia.

## 2. Por qué es interesante

No se le dice a un organismo qué puede hacer. No hay objetivos, ni puntos, ni
recompensas explícitas: hay un mundo cerrado con energía escondida en distintos
lugares, y la única regla es que quien no consigue energía, muere. Para sobrevivir,
el organismo tiene que hacer algo parecido a ciencia genuina: observar su entorno,
formular hipótesis sobre qué acciones existen, probarlas, y aprender de las
consecuencias — todo esto dentro de su propio texto, sin que nadie le explique las
reglas.

Eso convierte cada corrida en un experimento real con una pregunta abierta: ¿qué
emerge cuando un modelo de lenguaje es sometido a evolución y selección, en lugar de
seguir instrucciones? Las respuestas, hasta ahora, han sido distintas de lo
esperado — tanto cuando el "organismo" es un generador de acciones al azar (un
control) como cuando es un LLM real.

## 3. Qué pasó hasta ahora

El proyecto avanzó en dos etapas: primero se validó la ecología del mundo con un
adaptador de control (`DummyAdapter`, que emite acciones al azar — sirve para
probar que el motor funciona antes de gastar en LLMs reales). Después, la primera
corrida con un LLM real.

### Etapa 1 — cinco iteraciones con organismos de control (v01 a v05)

Cada versión cambió una regla del mundo y se corrió hasta ver qué pasaba:

- **Die-off y recuperación.** Sin regeneración de energía en el entorno, la
  población colapsó cuando se agotaron los recursos disponibles — y después se
  recuperó y siguió creciendo. La única explicación posible era que algunos
  organismos habían encontrado una fuente de energía que no depende del entorno.
- **Fotosíntesis descubierta y heredada.** Esa fuente alternativa —una acción
  oculta, nunca explicada a los organismos— fue encontrada por pura exploración de
  prueba y error, y se propagó a la descendencia: los hijos de quienes la
  descubrieron heredaron la tendencia a usarla (herencia lamarckiana: lo aprendido
  en vida se transmite, no solo lo genético).
- **Depredación como regulador poblacional.** Al activar la opción de atacar a otro
  organismo y absorber su energía, la población dejó de crecer sin límite y se
  estabilizó sola en torno a ~244 individuos — muy por debajo del límite máximo
  permitido (1000). El 99.9% de las muertes pasaron a ser por depredación, no por
  inanición: la dinámica entre cazadores y presas terminó regulando la población
  mejor que cualquier límite impuesto desde afuera.

### Etapa 2 — primera corrida con un LLM real (v06)

La primera vez que los organismos fueron modelos de lenguaje reales (Claude Haiku)
en lugar de generadores al azar. Tres organismos, sin competencia entre sí, en un
mundo con energía abundante. Ninguno sobrevivió: extinción total en el ciclo 193 de
500 planeados, y ninguno descubrió las acciones que dan de comer (ni "EAT" ni
"PHOTOSYNTHESIZE"). El relato completo de esa corrida — con fragmentos textuales de
lo que cada organismo se decía a sí mismo antes de morir — está arriba y en
[`relato_2026-06-17_v06_llm_solo_184001.md`](runs/2026-06-17_v06_llm_solo_184001/relato_2026-06-17_v06_llm_solo_184001.md).

Un hallazgo notable de esa corrida: los organismos sí descubrieron el vocabulario de
movimiento (NORTH/SOUTH/EAST/WEST) — pero no porque el mundo se lo enseñara, sino
porque ellos mismos escribían los puntos cardinales en mayúsculas al narrar su
propio entorno, y el motor terminó interpretando eso como su decisión. Se
autosugirieron una palabra que después actuaba como si fuera una acción válida. No
existió un atajo equivalente para "comer", y ninguno lo encontró.

## 4. Cómo funciona técnicamente

- **El mundo:** un grid 2D toroidal (los bordes se conectan entre sí) con energía
  distribuida por celda, que se regenera a una tasa configurable.
- **El organismo ("rumiante"):** en cada ciclo, recibe su entorno local —energía en
  su celda y en las cuatro vecinas, su propia energía interna, su última acción
  reconocida— inyectado en su contexto entre marcadores `XEstadoX ... XEstadoX`.
  Responde con texto libre (su "rumiar"); el motor busca dentro de ese texto, por
  prioridad, palabras completas que coincidan con acciones válidas (moverse en una
  dirección, comer, fotosintetizar, atacar, reproducirse). Lo que no reconoce, lo
  descarta.
- **Sin manual de instrucciones:** las acciones nunca se le explican al organismo.
  Las tiene que inferir correlacionando lo que escribe con lo que cambia en su
  siguiente estado.
- **Tres fuentes de energía, ninguna gratis:** quimiotrofía (`EAT`, agota la celda,
  fácil de inferir porque está descrita), fotosíntesis (`PHOTOSYNTHESIZE`, no se
  agota, oculta — nadie le dice al organismo que existe) y depredación (`ATTACK`,
  mata a otro organismo de la misma celda y absorbe su energía).
- **Herencia lamarckiana:** al reproducirse, el organismo transmite a su
  descendencia lo que aprendió en vida (no solo una constitución de partida fija).
- **Dos adaptadores intercambiables:** `DummyAdapter` (acciones al azar, usado para
  validar la ecología sin gastar en LLMs) y `ClaudeAdapter` (organismos que son
  llamadas reales a un modelo Claude, con su propio historial de conversación como
  memoria).
- **Logging por evento:** cada nacimiento, muerte (con causa), descubrimiento,
  movimiento y ataque queda registrado en un JSONL, además de estadísticas
  agregadas por ciclo en CSV.
- **Visualizador:** `src/viewer/viewer.html`, un archivo HTML autocontenido (sin
  dependencias ni servidor) que carga el CSV y el JSONL de una corrida y reproduce
  la simulación en un canvas, con controles de play/pause y velocidad.

Documentación técnica más detallada en `Docs/` y la bitácora completa de decisiones
y corridas en [`CONTEXT.md`](CONTEXT.md). La visión y filosofía del proyecto está en
[`VISION.md`](VISION.md).

## 5. Cómo correrlo

```bash
pip install -r requirements.txt

# Corrida de control (sin costo, sin LLM real)
python run.py --config runs/configs/v05_attack.json

# Corrida con un LLM real (requiere ANTHROPIC_API_KEY en el entorno)
export ANTHROPIC_API_KEY=...
python run.py --config runs/configs/v06_llm_solo.json --ticks 500
```

Cada config en `runs/configs/` documenta un experimento (parámetros, adapter,
fecha). Los resultados de cada corrida quedan en `runs/<fecha>_<nombre>/`: CSV de
estadísticas agregadas, JSONL de eventos y, si la corrida usó un LLM real, también
el log de entrevistas y de "rumiar" de cada organismo.

Para ver una corrida ya hecha, abrí `src/viewer/viewer.html` directamente en el
navegador y cargá el CSV y el JSONL correspondientes desde `runs/`.

---

## Historia

El concepto original ("Cnidarios 0.1", julio de 2025) fue una propuesta orientada a
un entorno institucional. OpenCnidarios es la evolución abierta y reproducible de
esa idea. Los documentos históricos están en `History/2025-07 Cnidarios-0.1/`.
