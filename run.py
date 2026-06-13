"""OpenCnidarios – simulation entrypoint.

Usage:
    python run.py --config runs/configs/v01_smoke_test.json
"""

from __future__ import annotations

import argparse
import json
import random

from src.world import World
from src.ruminant import Ruminant
from src.engine import Engine
from src.llm_adapter.dummy import DummyAdapter
from src.logger import Logger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to run config JSON")
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = json.load(f)

    params = cfg["params"]
    seed = cfg["seed"]
    random.seed(seed)

    world = World(n=params["N"], e_max=params["E_max"], regen_rate=params["regen_rate"], cell_energy_hi=cfg["world_energy_hi"])
    world.seed_energy_uniform(cfg["world_energy_lo"], cfg["world_energy_hi"], seed=seed)

    adapter_cfg = cfg["adapter"]
    assert adapter_cfg["type"] == "dummy"
    llm = DummyAdapter(p_action=adapter_cfg["p_action"], seed=seed)

    run_id = f"{cfg['meta']['date']}_{cfg['meta']['name']}"
    logger = Logger(out_dir=cfg["out_dir"], run_id=run_id)

    engine = Engine(world=world, llm_adapter=llm, params=params, logger=logger)

    ruminants = []
    for _ in range(params["P0"]):
        x = random.randrange(params["N"])
        y = random.randrange(params["N"])
        r = Ruminant(
            x=x,
            y=y,
            energy_internal=float(params["e_i0"]),
            constitution_text=cfg["constitution"],
            memory_text=cfg["memory"],
        )
        ruminants.append(r)

    engine.seed_population(ruminants)

    for _ in range(cfg["ticks"]):
        stats = engine.step()
        if stats.population == 0:
            break

    logger.close()


if __name__ == "__main__":
    main()
