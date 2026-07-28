## Run parcial — crash en tick 85 (2026-07-28)

Run: `v06c_parser_fixed`, mismo config que `_115750` (P0=3, P_max=10 en este
intento — luego bajado a 5 para el run siguiente), corrido antes de que
existiera el retry wrapper.

Crasheó en el tick 85 con `anthropic.OverloadedError` (529) al llamar al API
— no fue un bug del código ni del parser, sino sobrecarga temporal del lado
de Anthropic. `run.py` no tiene resume: un solo error no capturado tira todo
el proceso, y no hay forma de continuar desde donde quedó (el estado del
organismo, incluyendo el historial conversacional del `ClaudeAdapter`, vive
en memoria y no se serializa).

Este crash motivó el retry wrapper `_api_call()` en
`src/llm_adapter/claude.py` (commit `7a1472b`, mergeado a main en `eb8a996`):
reintentos con backoff 2s→4s→8s→60s→180s ante 529/429 antes de propagar la
excepción. El run siguiente de esta misma familia (`_115750`, 200 ticks
completos, ver ese `NOTES.md`) corrió con el retry activo y no necesitó
usarlo — cero 529 durante esos 200 ticks — pero la robustez ya queda
disponible para corridas futuras más largas.

Se conserva este run parcial (84 ticks completados antes del crash) porque
ya aportó señal real antes de cortarse: primer EAT disparado con el parser
corregido en un run con LLM real (tick 6, organismo `0998c63a`), confirmando
que el fix de parser (`cebea26`) tenía efecto en vivo, no solo en el
re-parseo offline de `184001`.
