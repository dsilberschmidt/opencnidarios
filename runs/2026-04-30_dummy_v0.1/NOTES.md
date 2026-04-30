# Run Notes – 2026-04-30 – DummyAdapter v0.1

## Setup

- Engine: OpenCnidarios v0.1 scaffold
- Model adapter: DummyAdapter
- Grid: 32×32 toroidal
- Initial population: 20
- Ticks: 500
- Hidden action probability: 0.02
- Parameters: hardcoded in `run.py`

## Result

The run completed successfully and produced `ticks.csv`.

Population increased from 20 to 37.

Mean internal energy increased from ~24 at tick 1 to ~563 at tick 500.

## Interpretation

The engine is functional: ticks advance, population changes, movement events occur, births occur, deaths occur, and absorption events are logged.

However, the ecology is not yet balanced.

The main issue is runaway energy accumulation.

Probable causes:

- Staying still and feeding is too profitable.
- Global regeneration is too generous.
- There is no base metabolic cost per tick.
- DummyAdapter emits very short outputs, so token cost is negligible.
- Reproduction occurs by random emission of `RS`, not by learned behavior.

## Conclusion

This is a successful engine smoke test, but not yet a meaningful evolutionary run.
