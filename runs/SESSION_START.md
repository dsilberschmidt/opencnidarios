Leé CONTEXT.md completo. Estamos en la branch experiment/v02-two-energy-sources. No toques nada. Resumime el estado actual y confirmá que entendiste los próximos pasos antes de arrancar.

Reglas de trabajo:
1. Antes de implementar cualquier cosa, escribí el plan completo en runs/pending_review.md y esperá confirmación explícita ("adelante", "ejecutá", "dale") antes de tocar ningún archivo.
2. Todo output relevante va en runs/pending_review.md (sobreescribí, solo lo último) Y en terminal.
3. Actualizá CONTEXT.md cuando haya cambios de estado importantes.
4. Chequeá memoria y disco libre al inicio y cada ~30 minutos.
5. pending_review.md no se commitea — es un archivo de trabajo local, fuera de git. Todo contenido con valor permanente va a CONTEXT.md o al NOTES.md del run correspondiente.
6. Después de cada commit de código (.py, .html, .js), mostrá en terminal Y en runs/pending_review.md: git log --oneline -3 y git diff HEAD~1 HEAD -- '*.py' '*.html' '*.js'. Para commits de solo docs/data, alcanza con --stat.
