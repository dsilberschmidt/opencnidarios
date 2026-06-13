# v04b_long_run

Config: `runs/configs/v04b_long_run.json`
Branch: `experiment/v02-two-energy-sources`
Fecha: 2026-06-13

## Propósito

Extender v04 a 100.000 ticks para ver si la población llega a una densidad
suficiente como para que ATTACK tenga sentido ecológico.

En v04 (10k ticks) la población llegó a 244 con P_max=1000 y un grid 32×32
(1024 celdas). A esa densidad hay ~0.24 organismos/celda — las colisiones son
poco frecuentes y ATTACK apenas mordería. La pregunta es si con más tiempo la
población se acerca al cap o alcanza una densidad donde las colisiones sean
frecuentes (~1+ organismo/celda en promedio).

## Parámetros clave

- N=32 (1024 celdas), P_max=1000
- regen_rate=0: PHOTOSYNTHESIZE es la única fuente renovable
- repro_cost=4, repro_threshold=60
- e_max_internal=100 (cap de energía interna)

## Resultados

| tick   | población | energía media |
|--------|-----------|---------------|
|      1 |        20 |         26.65 |
|  10000 |       244 |         94.14 |
|  25000 |       359 |         96.08 |
|  50000 |       404 |         97.92 |
|  75000 |       427 |         98.35 |
| 100000 |       439 |         99.11 |

## Conclusiones

- La población crece pero desacelera marcadamente: 244→359→404→427→439.
  Parece converger a un equilibrio en torno a ~440-460, lejos del cap de 1000.
- Densidad al tick 100k: 439/1024 ≈ 0.43 organismos/celda. Las colisiones ocurren
  pero no con frecuencia alta. ATTACK tiene sentido mecánico pero el impacto
  ecológico sería moderado con esta densidad.
- La energía media satura cerca del cap (99.11 al tick 100k), lo que confirma
  que `e_max_internal` funciona y que PHOTOSYNTHESIZE está siendo explotado
  de forma consistente por la mayoría de la población.
