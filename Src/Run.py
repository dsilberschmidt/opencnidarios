"""OpenCnidarios v0.1 – runnable entrypoint (with DummyAdapter).

This is a minimal end-to-end runner to validate:
- world energy + regeneration
- engine loop
- reproduction + absorption
- logging output

Later, replace DummyAdapter with a real adapter.
"""

from __future__ import annotations

import random

from src.world import World
from src.ruminant import Ruminant
from src.engine import Engine
from src.llm_adapter.dummy import DummyAdapter
from src.logger import Logger


def main():
    # Parameters (mirror docs/04_parameters_v1.md)
    params = {
        "N": 32,
        "E_max": 50,
        "regen_rate": 1,
        "P0": 20,
        "e_i0": 20,
        "max_tokens": 50,
        "token_cost": 0.05,
        "move_cost": 1.0,
        "feed_cap": 5,
        "feed_eff": 1.0,
        "repro_threshold": 40,
        "repro_cost": 2,
        "child_e0": 10,
        "absorb_ratio": 1.5,
        "absorb_frac": 0.30,
        "P_max": 200,
    }

    seed = 123
    random.seed(seed)

    # World
    world = World(n=params["N"], e_max=params["E_max"], regen_rate=params["regen_rate"])
    world.seed_energy_uniform(0, 20, seed=seed)

    # LLM adapter (dummy)
    llm = DummyAdapter(p_action=0.02, seed=seed)

    # Logger
    logger = Logger(out_dir="runs/latest")

    # Engine
    engine = Engine(world=world, llm_adapter=llm, params=params, logger=logger)

    # Seed population
    constitution = "You are a ruminant. Survive."
    memory = ""

    ruminants = []
    for _ in range(params["P0"]):
        x = random.randrange(params["N"])
        y = random.randrange(params["N"])
        r = Ruminant(
            x=x,
            y=y,
            energy_internal=float(params["e_i0"]),
            constitution_text=constitution,
            memory_text=memory,
        )
        ruminants.append(r)

    engine.seed_population(ruminants)

    # Run
    ticks = 500
    for _ in range(ticks):
        stats = engine.step()
        if stats.population == 0:
            break

    logger.close()


if __name__ == "__main__":
    main()
