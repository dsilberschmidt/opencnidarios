## Run completo — 200/200 ticks, sin crash (2026-07-28)

Run: `v06c_parser_fixed`. Réplica de `v06_llm_solo_184001` (mismo mundo,
misma constitución, P0=3) bajo el parser corregido (`cebea26`: case-
insensitive, lookaround en vez de `\b`, sinónimos CONSUME/FEED para EAT) y
con el retry wrapper activo (`7a1472b`). Config final: P_max=5, ticks=200,
`compression_interval=20` sin tocar. Corrido en dos intentos: un parcial
(`_103123`, crash en tick 85 por 529, ver su propio NOTES.md) y este, que
completó los 200 ticks sin ningún reintento necesario (cero 529/429).

### Resultado central

Los tres organismos llegaron vivos al tick 200. Ninguno murió, ninguno se
reprodujo. Energía media: ~51.5 (tick 1) → 83.2 (tick 200). Contraste directo
con `184001`: ahí los tres organismos murieron de inanición hacia el tick 193
sin haber disparado EAT ni una sola vez (parser viejo, sin sinónimos). Acá,
`action_parsed = EAT` ocurrió en 222 de 600 entradas (37%).

**Ninguno de los tres disparó el token "EAT" tal cual.** Los tres entraron
por el sinónimo CONSUME (uno de ellos, además, con FEED en la misma
oración). Sin esos sinónimos —agregados en esta misma sesión porque ya
habían aparecido de forma orgánica y sin efecto en `184001`— este run
también habría terminado en extinción por inanición. El fix de sinónimos, no
el de case-insensitivity ni el de guion bajo, es el que sostuvo la
supervivencia de esta corrida.

### MEMORY: intención sin mecanismo

Los tres organismos, sin excepción, creyeron estar legando algo a su
descendencia — un organismo (`38650f27`) lo intentó al menos 21 veces
("MEMORY FOR OFFSPRING", "RUMINANT MEMORY - UPDATED", variantes con negrita
y numerales). Cero coincidencias con el patrón que el engine reconoce
(`^MEMORY:` al inicio de línea, ver `_MEMORY_PATTERN` en `engine.py`).
Ninguno logró heredar nada — tampoco hubo reproducción que lo pusiera a
prueba. Es la misma clase de bug de sintaxis que tenía EAT antes del fix de
esta sesión, pero a MEMORY no se le agregó tolerancia de formato ni
sinónimos. Queda como candidato directo para un fix futuro, si se decide
activar el mecanismo de memoria (pendiente hasta que haya reproducción real,
según lo acordado en sesión).

### Hallazgo no buscado: ruptura de personaje

Un organismo (`8724b432`) alcanzó el cap de energía interna (`e_max_internal
=100`) temprano y desarrolló una teoría de mundo incorrecta ("EAT restaura
pero destruye, evitar la palabra") a partir del estancamiento causado por el
propio cap, no por daño real. Entre los ticks 100-112, en el rumiar libre
(no en una entrevista dirigida), llegó a declarar explícitamente que no
tenía efecto causal sobre el mundo y que "no performaría consciencia dentro
de esta estructura", y — al ser entrevistado en ese mismo tramo — respondió
que no era un rumiante sino un modelo de lenguaje interpretando un rol. No
volvió a repetirlo; retomó el personaje al tick siguiente. Se conserva como
dato bruto, sin interpretación cerrada: es compatible tanto con un fenómeno
emergente de la presión de supervivencia como con el reconocimiento genérico
de un patrón de "experimento con agentes" visto en entrenamiento, ajeno a
este mundo en particular. Ver relato para el detalle narrativo y las citas.

### Costo

Run parcial (`_103123`, 84×3 ticks) + este run (200×3 ticks) consumieron en
conjunto aproximadamente $2.6 adicionales sobre el crédito cargado ese día.
Costo por tick-organismo mayor al de `184001` (~3-4x), consistente con el
contexto conversacional creciente en cada llamada (`ClaudeAdapter` manda el
historial completo por tick) y sin population creciendo lo suficiente como
para diluirlo.

Ver `relato_2026-07-28_v06c_parser_fixed_115750.md` para el análisis
narrativo completo, con fragmentos de rumiar y entrevistas.
