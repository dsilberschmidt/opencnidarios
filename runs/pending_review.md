# Commit: docs: v05_attack/NOTES.md

Branch: experiment/v02-two-energy-sources
Fecha: 2026-06-15

## Verificación del run

Run en `runs/2026-06-15_v05_attack/` es el **válido (post-fix)**:
- 5.493 eventos "attack" presentes en el JSONL
- 5.493 muertes por "attacked" (99.9% del total)
- Corrida bugueada fue sobreescrita al re-correr con el config corregido

## git log --oneline -3

```
2220e19 docs: v05_attack/NOTES.md — propósito, bugs corregidos y resultados del run
2529aa2 docs: pending_review.md — confirmación fix commiteado
f765230 docs: pending_review.md — actualizar log post-fix
```

## git diff HEAD~1 HEAD --stat

```
 runs/2026-06-15_v05_attack/NOTES.md | 91 +++++++++++++++++++++++++++++++++++++
 1 file changed, 91 insertions(+)
```
