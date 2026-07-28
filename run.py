"""OpenCnidarios – simulation entrypoint.

Usage:
    python run.py --config runs/configs/v01_smoke_test.json
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime

from src.world import World
from src.ruminant import Ruminant
from src.engine import Engine
from src.llm_adapter.dummy import DummyAdapter
from src.llm_adapter.claude import ClaudeAdapter
from src.logger import Logger
from src.snapshot import write_snapshot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to run config JSON")
    parser.add_argument("--ticks", type=int, default=None, help="Override cfg['ticks']")
    parser.add_argument("--population", type=int, default=None, help="Override cfg['params']['P0']")
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = json.load(f)

    if args.ticks is not None:
        cfg["ticks"] = args.ticks
    if args.population is not None:
        cfg["params"]["P0"] = args.population

    params = cfg["params"]
    seed = cfg["seed"]
    random.seed(seed)

    world = World(n=params["N"], e_max=params.get("E_max", cfg["world_energy_hi"]), regen_rate=params["regen_rate"], cell_energy_hi=cfg["world_energy_hi"])
    world.seed_energy_uniform(cfg["world_energy_lo"], cfg["world_energy_hi"], seed=seed)

    adapter_cfg = cfg["adapter"]
    if adapter_cfg["type"] == "dummy":
        llm = DummyAdapter(p_action=adapter_cfg["p_action"], seed=seed)
    elif adapter_cfg["type"] == "llm":
        llm = ClaudeAdapter(
            model=adapter_cfg.get("model", "claude-haiku-4-5-20251001"),
            memory_cost_factor=adapter_cfg.get("memory_cost_factor", 0.00005),
            compression_interval=adapter_cfg.get("compression_interval", 20),
        )
    else:
        raise NotImplementedError(
            f"Adapter type '{adapter_cfg['type']}' not yet implemented."
        )

    run_id = f"{cfg['meta']['date']}_{cfg['meta']['name']}"
    out_dir = f"{cfg['out_dir']}_{datetime.now().strftime('%H%M%S')}"
    organisms_dir = "organisms"

    logger = Logger(
        out_dir=out_dir,
        run_id=run_id,
        event_logging=cfg.get("event_logging", False),
        interview_logging=cfg.get("interview_logging", False),
        ruminate_logging=cfg.get("ruminate_logging", False),
    )

    engine = Engine(world=world, llm_adapter=llm, params=params, logger=logger,
                    organisms_dir=organisms_dir, run_id=run_id)

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

    checkpoint_every = cfg.get("checkpoint_every")

    try:
        for _ in range(cfg["ticks"]):
            stats = engine.step()
            if stats.population == 0:
                break
            if (checkpoint_every is not None
                    and engine.tick % checkpoint_every == 0
                    and engine.tick < cfg["ticks"]):
                print(f"[checkpoint] tick={engine.tick} pop={stats.population} "
                      f"mean_e={stats.mean_internal_energy:.2f}")
                for r in engine.ruminants:
                    write_snapshot(r, cause="checkpoint", run_id=run_id,
                                   tick=engine.tick, adapter=llm,
                                   organisms_dir=organisms_dir)
                break
        else:
            for r in engine.ruminants:
                write_snapshot(r, cause="end_of_run", run_id=run_id,
                               tick=engine.tick, adapter=llm,
                               organisms_dir=organisms_dir)
    except Exception:
        for r in engine.ruminants:
            write_snapshot(r, cause="crash", run_id=run_id,
                           tick=engine.tick, adapter=llm,
                           organisms_dir=organisms_dir)
        raise
    finally:
        logger.close()


if __name__ == "__main__":
    main()
