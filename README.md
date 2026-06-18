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
