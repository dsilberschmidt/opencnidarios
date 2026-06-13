# Run: p_action=0.5, 10000 ticks

Fecha: 2026-06-13
Config base: runs/configs/v02_two_energy_sources.json

## Parámetros relevantes

| parámetro | valor |
|---|---|
| `p_action` | 0.5 |
| `ticks` | 10000 |
| `regen_rate` | 0.1 |
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

DummyAdapter: pool unificado, pesos iniciales no uniformes (EAT=100, RS=5, resto=1),
salto de descubrimiento activo, `p_hidden` eliminado.

## Resultado

- Población sobrevivió los 10.000 ticks completos. No hubo extinción.
- Primeros nacimientos en tick 70. Cap `P_max=100` alcanzado; población estable
  en rango 93–97 durante los últimos ~6.000 ticks.
- Energía media creció de ~27 (tick 1) a ~10.611 (tick 10.000), tasa ~1 u/tick
  lineal sostenida. No se estabilizó — mismo problema de acumulación que v01.

| tick | población | energía media |
|------|-----------|---------------|
| 1 | 20 | 26.6 |
| 1000 | 42 | 490 |
| 3000 | 72 | 1.954 |
| 6000 | 97 | 4.915 |
| 10000 | 93 | 10.611 |

## Hipótesis PHOTOSYNTHESIZE

No confirmable sin logging de pesos o conteo de acciones por tipo. El CSV solo
registra estadísticas agregadas por tick. Señal indirecta: la energía crece a
tasa constante incluso cuando las celdas del mundo deberían estar agotadas por
la alta frecuencia de EAT (p_action=0.5, EAT≈90% del pool) — consistente con
contribución de PHOTOSYNTHESIZE. Requiere instrumentación para confirmar.

## Próximo experimento

regen_rate=0: eliminar regeneración del mundo para forzar dependencia total en
PHOTOSYNTHESIZE una vez que EAT agote las celdas.
