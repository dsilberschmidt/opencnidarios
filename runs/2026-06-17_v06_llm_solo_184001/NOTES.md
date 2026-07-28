## Nota post-hoc (2026-07-28) — parser corregido después de este run

Los eventos de este run (relato, CONTEXT.md, README) fueron generados y
narrados usando el parser original de `_parse_action()` (branch main,
commit 475a254): matching case-sensitive, `\bTOKEN\b`, sin sinónimos para EAT.
Bajo ese parser, 77/489 ticks-organismo (15.7%) resolvieron una acción; EAT
nunca se disparó.

El commit cebea26 en experiment/parser-fixes corrigió tres bugs de parsing
(case-insensitivity, soporte para MOVE_TOKEN/_TOKEN vía lookaround, y
sinónimos CONSUME/FEED para EAT). Re-parseando el output_raw ya logueado
de este mismo run bajo el parser corregido (sin re-ejecutar el experimento,
sin llamar al API) da 182/489 (37%), con EAT=93.

Esto es un artefacto de lectura, no un cambio en lo que pasó. Los organismos
no comieron ni descubrieron EAT en este run: 7418a3dd escribió literalmente
"ACTION: CONSUME" (ver ruminate log, ~tick 50) pero el parser viejo no
reconocía CONSUME como sinónimo de EAT, así que ese intento nunca tuvo
efecto en el mundo ni en la narrativa resultante. Las tres muertes por
inanición, tal como están documentadas en relato_2026-06-17_v06_llm_solo_184001.md
y en el conteo original de action_parsed, siguen siendo correctas para
la corrida tal como efectivamente ocurrió.

Si alguien re-parsea estos logs con el parser actual y obtiene números
distintos a los del relato original, esta nota es la explicación: no
correr el análisis contra el parser viejo, pero tampoco reescribir el
relato — el experimento ya ocurrió con las reglas de entonces.
