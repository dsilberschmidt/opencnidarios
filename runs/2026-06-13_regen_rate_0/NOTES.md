# Run: regen_rate=0

Fecha: 2026-06-13
Config base: runs/configs/v02_two_energy_sources.json

## Parámetros relevantes

| parámetro | valor |
|---|---|
| `p_action` | 0.5 |
| `ticks` | 10000 |
| `regen_rate` | **0** |
| `base_metabolic_cost` | 0.4 |
| `photo_energy` | 4.0 |
| `feed_cap` | 6 |
| `feed_eff` | 1.0 |
| `repro_threshold` | 60 |
| `repro_cost` | 20 |
| `E_max` | 100 |
| `P0` | 20 |
| `P_max` | 100 |
| `e_i0` | 25 |
| `world_energy_lo` | 5 |
| `world_energy_hi` | 20 |
| `seed` | 42 |

## Resultado

- Población sobrevivió los 10.000 ticks completos. No hubo extinción.
- Die-off temprano: la población cayó de 20 a 11 organismos hacia el tick 200,
  luego se recuperó y creció hasta ~93–95 en los ticks tardíos.
- Energía media creció de ~27 (tick 1) a ~8.843 (tick 10.000).

| tick | población | energía media |
|------|-----------|---------------|
| 1 | 20 | 26.6 |
| 200 | 11 | 113 |
| 400 | 13 | 191 |
| 1000 | 22 | 470 |
| 3000 | 47 | 1.909 |
| 6000 | — | — |
| 10000 | 93 | 8.843 |

## Evidencia fuerte de descubrimiento de PHOTOSYNTHESIZE

Con `regen_rate=0` el mundo no regenera energía. Una vez que las celdas se agotan,
EAT aporta cero. Sin embargo la población sobrevivió y la energía creció de forma
sostenida durante 10.000 ticks. La única fuente de energía disponible después del
agotamiento celular es PHOTOSYNTHESIZE.

El die-off en tick ~200 es coherente con el mecanismo de descubrimiento:
- Organismos sin PHOTOSYNTHESIZE descubierto mueren cuando las celdas se agotan.
- Los que lo descubrieron por accidente (EAT weight=1.0 → salto a 100 al primer
  éxito → heredado por hijos) sobreviven y se reproducen.
- La recuperación de la población desde tick 200 en adelante refleja la propagación
  lamarckiana del descubrimiento.

Comparación con run anterior (regen_rate=0.1):
- Energía final: 8.843 vs 10.611 → ligeramente menor sin regeneración (esperado).
- Tasa de crecimiento similar (~0.88 vs ~1.06 u/tick) — consistente con PHOTOSYNTHESIZE
  siendo la fuente dominante en ambos casos una vez que las celdas se agotan.

## Conclusión

PHOTOSYNTHESIZE está siendo descubierto y explotado por los organismos. El salto de
descubrimiento y la herencia lamarckiana funcionan. Confirmar con logging de pesos
o conteo de acciones en próxima instrumentación.
